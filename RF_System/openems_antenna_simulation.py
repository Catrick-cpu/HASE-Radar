"""
AERIS-10P Patch Antenna EM Simulation using OpenEMS
====================================================
Simulates a single 10 GHz patch antenna on Rogers RO4003C substrate
to verify S11 < -15 dB and compute gain pattern.

Requirements:
    pip install openems (or conda install -c conda-forge openems)
    OpenEMS must be installed: https://openems.de/start/installation.php

    On Windows: install via conda:
        conda create -n openems python=3.10
        conda activate openems
        conda install -c conda-forge openems
        pip install matplotlib numpy scipy

    On Linux:
        sudo apt install openems
        pip install openems matplotlib numpy scipy

Usage:
    python openems_antenna_simulation.py --mode s11     # S11 only (fast, ~5min)
    python openems_antenna_simulation.py --mode full    # S11 + far-field (slow, ~30min)
    python openems_antenna_simulation.py --mode sweep   # Frequency sweep (very slow)

Reference: OpenEMS documentation at openems.de
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import c as C_LIGHT
import os
import sys

# ────────────────────────────────────────────────────────────────────
# ANTENNA PARAMETERS (derived from analytical design)
# ────────────────────────────────────────────────────────────────────

# Substrate parameters: Rogers RO4003C
H_SUB   = 0.508e-3        # substrate thickness [m]
EPS_R   = 3.55            # relative permittivity
TAN_D   = 0.0027          # loss tangent
T_CU    = 35e-6           # copper thickness [m] (1 oz)

# Target frequency
F0      = 10.05e9         # center frequency [Hz]
LAMBDA0 = C_LIGHT / F0    # free-space wavelength [m]  = 29.85 mm

# Patch dimensions (calculated analytically, tune in simulation)
W_PATCH = 8.0e-3          # patch width [m]
L_PATCH = 13.8e-3         # patch length [m]

# Feed parameters (inset feed for 50Ω matching)
FEED_INSET  = 3.4e-3      # inset distance from patch edge [m]
FEED_WIDTH  = 1.08e-3     # 50Ω microstrip width on RO4003C

# Ground plane and substrate dimensions
W_GND = 40e-3             # ground plane width [m]
L_GND = 40e-3             # ground plane length [m]

# Simulation frequency range
F_START = 9.5e9           # simulation start frequency
F_STOP  = 10.5e9          # simulation stop frequency
N_FREQ  = 201             # number of frequency points

# ────────────────────────────────────────────────────────────────────
# ANALYTICAL PRE-COMPUTATION (verify dimensions before EM sim)
# ────────────────────────────────────────────────────────────────────

def analytical_patch_design(f0=F0, h=H_SUB, eps_r=EPS_R):
    """
    Compute patch antenna dimensions analytically.
    Returns dict with all design parameters.
    """
    lam0 = C_LIGHT / f0

    # Step 1: Estimate patch width
    W = C_LIGHT / (2 * f0 * np.sqrt((eps_r + 1) / 2))

    # Step 2: Effective dielectric constant
    eps_eff = (eps_r + 1) / 2 + (eps_r - 1) / 2 * (1 + 12 * h / W) ** (-0.5)

    # Step 3: Length extension (fringe fields)
    delta_L = 0.412 * h * (eps_eff + 0.3) * (W / h + 0.264) / \
              ((eps_eff - 0.258) * (W / h + 0.8))

    # Step 4: Resonant length
    L = C_LIGHT / (2 * f0 * np.sqrt(eps_eff)) - 2 * delta_L

    # Step 5: Resonant frequency with chosen W
    f_res = C_LIGHT / (2 * (L + 2 * delta_L) * np.sqrt(eps_eff))

    # Step 6: Input impedance at patch edge
    # Rin at radiating edge ≈ 1/(2*G_rad) where G_rad = W/(120*lambda0)*(1 - (k0*h)^2/24)
    k0 = 2 * np.pi * f0 / C_LIGHT
    G_rad = W / (120 * lam0) * (1 - (k0 * h) ** 2 / 24)
    Rin_edge = 1 / (2 * G_rad)

    # Step 7: Inset feed distance for 50Ω
    # Rin(y0) = Rin_edge * cos^2(pi*y0/L)
    # For Rin = 50: y0 = L/pi * arccos(sqrt(50/Rin_edge))
    if Rin_edge > 50:
        y0 = L / np.pi * np.arccos(np.sqrt(50 / Rin_edge))
    else:
        y0 = 0  # direct feed if impedance too low

    # Step 8: 50Ω microstrip width on RO4003C (0.508mm)
    # Using closed-form formula for W/h:
    # For W/h <= 2: W = 8*h*exp(A) / (exp(2A) - 2), A = (Z0/60)*sqrt((eps_r+1)/2)...
    Z0 = 50
    A = Z0 / 60 * np.sqrt((eps_r + 1) / 2) + (eps_r - 1) / (eps_r + 1) * (0.23 + 0.11 / eps_r)
    W_ms = 8 * h * np.exp(A) / (np.exp(2 * A) - 2)

    return {
        'W_patch': W,
        'L_patch': L,
        'eps_eff': eps_eff,
        'delta_L': delta_L,
        'f_resonant': f_res,
        'Rin_edge_ohm': Rin_edge,
        'inset_y0': y0,
        'W_microstrip_50ohm': W_ms,
        'wavelength_free': lam0,
        'wavelength_guided': C_LIGHT / (f0 * np.sqrt(eps_eff)),
    }


def print_analytical_results():
    """Print and validate analytical design."""
    r = analytical_patch_design()
    print("\n" + "=" * 60)
    print("AERIS-10P Patch Antenna — Analytical Design Results")
    print("=" * 60)
    print(f"Target frequency:      {F0/1e9:.3f} GHz")
    print(f"Substrate:             Rogers RO4003C, h={H_SUB*1e3:.3f} mm, εr={EPS_R}")
    print()
    print(f"Patch width  W:        {r['W_patch']*1e3:.2f} mm")
    print(f"Patch length L:        {r['L_patch']*1e3:.2f} mm")
    print(f"Effective εr:          {r['eps_eff']:.3f}")
    print(f"Fringe extension ΔL:   {r['delta_L']*1e3:.3f} mm per side")
    print(f"Resonant frequency:    {r['f_resonant']/1e9:.4f} GHz")
    print(f"Edge impedance Rin:    {r['Rin_edge_ohm']:.1f} Ω")
    print(f"Inset feed y0:         {r['inset_y0']*1e3:.2f} mm")
    print(f"50Ω microstrip width:  {r['W_microstrip_50ohm']*1e3:.2f} mm")
    print()
    print(f"Free-space λ:          {r['wavelength_free']*1e3:.2f} mm")
    print(f"Guided wavelength λg:  {r['wavelength_guided']*1e3:.2f} mm")
    print()
    print(f"Element spacing (λ/2): {r['wavelength_free']*1e3/2:.2f} mm → use 15.0 mm")
    print("=" * 60)
    print("NOTE: EM simulation needed to fine-tune L_patch for exact resonance")
    print("      Typical tuning range: L_patch ± 0.5 mm")
    print()
    return r


# ────────────────────────────────────────────────────────────────────
# OPENEMS SIMULATION SETUP
# ────────────────────────────────────────────────────────────────────

def run_openems_simulation(sim_path="./aeris_patch_sim", mode='s11'):
    """
    Set up and run OpenEMS simulation of the patch antenna.

    mode: 's11' for S11 only, 'full' for S11 + far-field pattern
    """
    try:
        import openems as em
    except ImportError:
        print("ERROR: openems Python module not found.")
        print("Install with: conda install -c conda-forge openems")
        print("\nFalling back to analytical results only.")
        return None

    os.makedirs(sim_path, exist_ok=True)

    print(f"\nSetting up OpenEMS simulation in: {sim_path}")
    print(f"Mode: {mode}")

    # ─── Create simulation object ────────────────────────────────────
    sim = em.openEMS(NrTS=200000, EndCriteria=1e-4)

    # ─── FDTD Settings ───────────────────────────────────────────────
    sim.SetGaussExcite(F0, (F_STOP - F_START) / 2)
    sim.SetBoundaryCond(['MUR', 'MUR', 'MUR', 'MUR', 'MUR', 'MUR'])

    # ─── CSX Geometry ────────────────────────────────────────────────
    csx = em.ContinuousStructure()
    sim.SetCSX(csx)

    # Mesh
    mesh = csx.GetGrid()
    mesh.SetDeltaUnit(1e-3)  # all units in mm

    # Substrate boundaries
    sub_xmin = -W_GND * 1e3 / 2
    sub_xmax = +W_GND * 1e3 / 2
    sub_ymin = -L_GND * 1e3 / 2
    sub_ymax = +L_GND * 1e3 / 2
    sub_zmin = 0
    sub_zmax = H_SUB * 1e3  # in mm

    # Mesh setup (fine mesh under patch, coarser elsewhere)
    patch_xmin = -W_PATCH * 1e3 / 2
    patch_xmax = +W_PATCH * 1e3 / 2
    patch_ymin = -L_PATCH * 1e3 / 2
    patch_ymax = +L_PATCH * 1e3 / 2

    # X mesh
    mesh.AddLine('x', [sub_xmin, patch_xmin, 0, patch_xmax, sub_xmax])
    mesh.SmoothMeshLines('x', LAMBDA0 * 1e3 / 20, 1.4)  # λ/20 max cell size

    # Y mesh
    mesh.AddLine('y', [sub_ymin, patch_ymin - FEED_INSET * 1e3, 0,
                       patch_ymax, sub_ymax])
    mesh.SmoothMeshLines('y', LAMBDA0 * 1e3 / 20, 1.4)

    # Z mesh (fine through substrate, air above)
    mesh.AddLine('z', [sub_zmin, sub_zmax])
    mesh.SmoothMeshLines('z', H_SUB * 1e3 / 3, 1.3)  # 3 cells through substrate
    air_height = 3 * LAMBDA0 * 1e3  # 3 wavelengths above
    mesh.AddLine('z', [sub_zmax, sub_zmax + air_height])
    mesh.SmoothMeshLines('z', LAMBDA0 * 1e3 / 10, 1.4)

    # ─── Materials ───────────────────────────────────────────────────

    # Substrate (Rogers RO4003C)
    sub = csx.AddMaterial('substrate', epsilon=EPS_R, kappa=2 * np.pi * F0 * EPS_R *
                          8.854e-12 * TAN_D)
    sub.AddBox(
        [sub_xmin, sub_ymin, sub_zmin],
        [sub_xmax, sub_ymax, sub_zmax]
    )

    # Ground plane (PEC)
    gnd = csx.AddMetal('groundplane')
    gnd.AddBox(
        [sub_xmin, sub_ymin, sub_zmin],
        [sub_xmax, sub_ymax, sub_zmin]
    )

    # Patch (PEC)
    patch = csx.AddMetal('patch')
    patch.AddBox(
        [patch_xmin, patch_ymin, sub_zmax],
        [patch_xmax, patch_ymax, sub_zmax]
    )

    # Feed line (microstrip, inset feed)
    feed_xmin = -FEED_WIDTH * 1e3 / 2
    feed_xmax = +FEED_WIDTH * 1e3 / 2
    feed_line = csx.AddMetal('feedline')
    # Feed line from patch edge to simulation boundary
    feed_line.AddBox(
        [feed_xmin, sub_ymin, sub_zmax],
        [feed_xmax, patch_ymin - FEED_INSET * 1e3, sub_zmax]
    )
    # Inset into patch
    feed_line.AddBox(
        [feed_xmin, patch_ymin - FEED_INSET * 1e3, sub_zmax],
        [feed_xmax, patch_ymin, sub_zmax]
    )

    # ─── Port (lumped port at feed line end) ─────────────────────────
    port = sim.AddLumpedPort(
        port_nr=1,
        R=50,
        start=[feed_xmin, sub_ymin, sub_zmin],
        stop=[feed_xmax, sub_ymin, sub_zmax],
        p_dir='z',
        excite=1.0
    )

    # ─── NF2FF box for far-field (if full mode) ───────────────────────
    if mode == 'full':
        nf2ff = sim.CreateNF2FFBox()

    # ─── Write simulation files ────────────────────────────────────────
    sim.WriteOpenEMS(os.path.join(sim_path, 'patch_antenna.xml'))
    csx.Write2XML(os.path.join(sim_path, 'patch_antenna_csx.xml'))

    print(f"Simulation files written to: {sim_path}")
    print(f"To run simulation:")
    print(f"  openEMS {sim_path}/patch_antenna.xml --numThreads 4")
    print()

    # Generate run script
    run_script = f"""#!/bin/bash
