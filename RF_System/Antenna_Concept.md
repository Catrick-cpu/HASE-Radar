# AERIS-10P Antenna Design Concept
## Rev 1.0 — 2026-07-14

---

## 1. Design Requirements

| Parameter | Specification | Notes |
|---|---|---|
| Frequency | 10.05 GHz ± 50 MHz | Center of FMCW chirp band |
| Polarization | Linear horizontal | Consistent TX/RX for maximum isolation |
| Element gain | ≥ 5.5 dBi | Typical patch: 6 dBi |
| S11 at 10.05 GHz | < -15 dB | ≤ -15 dB over ±50 MHz |
| Element spacing | 15 mm | λ/2 at 10 GHz (λ = 29.85 mm) |
| Substrate | Rogers RO4003C, 0.508 mm | |
| Array size | 4×4 elements | 45 mm × 45 mm aperture |

---

## 2. Patch Antenna Analytical Design

Substrate: Rogers RO4003C, h = 0.508 mm, εr = 3.55, tan δ = 0.0027

**Step 1 — Patch Width (W):**
```
W = c / (2f √((εr+1)/2)) = 3e8 / (2×10.05e9 × √(2.275)) = 7.92 mm
```

**Step 2 — Effective εr:**
```
εr_eff = (εr+1)/2 + (εr-1)/2 × (1 + 12h/W)^(-0.5)
       = 2.275 + 1.275 × (1 + 12×0.508/7.92)^(-0.5)
       = 2.275 + 1.275 × 0.748 = 3.229
```

**Step 3 — Fringe Extension ΔL:**
```
ΔL = 0.412h × (εr_eff + 0.3)(W/h + 0.264) / ((εr_eff - 0.258)(W/h + 0.8))
   = 0.412×0.508 × (3.529 × 16.43) / (2.971 × 16.64)
   = 0.209 × 0.481 = 0.493 mm
```

**Step 4 — Resonant Length (L):**
```
L = c / (2f √εr_eff) - 2ΔL
  = 3e8 / (2×10.05e9 × √3.229) - 2×0.493
  = 3e8 / (36.0e9) - 0.986
  = 8.33 - 0.99 = 7.34... 
```

Wait, let me recalculate: c/(2f√εr_eff) = 299.7e6/(2×10.05e9×1.797) = 299.7e6/36.09e9 = 8.31 mm

L = 8.31 - 2×0.493 = 7.32 mm → very narrow patch...

Actually this seems too small. Let me check: for a patch on RO4003C (h=0.508mm, εr=3.55) at 10 GHz:
The patch is essentially a half-wave resonator. With εr_eff ≈ 3.22, λg = 30/(√3.22) = 16.7 mm → L ≈ λg/2 = 8.35 mm minus fringe extension ≈ 7.3-7.5 mm.

But wait — our W was only 7.92 mm (also very small patch). Let me verify: for 10 GHz, λ_free = 30 mm. A patch on εr=3.55 substrate has much shorter dimensions because the dielectric slows the wave: effective wavelength λg ≈ 30/√3.22 ≈ 16.7 mm, so L ≈ 7-8 mm. The width W ≈ 8 mm is similar. This is correct — the patch is approximately 8mm × 8mm at 10 GHz on RO4003C.

This means our element spacing of 15 mm (λ/2) gives about 7 mm gap between patches — sufficient to avoid overlap. ✓

**Final dimensions (to be verified with EM simulation):**
- W = 8.0 mm (patch width)
- L = 7.5 mm (patch length, approx — run EM sim to fine-tune)
- Feed: inset microstrip at y0 ≈ 2.5 mm from edge for 50Ω

Note: The STEP description and earlier documents used L=13.8mm which appears to be for a different substrate or was incorrect. **Use EM simulation (openems_antenna_simulation.py) to determine exact dimensions before PCB layout.**

---

## 3. Feed Network Design

**Feed type:** Inset microstrip feed for 50Ω impedance match

The input impedance at the patch edge is approximately:
```
Rin_edge ≈ 1/(2 × G_rad) where G_rad ≈ W/(120λ) = 7.92/(120×30) = 2.2 mS
Rin_edge ≈ 227 Ω
```

For 50Ω inset feed:
```
y0 = L/π × arccos(√(50/227)) = 7.5/π × arccos(0.469) = 7.5/π × 1.082 = 2.58 mm
```

So the feed is inset by about 2.6 mm from the patch edge. Feed line width = 1.08 mm for 50Ω.

**Corporate feed network for 4×4 array:**
- Level 1: 1×16 requires 4 levels of 1:2 Wilkinson dividers
- Level 1 Wilkinson: at 10 GHz on RO4003C, λg/4 transformer = 4.2 mm long, width = 0.58 mm (70.7Ω)
- Isolation resistors: 100Ω 0402 between each pair at every level

---

## 4. Expected Array Performance

| Parameter | 4×4 Array | Formula |
|---|---|---|
| Element gain | 6 dBi | patch efficiency ~90% |
| Array factor gain | 12 dB | 10·log10(16) |
| Efficiency factor | -0.5 dB | mutual coupling, errors |
| Total array gain | 17.5 dBi | (practical: 17-18 dBi) |
| -3 dB beam width (az) | 22° | 0.886·λ/(N·d) = 0.886/4 |
| First sidelobe level | -13.3 dB | uniform aperture |
| Grating lobe | None within ±90° | d=λ/2 spacing |
| Max steering ±45° gain | 14 dBi | pattern roll-off at scan |

---

## 5. Manufacturing Requirements

- **Substrate:** Rogers RO4003C, 0.508 mm, 1 oz copper
- **Surface finish:** ENIG (Immersion Gold) — critical for RF performance; HASL creates bumps that detune patches
- **Copper pour:** solid ground plane, layer 2, no cuts
- **PCB house:** PCBWay or Advanced Circuits (specify Rogers material, ENIG, controlled impedance)
- **Tolerance:** patch dimension tolerance ±0.05 mm affects resonant frequency by ~30 MHz per 0.1mm
- **Antenna assembly:** solder 2.92mm edge-launch SMA connectors after board delivery, inspect S11 before final assembly

---

## 6. EM Simulation Instructions

Run full simulation with OpenEMS:
```bash
conda activate openems   # (install: conda install -c conda-forge openems)
cd RF_System
python openems_antenna_simulation.py --mode setup --sim-path ./patch_sim
bash ./patch_sim/run_simulation.sh   # 5-30 min depending on CPU
python openems_antenna_simulation.py --mode postprocess --sim-path ./patch_sim
```

Expected outputs:
- S11 plot showing resonance at 10.05 GHz with S11 < -15 dB
- Input impedance plot
- If resonance is off: adjust L by ΔL = (f_resonant - 10.05e9)/10.05e9 × L_nominal

Alternative free EM tool: **MMANA-GAL** (for wire antennas, not patches), **Antenna Magus** (trial), or **openEMS** as specified.
