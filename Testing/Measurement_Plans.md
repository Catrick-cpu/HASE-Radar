# AERIS-10P Measurement Plans
## Rev 1.0 — 2026-07-14

---

## 1. Laboratory Measurement Plan

### Setup
```
Corner Reflector (0.3m edge)
         ↑
     (10–100m)
         ↑
  [AERIS-10P Radar]  ←→  [Laptop / Raspberry Pi 5]
         |                  (aeris_control.py + visualization.py)
    [24V supply]
```

### Test M-001: Short Range (10 m)
- **Objective:** Verify basic FMCW operation
- **Target:** 0.3m trihedral corner reflector (σ ≈ 133 m² = 21.2 dBsm)
- **Expected SNR:** ~60 dB (very high — will dominate the noise floor)
- **Expected range:** 10.0 m ± 1.5 m
- **Procedure:**
  1. Place corner reflector at 10.0 m in anechoic (or outdoor with no nearby reflectors)
  2. Enable TX, collect 100 chirps
  3. Compute range profile, identify peak
  4. Record: measured range, peak amplitude, SNR, noise floor
  5. Verify: peak at correct range bin (bin #6 for 10 m with 1.5 m resolution)

### Test M-002: Medium Range (50 m, 100 m)
- Repeat M-001 at 50 m and 100 m
- Expected SNR reduction: ~40·log10(10/50) = -28 dB at 50m, -40 dB at 100m from M-001
- Minimum detectable range at 100 m: still >15 dB SNR expected

### Test M-003: Car Target (100 m)
- Target: parked car (σ ≈ 10 m² = 10 dBsm)
- Measure SNR, compare to link budget prediction at 100 m
- Expected: ~40 dB SNR at 100 m for car target (well above 15 dB threshold)

---

## 2. Medium-Range Field Test Plan (500 m – 1 km)

### Location Requirements
- Open field, no obstacles in main beam direction
- Clear line of sight to target at all planned ranges
- Ground slope < 5° (to avoid multipath from ground)
- Minimum open area: 1 km × 0.1 km

### Test M-010: Car at 500 m
- Target: car driving at 30 km/h (8.3 m/s) in cross-path geometry
- Expected beat frequency at 500 m: f_beat = 2×500×100e6/(3e8×1e-3) = 333 Hz
- Expected Doppler: f_dop = 2×8.3/0.02985 = 556 Hz
- Capture 100-chirp CPI, compute range-Doppler map
- Identify car peak in RDM, record range, velocity, SNR

### Test M-011: Beam Steering Verification
- Place two corner reflectors at 0° and +30° azimuth (100 m range)
- Steer beam to 0°: verify reflector 1 peak > reflector 2 peak by >10 dB
- Steer beam to 30°: verify reflector 2 peak > reflector 1 peak by >10 dB
- Record beam pattern main lobe width

---

## 3. Maximum Range Test Plan (2 – 3 km)

### ⚠️ Regulatory Requirement
**Must receive BNetzA confirmation before this test.**
Operate under Klasse A amateur radio license, identify station every 10 min.

### Location Requirements
- Elevated position with >3 km clear line of sight
- No interference to/from primary users (satellite uplinks, etc.)
- Permission from landowner for field access
- Weather: no rain (adds attenuation), no lightning

### Test M-020: Vehicle Detection at 2 km
- Target: car at known distance (measure with GPS or rangefinder)
- Predicted SNR at 2 km: ~30 dB (car target, from link budget)
- Acceptance: detect car at 2 km with SNR > 15 dB in >80% of CPIs

### Test M-021: Maximum Range Determination
- Move car from 1 km to 5 km in 0.5 km steps
- At each range: capture 20 CPIs, record mean SNR and detection rate
- Plot SNR vs range, compare to link budget prediction
- Find R_max (range where SNR drops below 15 dB) — expected 3–5 km

---

## 4. Data Collection Workflow

```
1. aeris_control.py connect --port /dev/ttyACM0
2. aeris_control.py beam --az 0 --el 0
3. aeris_control.py chirp --start 10e9 --stop 10.1e9 --time-us 1000
4. aeris_control.py pa-enable 1
5. aeris_control.py capture --n-chirps 100 --save session_001
6. (repeat steps 2-5 for each steering angle)
7. aeris_control.py pa-enable 0
8. python fmcw_processing.py --session session_001 --plot
```

---

## 5. Expected Performance Table

| Range (km) | Target | σ (dBsm) | Predicted SNR (dB) | Detect? |
|---|---|---|---|---|
| 0.010 | Corner reflector | 21 | >60 | Yes |
| 0.100 | Car | 10 | ~45 | Yes |
| 0.500 | Car | 10 | ~33 | Yes |
| 1.000 | Car | 10 | ~27 | Yes |
| 2.000 | Car | 10 | ~21 | Yes |
| 3.000 | Car | 10 | ~17 | Yes (marginal) |
| 4.000 | Car | 10 | ~15 | Threshold |
| 5.000 | Car | 10 | ~12 | Borderline |
| 5.000 | Truck (σ=100m²) | 20 | ~22 | Yes |
