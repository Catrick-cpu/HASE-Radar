"""
AERIS-10P FMCW Radar Link Budget Calculator
============================================
Computes the complete radar link budget for the AERIS-10P system.
Generates console output, CSV file, and optional matplotlib plot.

Usage:
    python link_budget_calculator.py               # standard link budget
    python link_budget_calculator.py --plot        # with plot
    python link_budget_calculator.py --csv out.csv # save to CSV
    python link_budget_calculator.py --sweep       # range sweep
    python link_budget_calculator.py --monte-carlo # statistical analysis

Reference: Skolnik, "Introduction to Radar Systems", 3rd ed.
           Richards, Scheer, Holm, "Principles of Modern Radar", Vol. 1
"""

import argparse
import csv
import math
import sys
from dataclasses import dataclass, field
from typing import Optional

try:
    import numpy as np
    import matplotlib.pyplot as plt
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("Note: numpy/matplotlib not found. Install for plots: pip install numpy matplotlib")

# ────────────────────────────────────────────────────────────────────
# AERIS-10P SYSTEM PARAMETERS
# ────────────────────────────────────────────────────────────────────

@dataclass
class SystemParams:
    """Complete AERIS-10P system parameters for link budget."""

    # Waveform
    freq_center_hz:     float = 10.05e9   # Hz
    bandwidth_hz:       float = 100e6     # Hz — FMCW chirp BW
    sweep_time_s:       float = 1e-3      # s  — chirp duration
    num_chirps:         int   = 100       # chirps per CPI
    sample_rate_hz:     float = 8000.0   # Hz — ADC rate

    # Transmitter
    tx_power_dbm:       float = 27.0      # dBm — PA output (+27 conservative, +30 max)
    tx_cable_loss_db:   float = 0.5       # dB  — PA to power divider
    tx_divider_loss_db: float = 13.0      # dB  — 1:16 Wilkinson (ideal: 12.04, +1 loss)
    tx_phase_shift_loss_db: float = 4.0  # dB  — HMC647A insertion loss
    tx_feed_loss_db:    float = 0.3       # dB  — feed line to patch

    # TX Antenna Array
    tx_element_gain_dbi: float = 6.0     # dBi — single patch element gain
    tx_n_elements:       int   = 16      # 4×4 array
    tx_efficiency:       float = 0.85    # array efficiency (mutual coupling, errors)

    # Propagation
    freq_dependent_loss_db: float = 0.0  # dB  — atmospheric (negligible at 10 GHz, <3km)
    rain_loss_db_per_km: float = 0.01   # dB/km — light rain (ITU-R P.838)
    range_km:           float = 3.0     # km  — nominal analysis range

    # Target
    target_rcs_dbsm:    float = 10.0    # dBm² — car σ ≈ 10m² = 10 dBsm

    # RX Antenna Array
    rx_n_elements:      int   = 16      # 4×4 array
    rx_element_gain_dbi: float = 6.0   # dBi
    rx_efficiency:      float = 0.85

    # Receiver chain
    rx_feed_loss_db:    float = 0.3     # dB  — patch to phase shifter
    rx_phase_shift_loss_db: float = 4.0 # dB  — HMC647A
    rx_combiner_loss_db: float = 1.0   # dB  — 16:1 Wilkinson + combiner loss
    lna_gain_db:        float = 18.0   # dB  — HMC1040
    lna_nf_db:          float = 1.5    # dB  — HMC1040
    mixer_conversion_loss_db: float = 6.0  # dB — HMC213B
    mixer_nf_db:        float = 6.0    # dB  — (same as conversion loss for passive mixer)
    if_amp_gain_db:     float = 20.0   # dB  — post-mixer IF amplifier
    if_amp_nf_db:       float = 5.0    # dB  — IF amplifier noise figure

    # Detection
    required_snr_db:    float = 15.0   # dB  — detection threshold (Pd=0.9, Pfa=1e-6)

    # Physical constants
    c_mps:              float = 2.997e8  # m/s
    t0_kelvin:          float = 290.0   # K   — reference temperature
    k_joules_kelvin:    float = 1.38e-23 # J/K — Boltzmann constant

    @property
    def wavelength_m(self) -> float:
        return self.c_mps / self.freq_center_hz

    @property
    def tx_array_gain_dbi(self) -> float:
        """TX array gain including element gain and array factor."""
        n = self.tx_n_elements
        af_gain_dbi = 10 * math.log10(n)  # array factor gain = N for uniform
        efficiency_db = 10 * math.log10(self.tx_efficiency)
        return self.tx_element_gain_dbi + af_gain_dbi + efficiency_db

    @property
    def rx_array_gain_dbi(self) -> float:
        """RX array gain including element gain and array factor."""
        n = self.rx_n_elements
        af_gain_dbi = 10 * math.log10(n)
        efficiency_db = 10 * math.log10(self.rx_efficiency)
        return self.rx_element_gain_dbi + af_gain_dbi + efficiency_db

    @property
    def if_noise_bandwidth_hz(self) -> float:
        """Effective noise bandwidth at IF for FMCW.

        For FMCW: beat frequency for range R is f_beat = 2*R*B/(c*T).
        The maximum beat freq for max range: f_beat_max = 2*Rmax*B/(c*T).
        For R_max = max_range using Nyquist: f_beat_max = fs/2.
        Noise BW ≈ 1/T_CPI = 1/(num_chirps * sweep_time).

        This is the effective noise BW after range FFT and Doppler FFT processing.
        """
        return 1.0 / (self.num_chirps * self.sweep_time_s)

    @property
    def system_nf_db(self) -> float:
        """Cascaded noise figure of RX chain (Friis formula).

        Chain: RX antenna → RX feed loss → RX phase shifter loss →
               RX combiner loss → LNA → Mixer → IF Amp

        Note: losses before LNA add directly to noise figure.
        """
        # Pre-LNA losses (add directly)
        pre_lna_loss_db = (self.rx_feed_loss_db + self.rx_phase_shift_loss_db
                           + self.rx_combiner_loss_db)
        pre_lna_nf_db = pre_lna_loss_db  # lossy networks have NF = loss

        # LNA stage
        lna_nf_lin = 10 ** (self.lna_nf_db / 10)
        lna_gain_lin = 10 ** (self.lna_gain_db / 10)

        # Mixer stage
        mix_nf_lin = 10 ** (self.mixer_nf_db / 10)
        mix_gain_lin = 10 ** (-self.mixer_conversion_loss_db / 10)

        # IF Amp stage
        if_nf_lin = 10 ** (self.if_amp_nf_db / 10)

        # Friis: NF_sys = NF1 + (NF2-1)/G1 + (NF3-1)/(G1*G2) + ...
        pre_lna_nf_lin = 10 ** (pre_lna_nf_db / 10)
        pre_lna_gain_lin = 10 ** (-pre_lna_loss_db / 10)  # gain = 1/loss

        total_nf_lin = (pre_lna_nf_lin
                        + (lna_nf_lin - 1) / pre_lna_gain_lin
                        + (mix_nf_lin - 1) / (pre_lna_gain_lin * lna_gain_lin)
                        + (if_nf_lin - 1) / (pre_lna_gain_lin * lna_gain_lin * mix_gain_lin))

        return 10 * math.log10(total_nf_lin)

    @property
    def noise_power_dbm(self) -> float:
        """Thermal noise power in IF noise bandwidth."""
        kt0 = self.k_joules_kelvin * self.t0_kelvin
        noise_bw = self.if_noise_bandwidth_hz
        kt0b_dbw = 10 * math.log10(kt0 * noise_bw)
        return kt0b_dbw + 30 + self.system_nf_db  # dBm

    @property
    def processing_gain_db(self) -> float:
        """Coherent processing gain from range FFT + Doppler FFT.

        Range FFT: N_samp/2 samples → gain ≈ 10*log10(N_samp/2) for peak
        Doppler FFT: N_chirps → gain ≈ 10*log10(N_chirps)
        Total processing gain (approximate): 10*log10(N_samp/2 * N_chirps)

        Note: this is already implicit in the IF noise bandwidth calculation.
        Here we compute explicitly for the budget.
        """
        n_samp = int(self.sample_rate_hz * self.sweep_time_s)
        pg_range = 10 * math.log10(n_samp / 2)
        pg_doppler = 10 * math.log10(self.num_chirps)
        return pg_range + pg_doppler


