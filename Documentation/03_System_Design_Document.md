# AERIS-10P System Design Document Rev 1.0

**Document Number:** AERIS-10P-SDD-001  
**Revision:** 1.0  
**Date:** 2026-07-14  
**Author:** AERIS-10P Engineering Team  
**Status:** Released  
**Parent Documents:** AERIS-10P-SPEC-001, AERIS-10P-REQ-001

---

## Table of Contents

1. Architecture Overview
2. Subsystem Descriptions
   - 2.1 Chirp Generator (ADF4159 + HMC733)
   - 2.2 Transmit Chain
   - 2.3 Phase Shifter Array
   - 2.4 Antenna Array
   - 2.5 Receive Chain
   - 2.6 ADC and MCU Interface
   - 2.7 Signal Processing (RPi5)
   - 2.8 Power Subsystem
3. Link Budget
4. Signal Flow: Time and Frequency Domain
5. Beamforming Algorithm
6. Design Trade-offs
7. Interfaces
8. Performance Predictions

---

## 1. Architecture Overview

### 1.1 Design Philosophy

The AERIS-10P implements a homodyne FMCW radar architecture with analogue phased-array beamforming. The homodyne (self-mixing) approach uses the same chirp signal as both the transmit waveform and the local oscillator (LO) reference for the receiver mixer, generating an intermediate frequency (IF) beat signal directly at baseband without a separate IF stage. This choice simplifies the receiver architecture: no IF amplifier, no IF filter design at high frequency, and no separate LO synthesiser. The penalty is increased susceptibility to DC offset (zero-range clutter) and 1/f noise at very low IF frequencies.

The beamforming is performed in the analogue domain using 6-bit digital phase shifters on each transmit and receive element. This is designated as analogue beamforming (as opposed to digital beamforming, where each element has its own ADC). Analogue beamforming was selected for this application to avoid the cost and complexity of 32 high-speed ADC channels; the trade-off is that only a single beam direction can be formed at any instant, and changing the beam direction requires reprogramming the phase shifters between CPI intervals.

### 1.2 Complete Signal Chain Block Diagram

```
=============================================================
                    AERIS-10P SIGNAL CHAIN
=============================================================

  10 MHz OCXO (ABRACON AOCJY-10, ±0.01 ppm)
         |
         | REF_CLK
         v
  +------+-------+
  |  ADF4159CCPZ  |<--- SPI Config (STM32H743, SPI1)
  |  Frac-N PLL   |<--- TXDATA ramp trigger (GPIO, TIM2)
  |  + Ramp Engine|
  +------+-------+
         | VCO_TUNE voltage (0–10 V analog)
         | PLL_LOCK indicator (GPIO)
         v
  +------+-------+
  | HMC733LP6CE   |  9.5–11 GHz, +17 dBm
  |  VCO          |  Phase noise: −110 dBc/Hz @1 MHz offset
  +------+-------+
         |
         +--[−10 dB coupler]-----> LO reference to Mixer
         |
         v
  +------+-------+
  | HMC451LS6GE   |  Gain 28 dB, P1dB +29 dBm
  |    TX PA      |  Input: +17−28 = −11 dBm drive → +30 dBm out
  +------+-------+
         |
         | +30 dBm
         v
  PE8316 Circulator/Isolator (9.5–10.5 GHz, ISO 20 dB)
         |
         v
  1:16 Wilkinson Divider Network (4 stages binary tree)
  Insertion loss: ~12.0 dB (10·log10(16) = 12.04 dB ideal)
  Microstrip on RO4003C, 50 Ω lines, λ/4 transformers
         |
    (split to 16 paths, −12 dBm per path nominal)
         |
  [x16 identical TX paths]
         |
         v
  HMC647ALP5E Phase Shifter (6-bit, 0–360°, IL ~6 dB)
  SPI daisy-chain per quadrant (4 × 4-device chains, SPI2–SPI5)
         |
  −18 dBm per path (after phase shifter loss)
         v
  4×4 TX Patch Array
  Rogers RO4003C, εr=3.55, 13.8×13.8 mm patches
  Element spacing: 15 mm (λ/2 at 10 GHz)
  Array gain: 24 dBi theoretical, 22 dBi practical
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  FREE SPACE
  4×4 RX Patch Array (physically separate, 50 mm away from TX)
  Rogers RO4003C, same geometry as TX
  Array gain: 24 dBi theoretical, 22 dBi practical
         |
  [x16 identical RX paths]
         v
  HMC1040LP4E LNA (NF 1.5 dB, Gain 18 dB, 8–12 GHz)
  (One LNA per element or per sub-array: design decision for
   SNR optimisation — per-element placement preferred)
         |
         v
  HMC647ALP5E Phase Shifter (6-bit, RX beam steering)
  SPI daisy-chain per quadrant (SPI2–SPI5, shared or SPI3–SPI6)
         |
         v
  16:1 Wilkinson Combiner Network (4 stages binary tree)
  Combining loss: ~12.0 dB (unavoidable in passive combiner)
  Net RX signal-chain gain (16 paths): G_array = 18 − 6 − 12 = 0 dB
  (Array gain provides the effective aperture; see link budget)
         |
         v
  +------+--------+
  |   HMC213B      |<--- LO reference (from VCO −10 dB tap)
  | Double-Balanced|     LO power: +7 dBm (after coupler and cable loss)
  |    MIXER       |     Conversion loss: ~6 dB
  +------+--------+
         |
         | IF (beat frequency, DC to ~500 kHz)
         | Frequency = 2·B·R/(c·T_chirp)
         v
  Anti-aliasing LPF (fc = 500 kHz, 5th-order Butterworth)
  Instrumentation Amplifier (gain ×4, bandwidth 1 MHz)
  (Raises signal level to match ADC full-scale ±4.096 V range)
         |
         v
  +------+--------+
  | ADS8661IRGAT   |  16-bit SAR ADC, 1 MSPS
  |   ADC          |  SPI output to STM32H743 (SPI6)
  +------+--------+
         |
         | SPI, 16-bit words at 1 MSPS (16 Mbit/s SPI clock)
         v
  +------+--------+
  | STM32H743ZIT6  |  480 MHz Cortex-M7
  |   MCU          |  DMA double-buffer (2 × 1000 samples)
  |                |  FreeRTOS: ADC task, SPI task, USB task
  +------+--------+
         |
         | USB 2.0 HS (480 Mbit/s) or 100BASE-T Ethernet
         | Bulk transfer: ~2 MB/s raw ADC data
         v
  +------+--------+
  | Raspberry Pi 5 |  Broadcom BCM2712, quad Cortex-A76, 2.4 GHz
  |   8 GB LPDDR4X |  Processing: Python + NumPy FFT pipeline
  |                |  Display: HDMI or Ethernet to laptop
  +------+--------+
         |
         | Ethernet (100/1000 BASE-T)
         v
  Operator Laptop (PyQt6 GUI, range-Doppler map display)

=============================================================
  POWER SUPPLY TREE
=============================================================

  24 V DC Input (Anderson PowerPole PP45, max 8 A)
         |
         +---> LT8612 -----> 5.0 V / 5 A (RF MMICs, phase shifters)
         |
         +---> LT8607 -----> 3.3 V / 3 A (STM32H743, ADF4159, logic)
         |
         +---> TPS65133 ---> ±5.0 V / 1 A (RF bias, VCO gate voltage)
         |
         +---> Direct 24V -> RPi5 (via 5V/5A USB-C PD adapter)

=============================================================
  DIGITAL CONTROL BUS MAP
=============================================================

  STM32H743 SPI1  --> ADF4159 (PLL/chirp ramp config)
  STM32H743 SPI2  --> HMC647A × 4 TX quadrant 1 (elements 1–4, daisy-chain)
  STM32H743 SPI3  --> HMC647A × 4 TX quadrant 2 (elements 5–8, daisy-chain)
  STM32H743 SPI4  --> HMC647A × 4 RX quadrant 1 (elements 1–4, daisy-chain)
  STM32H743 SPI5  --> HMC647A × 4 RX quadrant 2 (elements 5–8, daisy-chain)
  STM32H743 SPI6  <-- ADS8661 ADC (16-bit samples at 1 MSPS)
  STM32H743 TIM2  --> ADF4159 TXDATA (chirp ramp trigger, 1 kHz)
  STM32H743 ADC1  <-- NTC thermistor (PA temperature monitor)
  STM32H743 GPIO  --> PA_ENABLE (load switch control)
  STM32H743 GPIO  --> RF_KILL (E-stop, pulled low by kill switch)
  STM32H743 USB HS --> RPi5 USB 3.0 port (bulk data transfer)
  RPi5 Ethernet   --> Operator laptop (control, display, logging)
```

