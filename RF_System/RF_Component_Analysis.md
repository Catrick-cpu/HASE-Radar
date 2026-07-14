# AERIS-10P RF Component Analysis
## Rev 1.0 — 2026-07-14

---

## 1. System Noise Figure Analysis

**Cascaded noise figure (Friis formula):**

For the receive chain: Antenna → Feed → Phase Shifter → Combiner → LNA → Mixer → IF Amp

```
Component          NF (dB)    Gain (dB)    NF (linear)   Gain (linear)
─────────────────────────────────────────────────────────────────────────
RX feed loss        0.3       -0.3          1.072          0.933
RX phase shifter    4.0       -4.0          2.512          0.398
RX combiner loss    1.0       -1.0          1.259          0.794
HMC1040 LNA         1.5      +18.0          1.413         63.096
HMC213B mixer       6.0       -6.0          3.981          0.251
IF amplifier        5.0      +20.0          3.162        100.0

Pre-LNA total loss: 0.3 + 4.0 + 1.0 = 5.3 dB = 3.388× loss
NF_pre_lna = 3.388 (linear)
G_pre_lna = 10^(-5.3/10) = 0.295 (linear)

Friis (LNA term): NF_LNA = (NF_lna_lin - 1) / G_pre_lna = (1.413-1)/0.295 = 1.400
Friis (mixer term): NF_mix = (NF_mix_lin - 1) / (G_pre_lna × G_lna) = (3.981-1)/(0.295×63.1) = 0.160
Friis (IF amp term): NF_if = (3.162-1)/(0.295×63.1×0.251) = 0.462

Total NF_sys (linear) = 3.388 + 1.400 + 0.160 + 0.462 = 5.41
Total NF_sys (dB) = 10 × log10(5.41) = 7.33 dB
```

Wait, that seems high. Let me recalculate more carefully:

The issue is the pre-LNA loss. 5.3 dB of loss before the LNA directly adds 5.3 dB to the noise figure. This is the main challenge.

**Practical consideration:** In a real system, the combiner and phase shifters would be after combining, which means the system NF is largely determined by:

NF_sys ≈ L_path + NF_LNA = 5.3 + 1.5 = 6.8 dB ≈ 7 dB

For a 7 dB NF, the noise floor at 10 Hz BW:
N_floor = -174 + 10 + 7 = -157 dBm

This is still acceptable — we have >>15 dB SNR at 3 km for a car.

**Improvement option:** Place LNA before phase shifter to reduce NF:
- Put HMC1040 immediately at antenna (before phase shifter)
- New pre-LNA loss: only 0.3 dB feed loss
- NF_sys ≈ 0.3 + 1.5 ≈ 1.8 dB
- This is the "LNA-first" architecture — used in sensitive radar receivers

**Design decision for v1.0:** Use LNA-first architecture (LNA → phase shifter → combiner) for best NF.
Updated architecture: Each element: Patch → LNA → Phase Shifter → Combiner → Mixer

---

## 2. Phase Noise Analysis

**VCO phase noise: HMC733**
- L(f) = -120 dBc/Hz at 100 kHz offset
- L(f) = -140 dBc/Hz at 1 MHz offset
- Typical flicker noise corner: ~1 kHz

**Impact on FMCW radar:**

Phase noise in FMCW creates range-dependent noise floor that limits clutter suppression:
```
Noise power from phase noise at range R:
  N_pn(R) ≈ 2 × L(f_beat) × (signal power at R)
  
where f_beat = 2R × B/(c×T) — the beat frequency for that range

At R = 100m: f_beat = 67 Hz
  L(67 Hz) ≈ -80 dBc/Hz (estimate from 1/f noise)
  Phase noise noise floor ≈ -80 - 10·log10(1/1) = -80 dBc relative to signal

At R = 1 km: f_beat = 667 Hz  
  L(667 Hz) ≈ -100 dBc/Hz (beyond flicker corner, starts dropping)
  Phase noise noise floor ≈ -100 dBc

At R = 3 km: f_beat = 2 kHz
  L(2 kHz) ≈ -115 dBc/Hz
  Negligible at this range
```

**Conclusion:** Phase noise is mainly a concern at short ranges (<500m) where it may limit clutter suppression. For 2–3 km detection of moving vehicles, phase noise from HMC733 is not the limiting factor.

---

## 3. Power Budget