def compute_link_budget(params: SystemParams, range_m: Optional[float] = None):
    """Compute complete radar link budget."""
    p = params
    R = range_m if range_m is not None else p.range_km * 1000

    lam = p.wavelength_m
    pi = math.pi

    # ─── TX side ─────────────────────────────────────────────────────
    tx_power_dbw      = p.tx_power_dbm - 30
    tx_total_loss_db  = p.tx_cable_loss_db + p.tx_divider_loss_db + p.tx_phase_shift_loss_db + p.tx_feed_loss_db
    tx_element_power_dbm = p.tx_power_dbm - p.tx_divider_loss_db  # power per element (before phase shifter)
    tx_eirp_dbm       = p.tx_power_dbm - tx_total_loss_db + p.tx_array_gain_dbi

    # ─── Path ────────────────────────────────────────────────────────
    fspl_db = 20 * math.log10(4 * pi * R / lam)  # one-way free-space path loss
    two_way_fspl_db = 2 * fspl_db                 # two-way (TX → target → RX)
    rcs_db_lambda4 = 10 * math.log10(p.target_rcs_dbsm / (4 * pi * lam**2))

    # Rain/atmospheric
    atm_loss_db = p.rain_loss_db_per_km * (R / 1000) * 2  # two-way

    # ─── RX side ─────────────────────────────────────────────────────
    rx_total_loss_db = p.rx_feed_loss_db + p.rx_phase_shift_loss_db + p.rx_combiner_loss_db

    # ─── Received power (radar range equation in dB) ──────────────────
    # Pr_dBm = Pt_dBm + Gt_dBi + Gr_dBi + 20log(lam) + RCS_dBsm
    #          - 30log(4pi) - 40log(R) - Losses_TX - Losses_RX
    pr_dbm = (p.tx_power_dbm
              - tx_total_loss_db
              + p.tx_array_gain_dbi
              + p.rx_array_gain_dbi
              - rx_total_loss_db
              + 20 * math.log10(lam)
              + p.target_rcs_dbsm
              - 30 * math.log10(4 * pi)
              - 40 * math.log10(R)
              - atm_loss_db)

    # ─── SNR ─────────────────────────────────────────────────────────
    snr_db = pr_dbm - p.noise_power_dbm

    # ─── Results ─────────────────────────────────────────────────────
    return {
        # TX parameters
        'tx_power_dbm':          p.tx_power_dbm,
        'tx_cable_loss_db':      p.tx_cable_loss_db,
        'tx_divider_loss_db':    p.tx_divider_loss_db,
        'tx_phase_shift_loss_db': p.tx_phase_shift_loss_db,
        'tx_feed_loss_db':       p.tx_feed_loss_db,
        'tx_total_loss_db':      tx_total_loss_db,
        'tx_array_gain_dbi':     p.tx_array_gain_dbi,
        'tx_eirp_dbm':           tx_eirp_dbm,

        # Path
        'range_m':               R,
        'range_km':              R / 1000,
        'wavelength_m':          lam,
        'fspl_one_way_db':       fspl_db,
        'fspl_two_way_db':       two_way_fspl_db,
        'target_rcs_dbsm':       p.target_rcs_dbsm,
        'atm_loss_db':           atm_loss_db,

        # RX
        'rx_array_gain_dbi':     p.rx_array_gain_dbi,
        'rx_total_loss_db':      rx_total_loss_db,
        'received_power_dbm':    pr_dbm,

        # Noise / SNR
        'system_nf_db':          p.system_nf_db,
        'if_noise_bw_hz':        p.if_noise_bandwidth_hz,
        'noise_power_dbm':       p.noise_power_dbm,
        'snr_db':                snr_db,
        'required_snr_db':       p.required_snr_db,
        'snr_margin_db':         snr_db - p.required_snr_db,
        'detection':             snr_db >= p.required_snr_db,
    }