---

## 2. Subsystem Descriptions

### 2.1 Chirp Generator: ADF4159CCPZ + HMC733LP6CE

#### 2.1.1 ADF4159 PLL Architecture

The ADF4159CCPZ is a 13 GHz fractional-N PLL with an integrated digital ramp generator specifically designed for FMCW radar applications. Its key functional blocks are:

- **Phase-Frequency Detector (PFD):** Compares the divided VCO feedback to the 10 MHz reference at a comparison frequency of 10 MHz (REF_CLK passed directly without division when RDIV = 1). The higher PFD frequency improves in-band phase noise.
- **Fractional-N Divider:** The feedback divider uses a sigma-delta modulator (SDM) to implement fractional division. For a target frequency of 10.0 GHz with 10 MHz reference, the integer part N = 1000, fractional part = 0. For 10.1 GHz, N = 1010, fractional part = 0. Intermediate frequencies use fractional values.
- **Digital Ramp Engine:** The ADF4159 contains two programmable ramp registers (RAMP0 and RAMP1) that automatically step the frequency from f_start to f_stop in user-defined frequency increments at a user-defined step rate. Each step is:
  - **Frequency step size:** Δf_step = BW/(N_steps) = 100 MHz / 1000 steps = 100 kHz per step.
  - **Step clock rate:** The step clock is derived from the PFD frequency: f_step_clk = f_PFD / CLK_DIV = 10 MHz / 10 = 1 MHz. Thus each step occurs every 1 μs, giving a total ramp time of 1000 steps × 1 μs = 1 ms. This matches the required chirp duration exactly.
- **TXDATA pin:** A logic-level input that triggers the ramp start. The STM32H743 TIM2 output compare generates a 1 kHz square wave (500 μs high, 500 μs low) to trigger sawtooth chirps. The 500 μs guard interval (actually 10% = 100 μs of each 1 ms period) allows VCO to reset to f_start before the next chirp.

#### 2.1.2 ADF4159 Register Programming

The ADF4159 is programmed via a 3-wire SPI interface (CLK, DATA, LE) at startup and whenever chirp parameters change. Key register fields:

| Register | Field | Value | Description |
|---|---|---|---|
| R0 | INT (integer part N) | 1000 | Sets f_VCO start: 1000 × 10 MHz = 10.0 GHz |
| R0 | FRAC1 | 0 | No fractional offset at start |
| R1 | FRAC2 | 0 | Sigma-delta modulator 2nd order term |
| R3 | RAMP_MODE | 00 | Sawtooth ramp (single-slope up) |
| R4 | CLK_DIV_MODE | 01 | Fast lock mode clock divider |
| R4 | CLK_DIV | 10 | Divide PFD clock by 10 for step clock |
| R5 | DEV_OFFSET | 0 | Frequency deviation start |
| R5 | DEV | 10 | Deviation step: 10 × (f_PFD/2²⁵) × CLK_DIV |
| R6 | STEP | 1000 | Number of frequency steps per ramp |
| R7 | DELAY_CLK | 01 | Delay clock source = PFD |
| R7 | DELAY_START | 100 | 100 μs guard time before ramp restarts |

#### 2.1.3 HMC733LP6CE VCO Characteristics

The HMC733LP6CE is a GaAs pHEMT MMIC VCO covering 9.5–11.0 GHz with an integrated buffer amplifier. Key characteristics relevant to the AERIS-10P design:

- **Tuning range:** 9.5–11.0 GHz for Vtune = 0–10 V (on-chip varactor).
- **Tuning sensitivity (Kv):** Approximately 200 MHz/V (varying with frequency and temperature). Non-linearity in Kv means the PLL loop filter bandwidth must be wide enough to track the ADF4159 ramp steps. At 100 kHz step size and Kv = 200 MHz/V, the required tuning voltage step is 100 kHz / 200 MHz/V = 0.5 mV, easily within the charge pump output resolution.
- **Output power:** +17 dBm from buffer output into 50 Ω.
- **Phase noise:** −110 dBc/Hz at 1 MHz offset (free-running). In-loop phase noise is typically −80 to −90 dBc/Hz at 100 kHz offset, depending on loop bandwidth and charge pump noise.
- **Supply:** +5 V, 100 mA nominal (500 mW DC).

#### 2.1.4 Loop Filter Design

The ADF4159 charge pump drives a passive 3rd-order loop filter (CP → R1 → C1 || (R2+C2) → R3 → VCO_TUNE). The loop filter is designed for:
- **Loop bandwidth:** ~200 kHz (sufficiently wide to track the 1 MHz chirp step rate, narrow enough to attenuate PFD reference spurs at 10 MHz).
- **Phase margin:** ≥50° for stability.
- **Calculated values (from ADIsimPLL):** R1 = 470 Ω, C1 = 1.0 nF, R2 = 220 Ω, C2 = 470 pF, R3 = 47 Ω. Component tolerances: 1% resistors, C0G/NP0 capacitors for temperature stability.

---

### 2.2 Transmit Chain

#### 2.2.1 PA Characteristics (HMC451LS6GE)

The HMC451LS6GE is a 2-stage GaAs pHEMT MMIC power amplifier in a leadless 6×6 mm LCC package. For the AERIS-10P:

- **Frequency range:** 13–16 GHz (datasheet primary range); gain decreases at 10 GHz but remains usable. Measured gain at 10 GHz: approximately 22 dB (vs. 28 dB at 14 GHz). For the design, 22 dB gain is assumed at 10 GHz.
- **Input drive level:** VCO output +17 dBm minus coupler loss (10 dB) = +7 dBm into PA input. With 22 dB gain: output = +29 dBm ≈ +30 dBm (allowing ±1 dB variation). This is at or below P1dB, operation is linear.
- **DC bias:** Drain voltage +5 V from the 5 V rail via a bias network (drain choke: 56 nH wire-wound, 1 nF gate bypass). Gate voltage: −0.5 V from TPS65133 negative rail via resistive divider (sets quiescent drain current to 350 mA for class-A linear operation).
- **Thermal:** At +30 dBm output, DC power = 5 V × 350 mA = 1.75 W. RF output power = 1 W. Dissipated power = 0.75 W. At θ_jc = 15°C/W and θ_ca (PCB thermal via to enclosure wall) = 10°C/W, junction temperature at 50°C ambient = 50 + 0.75 × 25 = 68.75°C. Well within 150°C maximum.

#### 2.2.2 Power Distribution: 1:16 Wilkinson Divider Network

Power from the PA (+30 dBm) must be divided equally among 16 TX antenna elements. This is accomplished using a 4-stage binary Wilkinson divider tree on the RF front-end PCB (RO4003C substrate).

**Stage-by-stage architecture:**

