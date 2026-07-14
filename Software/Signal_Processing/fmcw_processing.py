"""
AERIS-10P FMCW Radar Signal Processing Module
===============================================
Implements the complete FMCW signal processing pipeline:
  - Range FFT
  - Range-Doppler map (2D FFT)
  - Static clutter filtering (MTI / DC removal)
  - 1D and 2D CFAR detection
  - Detection extraction and formatting
  - Phase monopulse angle estimation
  - Target simulation for testing

Reference: Richards, Scheer, Holm — "Principles of Modern Radar" Vol. 1
"""

import numpy as np
from scipy import signal
from scipy.ndimage import label, center_of_mass
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import logging

log = logging.getLogger(__name__)


@dataclass
class FMCWParams:
    """FMCW system parameters — must match hardware configuration."""
    freq_start:    float = 10.00e9   # Hz
    freq_stop:     float = 10.10e9   # Hz
    sweep_time:    float = 1.0e-3    # s
    num_chirps:    int   = 100
    sample_rate:   float = 8000.0    # Hz
    tx_power_dbm:  float = 27.0
    tx_gain_dbi:   float = 22.0
    rx_gain_dbi:   float = 22.0
    noise_fig_db:  float = 2.0
    c:             float = 2.997e8

    @property
    def bandwidth(self) -> float:
        return self.freq_stop - self.freq_start

    @property
    def center_freq(self) -> float:
        return (self.freq_start + self.freq_stop) / 2.0

    @property
    def wavelength(self) -> float:
        return self.c / self.center_freq

    @property
    def range_resolution(self) -> float:
        return self.c / (2.0 * self.bandwidth)

    @property
    def sweep_rate(self) -> float:
        return self.bandwidth / self.sweep_time

    @property
    def max_range(self) -> float:
        return self.c * self.sample_rate / (4.0 * self.sweep_rate)

    @property
    def num_samples(self) -> int:
        return int(self.sample_rate * self.sweep_time)

    @property
    def max_velocity(self) -> float:
        return self.wavelength / (4.0 * self.sweep_time)

    @property
    def range_axis(self) -> np.ndarray:
        return np.linspace(0, self.max_range, self.num_samples // 2)

    @property
    def velocity_axis(self) -> np.ndarray:
        return np.fft.fftshift(
            np.fft.fftfreq(self.num_chirps, d=self.sweep_time) * self.wavelength / 2.0
        )

    def beat_freq(self, range_m: float) -> float:
        return 2.0 * range_m * self.bandwidth / (self.c * self.sweep_time)

    def doppler_freq(self, velocity_mps: float) -> float:
        return 2.0 * velocity_mps / self.wavelength


@dataclass
class Detection:
    range_m:      float
    velocity_mps: float
    amplitude_db: float
    snr_db:       float
    range_idx:    int
    vel_idx:      int
    az_deg:       float = 0.0
    el_deg:       float = 0.0


class FMCWProcessor:
    """Complete FMCW radar signal processing chain."""

    def __init__(self, params: FMCWParams):
        self.p = params
        self._rng = np.random.default_rng(seed=42)

    # ── Range FFT ─────────────────────────────────────────────────────

    def range_fft(self, beat_signal: np.ndarray,
                  window: str = 'hann',
                  n_fft: Optional[int] = None) -> np.ndarray:
        """
        Compute range FFT of one chirp's beat signal.

        Returns: complex one-sided spectrum, length n_fft//2
        Range axis: self.p.range_axis (same length)
        """
        n = len(beat_signal)
        n_fft = n_fft or n
        win = signal.get_window(window, n)
        spec = np.fft.fft(beat_signal * win, n=n_fft)
        return spec[:n_fft // 2]

    # ── Range-Doppler Map ─────────────────────────────────────────────

    def range_doppler_map(self,
                           chirp_matrix: np.ndarray,
                           range_window: str = 'hann',
                           doppler_window: str = 'hann',
                           clutter: str = 'dc_removal') -> np.ndarray:
        """
        Compute Range-Doppler Map from chirp matrix.

        Args:
            chirp_matrix: (num_chirps × num_samples) complex matrix
            range_window:   window for range FFT
            doppler_window: window for Doppler FFT
            clutter:        'dc_removal' | 'mti' | 'none'

        Returns:
            rdm: (num_chirps × num_samples//2) complex RDM
                 Axis 0: Doppler (velocity), fft-shifted
                 Axis 1: Range
        """
        Nc, Ns = chirp_matrix.shape
        n_rng = Ns

        # Range windowing + FFT
        rng_win = signal.get_window(range_window, Ns)
        range_processed = np.fft.fft(
            chirp_matrix * rng_win[np.newaxis, :],
            n=n_rng, axis=1
        )[:, :n_rng // 2]

        # Static clutter removal
        if clutter == 'dc_removal':
            # Subtract mean across chirps (removes zero-velocity clutter)
            range_processed -= range_processed.mean(axis=0, keepdims=True)
        elif clutter == 'mti':
            # 2-pulse MTI canceller
            range_processed = range_processed[1:] - range_processed[:-1]
            range_processed = np.vstack([np.zeros((1, n_rng // 2)), range_processed])

        # Doppler windowing + FFT (along chirp axis)
        dop_win = signal.get_window(doppler_window, Nc)
        rdm = np.fft.fftshift(
            np.fft.fft(range_processed * dop_win[:, np.newaxis], n=Nc, axis=0),
            axes=0
        )
        return rdm

    # ── CFAR Detection ────────────────────────────────────────────────

    def cfar_ca_1d(self,
                   profile: np.ndarray,
                   n_train: int = 16,
                   n_guard: int = 4,
                   pfa: float = 1e-4) -> np.ndarray:
        """
        1D Cell-Averaging CFAR detection.

        Args:
            profile: power profile (linear, not dB)
            n_train: number of training cells on each side
            n_guard: number of guard cells on each side
            pfa:     probability of false alarm

        Returns:
            mask: boolean detection mask (True = detection)
        """
        n = len(profile)
        mask = np.zeros(n, dtype=bool)
        # CA-CFAR threshold factor
        alpha = n_train * (pfa ** (-1.0 / n_train) - 1.0)

        for i in range(n):
            i_lo_tr = max(0, i - n_guard - n_train)
            i_lo_gd = max(0, i - n_guard)
            i_hi_gd = min(n, i + n_guard + 1)
            i_hi_tr = min(n, i + n_guard + n_train + 1)

            training = np.concatenate([
                profile[i_lo_tr:i_lo_gd],
                profile[i_hi_gd:i_hi_tr]
            ])
            if len(training) < max(1, n_train // 2):
                continue
            threshold = alpha * np.mean(training)
            mask[i] = profile[i] > threshold

        return mask

    def cfar_ca_2d(self,
                   power_map: np.ndarray,
                   n_train_r: int = 8,
                   n_guard_r: int = 2,
                   n_train_d: int = 4,
                   n_guard_d: int = 1,
                   pfa: float = 1e-5) -> np.ndarray:
        """
        2D Cell-Averaging CFAR on Range-Doppler map.

        Returns: boolean detection mask, same shape as power_map
        """
        Nd, Nr = power_map.shape
        mask = np.zeros_like(power_map, dtype=bool)

        # Total training cells
        n_train = (2*(n_train_r + n_guard_r) + 1) * (2*(n_train_d + n_guard_d) + 1) \
                  - (2*n_guard_r + 1) * (2*n_guard_d + 1)
        alpha = n_train * (pfa ** (-1.0 / n_train) - 1.0)

        # Use 2D convolution for efficiency
        kernel_total = np.ones((2*(n_train_d+n_guard_d)+1, 2*(n_train_r+n_guard_r)+1))
        kernel_guard = np.zeros_like(kernel_total)
        kernel_guard[n_train_d:n_train_d+2*n_guard_d+1,
                     n_train_r:n_train_r+2*n_guard_r+1] = 1.0

        from scipy.ndimage import convolve
        sum_total = convolve(power_map, kernel_total, mode='wrap')
        sum_guard = convolve(power_map, kernel_guard, mode='wrap')
        sum_train = sum_total - sum_guard

        n_guard_cells = (2*n_guard_r + 1) * (2*n_guard_d + 1)
        n_train_cells = np.count_nonzero(kernel_total) - n_guard_cells
        mean_train = sum_train / max(n_train_cells, 1)
        threshold_map = alpha * mean_train

        mask = power_map > threshold_map
        return mask

    # ── Detection Extraction ──────────────────────────────────────────

    def extract_detections(self,
                            rdm: np.ndarray,
                            cfar_mask: np.ndarray,
                            range_axis: Optional[np.ndarray] = None,
                            vel_axis: Optional[np.ndarray] = None,
                            noise_floor_db: float = -100.0) -> List[Detection]:
        """
        Extract individual detections from RDM and CFAR mask.

        Returns list of Detection objects.
        """
        if range_axis is None:
            range_axis = self.p.range_axis
        if vel_axis is None:
            vel_axis = self.p.velocity_axis

        rdm_mag = np.abs(rdm)
        rdm_db  = 20 * np.log10(rdm_mag + 1e-12)
        noise_floor = np.median(rdm_db)

        labeled, n_feats = label(cfar_mask)
        detections = []

        for feat_idx in range(1, n_feats + 1):
            region = (labeled == feat_idx)
            # Peak in region
            peak_idx = np.unravel_index(np.argmax(rdm_mag * region), rdm_mag.shape)
            d_idx, r_idx = peak_idx

            if r_idx >= len(range_axis) or d_idx >= len(vel_axis):
                continue

            amp_db = rdm_db[d_idx, r_idx]
            snr    = amp_db - noise_floor

            detections.append(Detection(
                range_m      = range_axis[r_idx],
                velocity_mps = vel_axis[d_idx],
                amplitude_db = amp_db,
                snr_db       = snr,
                range_idx    = int(r_idx),
                vel_idx      = int(d_idx),
            ))

        # Sort by range
        detections.sort(key=lambda d: d.range_m)
        return detections

    # ── Phase Monopulse Angle Estimation ──────────────────────────────

    def phase_monopulse_angle(self,
                               sig_a: np.ndarray,
                               sig_b: np.ndarray,
                               baseline_m: float,
                               freq_hz: float) -> float:
        """
        Estimate angle of arrival from two-element phase monopulse.

        Args:
            sig_a, sig_b: complex signals at two antennas
            baseline_m: separation between antennas [m]
            freq_hz: signal frequency [Hz]

        Returns: angle in degrees
        """
        lam = self.p.c / freq_hz
        # Phase difference
        dphi = np.angle(sig_a * np.conj(sig_b))
        # Angle: dphi = 2*pi/lambda * d * sin(theta)
        sin_theta = dphi * lam / (2.0 * np.pi * baseline_m)
        sin_theta = np.clip(sin_theta, -1.0, 1.0)
        return float(np.degrees(np.arcsin(sin_theta)))

    # ── Target Simulation ─────────────────────────────────────────────

    def simulate_target_return(self,
                                range_m: float,
                                velocity_mps: float,
                                rcs_dbsm: float,
                                snr_db: float,
                                t_start: float = 0.0) -> np.ndarray:
        """
        Generate synthetic FMCW beat signal for one chirp.

        Returns: (num_chirps × num_samples) complex matrix
        """
        p = self.p
        matrix = np.zeros((p.num_chirps, p.num_samples), dtype=complex)
        t_samples = np.arange(p.num_samples) / p.sample_rate
        sig_amp = np.sqrt(10.0 ** (snr_db / 10.0))

        for cidx in range(p.num_chirps):
            t_chirp = t_start + cidx * p.sweep_time
            R = range_m - velocity_mps * t_chirp
            if R <= 0 or R > p.max_range:
                continue
            f_beat    = p.beat_freq(R)
            phi_0     = -4.0 * np.pi * R * p.center_freq / p.c
            phi_dop   = 2.0 * np.pi * p.doppler_freq(velocity_mps) * t_chirp
            beat      = sig_amp * np.exp(1j * (2*np.pi*f_beat*t_samples + phi_dop + phi_0))
            noise     = (self._rng.standard_normal(p.num_samples)
                         + 1j * self._rng.standard_normal(p.num_samples)) / np.sqrt(2)
            matrix[cidx] = beat + noise

        return matrix

    def simulate_scenario(self,
                           targets: List[dict],
                           t_start: float = 0.0) -> np.ndarray:
        """
        Simulate multiple targets. Each target dict: {range_m, velocity_mps, snr_db}.
        Returns superposed complex chirp matrix.
        """
        p = self.p
        result = np.zeros((p.num_chirps, p.num_samples), dtype=complex)
        for tgt in targets:
            result += self.simulate_target_return(
                tgt['range_m'], tgt['velocity_mps'],
                tgt.get('rcs_dbsm', 10), tgt.get('snr_db', 20),
                t_start
            )
        return result

    # ── Utility ───────────────────────────────────────────────────────

    def range_profile(self, chirp_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Return (range_axis, range_profile_dB) from chirp matrix (Doppler-integrated)."""
        rdm = self.range_doppler_map(chirp_matrix)
        profile_db = 20 * np.log10(np.max(np.abs(rdm), axis=0) + 1e-12)
        profile_db -= np.median(profile_db)
        return self.p.range_axis, profile_db


def demo():
    """Quick self-test with synthetic targets."""
    params = FMCWParams()
    proc   = FMCWProcessor(params)

    targets = [
        {'range_m': 500,  'velocity_mps': -15.0, 'snr_db': 35},
        {'range_m': 1200, 'velocity_mps':   8.0, 'snr_db': 28},
        {'range_m': 2800, 'velocity_mps':   0.0, 'snr_db': 20},
    ]
    mat = proc.simulate_scenario(targets)
    rdm = proc.range_doppler_map(mat)
    rdm_pow = np.abs(rdm) ** 2
    mask = proc.cfar_ca_2d(rdm_pow)
    dets = proc.extract_detections(rdm, mask)

    print(f"FMCWProcessor demo: {len(dets)} detections found")
    print(f"{'Range [m]':>10}  {'Vel [m/s]':>10}  {'SNR [dB]':>10}")
    for d in dets:
        print(f"{d.range_m:10.0f}  {d.velocity_mps:10.1f}  {d.snr_db:10.1f}")
    return dets


if __name__ == '__main__':
    demo()