def print_link_budget(budget: dict) -> None:
    """Pretty-print the link budget table."""
    b = budget
    W = 60

    def section(title):
        print(f"\n  {'─'*(W-4)}")
        print(f"  {title}")
        print(f"  {'─'*(W-4)}")

    def row(label, value, unit='dB', indent=2):
        spaces = ' ' * indent
        label_pad = 40 - indent
        print(f"  {spaces}{label:<{label_pad}} {value:>8.2f}  {unit}")

    print()
    print("  " + "═" * W)
    print(f"  AERIS-10P FMCW RADAR LINK BUDGET")
    print(f"  Range: {b['range_km']:.1f} km   Target RCS: {b['target_rcs_dbsm']:.0f} dBsm")
    print("  " + "═" * W)

    section("TRANSMITTER")
    row("TX power (PA output)",            b['tx_power_dbm'],       'dBm')
    row("TX cable loss",                   -b['tx_cable_loss_db'],  'dB')
    row("TX power divider loss (1:16)",    -b['tx_divider_loss_db'],'dB')
    row("TX phase shifter loss (HMC647A)", -b['tx_phase_shift_loss_db'], 'dB')
    row("TX feed / connector loss",        -b['tx_feed_loss_db'],   'dB')
    row("TX array gain (4×4, 22 dBi)",    +b['tx_array_gain_dbi'], 'dBi')
    row("TX EIRP",                         b['tx_eirp_dbm'],        'dBm  ←')

    section("PROPAGATION")
    row(f"Free-space path loss (1-way)",   -b['fspl_one_way_db'],   'dB')
    row(f"Free-space path loss (2-way)",   -b['fspl_two_way_db'],   'dB')
    row(f"Target RCS",                     +b['target_rcs_dbsm'],   'dBsm')
    row(f"Atmospheric/rain loss (2-way)",  -b['atm_loss_db'],       'dB')

    section("RECEIVER")
    row("RX array gain (4×4, 22 dBi)",    +b['rx_array_gain_dbi'], 'dBi')
    row("RX feed / connector loss",        -b['rx_total_loss_db'],  'dB')
    print()
    row("Received signal power (Pr)",      b['received_power_dbm'], 'dBm  ←')

    section("NOISE & DETECTION")
    row("System noise figure (cascaded)",  b['system_nf_db'],       'dB')
    row("IF noise bandwidth",              b['if_noise_bw_hz'],     'Hz')
    noise_ktb = -174 + 10 * math.log10(b['if_noise_bw_hz'])
    row("Thermal noise kTB",              noise_ktb,                'dBm')
    row("Total noise power",              b['noise_power_dbm'],     'dBm  ←')

    section("SIGNAL-TO-NOISE RATIO")
    row("SNR",                            b['snr_db'],              'dB  ←')
    row("Required SNR",                   b['required_snr_db'],     'dB')
    row("SNR margin",                     b['snr_margin_db'],       'dB')

    det = "✓ DETECTED" if b['detection'] else "✗ BELOW THRESHOLD"
    print()
    print(f"  {'─'*(W-4)}")
    print(f"  RESULT: {det}  (margin = {b['snr_margin_db']:+.1f} dB)")
    print("  " + "═" * W)

    # Legal check
    print()
    print(f"  REGULATORY CHECK (German Klasse A Amateur Radio):")
    print(f"  TX power = {b['tx_power_dbm']:.0f} dBm = {10**(b['tx_power_dbm']/10)/1000:.3f} W")
    print(f"  Legal limit: 75 W PEP = 48.75 dBm")
    legal_margin = 48.75 - b['tx_power_dbm']
    status = "✓ COMPLIANT" if legal_margin > 0 else "✗ EXCEEDS LIMIT"
    print(f"  Power margin: {legal_margin:+.1f} dB → {status}")
    print()