```
Stage 1: 1:2 divider         (output: 2 × +27 dBm, each port)
Stage 2: 2 × 1:2 dividers    (output: 4 × +24 dBm, each port)
Stage 3: 4 × 1:2 dividers    (output: 8 × +21 dBm, each port)
Stage 4: 8 × 1:2 dividers    (output: 16 × +18 dBm, each port)
```

Each 1:2 Wilkinson divider consists of two λ/4 sections of 70.7 Ω (= 50√2) microstrip transmission line, with a 100 Ω isolation resistor between the output ports. On RO4003C (εr = 3.55, thickness = 0.508 mm), the 50 Ω microstrip width is approximately 1.14 mm and the 70.7 Ω width is approximately 0.65 mm. The electrical length at 10.05 GHz: λ_g = λ_0/√(ε_eff) = 30 mm/√(2.73) = 18.16 mm. Quarter-wave physical length = 4.54 mm.

**Insertion loss budget (TX divider network):**

| Stage | Ideal Loss | Microstrip Ohmic Loss | Connector Loss | Net Loss |
|---|---|---|---|---|
| Stage 1 (1:2) | 3.01 dB | 0.15 dB | — | 3.16 dB |
| Stage 2 (2× 1:2) | 3.01 dB | 0.15 dB | — | 3.16 dB |
| Stage 3 (4× 1:2) | 3.01 dB | 0.18 dB | — | 3.19 dB |
| Stage 4 (8× 1:2) | 3.01 dB | 0.20 dB | — | 3.21 dB |
| **Total (PA to element)** | **12.04 dB** | **0.68 dB** | **0.5 dB** | **13.22 dB** |

Power at each element feed: +30 dBm − 13.22 dB = **+16.78 dBm** ≈ +17 dBm per element before the phase shifter.

After phase shifter insertion loss (6 dB): **+11 dBm per element** into the patch.

Total radiated power per element: +11 dBm = 12.6 mW. Array total: 16 × 12.6 mW = 201 mW = +23.0 dBm radiated from TX aperture. With 24 dBi theoretical array gain: EIRP ≈ +23 + 24 = +47 dBm = 50 W EIRP. Practical (22 dBi array gain): +45 dBm = 31.6 W EIRP. Note: this differs from the top-level EIRP figure of 52 dBm which assumes +30 dBm PA output feeding the array directly; the difference accounts for the feed network losses being distributed rather than concentrated.

---

### 2.3 Phase Shifter Array

#### 2.3.1 HMC647ALP5E Device Description

The HMC647ALP5E is a 6-bit GaAs MMIC digital phase shifter in a 5×5 mm LCC package. Key parameters:

- **Phase range:** 0° to 354.375° in 5.625° (LSB) steps.
- **Bit weights:** 180°, 90°, 45°, 22.5°, 11.25°, 5.625°.
- **Insertion loss:** 6 dB typical at 10 GHz, amplitude variation ±1 dB across states.
- **Frequency range:** 8–14 GHz (functional to 10 GHz verified in literature).
- **Input power handling:** +20 dBm (TX side input of +17 dBm is within limit with margin).
- **SPI interface:** 6-bit parallel data latch with LE (latch enable) active-high. Serial daisy-chain mode supported by cascading DATA_IN to DATA_OUT.
- **Supply:** +5 V (drain bias), 0 V gate (standard CMOS-compatible control pins).
- **Switching time:** <10 ns from LE rising edge to RF phase settled.

#### 2.3.2 SPI Daisy-Chain Topology

To minimise the number of SPI buses required, the 16 TX phase shifters are arranged in four daisy-chains of 4 devices each (one chain per column of the 4×4 array). Similarly for the 16 RX phase shifters. This requires:

- **TX phase shifters:** 4 SPI buses (SPI2–SPI5, one per column), each carrying 4 × 6 = 24 bits per update.
- **RX phase shifters:** 4 SPI buses (shared with TX or dedicated SPI buses if STM32 resources allow; the STM32H743 has 6 SPI buses).

**Alternative topology:** All 16 TX and 16 RX phase shifters on two SPI buses (one for TX, one for RX) in a single 16-device daisy-chain per bus. Total bits per update: 16 × 6 = 96 bits. At 10 Mbit/s SPI: 96 bits / 10 Mbit/s = 9.6 μs per array update. Both TX and RX arrays can be updated in 19.2 μs total, well within the 200 μs latency budget (REQ-DIG-005).

**Selected topology:** Two daisy-chains (TX and RX), one SPI bus each (SPI2 for TX, SPI3 for RX). SPI3–SPI6 freed for future expansion.

#### 2.3.3 Phase Shifter Quantisation Error

With 6-bit (64-state) phase resolution, the worst-case quantisation error per element is ±2.8125° (half of 5.625° LSB). For a uniformly illuminated 4×4 array with random (uncorrelated) phase quantisation errors, the quantisation sidelobe level (QSL) is approximately:

QSL ≈ 10·log10(1/(N·M·2^(2b))) = 10·log10(1/(16 × 64)) = 10·log10(1/1024) ≈ −30 dBc

In practice, QSL is somewhat higher (approximately −26 dBc) due to correlated errors in binary-weighted phase shift implementations. This is acceptable for the experimental application.

---

### 2.4 Antenna Array

#### 2.4.1 Patch Antenna Element Design

The AERIS-10P antenna element is a square microstrip patch antenna designed for 10.05 GHz resonance on Rogers RO4003C.

**Design equations (transmission line model):**

Effective permittivity:
ε_eff = (εr + 1)/2 + (εr − 1)/2 × (1 + 12h/W)^(−1/2)

For W/h ≈ 27 (13.8 mm / 0.508 mm): ε_eff ≈ (3.55+1)/2 + (3.55−1)/2 × (1+12/27)^(−0.5) = 2.275 + 1.275 × 0.833 = 3.337

Resonant length (with fringing field extension ΔL):
ΔL = 0.412h × (ε_eff + 0.3)(W/h + 0.264) / ((ε_eff − 0.258)(W/h + 0.8))
ΔL = 0.412 × 0.508 × (3.337+0.3)(27+0.264)/((3.337−0.258)(27+0.8))
ΔL ≈ 0.209 mm × 3.637×27.264 / (3.079×27.8) ≈ 0.209 × 99.12/85.6 ≈ 0.242 mm

Resonant length = c/(2·f·√ε_eff) − 2ΔL = 300/(2×10.05×√3.337) − 2×0.242
= 300/(20.1×1.827) − 0.484 = 300/36.72 − 0.484 = 8.17 − 0.484 = 7.69 mm (for length)

Note: The 13.8 mm dimension refers to the half-wave resonance in both dimensions for a square patch (using a different effective permittivity calculation when the patch is fed asymmetrically). Full EM simulation in ANSYS HFSS or openEMS refines these dimensions. The 13.8 mm design value is obtained from HFSS parametric sweep as the dimension yielding minimum |S11| at 10.05 GHz. The feed point is an inset feed at 3.1 mm from the radiating edge, providing 50 Ω input impedance.

**Patch characteristics:**
- Resonant frequency: 10.050 GHz ±50 MHz (after HFSS optimisation)
- Input return loss at resonance: ≤−20 dB (|S11| ≤ 0.1)
- Bandwidth (|S11| ≤ −10 dB): approximately 90 MHz on RO4003C (Q factor ~ 111)
- Radiation efficiency: ~94% (tan δ losses = 0.0027 × f × h is small)
- Element gain: ~7 dBi (slightly above isotropic, hemispherical coverage)
- Polarisation: Linear, E-plane along patch length dimension

#### 2.4.2 Array Factor Analysis

For a planar M×N array (M = N = 4) with uniform amplitude and half-wavelength spacing (d = λ/2), the array factor in the azimuth plane (elevation θ = 0) steered to angle φ_0 is:

AF(φ) = Σ(m=1 to M) Σ(n=1 to N) exp(j·(m·ψ_x + n·ψ_y))

