# AERIS-10P Calibration Procedures
## Rev 1.0 — 2026-07-14

---

## Required Equipment

| Item | Specification | Purpose |
|---|---|---|
| Spectrum Analyzer | 0–20 GHz, resolution <1 kHz | Verify VCO frequency and PA output |
| Vector Network Analyzer (VNA) | 0–20 GHz (e.g., Keysight E5080B, R&S ZVA) | S11/S21 measurements, phase calibration |
| Power Meter | HP 437B + 8481A sensor or equivalent | TX power measurement |
| Frequency Counter | GPS-disciplined reference, 0.01 Hz resolution | OCXO calibration |
| Signal Generator | 10 GHz CW, ±1 dBm accuracy | Inject reference signal |
| Oscilloscope | ≥500 MHz, optional | FMCW chirp visualization |
| SMA attenuator | 20 dB, calibrated | Protect equipment from TX power |
| 50Ω terminator ×5 | SMA, 18 GHz | Terminate unused ports |

---

## 1. OCXO Frequency Calibration

**Objective:** Set OCXO to exactly 10.000000 MHz ±1 Hz

**Procedure:**
1. Connect OCXO output to frequency counter with GPS-disciplined reference
2. Allow 15 minutes warm-up time for OCXO temperature stabilization
3. Read displayed frequency. Target: 10.000000 MHz
4. If off by more than 1 Hz: adjust OCXO EFC (external frequency control) pin via firmware DAC
   - EFC voltage range: 0–5V (centered at 2.5V for nominal frequency)
   - Typical coefficient: ±0.5 ppm/V → ±5 Hz/V adjustment
5. Iterate until frequency counter shows 10.000000 ±0.001 MHz
6. Record OCXO serial number, calibration date, EFC voltage setting

**Acceptance:** Frequency within ±1 Hz of 10.000000 MHz

---

## 2. TX Power Calibration

**Objective:** Verify and document TX output power across chirp band

**Procedure:**
1. Connect 20 dB attenuator + power sensor to J_TX_RF SMA on main board
2. Send `CMD_SET_PA_ENABLE enable=1` via USB
3. Set chirp: 10.000–10.100 GHz, 1 ms sweep
4. Measure power at: 10.000, 10.025, 10.050, 10.075, 10.100 GHz (using SA in peak-hold mode)
5. Record all measured values in test data sheet
6. Compute flatness: max − min across band. Specification: ≤ 2 dB
7. Verify PA temperature: infrared thermometer on heatsink. Must be < 60°C after 5 min
8. If power is too high (> +30 dBm): reduce PA gate bias voltage via trimmer (R_VG on RF board)
9. If power is too low: check PA VDD supply voltage, verify SMA connections

**Acceptance:** Power at 10.05 GHz: +25 to +30 dBm. Flatness ≤ 2 dB across 100 MHz

---

## 3. Phase Shifter Calibration

**Objective:** Measure actual phase vs commanded code for all 32 phase shifters

**Setup:**
- VNA port 1 → HMC647A RF_IN (via SMA on antenna feed port, inject from divider side)
- VNA port 2 → HMC647A RF_OUT (antenna feed port for one element at a time)
- Measure S21 phase at 10.05 GHz

**Procedure (per element):**
1. Connect VNA to element under test (element 0 first)
2. Set all other elements to code=0 (isolation state)
3. For code = 0, 1, 2, ..., 63:
   a. Send SPI command via `aeris_control.py element_code --element N --code K`
   b. Wait 10 ms for VNA measurement
   c. Record VNA S21 phase reading
4. Compute phase error: error[k] = k × 5.625° − measured[k]
5. Store in calibration file: `calibration_tx_element_N.npy`
6. Repeat for all 16 TX elements, then all 16 RX elements

**Automation:**
```python
python Software/Signal_Processing/calibration.py --measure --element N --output cal_tx.npy
```
(Requires VNA Python interface — implement via pyvisa or similar)

**Acceptance:** RMS phase error per element ≤ 3° after calibration correction applied

---

## 4. RX Noise Figure Calibration

**Objective:** Measure RX chain noise figure using Y-factor method

**Setup:**
- Calibrated noise source (ENR known, e.g., Keysight 346B) → RX antenna input port
- IF output → spectrum analyzer

**Procedure:**
1. Record noise source ENR at 10.05 GHz (from calibration certificate)
2. With noise source OFF: measure output noise power N_cold on spectrum analyzer
3. With noise source ON: measure output noise power N_hot
4. Y-factor: Y = N_hot / N_cold (linear)
5. NF = ENR − 10·log10(Y − 1) (in dB, T_cold = 290 K assumed)
6. Expected result: ~2 dB (dominated by HMC1040 LNA NF = 1.5 dB)

**Acceptance:** System NF ≤ 3 dB

---

## 5. Range Calibration

**Objective:** Verify that detected range matches physical range to within ±1.5 m

**Setup:**
- Corner reflector at known distance (e.g., exactly 25.00 m in corridor or outdoor)
- Full radar system operating (PA enabled, calibration loaded)

**Procedure:**
1. Measure corner reflector distance precisely with tape measure (reference ±0.05 m)
2. Point radar antenna at corner reflector (broadside, 0° az, 0° el)
3. Capture 100 chirps and compute range profile
4. Identify range bin with peak amplitude
5. Compare detected range to physical distance
6. If offset: adjust software delay compensation in config.yaml → `range_offset_m`

**Acceptance:** Detected range within ±1.5 m (one range bin) of physical distance

---

## 6. Calibration Schedule

| Calibration | First Use | Periodic |
|---|---|---|
| OCXO frequency | ✓ | Every 100 operating hours |
| TX power | ✓ | Every 50 hours or after PA replacement |
| Phase shifter full | ✓ | Every 6 months |
| Phase shifter partial | — | After ±20°C temperature change |
| Noise figure | ✓ | Annually |
| Range calibration | ✓ | After software update |

---

## 7. Calibration Data Storage

All calibration files stored in `Software/Signal_Processing/` directory:
- `calibration_tx.npy` — TX array (16 × 64 float32 correction table)
- `calibration_rx.npy` — RX array (16 × 64 float32 correction table)
- `calibration_meta.yaml` — Date, temperature, operator, equipment used

Load calibration in control software:
```yaml
# In config.yaml:
array:
  calibration_file: calibration_tx.npy
```
