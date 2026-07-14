"""
AERIS-10P Radar Visualization Module
======================================
Real-time radar display: range profile, range-Doppler map, PPI, detection list.

Usage (standalone with synthetic data):
    python visualization.py

Usage (from control app):
    from visualization import RadarDisplay
    display = RadarDisplay(params)
    display.update(rdm, detections, frame_num=0, elapsed_s=0)
    plt.show()
"""

import queue
import threading
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
from typing import List, Optional
import logging

log = logging.getLogger(__name__)


# ─── Color theme ─────────────────────────────────────────────────────────────

DARK_BG   = '#1a1a2e'
DARK_AX   = '#16213e'
ACCENT    = '#00d4aa'   # teal
GRID      = '#0f3460'
TEXT      = '#e0e0e0'
HIGHLIGHT = '#ff4444'

def _apply_dark_theme():
    plt.rcParams.update({
        'figure.facecolor': DARK_BG,
        'axes.facecolor':   DARK_AX,
        'axes.edgecolor':   GRID,
        'axes.labelcolor':  TEXT,
        'xtick.color':      TEXT,
        'ytick.color':      TEXT,
        'text.color':       TEXT,
        'grid.color':       GRID,
        'grid.linestyle':   '--',
        'grid.alpha':       0.4,
    })


# ─── RadarDisplay ─────────────────────────────────────────────────────────────