### TX Power Budget
```
HMC733 VCO output:            +17.0 dBm
  - to ADF4159 RFIN (tap):    -10.0 dB coupler
  - to PA (main):               -0.5 dB cable

HMC451 PA input:               +6.5 dBm
  PA gain:                     +28.0 dB
HMC451 PA output:             +29.0 dBm (at P1dB = +29 dBm)
  (Operate at +27 dBm for 2dB backoff for linearity)

1:16 Wilkinson divider:
  Theoretical split loss:      -12.04 dB (10·log10(1/16))
  Practical insertion loss:     -1.00 dB
  Total divider loss:          -13.04 dB

Per-element power at divider output:   +27 - 13.04 = +13.96 dBm ≈ +14 dBm

HMC647A phase shifter IL:      -4.0 dB
Per-element power at antenna:  +14 - 4.0 = +10 dBm

Patch antenna gain:            +6.0 dBi
Per-element EIRP:              +10 + 6.0 = +16 dBm EIRP

Array EIRP (16 elements):
  Per-element EIRP + array combining factor:
  EIRP_array = 16 × (+16 dBm) = 16 × 39.8 mW = 637 mW EIRP ≈ +28.0 dBm
  OR: +10 dBm element power + 6 dBi gain + 12 dB array = +28 dBm EIRP
  
Total EIRP: +28 dBm = 631 mW
Legal limit (75W PEP TX power, no EIRP limit for amateur): PASS ✓
```

### RX Signal Budget at 3 km (Car Target)
```
Target RCS (car): 10 m² = 10 dBsm

TX EIRP:                    +28.0 dBm
Free-space loss TX (3km):   -92.0 dB  (20·log10(4π×3000/0.02985))
Target reflection:          +10.0 dBsm
Free-space loss RX (3km):   -92.0 dB
RX element gain:             +6.0 dBi
RX array combining:         +12.0 dB  (16 elements)
                            ─────────
Signal at combiner output: 28 - 92 + 10 - 92 + 6 + 12 = -128 dBm

HMC1040 LNA gain:           +18.0 dB  → -110 dBm at LNA output
HMC647A phase shifter:       -4.0 dB  → (before LNA in v2 architecture)
HMC213B mixer conversion:    -6.0 dB  → -116 dBm at IF
IF amplifier:               +20.0 dB  → -96 dBm at ADC

Noise floor (NF=2dB, BW=10Hz): -172 + 10 + 2 = -160 dBm at LNA input
After IF chain gain (18-6+20=32dB): -160 + 32 = -128 dBm at ADC

SNR = -96 - (-128) = +32 dB  → well above 15 dB threshold ✓
```

---

## 4. Component Availability (2026 Market)

| Component | Mouser Stock | Lead Time | Risk |
|---|---|---|---|
| HMC647ALP5E | Check: may be 4-8 weeks | Medium | HIGH — order early |
| HMC1040LP4E | Usually 2-4 weeks | Low | Medium |
| HMC213B | Usually in stock | Low | Low |
| HMC451LS6GE | 4-8 weeks typical | Medium | Medium |
| HMC733LP6CE | 4-8 weeks typical | Medium | Medium |
| ADF4159CCPZ | Usually in stock | Low | Low |
| STM32H743ZIT6 | Check availability — MCU shortages may apply | Variable | Medium |
| ADS8661IRGAT | Usually in stock | Low | Low |

**Action:** Check current stock on Mouser/DigiKey before finalizing design. If HMC647A is unavailable, investigate MAPS-010144 (5-bit alternative) — would require redesign of beam steering algorithm.

---

## 5. Component Alternatives

| Primary | Alternative | Trade-off |
|---|---|---|
| HMC647ALP5E | MAPS-010144 | 5-bit (11.25° LSB) vs 6-bit (5.625°) — slightly worse beam control |
| HMC1040LP4E | TQL9092 | NF 1.7 dB vs 1.5 dB — 0.2 dB system NF worse |
| HMC733LP6CE | HMC-SXX112 | Integrated PLL+VCO — simpler but less phase noise control |
| HMC451LS6GE | HMC943 | Higher output (+33 dBm) but $150+ and harder to source |
| ADF4159CCPZ | ADF4169 | Same function, different package (QFN vs CP) |
| STM32H743ZIT6 | STM32H753ZIT6 | STM32H753 has crypto engine, otherwise same |
| ADS8661IRGAT | ADS9224R | Higher speed (3 MSPS) — overkill but drop-in compatible |
