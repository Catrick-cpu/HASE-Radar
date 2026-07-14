# AERIS-10P RF System Architecture
## Rev 1.0 — 2026-07-14

---

## 1. RF Signal Chain Overview

```
TRANSMIT PATH:
══════════════
OCXO (10 MHz)
    │
    ▼
ADF4159 PLL (programs VCO frequency ramp: 10.000→10.100 GHz, 1 ms sawtooth)
    │ Vtune (0-12V control voltage)
    ▼
HMC733 VCO (+17 dBm, 10.000-10.100 GHz chirp)
    │ RF out, semi-rigid cable
    ├───────────────────────────────► Directional coupler (-10 dB tap → +7 dBm LO to mixer)
    │
    ▼
HMC451 PA (+28 dB gain → +29 dBm output)
    │ +29 dBm (1-way 1:16 Wilkinson divider)
    ▼
1:16 Wilkinson Power Divider Network
(-12 dB split + -1 dB loss = -13 dB → +16 dBm per element input)
    │ 16 outputs × +16 dBm
    ▼
16× HMC647ALP5E TX Phase Shifters (-4 dB IL → +12 dBm per element output)
    │ 16 outputs × +12 dBm, phase-controlled
    ▼
16× TX Patch Antennas (+6 dBi gain, λ/2 spacing = 15 mm)
    │ Total EIRP = 12 + 6 + 10·log10(16) + 12·log10(η) ≈ 30 dBm EIRP per element...
    │ Array EIRP = TX power + array gain = 27 dBm + 22 dBi = 49 dBm EIRP total
    ↓↓↓ RADIATED AT TARGET ↓↓↓

RECEIVE PATH:
═════════════
16× RX Patch Antennas (+6 dBi gain each)
    │ 16 signals × received power
    ▼
16× HMC647ALP5E RX Phase Shifters (-4 dB IL) — steer receive beam
    │ 16 coherent phase-shifted signals
    ▼
16× HMC1040LP4E LNA (+18 dB gain, NF 1.5 dB)
    │ Amplified signals
    ▼
16:1 Wilkinson Combiner (+12 dB combining - 13 dB split → -1 dB net from combining)
    │ Single combined signal
    ▼
HMC213B Double-Balanced Mixer
    │← LO: +10 dBm from VCO tap
    │ IF output: beat note (0–5 kHz for R=0–3 km)
    ▼
IF Amplifier (BFU610F or similar, +20 dB, low-noise)
    ▼
Low-Pass Filter (fc = 10 kHz, Chebyshev 7th order, >60 dB at 50 kHz)
    ▼
ADS8661 ADC (16-bit, 1 MSPS, decimate to 8 kSPS)
    ▼
STM32H743 MCU → USB → Raspberry Pi 5 → FMCW Processing
```

---

## 2. FMCW Chirp Parameters

| Parameter | Value | Calculation |
|---|---|---|
| Start frequency f_start | 10.000 GHz | Within 10.000–10.500 GHz amateur band |
| Stop frequency f_stop | 10.100 GHz | 100 MHz bandwidth |
| Bandwidth B | 100 MHz | f_stop − f_start |
| Chirp time T_chirp | 1 ms | Chosen for range-Doppler balance |
| Sweep rate | 100 GHz/s | B/T_chirp = 100e6/1e-3 |
| PRF | 1000 Hz | 1/T_chirp |
| Chirps per CPI | 100 | Integration time = 100 ms |

**Derived performance:**
- Range resolution: Δr = c/(2B) = 3e8/(2×100e6) = **1.5 m**
- Max unambiguous range: R_max = c·fs/(4·sweep_rate) = 3e8×8000/(4×100e9) = **6 m** — wait, this seems wrong.

Correction: R_max = c·fs/(4B/T) = c·T·fs/(4B) = 3e8×1e-3×8000/(4×100e6) = 2400/400e6 = 6 µm? No...