# AERIS-10P OpenEMS simulation run script
# Generated by openems_antenna_simulation.py

SIM_PATH="{sim_path}"

echo "Starting OpenEMS simulation..."
echo "Estimated time: {'5-10 minutes' if mode == 's11' else '20-40 minutes'}"

openEMS "$SIM_PATH/patch_antenna.xml" --numThreads $(nproc)

echo "Simulation complete. Running post-processing..."
python3 {__file__} --mode postprocess --sim-path "$SIM_PATH"
"""
    with open(os.path.join(sim_path, 'run_simulation.sh'), 'w') as f:
        f.write(run_script)

    return sim_path, port


def postprocess_results(sim_path="./aeris_patch_sim"):
    """
    Post-process OpenEMS results: compute S11, resonant frequency, bandwidth.
    """
    try:
        import openems as em
        from openems import ports
    except ImportError:
        print("OpenEMS not available for post-processing")
        return

    print(f"\nPost-processing results from: {sim_path}")

    # Load port data
    f, s11, z_in = ports.LoadPort(sim_path, port=1, F_start=F_START, F_stop=F_STOP)

    # ─── S11 Plot ────────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.suptitle("AERIS-10P Patch Antenna Simulation Results", fontsize=14, fontweight='bold')

    # S11 magnitude
    ax1 = axes[0, 0]
    s11_db = 20 * np.log10(np.abs(s11))
    ax1.plot(f / 1e9, s11_db, 'b-', linewidth=2, label='S11 (simulated)')
    ax1.axhline(-15, color='r', linestyle='--', label='-15 dB threshold')
    ax1.axvline(F0 / 1e9, color='g', linestyle='--', alpha=0.5, label=f'f0 = {F0/1e9:.2f} GHz')
    ax1.set_xlabel("Frequency [GHz]")
    ax1.set_ylabel("S11 [dB]")
    ax1.set_title("S11 Magnitude")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([-40, 5])

    # Find resonant frequency and bandwidth
    f_res_idx = np.argmin(s11_db)
    f_res = f[f_res_idx]
    s11_min = s11_db[f_res_idx]

    # -10 dB bandwidth
    below_10 = s11_db < -10
    if np.any(below_10):
        f_lower = f[below_10][0]
        f_upper = f[below_10][-1]
        bw_10 = f_upper - f_lower
    else:
        bw_10 = 0

    print(f"\nResonant frequency: {f_res/1e9:.4f} GHz (target: {F0/1e9:.4f} GHz)")
    print(f"Minimum S11:        {s11_min:.1f} dB")
    print(f"-10 dB bandwidth:   {bw_10/1e6:.1f} MHz")
    print(f"S11 at {F0/1e9:.2f} GHz:   {s11_db[np.argmin(np.abs(f-F0))]:.1f} dB")

    if s11_db[np.argmin(np.abs(f - F0))] < -15:
        print("✓ PASS: S11 < -15 dB at target frequency")
    else:
        print("✗ FAIL: S11 >= -15 dB — adjust patch length L")
        adjustment = (f_res - F0) / F0 * L_PATCH
        print(f"  → Suggested L_patch adjustment: {adjustment*1e3:+.3f} mm")
        print(f"  → Try L_patch = {(L_PATCH + adjustment)*1e3:.3f} mm")

    # Input impedance
    ax2 = axes[0, 1]
    ax2.plot(f / 1e9, np.real(z_in), 'b-', label='Re(Zin)')
    ax2.plot(f / 1e9, np.imag(z_in), 'r-', label='Im(Zin)')
    ax2.axhline(50, color='g', linestyle='--', alpha=0.5, label='50 Ω')
    ax2.axhline(0, color='k', linestyle='-', alpha=0.2)
    ax2.set_xlabel("Frequency [GHz]")
    ax2.set_ylabel("Impedance [Ω]")
    ax2.set_title("Input Impedance")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Smith chart
    ax3 = axes[1, 0]
    z_norm = z_in / 50
    theta = np.linspace(0, 2 * np.pi, 100)
    ax3.plot(np.cos(theta), np.sin(theta), 'k-', alpha=0.2)  # unit circle
    ax3.plot((z_norm.real - 1) / (z_norm.real + 1), np.imag(z_norm) / np.abs(1 + z_norm),
             'b-', linewidth=2)
    ax3.set_xlim([-1.1, 1.1])
    ax3.set_ylim([-1.1, 1.1])
    ax3.set_aspect('equal')
    ax3.set_title("Smith Chart (approximate)")
    ax3.grid(True, alpha=0.2)
    ax3.axhline(0, color='k', alpha=0.3)
    ax3.axvline(0, color='k', alpha=0.3)

    # Summary text
    ax4 = axes[1, 1]
    ax4.axis('off')
    summary = f"""