def range_sweep(params: SystemParams) -> None:
    """Print and optionally plot SNR vs range."""
    if not HAS_NUMPY:
        # Text-only version
        print("\nSNR vs Range sweep:")
        print(f"  {'Range':>8} {'Pr':>10} {'SNR':>8} {'Detect':>8}")
        print(f"  {'[m]':>8} {'[dBm]':>10} {'[dB]':>8} {'(≥15dB)':>8}")
        print(f"  {'─'*40}")
        ranges = [100, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 4000, 5000]
        for r in ranges:
            b = compute_link_budget(params, r)
            det = '✓' if b['detection'] else '✗'
            print(f"  {r:>8} {b['received_power_dbm']:>10.1f} {b['snr_db']:>8.1f} {det:>8}")
        return

    # With numpy/matplotlib
    ranges = np.logspace(2, 4, 500)  # 100m to 10 km
    snr_car    = [compute_link_budget(params, r)['snr_db'] for r in ranges]
    snr_person = [compute_link_budget(
        SystemParams(target_rcs_dbsm=0), r)['snr_db'] for r in ranges]

    # Find max range (SNR = required_snr)
    required = params.required_snr_db
    snr_arr = np.array(snr_car)
    above_threshold = ranges[snr_arr >= required]
    rmax = above_threshold[-1] if len(above_threshold) > 0 else 0

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("AERIS-10P Link Budget Analysis", fontsize=14)

    # SNR vs Range
    ax1.semilogx(ranges / 1000, snr_car, 'b-', lw=2, label='Car (σ=10m²)')
    ax1.semilogx(ranges / 1000, snr_person, 'g-', lw=2, label='Person (σ=1m²)')
    ax1.axhline(required, color='r', ls='--', lw=2, label=f'Threshold ({required}dB)')
    ax1.axvline(rmax / 1000, color='orange', ls=':', lw=1.5,
                label=f'R_max (car) = {rmax/1000:.1f} km')
    ax1.fill_between(ranges / 1000, snr_car, required,
                     where=np.array(snr_car) >= required,
                     alpha=0.15, color='blue', label='Detection zone')
    ax1.set_xlabel("Range [km]")
    ax1.set_ylabel("SNR [dB]")
    ax1.set_title("SNR vs Range")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim([0.1, 10])
    ax1.set_ylim([-20, 80])

    # Received power vs range
    pr_values = [compute_link_budget(params, r)['received_power_dbm'] for r in ranges]
    ax2.semilogx(ranges / 1000, pr_values, 'b-', lw=2, label='Pr (car)')
    ax2.axhline(params.noise_power_dbm + required, color='r', ls='--',
                label=f'Detection threshold ({params.noise_power_dbm + required:.0f} dBm)')
    ax2.axhline(params.noise_power_dbm, color='gray', ls=':', label='Noise floor')
    ax2.set_xlabel("Range [km]")
    ax2.set_ylabel("Received Power [dBm]")
    ax2.set_title("Received Signal vs Range")
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0.1, 10])

    plt.tight_layout()
    plt.savefig('aeris_link_budget.png', dpi=150, bbox_inches='tight')
    print(f"\nLink budget plot saved: aeris_link_budget.png")
    plt.show()