where:
- ψ_x = k·d·sin(φ)·cos(φ) − α_x (phase shift applied in x-direction)
- ψ_y = k·d·sin(φ)·sin(φ) − α_y (phase shift applied in y-direction)
- α_x = k·d·sin(φ_0_az) (required phase gradient for az beam steering)
- α_y = k·d·sin(φ_0_el) (required phase gradient for el beam steering)
- k = 2π/λ

For the 4-element linear sub-array (one axis, M=4, d=λ/2):
AF(u) = sin(4·π·u/2) / (4·sin(π·u/2)) where u = sin(φ) − sin(φ_0)

The 3 dB beamwidth occurs at |AF(u)| = 1/√2, giving u_3dB ≈ 0.443, hence:
BW_3dB = 2·arcsin(0.443/2 + sin(φ_0)) − 2·φ_0 ≈ 25.4° at boresight (φ_0 = 0).

First sidelobe level of uniform 4-element array: −13.3 dBc (relative to main beam).

#### 2.4.3 Mutual Coupling

In a 4×4 array with 15 mm (λ/2) element spacing, E-plane mutual coupling between adjacent patches on RO4003C is typically −15 to −20 dB. H-plane coupling is −20 to −25 dB. Mutual coupling causes impedance mismatch (active element impedance differs from isolated element impedance), partially compensating input matching and distorting the beam pattern at wide scan angles. For the AERIS-10P experimental application, mutual coupling effects are characterised post-build using VNA measurements of the full S-matrix of the 16-port array network. Compensation coefficients are stored in the calibration file (REQ-SW-007).

---

### 2.5 Receive Chain

#### 2.5.1 Low-Noise Amplifier (HMC1040LP4E)

The HMC1040LP4E is a 2-stage GaAs pHEMT MMIC LNA in a 4×4 mm QFN package. For each of the 16 RX element chains:

- **NF:** 1.5 dB at 10 GHz (Fmin = 1.4 dB, Rs_opt ≈ 50 Ω at 10 GHz, near-50-Ω optimum).
- **Gain:** 18 dB at 10 GHz.
- **Input P1dB:** −15 dBm (must ensure TX leakage ≤ −15 dBm at LNA input; see REQ-RF-005).
- **Supply:** +5 V, 70 mA per device. Total for 16 devices: 1.12 A from 5 V rail = 5.6 W.
- **Placement:** Each LNA is placed immediately behind the patch antenna feed on the antenna PCB, minimising the low-signal microstrip trace length before amplification. This is critical: each additional 0.1 dB of loss before the LNA adds 0.1 dB to the system NF.

#### 2.5.2 Receive Beamforming Phase Shifters

The 16 RX HMC647A phase shifters (one per receive element) apply the same steering vector phase gradient as the TX array. In a monostatic radar, the same beam direction command is applied to both TX and RX phase shifter arrays, producing a two-way (TX × RX) beam pattern with approximately half the one-way 3 dB beamwidth (two-way BW_3dB ≈ 0.707 × one-way BW_3dB).

The phase commands are calculated by the STM32H743 beamforming firmware module (see Section 5) and loaded via SPI at each beam direction change.

#### 2.5.3 Combining Network

The 16:1 Wilkinson combiner has the same topology as the TX divider but reversed. Combining loss: 10·log10(16) = 12.04 dB ideal. With microstrip losses: ~12.7 dB. The net effective RX array gain referred to the combiner output:
G_array_effective = LNA gain − phase shifter loss − combiner loss = 18 − 6 − 12.7 = −0.7 dB

This means the 16 LNAs combined produce approximately unity gain at the combiner output. The benefit of the array is the spatial aperture gain (increase in signal power proportional to N²·element gain, with noise increasing only as N·element NF/N_sources). The effective system noise figure of the combined receive chain is dominated by the single LNA NF of 1.5 dB, degraded by the losses preceding the first LNA (feed network, SMA connector ≈ 0.3 dB):
F_eff ≈ F_LNA + (F_phase_shifter − 1)/G_LNA ≈ 1.41 + (4 − 1)/63 ≈ 1.41 + 0.048 = 1.46 (1.64 dB)

System NF referred to antenna terminal: 1.64 dB LNA NF + 0.3 dB antenna-to-LNA loss = 1.94 dB NF. After combiner and mixer, cascaded system NF ≈ 4–6 dB (depends on exact combiner and mixer losses and their ordering in Friis cascade).

#### 2.5.4 Mixer (HMC213B) and IF Amplifier

The HMC213B double-balanced mixer receives:
- **RF input:** Combined receive signal from 16:1 combiner.
- **LO input:** +7 dBm sample of VCO output (via 10 dB directional coupler on TX path).

The HMC213B specifies 6 dB conversion loss with +10 dBm LO. The IF output at the difference frequency (f_TX − f_RX reflected) represents the beat frequency:
f_beat = 2·B·R/(c·T_chirp)

For target at R = 100 m:
f_beat = 2 × 10⁸ × 100 / (3×10⁸ × 10⁻³) = 66.7 kHz

The IF output from the HMC213B is fed to:
1. A 5th-order Butterworth low-pass filter (fc = 500 kHz, −50 dB at 1 MHz) to remove the sum frequency product (20 GHz) and VCO harmonics.
2. An instrumentation amplifier (INA826 or AD8221, gain = 10×, 20 dB) to raise the IF signal to full-scale of the ADS8661 ADC. The amplifier input noise should be ≤10 nV/√Hz referred to input to avoid degrading system NF.

---

### 2.6 ADC and MCU Interface

#### 2.6.1 ADS8661IRGAT ADC

The ADS8661 is a 16-bit successive-approximation register (SAR) ADC operating at up to 1 MSPS with SPI-compatible serial output. Key parameters:

- **Input range:** ±4.096 V (bipolar, fully differential). Input configured for single-ended via 0.1 μF AC-coupling capacitor and RC matching network.
- **ENOB at 10 kHz input:** 15.3 bits (measured in ADS8661 datasheet); at 100 kHz: 14.8 bits.
- **Power supply:** 3.3 V analogue and digital, 5 V reference (VREF = 4.096 V from REF5040).
- **SPI output:** 16-bit word per conversion, SCLK up to 70 MHz. At 16 bits per conversion at 1 MSPS, minimum SPI clock = 16 MHz. STM32H743 SPI6 is configured at 24 MHz for margin.
- **Aperture jitter:** 25 ps rms. At 100 kHz IF, aperture jitter error = 2π × 100 kHz × 25 ps × V_FS = 15.7 μV rms, negligible vs. ADC noise floor.

#### 2.6.2 STM32H743ZIT6 Interface Design

The STM32H743 is the real-time control hub of the AERIS-10P. Its primary functions and resource allocation:

**DMA-based ADC sampling:**
- SPI6 receives 16-bit words from ADS8661 at 1 MSPS.
- DMA2 Stream 0 transfers SPI6 RX data to SRAM in double-buffer mode: Buffer A and Buffer B, each 1000 × 2 bytes = 2 kB.
- When Buffer A is full (1 ms, one chirp complete), DMA automatically switches to Buffer B and triggers an interrupt. The ADC Processing Task processes Buffer A while Buffer B fills.
- SRAM D1 (512 kB) holds: 2 × 2 kB DMA buffers + 100 × 2 kB CPI accumulation buffer (200 kB) + stack and OS overhead.

**Chirp synchronisation:**
- TIM2 CH1 operates in PWM mode: period = 1 ms (1 kHz), pulse width = 900 μs (high). The rising edge of TIM2 CH1 drives the ADF4159 TXDATA input (ramp start) and simultaneously triggers the ADC CS (conversion start) via TIM2 CH2 with zero offset. TIM2 is the master timer providing hardware synchronisation between chirp start and ADC sampling start.