Let me recalculate correctly:
- Beat frequency: f_beat = 2R·B/(c·T_chirp) = 2R × 100e6/(3e8 × 1e-3) = 2R × 333.3 Hz/m
- For R=3 km: f_beat = 2000 Hz = 2 kHz
- Nyquist sampling: fs=8 kSPS → max f_beat = 4 kHz → R_max = 4000/(2×333.3) = **6 km**

- Velocity resolution: Δv = λ/(2·Nc·T_chirp) = 0.02985/(2×100×1e-3) = **0.15 m/s**
- Max velocity: v_max = λ/(4·T_chirp) = 0.02985/(4×1e-3) = **7.46 m/s** — this is the ambiguous velocity

Wait: for 100 chirps at 1ms: v_max = λ/(4·T_chirp) = 0.02985/0.004 = 7.46 m/s, or:
Actually: v_max = λ·PRF/4 = 0.02985×1000/4 = 7.46 m/s unambiguous.

For most vehicle targets this is sufficient. For faster targets: use range-velocity ambiguity resolution with multiple PRFs.

---

## 3. Link Budget

| Stage | Gain/Loss (dB) | Cumulative (dBm) |
|---|---|---|
| TX power (PA output) | +27 | +27.0 |
| TX cable loss | -0.5 | +26.5 |
| TX divider loss (1:16) | -13.0 | +13.5 |
| TX phase shifter IL | -4.0 | +9.5 |
| TX feed/connector | -0.3 | +9.2 |
| TX element gain | +6.0 | +15.2 |
| TX array factor (16 elem) | +12.0 | +27.2 |
| TX EIRP | = | **+27.2 dBm** |
| Free-space path loss (3 km, 2-way) | -146.8 | -119.6 |
| Target RCS (car, 10 m²) | +10.0 | -109.6 |
| RX element gain | +6.0 | -103.6 |
| RX array combining | +12.0 | -91.6 |
| RX combiner loss | -1.0 | -92.6 |
| RX phase shifter IL | -4.0 | -96.6 |
| RX feed/connector | -0.3 | -96.9 |
| LNA gain | +18.0 | -78.9 |
| Mixer conversion loss | -6.0 | -84.9 |
| IF amplifier gain | +20.0 | -64.9 |
| **Signal at ADC** | = | **-64.9 dBm** |
| System noise floor (NF=2dB, B=10Hz) | = | -172 dBm |
| **SNR at 3 km** | = | **+107 dB** |

Note: This theoretical SNR accounts for FMCW processing gain. Practical SNR after CFAR detection ~40-60 dB. Far exceeds 15 dB detection threshold.

---

## 4. Frequency Plan

```
Reference:    OCXO 10.000 MHz
PLL output:   ADF4159 programs HMC733 from 10.000 to 10.100 GHz (chirp)
TX signal:    10.000–10.100 GHz (100 MHz bandwidth)
LO signal:    Same as TX (homodyne / zero-IF → actually very low IF = beat note)
IF output:    f_beat = 2R × B/(c×T) 
              R=100m: f_beat = 67 Hz
              R=1km:  f_beat = 667 Hz
              R=3km:  f_beat = 2000 Hz
              R=6km:  f_beat = 4000 Hz (Nyquist limit at 8 kSPS)
ADC:          8 kSPS → covers 0–4 kHz → 0–6 km range
```

---

## 5. Spurious Emissions Analysis

| Source | Frequency | Level (approx) | Mitigation |
|---|---|---|---|
| VCO 2nd harmonic | 20 GHz | -20 dBc | Low-pass filter after PA (if needed) |
| VCO 3rd harmonic | 30 GHz | -30 dBc | Beyond amateur bands, low impact |
| PLL reference spurs | 10 GHz ± 10 MHz | -60 dBc | ADF4159 fractional-N suppresses spurs |
| PLL in-band phase noise | | -120 dBc/Hz@100kHz | Limits clutter suppression |
| IF mixer products | DC to 20 GHz | -40 dBc | IF LPF removes most |

**Assessment:** Spurious emissions are well below 75W PEP legal limit and cause no interference concern at 1W TX power level.
