# AERIS-10P Phased Array System Design
## Rev 1.0 — 2026-07-14

---

## 1. Array Geometry

**4×4 Rectangular Array** — separate TX and RX panels

```
Array layout (top view, looking toward target):

TX Array:                      RX Array:
Col: 0   1   2   3            Col: 0   1   2   3
     |   |   |   |                  |   |   |   |
Row 0: [P] [P] [P] [P]         Row 0: [P] [P] [P] [P]  
Row 1: [P] [P] [P] [P]         Row 1: [P] [P] [P] [P]
Row 2: [P] [P] [P] [P]         Row 2: [P] [P] [P] [P]
Row 3: [P] [P] [P] [P]         Row 3: [P] [P] [P] [P]

Element spacing: 15 mm × 15 mm (λ/2 at 10 GHz)
Array aperture:  45 mm × 45 mm (3 spaces × 15 mm)
Array area:      2025 mm²
```

**Element numbering:** element(row, col), row 0 = top, col 0 = left. Element index in SPI chain: 4×row + col.

---

## 2. Beam Steering Mathematics

**Phase gradient for beam steering to (az, el):**

For element at position (row i, col j), centered at array midpoint (1.5, 1.5):
```
x_pos = (j - 1.5) × d    [mm]   (azimuth direction)
y_pos = (i - 1.5) × d    [mm]   (elevation direction)

Phase: φ(i,j) = (2π/λ) × (x_pos × sin(az) + y_pos × sin(el))
             = (2π/0.02985) × (15e-3 × (j-1.5) × sin(az) + 15e-3 × (i-1.5) × sin(el))
             = π × ((j-1.5) × sin(az) + (i-1.5) × sin(el))   [radians]
             = 180 × ((j-1.5) × sin(az) + (i-1.5) × sin(el)) [degrees]
```

**Examples:**
- Broadside (az=0°, el=0°): φ(i,j) = 0° for all elements ✓
- Steer az=30°, el=0°:
  - φ(0,0) = 180×((0-1.5)×0.5) = 180×(-0.75) = -135° → +225° (add 360°)
  - φ(0,3) = 180×((3-1.5)×0.5) = 180×(0.75) = +135°
  - Gradient: 180×0.5 = 90° per column spacing

**Code calculation:**
```python
code = round(phase_deg / 5.625) % 64  # 5.625° per LSB
```

---

## 3. Array Factor

For N×M rectangular array with uniform weighting:

```
AF(θ_az, θ_el) = AF_x(θ_az) × AF_y(θ_el)

AF_x(θ_az) = sin(N π d/λ sin(θ_az - θ_0_az)) / (N sin(π d/λ sin(θ_az - θ_0_az)))

For N=4, d=λ/2:
  AF_x(θ) = sin(2π sin(θ - θ_0)) / (4 sin(π/2 sin(θ - θ_0)))
```

**Beam width (−3 dB) for 4-element, λ/2 spacing:**
```
BW_3dB ≈ 0.886 × λ / (N × d) = 0.886 / (4 × 0.5) = 0.443 radian = 25.4°
```
(for broadside; increases at scan angles)

**Grating lobes:** with d = λ/2, grating lobe at sin(θ_GL) = ±1 → θ_GL = ±90° (beyond visible space). No grating lobes within ±90°. ✓

**First sidelobe level (uniform):** −13.3 dB

**With Chebyshev weighting (30 dB SLL):**
- Weights: [0.745, 1.0, 1.0, 0.745] (for 4 elements, 30 dB SLL)
- SLL improves to −30 dB at cost of slightly wider beam (+15%)
- Implement by weighting combining network or post-processing

---

## 4. Digital Phase Shifter Control

**HMC647ALP5E programming:**
- 6-bit control word sent via SPI
- Bit 5 (MSB) = 180°, Bit 4 = 90°, Bit 3 = 45°, Bit 2 = 22.5°, Bit 1 = 11.25°, Bit 0 = 5.625°
- Phase = sum of active bits
- Code 0 = 0°, Code 63 = 354.375° (not 360° — there's a 5.625° "dead zone")

**Beam update rate:**
- 16 bytes per array × 8 bits / 10 MHz SPI = 12.8 µs per array update
- Both TX and RX arrays: 2 × 12.8 = 25.6 µs total beam update time
- This allows >39,000 beam positions per second — far more than needed

**Scan rate:**
- With 100 chirps per CPI (100 ms), we can scan 10 beam positions per second
- For ±45° range in 5° steps: 19 positions × 100 ms = 1.9 s per full scan

---

## 5. MIMO Virtual Array

Using separate 4×4 TX and 4×4 RX arrays, we can achieve MIMO processing:

**Virtual aperture:** For MIMO with TX at positions x_tx and RX at positions x_rx:
- Virtual element at x_tx + x_rx for each TX-RX pair
- 16 TX × 16 RX = 256 virtual elements (but many are co-located)
- With TX and RX panels displaced by half the array aperture: 
  Maximum unique virtual positions ≈ 32 (8×4 virtual array)
- Effective aperture: 8×4 virtual elements → beam width ≈ 11° azimuth

**MIMO processing** (for future implementation):
- Transmit orthogonal waveforms from TX elements (e.g., frequency-domain multiplexing)
- Separate received signals per TX element at RX
- Combine for larger virtual aperture
- Beyond scope of v1.0 — document for future upgrade

---

## 6. Calibration Algorithm

**Phase calibration procedure:**
1. Inject known CW signal at element i RF port
2. All other elements: set to max attenuation (if available) or disconnect
3. Measure S21 phase at IF output for each of 64 codes
4. Compute error: error[i][k] = k × 5.625° − measured[i][k]
5. Store correction table (16×64 float32 = 4096 values per array)
6. At runtime: corrected_code = nominal_code + round(error[i][nominal_code]/5.625)

**Expected calibration stability:** 
- Temperature coefficient: ~0.1°/°C for HMC647A
- For 20°C temperature change: 2° drift — recalibrate if temp changes >20°C

---

## 7. Failure Mode Analysis

**One phase shifter fails (stuck at 0°):**
- 15/16 elements correctly steered
- One element contributes to broadside beam, not steered beam
- Effect: ~0.6 dB gain loss, sidelobe level increases by ~1 dB
- Detection: compare phase shifter response to expected during self-test
- Mitigation: set failed element's code to 0 and apply weight 0 in software

**One LNA fails (open circuit):**
- 15/16 RX elements active
- Effect: ~0.3 dB gain loss
- Still functional at reduced sensitivity

**PA fails:**
- Complete loss of TX → no radar function
- Replace HMC451 (QFN package, hot-air rework required)