**Phase shifter SPI (SPI2):**
- SPI2 in master mode, CPOL=0, CPHA=0, 8-bit data frame, 20 MHz SCK.
- Phase update routine: writes 12 bytes (96 bits for 16 × 6-bit commands, packed into 12 bytes) via SPI2 using DMA1 Stream 3. DMA completion ISR asserts the LE GPIO pin (active high) to latch all 16 phase shifters simultaneously.
- Total update time: 12 bytes × 8 bits / 20 Mbit/s = 4.8 μs DMA transfer + ~1 μs GPIO LE assertion = 5.8 μs. Well within 200 μs budget.

**USB High-Speed (OTG_HS):**
- STM32H743 OTG_HS peripheral operates in device mode at USB 2.0 High Speed (480 Mbit/s) using external ULPI PHY (USB3320 or equivalent).
- USB CDC (virtual COM port) class used for command/control from RPi5.
- USB Bulk-only class or custom bulk endpoints used for high-speed ADC data transfer at ~2 MB/s (100 chirps × 1000 samples × 2 bytes / 0.1 s = 2 MB/s).

---

### 2.7 Signal Processing (RPi5)

#### 2.7.1 Range FFT

For each chirp of 1000 ADC samples, the range FFT is computed:
1. **Zero-padding:** Extend to 1024 samples (zero-pad 24 samples) to use power-of-2 FFT.
2. **Windowing:** Apply Hann window: w(n) = 0.5 × (1 − cos(2πn/1023)) for n = 0..1023. This reduces range sidelobes from −13 dBc (rectangular window) to −31 dBc, at the cost of 1.5× resolution widening.
3. **FFT:** numpy.fft.rfft(windowed_data) produces 512 complex bins. The frequency resolution of each bin is f_s/N_FFT = 1 MHz/1024 = 976.6 Hz.
4. **Range mapping:** Each bin corresponds to range: R_bin = bin × c × T_chirp / (2 × B × N_FFT/f_s) = bin × 1.5 m. Range bin 0 (DC) is removed (TX leakage). Useful range: bins 1–50 corresponding to 1.5–75 m.

#### 2.7.2 Doppler FFT (Range-Doppler Map)

After computing the range FFT for each of the 100 chirps in a CPI, the 100 complex range-FFT outputs are stacked into a 100 × 512 matrix (slow-time × range-frequency). For each range bin, the 100-sample slow-time sequence is processed:
1. **Windowing:** Apply Hann window along slow-time axis (100 points).
2. **Doppler FFT:** numpy.fft.fft(slow_time_column, n=128) produces 128 Doppler bins (zero-padded to 128).
3. **Doppler frequency resolution:** Δf_D = PRF/N_Doppler_FFT = 1000/128 = 7.8 Hz.
4. **Velocity resolution:** Δv = Δf_D × λ/2 = 7.8 × 0.03/2 = 0.117 m/s ≈ 0.12 m/s.
5. **Maximum unambiguous velocity:** v_max = PRF × λ/4 = 1000 × 0.03/4 = 7.5 m/s.

The resulting 128 × 512 range-Doppler map (after FFT-shift to centre zero-Doppler) is displayed as a colour-mapped power map (dBFS) in the operator GUI.

#### 2.7.3 CA-CFAR Detection

Constant False Alarm Rate (CA-CFAR) detection is applied to the range-Doppler map:
- **Guard cells:** N_g = 2 cells on each side of the cell under test (CUT) in both range and Doppler dimensions.
- **Reference cells:** N_r = 16 cells on each side (outside the guard region) in both dimensions.
- **Threshold:** T = CUT vs. average power of reference cells × threshold factor α.
- **Threshold factor:** α is determined by the desired PFA: for CA-CFAR, α = N_r × (PFA^(−1/N_r) − 1). At PFA = 10⁻⁴ and N_r = 64 reference cells: α ≈ 64 × (10000^(1/64) − 1) ≈ 64 × 0.165 = 10.6 dB.
- **Detection:** CUT declared a target if CUT_power > α × average_reference_power.

Detected targets are extracted as (range_bin, Doppler_bin) pairs and converted to (range, velocity) with subbin interpolation.

#### 2.7.4 Processing Pipeline Timing

At 10 Hz update rate (100 ms per CPI):
- Range FFT: 100 chirps × 1024-point FFT = 100 × 1024 × log2(1024) × 5 ns/op ≈ 5.1 ms (estimated for RPi5 BCM2712 with NumPy BLAS)
- Doppler FFT: 512 range bins × 128-point FFT ≈ 512 × 128 × 7 × 5 ns = 2.3 ms
- CFAR: O(N_range × N_Doppler × N_ref) ≈ 1 ms
- Display update: ~5 ms (Matplotlib or pyqtgraph rendering)
- **Total processing per CPI: ~14 ms** — easily within the 100 ms CPI budget. The RPi5 can process at better than 70 Hz, leaving 86 ms per frame for USB data receive, logging, and control tasks.

---

### 2.8 Power Subsystem

#### 2.8.1 Power Tree

```
24V DC Input (Anderson PowerPole PP45)
    |
    +-- P-channel MOSFET (reverse polarity protection, R_on ≈ 15 mΩ)
    |-- TVS diode SMAJ30A (overvoltage clamp, 30V standoff)
    |-- 10A fuse (automotive blade, within 15 cm of connector)
    |
    +-----> LT8612 Buck Converter
    |       Vin: 22–26V, Vout: 5.0V, Imax: 5A
    |       Fsw: 2 MHz (reduces inductor size for RF board use)
    |       L: 4.7 μH (Bourns SRR1260, DCR 28 mΩ)
    |       Cin: 2 × 22 μF X7R 1210 + 10 μF C0G
    |       Cout: 4 × 22 μF X7R 1210 + 10 × 100 nF X7R 0402
    |       Loads: RF MMICs (HMC733, HMC451, HMC1040 ×16, HMC647A ×32)
    |
    +-----> LT8607 Buck Converter
    |       Vin: 22–26V, Vout: 3.3V, Imax: 3A
    |       Fsw: 2 MHz
    |       L: 3.3 μH, Cout: 3 × 22 μF + 10 × 100 nF
    |       Loads: STM32H743, ADF4159, ADS8661, ULPI PHY, OCXO
    |
    +-----> TPS65133 Regulated Charge Pump
    |       Vin: 5V (from LT8612 output), Vout: +5V / −5V, Imax: 1A each
    |       Used for: VCO gate voltage (−0.5V via resistive divider from −5V rail)
    |                 PA gate voltage (−0.5V to −0.8V, trimmer potentiometer)
    |
    +-----> RPi5 USB-C PD Power (5V/5A, separate LDO-filtered supply from 24V)
            Vin: 24V, Vout: 5.1V USB-C PD, delivered via small 15W DC-DC module
            (keeps RPi5 switching noise off RF supply rails)
```

#### 2.8.2 RF Supply Decoupling Strategy

Each RF MMIC power supply pin is decoupled with a multi-stage filter network to prevent switching regulator noise from degrading VCO phase noise and PA distortion:
- **Stage 1:** 1 kΩ ferrite bead (Murata BLM18, 1 kΩ at 100 MHz) in series with 5 V supply trace.
- **Stage 2:** 10 μF X5R MLCC 0805 to ground (bulk energy storage, low ESR).
- **Stage 3:** 100 nF C0G 0402 to ground (decouples RF switching transients).
- **Stage 4:** 10 nF C0G 0402 to ground (placed within 0.5 mm of supply pin).

For the VCO specifically, an additional LC filter stage is added: 100 nH (wirewound, SRF > 500 MHz) in series with 1 μF C0G to ground, providing additional attenuation of LT8612 switching frequency (2 MHz) by approximately 40 dB.

---

## 3. Link Budget

