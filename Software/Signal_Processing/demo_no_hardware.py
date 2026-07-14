"""
AERIS-10P Signal Processing Demo — No Hardware Required
========================================================
Generates synthetic FMCW radar data and runs the complete
signal processing pipeline including:
  - Range profile
  - Range-Doppler map
  - CFAR detection
  - Beam steering simulation
  - Animated display

Usage:
    python demo_no_hardware.py                    # basic demo
    python demo_no_hardware.py --targets 3        # 3 targets
    python demo_no_hardware.py --save-hdf5        # save session to HDF5
    python demo_no_hardware.py --no-display       # headless mode

Requirements: numpy, scipy, matplotlib
    pip install numpy scipy matplotlib
"""

import argparse
import logging
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from dataclasses import dataclass, field
from typing import List, Optional
import time

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

# ────────────────────────────────────────────────────────────────────
# AERIS-10P PARAMETERS (must match hardware configuration)
# ────────────────────────────────────────────────────────────────────

@dataclass
class FMCWParams:
    """FMCW radar parameters matching AERIS-10P hardware."""
    freq_start:     float = 10.00e9   # Hz — chirp start
    freq_stop:      float = 10.10e9   # Hz — chirp stop
    sweep_time:     float = 1.0e-3    # s  — chirp duration
    num_chirps:     int   = 100       # chirps per coherent processing interval
    sample_rate:    float = 8000.0    # Hz — ADC sample rate (ADS8661 decimated)
    tx_power_dbm:   float = 27.0      # dBm — PA output
    tx_gain_dbi:    float = 22.0      # dBi — TX array gain
    rx_gain_dbi:    float = 22.0      # dBi — RX array gain
    noise_figure_db: float = 2.0      # dB  — system NF (LNA dominated)
    c:              float = 2.997e8   # m/s — speed of light

    @property
    def bandwidth(self) -> float:
        return self.freq_stop - self.freq_start

    @property
    def center_freq(self) -> float:
        return (self.freq_start + self.freq_stop) / 2

    @property
    def wavelength(self) -> float:
        return self.c / self.center_freq

    @property
    def range_resolution(self) -> float:
        """Range resolution in meters: c/(2B)"""
        return self.c / (2 * self.bandwidth)

    @property
    def max_range(self) -> float:
        """Maximum unambiguous range: c * fs / (4 * sweep_rate)"""
        sweep_rate = self.bandwidth / self.sweep_time
        return self.c * self.sample_rate / (4 * sweep_rate)

    @property
    def num_samples(self) -> int:
        return int(self.sample_rate * self.sweep_time)

    @property
    def range_axis(self) -> np.ndarray:
        return np.linspace(0, self.max_range, self.num_samples // 2)

    @property
    def velocity_axis(self) -> np.ndarray:
        v_max = self.wavelength / (4 * self.sweep_time)
        return np.linspace(-v_max, v_max, self.num_chirps)

    @property
    def max_velocity(self) -> float:
        return self.wavelength / (4 * self.sweep_time)

    def beat_freq(self, range_m: float) -> float:
        """Beat frequency for a target at given range."""
        return 2 * range_m * self.bandwidth / (self.c * self.sweep_time)

    def doppler_freq(self, velocity_mps: float) -> float:
        """Doppler frequency for a target at given velocity."""
        return 2 * velocity_mps / self.wavelength

    def rx_power_dbm(self, range_m: float, rcs_dbsm: float) -> float:
        """Received power using radar range equation (dBm)."""
        lam = self.wavelength
        # Radar equation: Pr = Pt*Gt*Gr*lambda^2*sigma / ((4*pi)^3 * R^4)
        # In dB: Pr_dBW = Pt_dBW + Gt_dBi + Gr_dBi + 20log(lambda) + rcs_dBsm
        #                 - 30*log10(4pi) - 40*log10(R)
        pt_dbw = self.tx_power_dbm - 30  # dBW
        pr_dbw = (pt_dbw + self.tx_gain_dbi + self.rx_gain_dbi
                  + 20 * np.log10(lam) + rcs_dbsm
                  - 30 * np.log10(4 * np.pi)
                  - 40 * np.log10(range_m))
        return pr_dbw + 30  # dBm

    def noise_power_dbm(self) -> float:
        """Noise power in IF bandwidth (for FMCW, very narrow ~Hz)."""
        # Thermal noise: kTB where B is the equivalent noise BW ≈ 1/sweep_time for single target
        # For FMCW: B_noise ≈ 1/(num_chirps * sweep_time)
        b_noise = 1 / (self.num_chirps * self.sweep_time)
        kt_dbm_hz = -174.0  # dBm/Hz at 290K
        return kt_dbm_hz + 10 * np.log10(b_noise) + self.noise_figure_db

    def snr_db(self, range_m: float, rcs_dbsm: float) -> float:
        return self.rx_power_dbm(range_m, rcs_dbsm) - self.noise_power_dbm()


@dataclass
class Target:
    """Simulated radar target."""
    range_m:      float   # initial range [m]
    velocity_mps: float   # radial velocity [m/s], positive = approaching
    rcs_dbsm:     float   # radar cross section [dBm²]
    az_deg:       float = 0.0   # azimuth angle [deg]
    el_deg:       float = 0.0   # elevation angle [deg]
    label:        str  = ""

    def range_at_time(self, t: float) -> float:
        """Range at time t seconds."""
        return self.range_m - self.velocity_mps * t


# ────────────────────────────────────────────────────────────────────
# SIGNAL SYNTHESIS
# ────────────────────────────────────────────────────────────────────

class FMCWSynthesizer:
    """Generate synthetic FMCW beat signals."""

    def __init__(self, params: FMCWParams):
        self.p = params
        self.rng = np.random.default_rng(seed=42)

    def generate_chirp_matrix(self, targets: List[Target],
                               t_start: float = 0.0) -> np.ndarray:
        """
        Generate num_chirps × num_samples beat signal matrix.

        Returns array of shape (num_chirps, num_samples) with complex beat signal.
        """
        p = self.p
        matrix = np.zeros((p.num_chirps, p.num_samples), dtype=complex)

        t_samples = np.arange(p.num_samples) / p.sample_rate

        for chirp_idx in range(p.num_chirps):
            t_chirp = t_start + chirp_idx * p.sweep_time
            beat = np.zeros(p.num_samples, dtype=complex)

            for tgt in targets:
                # Range at this chirp
                R = tgt.range_at_time(t_chirp)
                if R <= 0 or R > p.max_range:
                    continue

                # Beat frequency
                f_beat = p.beat_freq(R)
                if f_beat > p.sample_rate / 2:
                    continue  # beyond Nyquist

                # Received power and amplitude
                snr = p.snr_db(R, tgt.rcs_dbsm)
                # Signal amplitude (SNR relative to noise)
                # Noise voltage std = 1.0 (normalized)
                sig_amplitude = np.sqrt(10 ** (snr / 10))

                # Beat signal: A * exp(j * 2*pi * f_beat * t + j * phi_doppler)
                # Doppler phase accumulation across chirps:
                phi_doppler = 2 * np.pi * p.doppler_freq(tgt.velocity_mps) * t_chirp

                # Phase of target return at start of this chirp:
                phi_0 = -4 * np.pi * R * p.center_freq / p.c

                beat_signal = sig_amplitude * np.exp(
                    1j * (2 * np.pi * f_beat * t_samples + phi_doppler + phi_0)
                )
                beat += beat_signal

            # Add complex Gaussian noise (normalized)
            noise = (self.rng.standard_normal(p.num_samples) +
                     1j * self.rng.standard_normal(p.num_samples)) / np.sqrt(2)
            matrix[chirp_idx] = beat + noise

        return matrix


# ────────────────────────────────────────────────────────────────────
# SIGNAL PROCESSING
# ────────────────────────────────────────────────────────────────────

class FMCWProcessor:
    """FMCW radar signal processing pipeline."""

    def __init__(self, params: FMCWParams):
        self.p = params

    def range_fft(self, beat_signal: np.ndarray,
                  window: str = 'hann') -> np.ndarray:
        """
        Compute range FFT of single chirp beat signal.
        Returns complex spectrum (one-sided, half length).
        """
        n = len(beat_signal)
        win = signal.get_window(window, n)
        windowed = beat_signal * win
        spectrum = np.fft.fft(windowed, n=n)
        return spectrum[:n // 2]

    def range_doppler_map(self, chirp_matrix: np.ndarray,
                           range_window: str = 'hann',
                           doppler_window: str = 'hann') -> np.ndarray:
        """
        Compute Range-Doppler Map from chirp matrix.

        Input: (num_chirps × num_samples) complex matrix
        Output: (num_chirps × num_samples//2) complex RDM
        """
        Nc, Ns = chirp_matrix.shape

        # Range FFT (along sample axis)
        range_win = signal.get_window(range_window, Ns)
        range_processed = np.fft.fft(chirp_matrix * range_win[np.newaxis, :],
                                      n=Ns, axis=1)[:, :Ns // 2]

        # Static clutter removal (mean subtraction per range bin)
        range_processed -= range_processed.mean(axis=0, keepdims=True)

        # Doppler FFT (along chirp axis)
        doppler_win = signal.get_window(doppler_window, Nc)
        rdm = np.fft.fftshift(
            np.fft.fft(range_processed * doppler_win[:, np.newaxis],
                       n=Nc, axis=0),
            axes=0
        )
        return rdm

    def cfar_ca_1d(self, profile: np.ndarray,
                   n_train: int = 16, n_guard: int = 4,
                   pfa: float = 1e-4) -> np.ndarray:
        """
        1D Cell-Averaging CFAR detector.
        Returns binary detection mask.
        """
        n = len(profile)
        mask = np.zeros(n, dtype=bool)
        alpha = n_train * (pfa ** (-1 / n_train) - 1)  # CA-CFAR threshold factor

        for i in range(n):
            # Training cells: avoid guard zone and cell under test
            left_idx = max(0, i - n_guard - n_train)
            left_end = max(0, i - n_guard)
            right_start = min(n, i + n_guard + 1)
            right_end = min(n, i + n_guard + n_train + 1)

            training = np.concatenate([
                profile[left_idx:left_end],
                profile[right_start:right_end]
            ])

            if len(training) < n_train // 2:
                continue

            threshold = alpha * np.mean(training)
            mask[i] = profile[i] > threshold

        return mask

    def extract_detections(self, rdm: np.ndarray,
                            range_axis: np.ndarray,
                            vel_axis: np.ndarray,
                            cfar_threshold_db: float = 15.0) -> list:
        """Extract detections from RDM above threshold."""
        rdm_mag = np.abs(rdm)
        # Normalize
        rdm_norm = rdm_mag / np.median(rdm_mag)
        rdm_db = 20 * np.log10(rdm_norm + 1e-12)

        detections = []
        # Simple threshold detector (replace with CFAR in production)
        above = rdm_db > cfar_threshold_db

        # Find connected components / peaks
        from scipy.ndimage import label, center_of_mass
        labeled, num_features = label(above)

        for feat_idx in range(1, num_features + 1):
            region = labeled == feat_idx
            cy, cx = center_of_mass(rdm_mag * region)  # (doppler, range) indices
            cy = int(round(cy))
            cx = int(round(cx))
            if 0 <= cx < len(range_axis) and 0 <= cy < len(vel_axis):
                detections.append({
                    'range_m':       range_axis[cx],
                    'velocity_mps':  vel_axis[cy],
                    'amplitude_db':  rdm_db[cy, cx],
                    'range_idx':     cx,
                    'vel_idx':       cy,
                })

        return detections


# ────────────────────────────────────────────────────────────────────
# VISUALIZATION
# ────────────────────────────────────────────────────────────────────

class RadarDisplay:
    """Real-time radar display with multiple subplots."""

    def __init__(self, params: FMCWParams, title: str = 'AERIS-10P Demo'):
        self.p = params
        plt.rcParams['figure.facecolor'] = '#1a1a2e'
        plt.rcParams['axes.facecolor'] = '#16213e'
        plt.rcParams['axes.edgecolor'] = '#0f3460'
        plt.rcParams['axes.labelcolor'] = '#e0e0e0'
        plt.rcParams['xtick.color'] = '#e0e0e0'
        plt.rcParams['ytick.color'] = '#e0e0e0'
        plt.rcParams['text.color'] = '#e0e0e0'
        plt.rcParams['grid.color'] = '#0f3460'
        plt.rcParams['grid.linestyle'] = '--'
        plt.rcParams['grid.alpha'] = 0.5

        self.fig = plt.figure(figsize=(16, 9), dpi=100)
        self.fig.patch.set_facecolor('#1a1a2e')
        self.fig.suptitle(f'  {title}  —  AERIS-10P 10 GHz FMCW Phased-Array Radar',
                          fontsize=14, fontweight='bold', color='#00d4aa',
                          fontfamily='monospace')

        gs = self.fig.add_gridspec(2, 3, hspace=0.35, wspace=0.35,
                                    left=0.07, right=0.97, top=0.92, bottom=0.08)
        self.ax_range   = self.fig.add_subplot(gs[0, 0])
        self.ax_rdm     = self.fig.add_subplot(gs[0, 1])
        self.ax_ppi     = self.fig.add_subplot(gs[0, 2], projection='polar')
        self.ax_detect  = self.fig.add_subplot(gs[1, 0])
        self.ax_info    = self.fig.add_subplot(gs[1, 1])
        self.ax_link    = self.fig.add_subplot(gs[1, 2])

        self._setup_axes()
        self._ppi_history = []

    def _setup_axes(self):
        p = self.p
        # Range profile
        self.ax_range.set_title('Range Profile', color='#00d4aa', fontsize=10)
        self.ax_range.set_xlabel('Range [m]')
        self.ax_range.set_ylabel('Amplitude [dB]')
        self.ax_range.set_xlim([0, p.max_range])
        self.ax_range.set_ylim([-20, 60])
        self.line_range, = self.ax_range.plot([], [], 'g-', lw=1.5)

        # Range-Doppler map
        self.ax_rdm.set_title('Range-Doppler Map', color='#00d4aa', fontsize=10)
        self.ax_rdm.set_xlabel('Range [m]')
        self.ax_rdm.set_ylabel('Velocity [m/s]')
        dummy_rdm = np.zeros((p.num_chirps, p.num_samples // 2))
        self.im_rdm = self.ax_rdm.imshow(
            dummy_rdm, aspect='auto', origin='lower',
            extent=[0, p.max_range, -p.max_velocity, p.max_velocity],
            cmap='plasma', vmin=-20, vmax=40
        )
        plt.colorbar(self.im_rdm, ax=self.ax_rdm, label='dB').ax.yaxis.label.set_color('#e0e0e0')

        # PPI plot (polar)
        self.ax_ppi.set_title('PPI Display', color='#00d4aa', fontsize=10, pad=20)
        self.ax_ppi.set_theta_zero_location('N')
        self.ax_ppi.set_theta_direction(-1)
        self.ax_ppi.set_rlim([0, min(p.max_range, 4000)])
        self.ax_ppi.set_rticks([500, 1000, 2000, 3000])
        self.ax_ppi.set_rlabel_position(45)
        self.ax_ppi.tick_params(labelcolor='#e0e0e0')

        # Detection list
        self.ax_detect.set_title('Detections', color='#00d4aa', fontsize=10)
        self.ax_detect.axis('off')
        self.det_text = self.ax_detect.text(
            0.02, 0.98, 'No detections', transform=self.ax_detect.transAxes,
            va='top', ha='left', fontfamily='monospace', fontsize=8,
            color='#e0e0e0'
        )

        # System info panel
        self.ax_info.set_title('System Status', color='#00d4aa', fontsize=10)
        self.ax_info.axis('off')
        info = (
            f"{'─'*35}\n"
            f" AERIS-10P  v1.0   DEMO MODE\n"
            f"{'─'*35}\n"
            f" Freq:    {p.freq_start/1e9:.3f} – {p.freq_stop/1e9:.3f} GHz\n"
            f" BW:      {p.bandwidth/1e6:.0f} MHz\n"
            f" Sweep:   {p.sweep_time*1e3:.1f} ms\n"
            f" Chirps:  {p.num_chirps}\n"
            f" Fs:      {p.sample_rate:.0f} Hz\n"
            f"{'─'*35}\n"
            f" ΔR:      {p.range_resolution:.1f} m\n"
            f" R_max:   {p.max_range:.0f} m\n"
            f" V_max:   ±{p.max_velocity:.1f} m/s\n"
            f"{'─'*35}\n"
            f" TX pwr:  {p.tx_power_dbm:.0f} dBm ({10**(p.tx_power_dbm/10)/1000:.1f} W)\n"
            f" TX ant:  {p.tx_gain_dbi:.0f} dBi (4×4 array)\n"
            f" RX ant:  {p.rx_gain_dbi:.0f} dBi (4×4 array)\n"
            f" NF:      {p.noise_figure_db:.0f} dB\n"
            f"{'─'*35}\n"
            f" STATUS:  DEMO MODE\n"
            f" HW:      NOT CONNECTED\n"
        )
        self.ax_info.text(0.02, 0.98, info, transform=self.ax_info.transAxes,
                          va='top', ha='left', fontfamily='monospace', fontsize=7.5,
                          color='#00d4aa',
                          bbox=dict(boxstyle='round', facecolor='#0d1117', alpha=0.8))

        # Link budget
        self.ax_link.set_title('SNR vs Range', color='#00d4aa', fontsize=10)
        ranges = np.linspace(100, p.max_range, 200)
        snr_car = [p.snr_db(r, 10) for r in ranges]   # car σ=10m²=10dBsm
        snr_person = [p.snr_db(r, 0) for r in ranges]  # person σ=1m²=0dBsm
        self.ax_link.plot(ranges, snr_car, 'g-', lw=2, label='Car (10m²)')
        self.ax_link.plot(ranges, snr_person, 'y-', lw=2, label='Person (1m²)')
        self.ax_link.axhline(15, color='r', ls='--', alpha=0.8, label='SNR=15 dB (detect)')
        self.ax_link.set_xlabel('Range [m]')
        self.ax_link.set_ylabel('SNR [dB]')
        self.ax_link.legend(fontsize=7, loc='upper right')
        self.ax_link.set_ylim([-20, 80])
        self.ax_link.set_xlim([0, p.max_range])
        self.ax_link.grid(True)

    def update(self, rdm: np.ndarray, detections: list,
               frame_num: int, elapsed_s: float) -> None:
        """Update all display panels with new data."""
        p = self.p
        rdm_mag = np.abs(rdm)

        # Range profile (Doppler-integrated)
        range_profile = 20 * np.log10(np.max(rdm_mag, axis=0) + 1e-12)
        range_profile -= np.median(range_profile)
        self.line_range.set_data(p.range_axis, range_profile)
        for det in detections:
            self.ax_range.axvline(det['range_m'], color='r', alpha=0.5, lw=1)

        # Range-Doppler map
        rdm_db = 20 * np.log10(rdm_mag + 1e-12)
        rdm_db -= np.median(rdm_db)
        self.im_rdm.set_array(rdm_db)
        self.im_rdm.set_clim(vmin=-10, vmax=rdm_db.max() * 0.9)

        # Detections text
        if detections:
            det_lines = [f"{'Range':>8} {'Vel':>8} {'Amp':>7}",
                         f"{'[m]':>8} {'[m/s]':>8} {'[dB]':>7}",
                         "─" * 26]
            for d in sorted(detections, key=lambda x: x['range_m'])[:8]:
                det_lines.append(
                    f"{d['range_m']:>8.0f} {d['velocity_mps']:>8.1f} {d['amplitude_db']:>7.1f}"
                )
        else:
            det_lines = ["  No detections"]
        self.det_text.set_text("\n".join(det_lines))

        # PPI (add detections as dots, fade history)
        self._ppi_history.append((time.time(), detections[:]))
        # Remove old history (>5 s)
        cutoff = time.time() - 5.0
        self._ppi_history = [(t, d) for t, d in self._ppi_history if t > cutoff]

        self.ax_ppi.cla()
        self.ax_ppi.set_theta_zero_location('N')
        self.ax_ppi.set_theta_direction(-1)
        self.ax_ppi.set_rlim([0, min(p.max_range, 4000)])
        self.ax_ppi.set_rticks([500, 1000, 2000, 3000])
        self.ax_ppi.tick_params(labelcolor='#e0e0e0')
        self.ax_ppi.set_title(f'PPI  |  Frame {frame_num}  |  t={elapsed_s:.1f}s',
                               color='#00d4aa', fontsize=9, pad=20)

        for t_hist, dets in self._ppi_history:
            age = (time.time() - t_hist) / 5.0
            alpha = max(0.1, 1.0 - age)
            for d in dets:
                az_rad = np.radians(d.get('az_deg', 0))
                r = d['range_m']
                self.ax_ppi.plot(az_rad, r, 'o', color='#ff4444',
                                  markersize=6 * alpha, alpha=alpha)

        self.fig.canvas.draw_idle()


# ────────────────────────────────────────────────────────────────────
# DEMO SCENARIOS
# ────────────────────────────────────────────────────────────────────

def make_targets(scenario: str = 'default') -> List[Target]:
    """Return list of targets for given scenario."""
    scenarios = {
        'default': [
            Target(range_m=500,  velocity_mps=-15.0, rcs_dbsm=10, az_deg=0,
                   label='Car approaching at 54 km/h'),
            Target(range_m=1200, velocity_mps=8.0,   rcs_dbsm=10, az_deg=10,
                   label='Car receding at 29 km/h'),
            Target(range_m=2800, velocity_mps=0.0,   rcs_dbsm=20, az_deg=-5,
                   label='Large static reflector (building)'),
        ],
        'highway': [
            Target(range_m=300,  velocity_mps=-30.0, rcs_dbsm=12, az_deg=-2,  label='Truck'),
            Target(range_m=800,  velocity_mps=-25.0, rcs_dbsm=10, az_deg=3,   label='Car 1'),
            Target(range_m=1100, velocity_mps=-22.0, rcs_dbsm=10, az_deg=-1,  label='Car 2'),
            Target(range_m=1500, velocity_mps=28.0,  rcs_dbsm=10, az_deg=2,   label='Oncoming'),
        ],
        'long_range': [
            Target(range_m=1500, velocity_mps=-20.0, rcs_dbsm=15, az_deg=0,   label='Vehicle 1'),
            Target(range_m=2500, velocity_mps=-15.0, rcs_dbsm=15, az_deg=5,   label='Vehicle 2'),
            Target(range_m=3500, velocity_mps=-10.0, rcs_dbsm=20, az_deg=-3,  label='Truck'),
        ],
        'single': [
            Target(range_m=1000, velocity_mps=-20.0, rcs_dbsm=10, az_deg=0,   label='Test target'),
        ],
    }
    return scenarios.get(scenario, scenarios['default'])


# ────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='AERIS-10P FMCW Radar Demo (no hardware required)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Scenarios: default, highway, long_range, single

Examples:
  python demo_no_hardware.py
  python demo_no_hardware.py --scenario highway --frames 50
  python demo_no_hardware.py --scenario long_range --save-png
  python demo_no_hardware.py --no-display --frames 10  # headless
        """
    )
    parser.add_argument('--scenario', default='default',
                        choices=['default', 'highway', 'long_range', 'single'],
                        help='Target scenario')
    parser.add_argument('--frames', type=int, default=20,
                        help='Number of animation frames')
    parser.add_argument('--interval-ms', type=int, default=800,
                        help='Animation frame interval [ms]')
    parser.add_argument('--no-display', action='store_true',
                        help='Headless mode: no animation')
    parser.add_argument('--save-png', action='store_true',
                        help='Save final frame as PNG')
    parser.add_argument('--print-link-budget', action='store_true',
                        help='Print link budget table and exit')
    args = parser.parse_args()

    params = FMCWParams()
    targets = make_targets(args.scenario)

    if args.print_link_budget:
        print("\nAERIS-10P Link Budget")
        print("=" * 60)
        print(f"{'Parameter':<30} {'Value':>15} {'Unit'}")
        print("─" * 60)
        print(f"{'TX power':<30} {params.tx_power_dbm:>15.1f} dBm")
        print(f"{'TX antenna gain':<30} {params.tx_gain_dbi:>15.1f} dBi")
        print(f"{'RX antenna gain':<30} {params.rx_gain_dbi:>15.1f} dBi")
        print(f"{'Noise figure':<30} {params.noise_figure_db:>15.1f} dB")
        print(f"{'Center wavelength':<30} {params.wavelength*1e3:>15.2f} mm")
        print(f"{'Chirp bandwidth':<30} {params.bandwidth/1e6:>15.0f} MHz")
        print(f"{'Range resolution':<30} {params.range_resolution:>15.1f} m")
        print(f"{'Max range (Nyquist)':<30} {params.max_range:>15.0f} m")
        print(f"{'Max velocity':<30} {params.max_velocity:>15.1f} m/s")
        print("─" * 60)
        print(f"\nSNR vs Range (car target, σ=10 m²):")
        for r in [100, 250, 500, 1000, 2000, 3000, 4000]:
            snr = params.snr_db(r, 10)
            detect = '✓' if snr > 15 else '✗'
            print(f"  R = {r:5d} m: SNR = {snr:6.1f} dB  {detect}")
        return

    log.info(f"AERIS-10P Demo starting — scenario: {args.scenario}")
    log.info(f"System parameters: BW={params.bandwidth/1e6:.0f}MHz, "
             f"Nc={params.num_chirps}, ΔR={params.range_resolution:.1f}m, "
             f"Rmax={params.max_range:.0f}m")
    log.info(f"Targets: {len(targets)}")
    for t in targets:
        snr = params.snr_db(t.range_m, t.rcs_dbsm)
        log.info(f"  {t.label}: R={t.range_m:.0f}m, v={t.velocity_mps:.1f}m/s, "
                 f"RCS={t.rcs_dbsm:.0f}dBsm, SNR={snr:.1f}dB")

    synth = FMCWSynthesizer(params)
    proc  = FMCWProcessor(params)

    if args.no_display:
        log.info("Headless mode: processing without display")
        for frame in range(args.frames):
            t0 = time.time()
            mat = synth.generate_chirp_matrix(targets, t_start=frame * params.sweep_time * params.num_chirps)
            rdm = proc.range_doppler_map(mat)
            rdm_mag = np.abs(rdm)
            rdm_norm = rdm_mag / (np.median(rdm_mag) + 1e-12)
            rdm_db = 20 * np.log10(rdm_norm + 1e-12)
            detections = proc.extract_detections(rdm, params.range_axis, params.velocity_axis)
            elapsed = time.time() - t0
            log.info(f"Frame {frame+1}/{args.frames}: {len(detections)} detections, "
                     f"processing time {elapsed*1e3:.0f} ms")
        log.info("Demo complete (headless)")
        return

    # Animated display
    display = RadarDisplay(params, title=f'Scenario: {args.scenario}')
    frame_counter = [0]
    t_start = [time.time()]

    def animate(frame_idx):
        t_sim = frame_idx * params.sweep_time * params.num_chirps
        mat = synth.generate_chirp_matrix(targets, t_start=t_sim)
        rdm = proc.range_doppler_map(mat)
        detections = proc.extract_detections(rdm, params.range_axis, params.velocity_axis)
        elapsed = time.time() - t_start[0]
        display.update(rdm, detections, frame_idx, elapsed)
        frame_counter[0] += 1

    ani = animation.FuncAnimation(
        display.fig, animate,
        frames=args.frames if args.frames > 0 else None,
        interval=args.interval_ms,
        repeat=True
    )

    if args.save_png:
        animate(0)
        outfile = f'aeris_demo_{args.scenario}.png'
        display.fig.savefig(outfile, dpi=120, bbox_inches='tight',
                             facecolor=display.fig.get_facecolor())
        log.info(f"Saved: {outfile}")

    plt.show()
    log.info("Demo complete.")


if __name__ == '__main__':
    main()