def save_csv(params: SystemParams, filename: str) -> None:
    """Save link budget to CSV for ranges 100m to 5km."""
    ranges = list(range(100, 500, 50)) + list(range(500, 1000, 100)) + \
             list(range(1000, 5001, 250))

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Range_m', 'Range_km', 'Rx_Power_dBm', 'Noise_Floor_dBm',
            'SNR_dB', 'SNR_Margin_dB', 'Detected',
            'TX_EIRP_dBm', 'TX_Array_Gain_dBi', 'RX_Array_Gain_dBi',
            'System_NF_dB', 'FSPL_2way_dB', 'Target_RCS_dBsm'
        ])
        for r in ranges:
            b = compute_link_budget(params, r)
            writer.writerow([
                r, f"{r/1000:.3f}",
                f"{b['received_power_dbm']:.2f}",
                f"{b['noise_power_dbm']:.2f}",
                f"{b['snr_db']:.2f}",
                f"{b['snr_margin_db']:.2f}",
                'YES' if b['detection'] else 'NO',
                f"{b['tx_eirp_dbm']:.2f}",
                f"{b['tx_array_gain_dbi']:.2f}",
                f"{b['rx_array_gain_dbi']:.2f}",
                f"{b['system_nf_db']:.2f}",
                f"{b['fspl_two_way_db']:.2f}",
                f"{b['target_rcs_dbsm']:.1f}",
            ])

    print(f"Link budget CSV saved: {filename}")
    print(f"  Rows: {len(ranges)} range points (100m to 5km)")