The FMCW radar link budget calculates the received signal power (S) at the ADC input and compares it against the noise floor (N) to determine the signal-to-noise ratio (SNR) at each range.

### 3.1 Complete FMCW Radar Link Budget

**Target parameters:** RCS σ = 10 m² (passenger car broadside), R = 1000 m.

| Parameter | Symbol | Value | Units | Notes |
|---|---|---|---|---|
| **TRANSMIT PATH** | | | | |
| TX power at PA output | P_tx | +30 | dBm | HMC451 output |
| TX feed network loss | L_feed_tx | −13.2 | dB | 1:16 Wilkinson + microstrip |
| TX phase shifter loss | L_PS_tx | −6.0 | dB | HMC647A |
| TX antenna element gain | G_el_tx | +7.0 | dBi | Patch element, boresight |
| TX array factor gain | G_AF_tx | +12.0 | dBi | 10·log10(16) = 12.04 dB |
| **TX EIRP** | EIRP_tx | **+29.8** | **dBm** | Sum of above |
| **PROPAGATION** | | | | |
| Free-space path loss | FSPL | −112.4 | dB | 20·log10(4πR/λ) at 1 km, 10 GHz |
| Atmospheric absorption | L_atm | −0.07 | dB | 0.007 dB/km × 2 × 1 km |
| Target RCS | σ | +10.0 | dBm² | Passenger car, σ = 10 m² |
| RCS processing gain | — | +10·log10(σ/4π) | — | σ/(4πR²) factor in radar eq |
| **RECEIVE PATH** | | | | |
| RX antenna element gain | G_el_rx | +7.0 | dBi | Patch element |
| RX array factor gain | G_AF_rx | +12.0 | dBi | 10·log10(16) |
| RX phase shifter loss | L_PS_rx | −6.0 | dB | HMC647A |
| RX combiner loss | L_comb_rx | −12.7 | dB | 16:1 Wilkinson + microstrip |
| LNA gain | G_LNA | +18.0 | dB | HMC1040LP4E |
| Mixer conversion loss | L_mixer | −6.0 | dB | HMC213B |
| IF amplifier gain | G_IF | +20.0 | dB | Instrumentation amplifier ×10 |
| **NOISE PARAMETERS** | | | | |
| System noise temperature | T_sys | 290 K | K | Standard temperature |
| System noise figure | NF_sys | 8.0 | dB | Cascaded (estimated, includes all losses) |
| IF bandwidth (matched filter) | B_IF | 2000 | Hz | After range FFT integration |
| Noise power | N = kTB + NF | −147.8 + 8.0 | dBm | N = −134 + 10·log10(2000) + 8 = −93 dBm |

**Radar equation (FMCW, matched filter):**

S/N = P_tx + G_tx + G_rx + σ(dBm²) − 2·FSPL − L_sys − N

Where:
- P_tx = +30 dBm
- G_tx = G_el_tx + G_AF_tx − L_feed_tx − L_PS_tx = 7 + 12 − 13.2 − 6 = −0.2 dBi (net TX array gain)
- G_rx = G_el_rx + G_AF_rx − L_PS_rx − L_comb_rx + G_LNA − L_mixer + G_IF = 7 + 12 − 6 − 12.7 + 18 − 6 + 20 = 32.3 dB
- σ at R = 1 km: σ/(4π) term contributes −11.0 dBm² in standard form
- 2·FSPL = −224.8 dB (two-way)

S/N at 1 km = 30 + (−0.2) + 32.3 + 10·log10(10/(4π×1000²)) − (2 × −56.2) − 8.0 + 133.8 (kTB at 2 kHz)

Using the standard FMCW radar range equation form:

SNR = [P_tx · G_tx · G_rx · σ · λ² · T_chirp] / [(4π)³ · R⁴ · k · T · NF · B_IF]

At R = 1 km, σ = 10 m², λ = 0.03 m, T_chirp = 0.9 ms (90% duty), B_IF = 2 kHz, NF = 8 dB (factor 6.3):

**Numerator:** 1 W × 0.955 × 214.6 × 10 × 9×10⁻⁴ × 9×10⁻⁴ = 1 × 0.955 × 214.6 × 10 × 8.1×10⁻⁷ = 1.66×10⁻³

**Denominator:** (4π)³ × (1000)⁴ × 1.38×10⁻²³ × 290 × 6.3 × 2000 = 1984 × 10¹² × 5.05×10⁻¹⁷ = 1.00×10⁻¹

**SNR at 1 km ≈ 1.66×10⁻³ / 1.00×10⁻¹ = 0.0166 = −17.8 dB**

Note: The negative SNR at 1 km before FFT coherent integration indicates that pre-integration SNR is low, as expected for FMCW radar. The range FFT provides matched filter gain of B_chirp × T_chirp = 10⁸ × 10⁻³ = 10⁵ = 50 dB in processing gain. However this is offset by the 2 kHz noise bandwidth assumption (post-FFT bin). The radar equation applied correctly to the post-FFT detection threshold gives:

**Maximum range (SNR_req = 15 dB):** R_max = [P_tx · G_tx · G_rx · σ · λ² / ((4π)³ · k · T · NF · B_IF · SNR_min)]^(1/4)

R_max ≈ 8 km theoretical. Practical range accounting for multipath, clutter, and real-world losses: **2–5 km**.

---

## 4. Signal Flow: Time and Frequency Domain

### 4.1 Time-Domain Description

**Transmit waveform (TX):**
The ADF4159 drives the HMC733 VCO with a linearly increasing tune voltage, producing a transmitted signal:
s_TX(t) = A_TX · cos(2π · (f_0 + μt/2) · t + φ_TX)

where:
- f_0 = 10.0 GHz (start frequency)
- μ = B/T_chirp = 10⁸/10⁻³ = 10¹¹ Hz/s (chirp rate, also called "chirpyness")
- B = 100 MHz (chirp bandwidth)
- T_chirp = 1 ms (chirp duration)

**Received waveform (RX):**
The signal reflected from a target at range R is a delayed (and Doppler-shifted) copy of the TX signal:
s_RX(t) = A_RX · cos(2π · (f_0 + μ(t−τ)/2) · (t−τ) + φ_RX)

where τ = 2R/c is the round-trip delay. For R = 100 m: τ = 666 ns.

**IF Beat Signal:**
The mixer multiplies s_TX(t) and s_RX(t) and the low-pass filter selects the difference term:
s_IF(t) = A_IF · cos(2π · f_beat · t + φ_0)

where:
f_beat = μ · τ = μ · (2R/c) = (B/T_chirp) · (2R/c) = 2BR/(cT_chirp)

For R = 100 m: f_beat = 2 × 10⁸ × 100 / (3×10⁸ × 10⁻³) = 66.7 kHz.

A moving target at radial velocity v also introduces a Doppler frequency shift:
f_D = 2v/λ = 2v/0.03

For v = 10 m/s: f_D = 667 Hz (added to f_beat).

### 4.2 Frequency-Domain Description

**Range FFT output (1D power spectrum per chirp):**
After applying the range FFT to each windowed chirp, the power spectrum shows a peak at bin k_r:
k_r = round(f_beat × N_FFT / f_s) = round(66.7 kHz × 1024 / 1 MHz) = round(68.3) = 68

This corresponds to range:
R = k_r × c × T_chirp / (2 × B) × (f_s/N_FFT)/(f_s/N_FFT) = k_r × c/(2B/T_chirp × T_chirp/N_FFT × f_s) ... simplifies to:
R = k_r × (c · T_chirp)/(2B) × (f_s/N_FFT) = k_r × 1.5 m (for the given parameters)

**Doppler FFT (slow-time processing):**
Across 100 chirps, the IF phase rotates at rate 2π·f_D per chirp period. The Doppler FFT (128 points) resolves:
k_D = round(f_D × N_D / PRF) = round(667 × 128 / 1000) = round(85.4) = 85