class RadarDisplay:
    """
    Four-panel radar display:
      Upper-left:  Range profile (amplitude vs range)
      Upper-right: Range-Doppler map (2D color)
      Lower-left:  PPI (plan position indicator, polar plot)
      Lower-right: Detection table + system info
    """

    def __init__(self, params=None, title: str = 'AERIS-10P Radar'):
        _apply_dark_theme()
        self.params = params
        self.title  = title

        self.fig = plt.figure(figsize=(16, 9), dpi=100)
        self.fig.patch.set_facecolor(DARK_BG)
        self.fig.suptitle(f'  {title}  —  10 GHz FMCW Phased Array Radar',
                          fontsize=13, fontweight='bold',
                          color=ACCENT, fontfamily='monospace')

        gs = GridSpec(2, 3, figure=self.fig,
                      hspace=0.38, wspace=0.32,
                      left=0.06, right=0.97, top=0.91, bottom=0.07)

        self.ax_rp    = self.fig.add_subplot(gs[0, 0])           # range profile
        self.ax_rdm   = self.fig.add_subplot(gs[0, 1])           # range-Doppler
        self.ax_ppi   = self.fig.add_subplot(gs[0, 2], projection='polar')  # PPI
        self.ax_det   = self.fig.add_subplot(gs[1, 0])           # detections
        self.ax_info  = self.fig.add_subplot(gs[1, 1])           # system info
        self.ax_snr   = self.fig.add_subplot(gs[1, 2])           # SNR vs range

        self._ppi_history: list = []   # list of (timestamp, detections)
        self._rp_line = None
        self._rdm_im  = None
        self._setup_axes()

    def _setup_axes(self):
        p = self.params

        # ── Range profile ──────────────────────────────────────────
        ax = self.ax_rp
        ax.set_facecolor(DARK_AX)
        ax.set_title('Range Profile', color=ACCENT, fontsize=10, pad=6)
        ax.set_xlabel('Range [m]', fontsize=9)
        ax.set_ylabel('Amplitude [dB]', fontsize=9)
        ax.set_xlim([0, 4000 if p is None else p.max_range])
        ax.set_ylim([-20, 60])
        ax.grid(True)
        self._rp_line, = ax.plot([], [], color='#00ffaa', lw=1.2, label='Profile')
        ax.legend(fontsize=8, loc='upper right')

        # ── Range-Doppler map ──────────────────────────────────────
        ax = self.ax_rdm
        ax.set_facecolor(DARK_AX)
        ax.set_title('Range-Doppler Map', color=ACCENT, fontsize=10, pad=6)
        ax.set_xlabel('Range [m]', fontsize=9)
        ax.set_ylabel('Velocity [m/s]', fontsize=9)
        rmax = 4000 if p is None else p.max_range
        vmax = 7.5 if p is None else p.max_velocity
        dummy = np.zeros((100, 100))
        self._rdm_im = ax.imshow(
            dummy, aspect='auto', origin='lower',
            extent=[0, rmax, -vmax, vmax],
            cmap='plasma', vmin=-20, vmax=40
        )
        cb = plt.colorbar(self._rdm_im, ax=ax, label='dB', fraction=0.035, pad=0.02)
        cb.ax.yaxis.label.set_color(TEXT)
        cb.ax.tick_params(colors=TEXT)

        # ── PPI ────────────────────────────────────────────────────
        ax = self.ax_ppi
        ax.set_facecolor(DARK_AX)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_rlim([0, 4000 if p is None else min(p.max_range, 4000)])
        ax.set_rticks([500, 1000, 2000, 3000])
        ax.tick_params(labelcolor=TEXT)
        ax.set_title('PPI', color=ACCENT, fontsize=10, pad=20)

        # ── Detection table ────────────────────────────────────────
        ax = self.ax_det
        ax.set_facecolor(DARK_AX)
        ax.set_title('Detections', color=ACCENT, fontsize=10, pad=6)
        ax.axis('off')
        self._det_text = ax.text(
            0.02, 0.97, 'No detections',
            transform=ax.transAxes, va='top', ha='left',
            fontfamily='monospace', fontsize=8.5, color=TEXT
        )

        # ── System info ────────────────────────────────────────────
        ax = self.ax_info
        ax.set_facecolor(DARK_AX)
        ax.set_title('System', color=ACCENT, fontsize=10, pad=6)
        ax.axis('off')
        if p:
            info = (
                f"{'─'*32}\n"
                f" AERIS-10P  v1.0\n"
                f"{'─'*32}\n"
                f" {p.freq_start/1e9:.3f}–{p.freq_stop/1e9:.3f} GHz\n"
                f" BW: {p.bandwidth/1e6:.0f} MHz\n"
                f" Sweep: {p.sweep_time*1e3:.1f} ms\n"
                f" Chirps: {p.num_chirps}\n"
                f" Fs: {p.sample_rate:.0f} Hz\n"
                f"{'─'*32}\n"
                f" ΔR: {p.range_resolution:.1f} m\n"
                f" Rmax: {p.max_range:.0f} m\n"
                f" Vmax: ±{p.max_velocity:.1f} m/s\n"
                f"{'─'*32}\n"
                f" TX: {p.tx_power_dbm:.0f} dBm / {10**(p.tx_power_dbm/10)/1000:.2f} W\n"
                f" TX ant: {p.tx_gain_dbi:.0f} dBi\n"
                f" RX ant: {p.rx_gain_dbi:.0f} dBi\n"
            )
        else:
            info = " AERIS-10P\n Demo mode\n No params"
        ax.text(0.03, 0.97, info, transform=ax.transAxes, va='top', ha='left',
                fontfamily='monospace', fontsize=8, color=ACCENT,
                bbox=dict(boxstyle='round', facecolor='#0d1117', alpha=0.8))

        # ── SNR vs range curve ──────────────────────────────────────
        ax = self.ax_snr
        ax.set_facecolor(DARK_AX)
        ax.set_title('SNR vs Range', color=ACCENT, fontsize=10, pad=6)
        ax.set_xlabel('Range [km]', fontsize=9)
        ax.set_ylabel('SNR [dB]', fontsize=9)
        ax.grid(True)
        if p:
            ranges = np.linspace(100, min(p.max_range, 5000), 200)
            # Simplified SNR from radar equation
            snr_car = [self._snr_estimate(p, r, 10) for r in ranges]
            ax.plot(ranges/1000, snr_car, color='#00ffaa', lw=2, label='Car (10m²)')
            ax.axhline(15, color='red', ls='--', alpha=0.7, label='Threshold (15 dB)')
            ax.legend(fontsize=8)
            ax.set_ylim([-20, 80])

    @staticmethod
    def _snr_estimate(p, range_m: float, rcs_dbsm: float) -> float:
        """Quick SNR estimate for display."""
        lam   = p.c / ((p.freq_start + p.freq_stop) / 2)
        pi    = np.pi
        tx_w  = 10 ** (p.tx_power_dbm / 10) / 1000
        gt_lin = 10 ** (p.tx_gain_dbi / 10)
        gr_lin = 10 ** (p.rx_gain_dbi / 10)
        sigma = 10 ** (rcs_dbsm / 10)
        pr    = tx_w * gt_lin * gr_lin * lam**2 * sigma / ((4*pi)**3 * range_m**4)
        # IF noise BW for FMCW: ~10 Hz for 100 chirps × 1ms
        bw_if = 10.0
        nf_lin = 10 ** (p.noise_fig_db / 10)
        kTBF  = 1.38e-23 * 290 * bw_if * nf_lin
        return 10 * np.log10(pr / kTBF) if pr > 0 else -999

    # ── Update methods ────────────────────────────────────────────────────────

    def update(self, rdm: np.ndarray, detections: list,
               frame_num: int = 0, elapsed_s: float = 0.0):
        """Update all panels with new radar data."""
        if rdm is None:
            return

        # Range profile (Doppler-integrated)
        rdm_mag = np.abs(rdm)
        rp = 20 * np.log10(np.max(rdm_mag, axis=0) + 1e-12)
        rp -= np.median(rp)

        p = self.params
        rng_ax = np.linspace(0, p.max_range if p else 4000, len(rp))
        self._rp_line.set_data(rng_ax, rp)
        self.ax_rp.set_xlim([0, rng_ax[-1]])

        # Clear detection markers
        for line in self.ax_rp.lines[1:]:
            line.remove()
        for d in detections:
            self.ax_rp.axvline(d.range_m, color=HIGHLIGHT, alpha=0.5, lw=0.8)

        # Range-Doppler map
        rdm_db = 20 * np.log10(rdm_mag + 1e-12)
        rdm_db -= np.median(rdm_db)
        self._rdm_im.set_array(rdm_db)
        self._rdm_im.set_clim(vmin=-10, vmax=min(rdm_db.max() * 0.9, 50))

        # PPI
        cutoff = time.monotonic() - 5.0
        self._ppi_history = [(t, ds) for t, ds in self._ppi_history if t > cutoff]
        self._ppi_history.append((time.monotonic(), list(detections)))

        self.ax_ppi.cla()
        self.ax_ppi.set_theta_zero_location('N')
        self.ax_ppi.set_theta_direction(-1)
        rmax_ppi = p.max_range if p else 4000
        self.ax_ppi.set_rlim([0, min(rmax_ppi, 4000)])
        self.ax_ppi.set_rticks([500, 1000, 2000, 3000])
        self.ax_ppi.tick_params(labelcolor=TEXT)
        self.ax_ppi.set_facecolor(DARK_AX)
        self.ax_ppi.set_title(f'PPI  frame={frame_num}  t={elapsed_s:.0f}s',
                               color=ACCENT, fontsize=9, pad=20)

        for t_hist, dets in self._ppi_history:
            age = (time.monotonic() - t_hist) / 5.0
            alpha = max(0.08, 1.0 - age)
            for d in dets:
                az_rad = np.radians(getattr(d, 'az_deg', 0.0))
                self.ax_ppi.plot(az_rad, d.range_m, 'o',
                                 color=HIGHLIGHT, markersize=max(2, 8*alpha), alpha=alpha)

        # Detections text
        if detections:
            lines = [
                f"{'Range':>9} {'Vel':>8} {'SNR':>7}",
                f"{'[m]':>9} {'[m/s]':>8} {'[dB]':>7}",
                "─" * 28
            ]
            for d in sorted(detections, key=lambda x: x.range_m)[:8]:
                lines.append(f"{d.range_m:9.0f} {d.velocity_mps:8.1f} {d.snr_db:7.1f}")
        else:
            lines = ["  (no detections)"]
        self._det_text.set_text("\n".join(lines))

        self.fig.canvas.draw_idle()

    def save_snapshot(self, filename: str = 'aeris_snapshot.png', dpi: int = 150):
        """Save current display to PNG."""
        self.fig.savefig(filename, dpi=dpi, bbox_inches='tight',
                          facecolor=self.fig.get_facecolor())
        log.info(f"Snapshot saved: {filename}")