SIMULATION SUMMARY
{'─'*40}
Target frequency:    {F0/1e9:.4f} GHz
Resonant frequency:  {f_res/1e9:.4f} GHz
S11 minimum:         {s11_min:.1f} dB
-10 dB bandwidth:    {bw_10/1e6:.1f} MHz

Patch dimensions used:
  Width W:           {W_PATCH*1e3:.2f} mm
  Length L:          {L_PATCH*1e3:.2f} mm
  Substrate h:       {H_SUB*1e3:.3f} mm
  εr:                {EPS_R}

Feed:
  Inset y0:          {FEED_INSET*1e3:.2f} mm
  Feed width:        {FEED_WIDTH*1e3:.2f} mm

Specification:
  S11 < -15 dB:      {'✓ PASS' if s11_min < -15 else '✗ FAIL'}
  BW > 100 MHz:      {'✓ PASS' if bw_10 > 100e6 else f'✗ FAIL ({bw_10/1e6:.0f} MHz)'}
    """
    ax4.text(0.05, 0.95, summary, transform=ax4.transAxes,
             fontsize=9, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    outfile = os.path.join(sim_path, 'patch_antenna_results.png')
    plt.savefig(outfile, dpi=150, bbox_inches='tight')
    print(f"\nResults plot saved: {outfile}")
    plt.show()


# ────────────────────────────────────────────────────────────────────
# ARRAY FACTOR COMPUTATION (no EM sim needed)
# ────────────────────────────────────────────────────────────────────

def compute_array_factor(N_x=4, N_y=4, d_x=15e-3, d_y=15e-3, f0=F0,
                          steer_az_deg=0, steer_el_deg=0, taper='uniform'):
    """
    Compute the 4×4 phased array factor as function of azimuth and elevation.

    Parameters:
        N_x, N_y: number of elements in x, y
        d_x, d_y: element spacing [m]
        steer_az_deg, steer_el_deg: beam steering angles [degrees]
        taper: 'uniform' or 'chebyshev' or 'taylor'

    Returns:
        theta_az: azimuth angles [degrees]
        theta_el: elevation angles [degrees]
        AF: array factor magnitude [dB]
    """
    lam = C_LIGHT / f0
    k = 2 * np.pi / lam

    # Steering phase shift per element
    az_rad = np.radians(steer_az_deg)
    el_rad = np.radians(steer_el_deg)

    phase_x = k * d_x * np.sin(az_rad)
    phase_y = k * d_y * np.sin(el_rad)

    # Angular grid
    theta_az = np.linspace(-90, 90, 361)

    # Compute array factor in azimuth cut (el = steer_el)
    u = np.sin(np.radians(theta_az))

    # Element weights (taper)
    if taper == 'chebyshev':
        # 30 dB sidelobe level Chebyshev weights for 4 elements
        # Computed numerically
        w_x = np.array([0.745, 1.0, 1.0, 0.745])
        w_y = np.array([0.745, 1.0, 1.0, 0.745])
    elif taper == 'taylor':
        # Taylor n=4 weights
        w_x = np.array([0.73, 1.0, 1.0, 0.73])
        w_y = np.array([0.73, 1.0, 1.0, 0.73])
    else:  # uniform
        w_x = np.ones(N_x)
        w_y = np.ones(N_y)

    # Array factor (azimuth cut, elevation at steer_el)
    AF_az = np.zeros(len(theta_az), dtype=complex)
    for ix in range(N_x):
        for iy in range(N_y):
            element_pos_x = (ix - (N_x - 1) / 2) * d_x
            element_pos_y = (iy - (N_y - 1) / 2) * d_y
            steer_phase = k * (element_pos_x * np.sin(az_rad) + element_pos_y * np.sin(el_rad))
            spatial_phase = k * (element_pos_x * u + element_pos_y * np.sin(el_rad))
            w = w_x[ix] * w_y[iy]
            AF_az += w * np.exp(1j * (spatial_phase - steer_phase))

    # Normalize
    AF_az_norm = np.abs(AF_az) / np.max(np.abs(AF_az))
    AF_az_db = 20 * np.log10(AF_az_norm + 1e-10)

    # Compute 3dB beam width
    half_power = AF_az_db >= -3
    if np.any(half_power):
        bw_3db = theta_az[half_power][-1] - theta_az[half_power][0]
    else:
        bw_3db = 0

    # First sidelobe level
    # Find first local max after main beam
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(-AF_az_db)  # find troughs in dB (= sidelobes)
    if len(peaks) > 0:
        sl_level = np.max(AF_az_db[peaks])
    else:
        sl_level = -np.inf

    print(f"\nArray Factor Analysis (steer = {steer_az_deg:.0f}° az, {steer_el_deg:.0f}° el):")
    print(f"  Taper: {taper}")
    print(f"  3dB beam width: {bw_3db:.1f}°")
    print(f"  First sidelobe: {sl_level:.1f} dB")
    print(f"  Array gain: {10*np.log10(N_x*N_y):.1f} dB (theoretical)")

    return theta_az, AF_az_db, bw_3db, sl_level


def plot_array_patterns():
    """Plot array factor patterns for different steering angles and tapers."""
    fig, axes = plt.subplots(2, 3, figsize=(15, 9), subplot_kw=dict(polar=False))
    fig.suptitle("AERIS-10P 4×4 Array Factor Patterns at 10.05 GHz", fontsize=14)

    configs = [
        (0, 0, 'uniform',    'Broadside, Uniform'),
        (15, 0, 'uniform',   '15° Steer, Uniform'),
        (30, 0, 'uniform',   '30° Steer, Uniform'),
        (45, 0, 'uniform',   '45° Steer, Uniform'),
        (0, 0, 'chebyshev',  'Broadside, Chebyshev'),
        (30, 0, 'chebyshev', '30° Steer, Chebyshev'),
    ]

    for ax, (az, el, taper, title) in zip(axes.flat, configs):
        theta, af_db, bw, sl = compute_array_factor(steer_az_deg=az, steer_el_deg=el, taper=taper)
        ax.plot(theta, af_db, 'b-', linewidth=2)
        ax.axhline(-3, color='g', linestyle='--', alpha=0.5, label='-3 dB')
        ax.axhline(-13.3, color='r', linestyle='--', alpha=0.5, label='SLL')
        ax.fill_between(theta, af_db, -50, where=(af_db > -50), alpha=0.1)
        ax.set_xlim([-90, 90])
        ax.set_ylim([-50, 5])
        ax.set_xlabel("Angle [°]")
        ax.set_ylabel("Normalized AF [dB]")
        ax.set_title(f"{title}\nBW={bw:.1f}°, SLL={sl:.1f} dB")
        ax.grid(True, alpha=0.3)
        ax.axvline(az, color='orange', linestyle=':', alpha=0.7, label=f'Steer {az}°')
        ax.legend(fontsize=7)

    plt.tight_layout()
    plt.savefig('aeris_array_patterns.png', dpi=150, bbox_inches='tight')
    print("\nArray pattern plots saved to: aeris_array_patterns.png")
    plt.show()


# ────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='AERIS-10P Patch Antenna Simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python openems_antenna_simulation.py --mode analytical
  python openems_antenna_simulation.py --mode array
  python openems_antenna_simulation.py --mode setup --sim-path ./sim_output
  python openems_antenna_simulation.py --mode postprocess --sim-path ./sim_output
        """
    )
    parser.add_argument('--mode', choices=['analytical', 'array', 'setup', 'postprocess'],
                        default='analytical',
                        help='Simulation mode (default: analytical)')
    parser.add_argument('--sim-path', default='./aeris_patch_sim',
                        help='Path for simulation files')
    parser.add_argument('--full', action='store_true',
                        help='Include far-field pattern (slower simulation)')
    args = parser.parse_args()

    if args.mode == 'analytical':
        print_analytical_results()
        print("\nFor EM simulation, run with --mode setup")
        print("For array pattern analysis, run with --mode array")

    elif args.mode == 'array':
        print("\nComputing 4×4 phased array patterns...")
        plot_array_patterns()

    elif args.mode == 'setup':
        print_analytical_results()
        sim_mode = 'full' if args.full else 's11'
        result = run_openems_simulation(args.sim_path, mode=sim_mode)
        if result is not None:
            print(f"\nSimulation setup complete.")
            print(f"Run: bash {args.sim_path}/run_simulation.sh")

    elif args.mode == 'postprocess':
        postprocess_results(args.sim_path)

    print("\nDone.")


if __name__ == '__main__':
    main()