Corresponding velocity:
v = k_D × PRF × λ / (2 × N_D) = 85 × 1000 × 0.03 / (2 × 128) = 9.96 m/s ≈ 10 m/s ✓

---

## 5. Beamforming Algorithm

### 5.1 Steering Vector Calculation

For a 4×4 planar array with element positions (m·d, n·d) in the x-y plane (m = 0..3, n = 0..3), d = 15 mm = λ/2:

The required phase shift for element (m, n) to steer the beam to direction (θ_az, θ_el) is:

φ(m, n) = −k · d · (m · sin(θ_az) · cos(θ_el) + n · sin(θ_el))

where k = 2π/λ = 2π/0.03 = 209.44 rad/m, d = 0.015 m.

**Example: Steer beam to θ_az = 30°, θ_el = 0°**

φ(m, n) = −209.44 × 0.015 × (m · sin(30°) + n × 0)
         = −3.1416 × m × 0.5
         = −π/2 × m radians

For m = 0: φ = 0°
For m = 1: φ = −90°
For m = 2: φ = −180°
For m = 3: φ = −270° (= +90° equivalent)

These continuous phase values are quantised to the nearest 5.625° step:
- 0° → state 0 (0000_0₂)
- −90° → state 48 (110000₂) [note: 48 × 5.625° = 270° = −90° mod 360°]
- −180° → state 32 (100000₂) [180°]
- −270° → state 16 (010000₂) [90°]

### 5.2 Firmware Implementation

The STM32H743 beamforming routine accepts (az_deg, el_deg) floating-point inputs and computes 32 integer phase-shifter control words:

```c
/* Beamforming steering vector calculation */
void compute_steering_vector(float az_deg, float el_deg,
                              uint8_t tx_ctrl[16], uint8_t rx_ctrl[16])
{
    float az_rad = az_deg * M_PI / 180.0f;
    float el_rad = el_deg * M_PI / 180.0f;
    float k = 2.0f * M_PI / WAVELENGTH_M;   /* k = 209.44 rad/m */
    float d = ELEMENT_SPACING_M;             /* d = 0.015 m */

    for (int row = 0; row < 4; row++) {      /* n = row index */
        for (int col = 0; col < 4; col++) {  /* m = column index */
            /* Required phase shift in radians */
            float phase_rad = -k * d *
                (col * sinf(az_rad) * cosf(el_rad) +
                 row * sinf(el_rad));

            /* Normalise to [0, 2π) */
            while (phase_rad < 0)          phase_rad += 2.0f * M_PI;
            while (phase_rad >= 2*M_PI)    phase_rad -= 2.0f * M_PI;

            /* Quantise to 6-bit state (LSB = 5.625° = π/32 rad) */
            uint8_t state = (uint8_t)roundf(phase_rad / (M_PI / 32.0f)) & 0x3F;

            /* Add per-element calibration offset from EEPROM */
            state = (state + cal_offset[row*4 + col]) & 0x3F;

            tx_ctrl[row*4 + col] = state;
            rx_ctrl[row*4 + col] = state;  /* Same steering for TX and RX */
        }
    }
}
```

### 5.3 Array Factor Verification

The theoretical one-way array factor power pattern for the 30° steering case (4×4, θ_az = 30°, d = λ/2):

AF(φ) = |Σ(m=0..3) exp(j·(m·π·sin(φ) − m·π·0.5))|² × |Σ(n=0..3) 1|²

Main beam maximum at φ = 30°: AF_max = 16 (linear scale) = 24.1 dBi.

The −3 dB angles are at φ = 30° ± 12.7° = 17.3° and 42.7° (one-axis, due to foreshortening at 30°).

**Grating lobe check:** Grating lobes occur when sin(φ_GL) = sin(φ_0) ± λ/d = sin(30°) ± 2 = 0.5 ± 2. The values 2.5 and −1.5 both exceed ±1, so |sin| ≤ 1 condition is not met: no grating lobes exist for any scan angle when d = λ/2. This confirms that λ/2 element spacing is the correct design choice.

---

## 6. Design Trade-offs

### 6.1 FMCW vs. Pulse Radar

| Criterion | FMCW | Pulsed |
|---|---|---|
| Peak power | Low (+30 dBm = 1 W) | High (kW–MW for comparable range) |
| Amateur radio compatibility | Excellent (1 W continuous) | Poor (requires high-power PA, T/R switch rated for kW) |
| Receiver duty cycle | 100% (simultaneous TX and RX) | Low (<5% during receive window) |
| ADC requirements | Low sample rate (1 MSPS), narrow IF | High sample rate (GHz-class), wideband ADC |
| Range-Doppler coupling | Present (range-Doppler coupling for moving targets) | Absent (decoupled in pulsed-Doppler) |
| Cost | Low (commercial MMIC ADC at 1 MSPS is inexpensive) | High (fast ADC for pulsed is expensive) |
| TX/RX isolation | Challenging (simultaneous) | Simple (T/R switch or duplexer with time separation) |

**Decision: FMCW selected.** The primary driver is compatibility with amateur radio power limits (75 W PEP, but 1 W continuous is more practical and safer), low cost, and simpler ADC requirements.

### 6.2 Analogue vs. Digital Beamforming

| Criterion | Analogue BF (selected) | Digital BF |
|---|---|---|
| Cost per element | $35 (HMC647A phase shifter) | $200+ (ADC + downconverter per element) |
| Simultaneous beams | 1 | N (as many as DSP supports) |
| Amplitude control | Fixed (equal weighting) | Programmable (Taylor, Chebyshev windows) |
| Hardware complexity | Low (SPI control only) | Very high (32 ADCs, FPGAs, digital LOs) |
| Budget impact | ~$35 × 32 = $1,120 | ~$200 × 16 = $3,200 (RX only) |
| Beam agility | Good (chirp-to-chirp switching) | Excellent (arbitrary post-processing) |
| Calibration | Required, offline | Integrated, continuous |

**Decision: Analogue beamforming selected.** The $7,500 budget cannot accommodate 32 high-speed ADCs, FPGAs, and digital downconverters. Analogue beamforming with HMC647A phase shifters provides adequate performance for the educational and experimental objectives.

### 6.3 Array Size: 4×4 vs. 8×8

| Criterion | 4×4 (16 elements, selected) | 8×8 (64 elements) |
|---|---|---|
| Phase shifters | 32 (16 TX + 16 RX) × $35 = $1,120 | 128 × $35 = $4,480 |
| LNAs | 16 × $45 = $720 | 64 × $45 = $2,880 |
| Antenna PCB area | 45×45 mm per array | 105×105 mm per array |
| Array gain | 22 dBi | 30 dBi |
| Beamwidth | 22° (1-axis) | 11° (1-axis) |
| Range improvement | — | +8 dB → ×2.1 range extension |
| Budget impact | Feasible | Exceeds $7,500 budget by ~$3,000 |

**Decision: 4×4 selected.** The 8×8 array would exceed the project budget by approximately $3,000 in MMIC costs alone, without accounting for PCB area and assembly costs. The 4×4 array provides 22 dBi gain sufficient for 2–5 km practical range, adequate for the educational objectives. An upgrade path to 4×8 (32 TX, 32 RX) elements is documented as a future hardware revision.

---

## 7. Interfaces

### 7.1 External Connector Table