# ─── Animated loop ────────────────────────────────────────────────────────────

def run_live_display(data_queue: queue.Queue, params=None,
                     interval_ms: int = 500, title: str = 'AERIS-10P'):
    """
    Run animated radar display consuming (rdm, detections) tuples from queue.

    Args:
        data_queue: Queue of (rdm_array, detections_list) tuples
        params:     FMCWParams instance
        interval_ms: animation update interval
    """
    display = RadarDisplay(params, title=title)
    frame_counter = [0]
    t_start = [time.monotonic()]

    def _update(_frame_idx):
        try:
            rdm, dets = data_queue.get_nowait()
        except queue.Empty:
            return
        elapsed = time.monotonic() - t_start[0]
        display.update(rdm, dets, frame_counter[0], elapsed)
        frame_counter[0] += 1

    ani = animation.FuncAnimation(
        display.fig, _update, interval=interval_ms, cache_frame_data=False
    )
    plt.show()
    return display


# ─── Standalone demo ─────────────────────────────────────────────────────────

def main():
    """Standalone demo with synthetic FMCW data."""
    try:
        from fmcw_processing import FMCWParams, FMCWProcessor
    except ImportError:
        print("Run from Software/Signal_Processing/ directory.")
        return

    params = FMCWParams()
    proc   = FMCWProcessor(params)

    targets = [
        {'range_m': 450,  'velocity_mps': -15.0, 'snr_db': 40},
        {'range_m': 1100, 'velocity_mps':   8.0, 'snr_db': 30},
        {'range_m': 2600, 'velocity_mps':   0.0, 'snr_db': 20},
    ]

    display = RadarDisplay(params, title='AERIS-10P Demo')
    t_start = time.monotonic()

    def update_fn(frame_idx):
        t_sim = frame_idx * params.sweep_time * params.num_chirps
        mat   = proc.simulate_scenario(targets, t_start=t_sim)
        rdm   = proc.range_doppler_map(mat)
        dets  = proc.extract_detections(rdm, proc.cfar_ca_2d(np.abs(rdm)**2))
        elapsed = time.monotonic() - t_start
        display.update(rdm, dets, frame_idx, elapsed)

    ani = animation.FuncAnimation(
        display.fig, update_fn, interval=800, cache_frame_data=False
    )
    plt.show()


if __name__ == '__main__':
    main()