def main():
    parser = argparse.ArgumentParser(
        description='AERIS-10P Radar Link Budget Calculator'
    )
    parser.add_argument('--range-km', type=float, default=3.0,
                        help='Analysis range in km (default: 3.0)')
    parser.add_argument('--rcs', type=float, default=10.0,
                        help='Target RCS in dBsm (default: 10 = car)')
    parser.add_argument('--tx-power', type=float, default=27.0,
                        help='TX power in dBm (default: 27)')
    parser.add_argument('--sweep', action='store_true',
                        help='Print/plot SNR vs range sweep')
    parser.add_argument('--csv', type=str, metavar='FILE',
                        help='Save range sweep to CSV file')
    parser.add_argument('--plot', action='store_true',
                        help='Generate matplotlib plots')
    args = parser.parse_args()

    params = SystemParams(
        range_km=args.range_km,
        target_rcs_dbsm=args.rcs,
        tx_power_dbm=args.tx_power,
    )

    # Always print the point-design link budget
    budget = compute_link_budget(params)
    print_link_budget(budget)

    # Optional outputs
    if args.sweep or args.plot:
        range_sweep(params)

    if args.csv:
        save_csv(params, args.csv)

    # Summary stats
    params_1km = SystemParams(range_km=1.0, target_rcs_dbsm=args.rcs)
    params_3km = SystemParams(range_km=3.0, target_rcs_dbsm=args.rcs)
    params_5km = SystemParams(range_km=5.0, target_rcs_dbsm=args.rcs)

    print("\n  Quick Reference (car target, σ=10m²):")
    for p, label in [(params_1km, '1 km'), (params_3km, '3 km'), (params_5km, '5 km')]:
        b = compute_link_budget(p)
        print(f"    {label}: SNR = {b['snr_db']:+.1f} dB  {'✓' if b['detection'] else '✗'}")

    print(f"\n  System noise figure: {params.system_nf_db:.2f} dB")
    print(f"  IF noise bandwidth:  {params.if_noise_bandwidth_hz:.1f} Hz")
    print(f"  Noise floor:         {params.noise_power_dbm:.1f} dBm")
    n_samp = int(params.sample_rate_hz * params.sweep_time_s)
    pg = 10 * math.log10(n_samp / 2 * params.num_chirps)
    print(f"  Processing gain:     {pg:.1f} dB ({n_samp//2} range bins × {params.num_chirps} Doppler bins)")
    print(f"  Range resolution:    {params.c_mps / (2 * params.bandwidth_hz):.1f} m")
    print()


if __name__ == '__main__':
    main()