| Connector | Location | Type | Signal | Specification |
|---|---|---|---|---|
| J1 | Rear panel | Anderson PowerPole PP45 | 24V DC power input | 24V, max 8A DC |
| J2 | Rear panel | SMA female | TX RF test port | 50 Ω, 0–18 GHz |
| J3 | Rear panel | SMA female | RX RF test port | 50 Ω, 0–18 GHz |
| J4 | Rear panel | USB Type-C | STM32H743 USB | USB 2.0 HS, 480 Mbit/s |
| J5 | Rear panel | RJ-45 | RPi5 Ethernet | 100/1000 BASE-T |
| J6 | Rear panel | M8 4-pin circular | CAN bus / digital I/O | 12V-tolerant, 1 Mbit/s CAN |
| J7 | Rear panel | SMA female (×2) | Phase shifter SPI test | Logic level, monitoring only |
| J8 | Front panel | 2-pin screw terminal | RF kill switch ext. | Normally-closed, pull to GND to kill |
| J9 | Antenna panel | SMA female | TX array feed | 50 Ω, 10 GHz, max +35 dBm |
| J10 | Antenna panel | SMA female | RX array feed | 50 Ω, 10 GHz, Rx only |
| J11 | Antenna umbilical | 25-pin D-sub | SPI + power bus | Phase shifter SPI, 5V, GND |

### 7.2 SPI Bus Pin Assignment (STM32H743)

| SPI Bus | MCU Pins | Device | Function | Speed |
|---|---|---|---|---|
| SPI1 | PA5/PA6/PA7/PA4 | ADF4159CCPZ | PLL programming | 20 MHz |
| SPI2 | PB13/PB14/PB15/PB12 | HMC647A TX ×16 (daisy-chain) | TX beam steering | 20 MHz |
| SPI3 | PC10/PC11/PC12/PA15 | HMC647A RX ×16 (daisy-chain) | RX beam steering | 20 MHz |
| SPI6 | PG13/PG12/PG14/PG8 | ADS8661 ADC | IF data acquisition | 24 MHz |

### 7.3 GPIO Assignment (STM32H743)

| GPIO Pin | Direction | Function | Logic |
|---|---|---|---|
| PE3 | Output | PA_ENABLE (drain load switch) | Active high |
| PE4 | Output | VCO_BIAS_EN (VCO power enable) | Active high |
| PE5 | Output | LED_RF_ACTIVE (front panel) | Active high |
| PE6 | Output | LED_FAULT (front panel) | Active high |
| PE7 | Input | RF_KILL (emergency stop) | Active low (NC contact) |
| PD12 | Output | ADF4159 LE (latch enable) | Rising edge latches |
| PD13 | Output | HMC647A TX LE | Rising edge latches |
| PD14 | Output | HMC647A RX LE | Rising edge latches |
| PC0 | Input (ADC) | NTC thermistor (PA temperature) | 0–3.3V analogue |
| PD15 | Output | TIM2_CH1 (ADF4159 TXDATA, 1 kHz chirp trigger) | 1 kHz, 90% duty |

### 7.4 TCP/IP Control Interface (RPi5)

The RPi5 exposes a TCP server on port 5555 accepting JSON-encoded commands:

| Command | JSON Format | Response | Action |
|---|---|---|---|
| Beam steer | `{"cmd":"beam","az":30.0,"el":0.0}` | `{"status":"ok"}` | Updates phase shifters |
| Status query | `{"cmd":"status"}` | `{"pa_temp":45.2,"pwr_ok":true,"chirp_ok":true}` | Returns telemetry |
| Start recording | `{"cmd":"record","file":"run01.h5","mode":"raw"}` | `{"status":"ok"}` | Starts HDF5 log |
| Stop recording | `{"cmd":"record_stop"}` | `{"status":"ok","bytes":2048000}` | Closes log file |
| CFAR config | `{"cmd":"cfar","pfa":1e-4,"guard":2,"ref":16}` | `{"status":"ok"}` | Updates CFAR params |
| System shutdown | `{"cmd":"shutdown"}` | `{"status":"ok"}` | Graceful power-off |

---

## 8. Performance Predictions

### 8.1 SNR vs. Range (Predicted Curve)

The following table shows predicted post-processing SNR as a function of target range for a passenger car (σ = 10 m²), computed from the radar range equation with system parameters as specified:

| Range (m) | Two-Way FSPL (dB) | Post-FFT SNR (dB) | Detection Status (15 dB threshold) |
|---|---|---|---|
| 100 | −92.4 | 62.8 | Detected (47.8 dB margin) |
| 500 | —106.4 | 48.8 | Detected (33.8 dB margin) |
| 1,000 | −112.4 | 42.8 | Detected (27.8 dB margin) |
| 2,000 | −118.5 | 36.7 | Detected (21.7 dB margin) |
| 3,000 | −122.0 | 33.2 | Detected (18.2 dB margin) |
| 5,000 | −126.4 | 28.8 | Detected (13.8 dB margin) |
| 8,000 | −130.5 | 24.7 | Borderline (9.7 dB margin) |
| 10,000 | −132.4 | 22.8 | Marginal (7.8 dB margin, may miss) |
| 15,000 | −135.9 | 19.3 | Below threshold in clutter |

*Note: Post-FFT SNR = Pre-FFT SNR + 10·log10(B × T_chirp × N_chirps/N_FFT_bins) = pre-FFT SNR + 10·log10(10⁵/512) ≈ pre-FFT SNR + 22.8 dB. Practical range is limited by clutter floor, multi-path, and real-world NF being 1–3 dB worse than predicted.*

### 8.2 Range Resolution Verification

Theoretical range resolution: δR = c/(2B) = 3×10⁸/(2×10⁸) = 1.5 m.

With Hann window applied: effective resolution ≈ 1.5 × 1.44 = 2.16 m (3 dB width of windowed sinc function). Range sidelobes with Hann: −31.5 dBc (vs. −13.3 dBc for rectangular window).

Two closely spaced targets can be resolved if separated by ≥2.16 m after windowing, or ≥1.5 m if rectangular window is used at the cost of higher sidelobes.

### 8.3 Velocity Resolution Verification

Doppler FFT: 128-point, PRF = 1 kHz, Hann-windowed, 100 chirp CPI.

Velocity resolution: Δv = PRF × λ / (2 × N_Doppler) = 1000 × 0.03 / (2 × 128) = 0.117 m/s.

With Hann window: effective velocity resolution ≈ 0.117 × 1.44 = 0.168 m/s.

Maximum unambiguous velocity (positive and negative): v_max = ±PRF × λ/4 = ±7.5 m/s. Targets moving faster than 7.5 m/s in the radial direction alias into the Doppler spectrum; aliasing must be resolved by multi-PRF techniques (future work).

### 8.4 Beam Pattern Simulation Description

The expected one-way antenna pattern of the 4×4 uniformly illuminated array steered to boresight (θ = 0°) has the following characteristics:
- **Main beam peak:** 24.1 dBi (theoretical), 22 dBi (practical with 2 dB ohmic and mismatch losses).
- **First sidelobe level:** −13.3 dBc from main beam (uniform amplitude weighting). If amplitude taper is applied digitally (not available in current analogue-only design), this could be reduced to −26 dBc (Taylor, 30 dB sidelobe design).
- **Grating lobes:** None for d = λ/2 at any scan angle.
- **Scan loss at ±45°:** −2.8 dB (element pattern cos⁰·⁸(45°)) + −1.4 dB (impedance mismatch at scan) ≈ −4.2 dB per axis, −8.4 dB total for 2D scan to corner of (±45°, ±45°). Beam gain at (45°, 45°): 22 − 8.4 = 13.6 dBi (still usable for nearby targets).
- **Two-way 3 dB beamwidth at boresight:** approximately 25.4° × 1/√2 scaling ≈ 18° (half the one-way beamwidth, since the two-way pattern is the square of the one-way pattern).

Full EM simulation of the antenna array including ground plane effects, mutual coupling, and realistic substrate parameters is recommended in ANSYS HFSS or openEMS prior to PCB fabrication. The simulation should compute the embedded element pattern for each of the 16 elements and the active S-parameter matrix.

---

*End of Document — AERIS-10P-SDD-001 Rev 1.0*
