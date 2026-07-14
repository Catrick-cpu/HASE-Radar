# AERIS-10P Test and Measurement Procedures
## Rev 1.0 — AERIS-10P Affordable Experimental Radar Intelligence System, 10 GHz Phased Array

**Document Number:** AERIS-TP-001  
**Revision:** 1.0  
**Date:** 2026-07-14  
**Author:** RF Systems Engineering  
**Status:** Released  

---

## 1. Scope and Purpose

This document defines the complete test and measurement procedures for the AERIS-10P phased-array FMCW radar system. All tests must be performed in the sequence specified. Each test phase builds on the verified results of the previous phase. No phase may be skipped; any failure must be resolved and the failing test repeated before proceeding.

The AERIS-10P operates in the X-band amateur allocation 10.000–10.500 GHz (German AFuG 2017 / AFuV 2017, Klasse A license). All measurements involving radiated power must comply with the 75 W PEP limit and the DARC 3 cm band plan. A valid amateur radio license (Klasse A) must be held by the operator or a licensed operator must be present during any radiated tests.

---

## 2. Test Equipment

The following calibrated instruments are required. All instruments must have valid calibration certificates traceable to national standards (PTB or equivalent). Calibration status must be verified before commencing any test phase.

| Item | Instrument | Model | Frequency / Range | Notes |
|------|-----------|-------|-------------------|-------|
| VNA | Vector Network Analyzer | Keysight E5080B or R&S ZVA40 | 100 kHz – 20 GHz (ZVA40) / 9 GHz (E5080B) | 2-port minimum; 4-port preferred for array work |
| SA | Spectrum Analyzer | R&S FSP40 or Keysight N9020B | 3 Hz – 40 GHz | Pre-amplifier required for noise figure work |
| PM | Power Meter | Keysight E4418B (or HP 437B) | — | With 8481A (10 MHz–18 GHz) and 8485A (0.5–26.5 GHz) sensors |
| OSC | Oscilloscope | Keysight MSOX3054T or Tektronix MDO3054 | 500 MHz, 4 Ch | With FFT capability for IF analysis |
| SG | Signal Generator | Keysight E8257D or R&S SMW200A | 10 MHz – 20 GHz | For LO injection and loopback tests |
| NF | Noise Figure Analyzer | R&S FSV-K30 option or Keysight N8975A | 10 MHz – 26.5 GHz | Or use Y-factor with calibrated noise source |
| NS | Noise Source | Keysight 346B | 10 MHz – 18 GHz | ENR ~15 dB at 10 GHz, NIST-traceable cal |
| CR | Corner Reflector | Trihedral, 0.3 m edge length | — | RCS ~10 m² at 10 GHz |
| ATT | Step Attenuator | R&S RSC or HP 355D | DC – 18 GHz | 0–110 dB in 10 dB steps |
| CAL | Calibration Kit | Keysight 85052D (3.5 mm) or 85056D (2.4 mm) | — | SOL or TOSM standard |
| DMM | Digital Multimeter | Fluke 87V or Keysight 34401A | — | 4.5 digit minimum |
| THERM | Thermal Camera or Type-K probe | FLIR E8 or similar | — | For thermal testing |

### 2.1 Cable and Adaptor Inventory

Before starting, assemble and characterize the following test cables:

- 2× 3.5 mm (m) to 3.5 mm (m), phase-stable, 50 cm, ≤0.5 dB loss at 10 GHz
- 2× 2.92 mm (m) to SMA (f) adaptor
- 1× SMA (m) to SMA (m) barrel (for loopback)
- 30 dB SMA attenuator (rated >2 W) for loopback tests

Measure cable insertion loss at 10 GHz with the VNA and record values in the Cable Loss Log. All subsequent power measurements must be corrected for cable loss.

---

## 3. Phase 1 — DC / Power Supply Tests (PT-001 through PT-005)

**Prerequisites:** PCB assembly complete; firmware not required for this phase. All RF ICs must be unpowered or their supply pins left unconnected during supply characterisation.

### PT-001 — Input Voltage Range Test

**Objective:** Verify correct operation of all DC-DC regulators over the specified input voltage range 22–28 V DC.

**Procedure:**
1. Connect a laboratory bench supply (current-limited to 2 A) to the 24 V input terminals. Do not connect any load boards.
2. Set supply to 22.0 V. Enable output. Measure and record the following output voltages with the DMM: +5 V rail, +3.3 V rail, +5 V_RF rail, −5 V_RF rail.
3. Increase supply voltage in 1 V steps to 28.0 V. Record all rail voltages at each step.
4. Return supply to 24.0 V nominal. This is the nominal test voltage for all subsequent tests.

**Pass Criteria:** All output rails remain within their specified tolerance bands (see PT-002) at all input voltages from 22 to 28 V. No output rail shall deviate by more than 0.5% from the 22 V value as input changes from 22 to 28 V (line regulation).

**Data Sheet:** Table PT-001-A (Input Voltage Sweep).

---

### PT-002 — Rail Voltage Accuracy

**Objective:** Verify DC output voltage accuracy at 24 V nominal input and rated load.

**Procedure:**
1. Connect representative resistive loads to each rail to simulate nominal current: +5 V at 3 A (resistor ≈ 1.67 Ω / 15 W), +3.3 V at 2 A (1.65 Ω / 7 W), +5 V_RF at 0.5 A (10 Ω / 2.5 W), −5 V_RF at 0.5 A.
2. Allow 5 minutes for temperatures to stabilise.
3. Measure each rail voltage at the load resistor terminals with calibrated DMM.

**Pass Criteria:**

| Rail | Nominal | Tolerance | Min | Max |
|------|---------|-----------|-----|-----|
| +5 V (LT8612) | 5.000 V | ±2% | 4.900 V | 5.100 V |
| +3.3 V (LT8607) | 3.300 V | ±1.5% | 3.251 V | 3.350 V |
| +5 V_RF (TPS65133) | 5.000 V | ±3% | 4.850 V | 5.150 V |
| −5 V_RF (TPS65133) | −5.000 V | ±3% | −5.150 V | −4.850 V |

---

### PT-003 — Ripple and Noise Measurement

**Objective:** Measure DC-DC converter output ripple and noise to verify it does not degrade RF performance.

**Procedure:**
1. Connect oscilloscope probe (AC-coupled, 20 MHz bandwidth limit OFF) directly at the output capacitor of each DC-DC converter.
2. Set scope timebase to 50 µs/div to capture switching frequency (LT8612 and LT8607 switch at ~2 MHz).
3. Measure peak-to-peak ripple voltage.
4. Change scope to 10 MHz bandwidth limit; measure residual noise floor.

**Pass Criteria:** Peak-to-peak ripple ≤50 mV on +5 V; ≤30 mV on +3.3 V; ≤20 mV on ±5 V RF rails. Noise floor ≤5 mV RMS on RF rails.

---

### PT-004 — Efficiency Measurement

**Objective:** Measure power supply conversion efficiency at nominal load.

**Procedure:**
1. With loads from PT-002 connected, measure:
   - Input power: P_in = V_in × I_in (use DMM for V, clamp meter or shunt resistor for I)
   - Output power: P_out = sum of (V_rail × I_rail) for all rails
2. Calculate efficiency: η = P_out / P_in × 100%

**Pass Criteria:** Overall efficiency ≥80% at nominal 24 V input and nominal load.

---

### PT-005 — Thermal Test

**Objective:** Verify that no component exceeds its maximum rated junction temperature during 30 minutes of continuous operation at rated load.

**Procedure:**
1. Apply rated loads from PT-002. Apply 24 V input. Allow system to run for 30 minutes in still air (no forced cooling, no heatsink — baseline measurement).
2. At t = 30 minutes, measure case temperature of each DC-DC IC with thermocouple or thermal camera. Record ambient air temperature.
3. Calculate estimated junction temperature: T_j = T_case + (P_dissipated × θ_jc) for each device.
4. Repeat with 80 mm cooling fan operational.

**Pass Criteria:** No IC case temperature shall exceed 85°C in still air; ≤70°C with fan at rated 24 V load and 25°C ambient. LT8612 maximum T_j = 125°C; LT8607 maximum T_j = 125°C; TPS65133 maximum T_j = 150°C.

---

## 4. Phase 2 — VCO / PLL Tests (PT-010 through PT-015)

**Prerequisites:** Phase 1 complete (all rails verified). STM32H743 firmware loaded (PLL configuration firmware v0.1 or later). ADF4159CCPZ and HMC733LP6CE populated.

### PT-010 — ADF4159 Lock Detect Verification

**Objective:** Confirm that the ADF4159 PLL achieves and maintains frequency lock.

**Procedure:**
1. Power up the RF front-end board (apply 5 V and 3.3 V to the board).
2. Connect OCXO-10 MHz (ABRACON AOCJY-10) reference to the ADF4159 REF_IN pin.
3. Verify OCXO output level at REF_IN: should be 0 dBm ±3 dBm into 50 Ω.
4. Program the ADF4159 via SPI (STM32 firmware command `PLL_INIT`) for CW output at 10.050 GHz.
5. Measure the MUXOUT/LD pin voltage. In lock-detect mode, this pin should read >2.5 V (logic high) when locked.
6. Verify lock is maintained by holding the measurement for 60 seconds.
7. Program through the sweep range: 10.000 GHz, 10.025 GHz, 10.050 GHz, 10.075 GHz, 10.100 GHz. Verify lock at each frequency.

**Pass Criteria:** LD pin HIGH (>2.5 V) within 5 ms of any frequency change. Lock maintained for ≥60 s at each frequency. No cycle slips observed on scope during 60 s measurement.

---

### PT-011 — Frequency Accuracy

**Objective:** Verify that the synthesized frequency is within specification across the 10.000–10.100 GHz band.

**Procedure:**
1. Connect the HMC733 output (after buffer, before PA) to the spectrum analyzer input via a calibrated 20 dB attenuator and 2.92 mm cable.
2. Set SA: center 10.050 GHz, span 200 MHz, RBW 1 kHz, VBW 300 Hz, detector peak.
3. Program five CW frequencies: 10.000, 10.025, 10.050, 10.075, 10.100 GHz.
4. At each frequency, use the SA marker function to read the peak frequency. Record both the programmed and measured frequency.
5. Correct for any known SA frequency reference error.

**Pass Criteria:** Measured frequency within ±1 MHz of programmed frequency at all five test points (limited by the 10 MHz OCXO reference accuracy of ±0.01 ppm over temperature, corresponding to ±0.1 Hz error — any larger error indicates reference or PLL configuration issue).

---

### PT-012 — Chirp Linearity Test

**Objective:** Verify that the FMCW chirp is linear over the full 100 MHz bandwidth, chirp time 1 ms.

**Procedure:**
1. Configure ADF4159 for sawtooth FMCW: start frequency 10.000 GHz, stop 10.100 GHz, ramp time 1 ms, PRF 1 kHz.
2. Connect the VCO output to the oscilloscope via a broadband envelope detector (or use a directional coupler and mixer to produce a baseband representation of the instantaneous frequency).
3. Alternative (preferred): connect HMC733 output to a calibrated mixer with a stable CW LO at 10.000 GHz. The IF output (0–100 MHz range) represents the instantaneous frequency deviation. Capture the IF on the oscilloscope at 1 GS/s, 2 ms window.
4. Post-process the IF waveform: use FFT on sliding windows (e.g., 10 µs Hanning window, 1 µs step) to compute the instantaneous frequency as a function of time. Fit a linear regression to the resulting f(t) curve.
5. Calculate residual non-linearity: RMS deviation from the linear fit, expressed in MHz.

**Pass Criteria:** Chirp linearity error ≤1% of chirp bandwidth (≤1 MHz RMS deviation from ideal linear ramp over the 1 ms chirp). The measured sweep rate must be 100 MHz / 1 ms = 100 GHz/s ± 2%.

---

### PT-013 — Phase Noise Measurement

**Objective:** Measure single-sideband (SSB) phase noise of the synthesized carrier.

**Procedure:**
1. Set ADF4159 to CW mode at 10.050 GHz. Connect HMC733 output (via 20 dB attenuator) to SA.
2. Using the SA phase noise measurement function (e.g., R&S FSP Phase Noise option, or use cross-correlation if available): measure L(f) at offsets 10 kHz, 100 kHz, and 1 MHz from carrier.
3. Correct the measurement for attenuator loss. Subtract 3 dB for two-sideband to SSB conversion if required by instrument.
4. Record L(f) in dBc/Hz at each offset frequency.

**Pass Criteria:** L(10 kHz) ≤ −80 dBc/Hz; L(100 kHz) ≤ −95 dBc/Hz; L(1 MHz) ≤ −110 dBc/Hz. (These values are consistent with the ADF4159 + HMC733 combination with 10 MHz OCXO reference.)

---

### PT-014 — Sweep Rate Verification

**Objective:** Confirm that the ADF4159 sawtooth ramp achieves exactly 100 MHz / 1 ms sweep rate.

**Procedure:**
1. Using the IF output from the mixer arrangement in PT-012, measure the time for the IF to sweep from 0 to 100 MHz (i.e., the time for the chirp to cover the full bandwidth) using the oscilloscope time-domain capture.
2. Trigger the oscilloscope on the PRF sync output from the STM32 (RAMP_START GPIO).
3. Measure: T_chirp (time from ramp start to ramp end at 10.100 GHz).
4. Measure: T_retrace (time from ramp end to next ramp start — should be <50 µs to maintain effective PRF).
5. Compute effective sweep rate = 100 MHz / T_chirp.

**Pass Criteria:** T_chirp = 1.000 ms ± 10 µs. Sweep rate = 100.0 GHz/s ± 1.0 GHz/s. T_retrace ≤50 µs.

---

### PT-015 — Spectral Purity

**Objective:** Verify absence of spurious signals within the chirp bandwidth.

**Procedure:**
1. CW mode at 10.050 GHz. SA span 500 MHz, RBW 100 kHz, VBW 30 kHz. Peak search across the band.
2. Identify any spur above the noise floor. Characterise frequency offset, amplitude relative to carrier.

**Pass Criteria:** No spurious signal within the 10.000–10.100 GHz band exceeding −50 dBc. No reference spur at ±10 MHz offset exceeding −60 dBc.

---

## 5. Phase 3 — TX Chain Tests (PT-020 through PT-025)

**Prerequisites:** Phases 1 and 2 complete. HMC451LS6GE PA populated. A 30 dB, 5 W load attenuator must be connected to the TX output at all times during powered tests.

**WARNING:** The TX output delivers up to +30 dBm (1 W). Never connect a power meter, spectrum analyzer, or VNA port directly to the PA output without a sufficient attenuator. Verify attenuator power rating before connecting.

### PT-020 — Output Power Measurement

**Objective:** Verify PA output power at the TX output port.

**Procedure:**
1. Configure system for CW at 10.050 GHz. PA bias applied.
2. Connect: PA output → 30 dB attenuator → power meter (HP 437B + 8485A sensor). Account for cable loss.
3. Measure output power. Enter PA drive level at nominal setting.
4. Sweep frequency from 10.000 to 10.100 GHz in 10 MHz steps. Record power at each step.

**Pass Criteria:** Output power +29 dBm ±1 dB (allowing for measurement uncertainty) at all frequencies 10.000–10.100 GHz. Power flatness ≤1.5 dB across the band.

---

### PT-021 — Harmonic and Spurious Emissions

**Objective:** Verify compliance with spurious emission limits and characterise harmonic content.

**Procedure:**
1. CW at 10.050 GHz. Connect: PA output → 30 dB attenuator → SA. SA span: 500 MHz to 40 GHz.
2. Set RBW 1 MHz, VBW 300 kHz. Peak-search for all signals.
3. Measure absolute level of fundamental and harmonics (20.1 GHz second harmonic, 30.15 GHz third harmonic).
4. Calculate harmonic suppression relative to fundamental.

**Pass Criteria:** Second harmonic ≤ −30 dBc; third harmonic ≤ −40 dBc. All spurious ≤ −40 dBc within 10.000–10.500 GHz band. Compliance with AFuV 2017 spurious emission limits required.

---

### PT-022 — PA Gain Compression (P1dB)

**Objective:** Determine the 1 dB gain compression point of the HMC451LS6GE PA.

**Procedure:**
1. Inject a CW signal at 10.050 GHz from the signal generator into the PA input through a calibrated step attenuator.
2. Measure output power with power meter as a function of input power, sweeping input from −20 dBm to +5 dBm in 1 dB steps.
3. Plot P_out vs P_in. Fit the linear region. Find the input level at which P_out deviates 1 dB below the linear extrapolation.
4. Record P1dB_in and P1dB_out.

**Pass Criteria:** P1dB_out ≥ +28 dBm (HMC451LS6GE datasheet specifies +29 dBm; 1 dB margin allowed for board losses). Nominal gain = P_out − P_in in linear region should be 28 dB ± 2 dB.

---

### PT-023 — Phase Shifter Characterisation

**Objective:** Verify that each HMC647ALP5E 6-bit digital phase shifter covers the full 360° range with adequate resolution and accuracy.

**Procedure:**
1. Connect VNA port 1 to the phase shifter input (SMA), VNA port 2 to the phase shifter output.
2. Configure VNA: S21 measurement, frequency 10.000–10.100 GHz, 101 points.
3. For each phase shifter on the array (16 TX elements): sweep all 64 phase codes (0x00 through 0x3F) via SPI command from STM32. Record S21 magnitude and phase at 10.050 GHz for each code.
4. Compute: phase vs code (should be linear, 360°/64 ≈ 5.625° per step). Compute RMS phase error (deviation from ideal linear relationship). Compute insertion loss variation across phase states.

**Pass Criteria:** Phase range ≥350° (full 360° nominally, ≥350° allowed for boundary states). Phase step accuracy ≤1° RMS per step versus ideal. Insertion loss variation ≤1 dB across all 64 states (HMC647A specified ≤1 dB). Maximum insertion loss (worst state) ≤7 dB at 10 GHz.

---

### PT-024 — TX Antenna Port Impedance (S11)

**Objective:** Verify TX output port impedance matching.

**Procedure:**
1. VNA 2-port TOSM calibration at the TX output SMA connector reference plane.
2. Connect PA output (at rated bias, PA active) to VNA port 1 via 30 dB coupler/attenuator arrangement to protect VNA.
3. Measure S11 from 9.5–10.5 GHz. 

**Pass Criteria:** Return loss ≥15 dB (S11 ≤ −15 dB) at 10.000–10.100 GHz.

---

### PT-025 — TX Chain Gain Budget Verification

**Objective:** Verify the end-to-end TX gain chain: VCO → PA → antenna feed.

**Procedure:**
1. Measure S21 of: VCO buffer output → phase shifter → PA → feed cable → antenna SMA port.
2. Total chain gain = PA gain (28 dB) − phase shifter loss (~6 dB) − cable loss (~1 dB) = ~21 dB.
3. Record gain at CW 10.050 GHz and across 10.000–10.100 GHz.

**Pass Criteria:** End-to-end TX gain within ±2 dB of budget value. Variation across band ≤2 dB.

---

## 6. Phase 4 — RX Chain Tests (PT-030 through PT-035)

**Prerequisites:** Phase 3 complete. HMC1040LP4E LNA and HMC213B mixer populated with correct bias.

### PT-030 — LNA Gain (S21)

**Objective:** Measure HMC1040LP4E LNA gain.

**Procedure:**
1. 2-port VNA calibration at the LNA input and output SMA reference planes.
2. Measure S21 from 8–12 GHz, 101 points, at nominal LNA bias (typically 3 V drain, 100 mA quiescent or per datasheet).
3. Record gain and bandwidth.

**Pass Criteria:** S21 ≥ 17 dB at 10.050 GHz (HMC1040 specifies 18 dB ± 1 dB). Flatness ≤1.5 dB across 10.000–10.100 GHz. Input return loss S11 ≥10 dB.

---

### PT-031 — Noise Figure (Y-Factor Method)

**Objective:** Measure system noise figure of the RX front end (LNA + Mixer).

**Procedure:**
1. Connect calibrated noise source (Keysight 346B, ENR known at 10 GHz) to LNA input.
2. Connect LNA output through mixer (LO at 9.950 GHz) to IF port (100 MHz IF) to SA noise figure personality (or noise figure meter).
3. Perform Y-factor measurement: record noise power with noise source ON and OFF.
4. Y = P_on / P_off (linear). NF = ENR / (Y − 1).
5. Measure NF at 10.000, 10.050, 10.100 GHz.

**Pass Criteria:** LNA NF ≤ 2.0 dB at 10.050 GHz (HMC1040 specified 1.5 dB; 0.5 dB allowed for board parasitics and connector loss). Total RX chain NF (LNA + mixer) ≤ 4.5 dB. System NF (including all RX components) ≤ 8 dB.

---

### PT-032 — Mixer Conversion Loss

**Objective:** Measure HMC213B double-balanced mixer conversion loss.

**Procedure:**
1. Apply LO: 10.000 GHz, +10 dBm from signal generator to LO port.
2. Apply RF: 10.050 GHz, −20 dBm (well below LNA compression) to RF port.
3. Expected IF: 50 MHz.
4. Measure IF output power at 50 MHz with SA (RBW 100 kHz).
5. Conversion loss = P_RF − P_IF (all in dBm, corrected for cable losses).
6. Sweep RF from 10.000 to 10.100 GHz (IF from 0 to 100 MHz).

**Pass Criteria:** Conversion loss ≤7 dB at 10.050 GHz (HMC213B specified ~6 dB ± 1 dB). Conversion loss variation ≤1.5 dB across 0–100 MHz IF bandwidth.

---

### PT-033 — IF Output Frequency Verification

**Objective:** Verify that beat frequencies produced by the FMCW system are within the ADC input range and FFT analysis window.

**Procedure:**
1. Connect a delay line (coax cable, known electrical length) from the TX output (through 60 dB of attenuation) back into the RX input to simulate a target at a known range.
2. Delay line of 20 ns represents range = c × τ / 2 = 3 m.
3. Configure system in FMCW mode. Measure IF output with SA. Verify beat frequency = (sweep rate) × delay = 100 GHz/s × 20 ns = 2 kHz.
4. Vary delay line length and verify that beat frequency scales correctly.

**Pass Criteria:** Measured beat frequency within ±5% of calculated value for all tested delay lengths. IF signal visible at ADC output in software FFT.

---

### PT-034 — ADC Full-Scale Calibration

**Objective:** Calibrate the ADS8661IRGAT ADC and verify dynamic range.

**Procedure:**
1. Apply a known sine wave from the signal generator at 50 kHz, 0 dBm (adjusted to match ADC input range, nominally 0–5 V differential) to the ADC input.
2. Capture 1024 samples at 1 MSPS via SPI into STM32 buffer.
3. Compute FFT. Measure fundamental amplitude and noise floor.
4. Compute SNR and ENOB: ENOB = (SNR − 1.76) / 6.02.
5. Sweep input amplitude from −60 dBFS to 0 dBFS and verify linearity.

**Pass Criteria:** ENOB ≥ 14 bits at 50 kHz input (ADS8661 specified SNR = 91 dB → ENOB = 14.8 bits). No missing codes over full-scale range.

---

### PT-035 — RX Chain Gain Budget Verification

**Objective:** Verify end-to-end RX chain gain from antenna SMA port to ADC input.

**Procedure:**
1. Apply known CW at 10.050 GHz, −50 dBm to the RX antenna SMA port.
2. Measure the IF output level at the ADC input.
3. Total expected RX chain gain: LNA (+18 dB) − Mixer conversion loss (−6 dB) + IF amplifier stages (as designed) = target ADC input level −20 to −3 dBFS for a −50 dBm RF input.

**Pass Criteria:** ADC input level within ±3 dB of expected value calculated from gain budget.

---

## 7. Phase 5 — Antenna Array Tests (PT-040 through PT-045)

**Prerequisites:** Antenna panel assembly complete. Rogers RO4003C PCB, immersion gold finish, SMA connectors soldered.

### PT-040 — Individual Element S11

**Objective:** Verify impedance matching of each of the 32 patch antenna elements (16 TX, 16 RX).

**Procedure:**
1. VNA 1-port calibration at the SMA connector reference plane (OSL or TOSM).
2. Terminate all other antenna ports with 50 Ω loads.
3. For each of the 32 elements, measure S11 from 9.5–10.5 GHz, 201 points.
4. Extract: resonant frequency (minimum S11), return loss at 10.050 GHz, −10 dB bandwidth.

**Pass Criteria:** Return loss ≥15 dB at 10.050 GHz for all 32 elements. Resonant frequency 10.050 ± 50 MHz. Element-to-element resonant frequency variation ≤30 MHz. (Patch dimensions: 13.8 mm × 13.8 mm on RO4003C, εr = 3.55.)

---

### PT-041 — Element-to-Element Isolation

**Objective:** Measure coupling between adjacent TX elements and between TX and RX arrays.

**Procedure:**
1. 2-port VNA. Connect port 1 to element under test, port 2 to adjacent element. Terminate all other elements in 50 Ω.
2. Measure S21 at 10.050 GHz for: nearest neighbour (15 mm spacing), diagonal neighbour, TX element to nearest RX element.
3. Record isolation values.

**Pass Criteria:** Adjacent element isolation ≥20 dB. TX-to-RX array isolation ≥30 dB at 10.050 GHz.

---

### PT-042 — Phase Coherence Across Array

**Objective:** Verify that all array elements exhibit the correct relative phase when driven from the common source.

**Procedure:**
1. Configure system to output CW at 10.050 GHz. Connect system RF source output (pre-phase-shifter) to each of the 16 TX elements in turn via a common feed.
2. For each element port, use VNA port 2 (reference: port 1 locked to the TX source) to measure S21 phase.
3. With all phase shifters set to 0x00 (minimum phase state), record S21 phase for each element.
4. Compute element-to-element phase variation (RMS deviation from mean).

**Pass Criteria:** Phase uniformity ≤±5° RMS across all 16 elements of each array (TX and RX) with phase shifters set to a common state. This verifies consistent feed network electrical length.

---

### PT-043 — Radiation Pattern Verification (Near-Field Scan)

**Objective:** Verify beam shape and steering capability using an improvised near-field measurement.

**Procedure:**
1. Mount the AERIS-10P antenna panel vertically at 1.5 m height on a non-metallic support.
2. Mount a calibrated reference antenna (standard gain horn, minimum 15 dBi at 10 GHz) on a camera tripod at distance R = 2 m from the aperture (near-field, adequate for pattern characterisation at this aperture size).
3. Connect reference horn to SA.
4. Apply CW from the AERIS TX chain at reduced power (−10 dBm at each element).
5. With all phase shifters at broadside setting (all 0x00), record received power as the reference horn is swept manually across ±60° in azimuth in 5° steps.
6. Repeat with phase shifters set to steer to +30° and −30° (calculate required phase gradient: Δφ = 2π × d/λ × sin(θ) = 2π × 0.5 × sin(30°) = π/2 radians = 90° per element).
7. Plot received power vs angle for each beam setting.

**Pass Criteria:** Broadside beam peak within ±2° of the array normal. 3 dB beamwidth 20°–25° per axis (calculated 22° for 4 elements at λ/2 spacing). Steered beam peak within ±5° of commanded angle for ±30° steering. Side lobes ≤−10 dBc (theoretical first sidelobe −13 dBc for uniform aperture).

---

### PT-044 — Antenna Gain Estimation

**Objective:** Estimate TX and RX array gain using the Friis transmission equation with the calibrated reference horn.

**Procedure:**
1. Using the near-field setup from PT-043, position reference horn at broadside, distance R = 2 m. Measure received power P_r with SA.
2. Apply: P_r = P_t + G_t + G_r − FSPL, where FSPL = 20 log(4πR/λ) at 2 m, 10 GHz = 20 log(4π × 2 / 0.03) = 58.4 dB.
3. G_t = known horn gain (from calibration certificate). Compute G_AERIS_TX from the measurement.

**Pass Criteria:** Measured TX array gain ≥20 dBi (practical target: 22 dBi theoretical minus ≤2 dB for feed losses).

---

### PT-045 — Array Polarisation Check

**Objective:** Verify linear polarisation and polarisation purity of the patch array.

**Procedure:**
1. Mount calibrated horn antenna (known polarisation) at broadside at 2 m.
2. Rotate the horn 0°, 45°, 90°, 135° (cross-polarisation). Record received power at each orientation.

**Pass Criteria:** Cross-polarisation discrimination ≥15 dB (difference between co-pol and cross-pol received power).

---

## 8. Phase 6 — Integration Tests (PT-050 through PT-055)

**Prerequisites:** All previous phases complete and passed. Full system assembled in chassis.

### PT-050 — End-to-End FMCW Loopback Test

**Objective:** Verify that the complete FMCW signal chain (TX → loopback → RX → ADC → FFT) produces a coherent beat note at the expected frequency.

**Procedure:**
1. Connect TX output to RX input via a coaxial cable with known electrical length τ and 30 dB in-line attenuation. The cable delay τ determines the expected beat frequency: f_beat = K × τ, where K = 100 GHz/s.
2. Use a precision coax delay of 2 µs (physically ~40 cm of air-filled coax or equivalent cable). Expected beat: 100 GHz/s × 2 µs = 200 kHz.
3. Configure AERIS software for FMCW acquisition, 1 ms chirp, 1 kHz PRF. Capture 100 chirps.
4. Apply FFT to IF data. Identify beat note peak.
5. Compute range from beat frequency: R = c × f_beat / (2K) = 3e8 × 200e3 / (2 × 100e9) = 0.3 m (represents the one-way delay equivalent — a target at equivalent range).

**Pass Criteria:** Beat note detected with SNR ≥ 20 dB in the FFT. Beat frequency within ±2 kHz of expected value. Phase coherence between chirps verified by Doppler FFT (zero Doppler for static cable).

---

### PT-051 — Radiated Range Measurement with Corner Reflector

**Objective:** Verify that the complete system can detect and correctly range a corner reflector at known distances.

**Safety:** Ensure a valid Klasse A amateur radio license is held by the operator. Transmit power +30 dBm EIRP ≈ 52 dBm — well below the 75 W PEP limit. Operate in the 10.000–10.100 GHz German amateur band. Provide station identification (callsign) every 10 minutes. If required, obtain experimental radar permit from BNetzA prior to radiated testing.

**Procedure:**
1. Set up system on tripod (3/8-16 UNC mount) in open area with clear line of sight (parking area, field). Minimum 50 m clear area.
2. Place trihedral corner reflector (0.3 m edge, RCS ≈ 10 m²) at 10 m.
3. Acquire 100 chirps. Compute range-FFT. Identify peak corresponding to the corner reflector.
4. Compare measured range to physical distance. Record range error.
5. Move corner reflector to 50 m. Repeat.
6. Move corner reflector to 100 m. Repeat.
7. Determine maximum detection range with SNR ≥ 15 dB.

**Pass Criteria:** Range accuracy ±3 m (corresponding to ±2 range bins at 1.5 m resolution) at all three distances. Corner reflector detected (SNR ≥ 15 dB) at all three test distances.

---

### PT-052 — Beam Steering Verification (Radiated)

**Objective:** Verify beam steering to ±30° using a fixed receive reference antenna.

**Procedure:**
1. Mount AERIS system on tripod. At distance 5 m, set up a reference receiving horn antenna (calibrated, 15 dBi) connected to SA, positioned at broadside to the AERIS array.
2. Program beam steering: 0°, +15°, +30°, −15°, −30°.
3. At each steering angle, measure received power at the reference horn.
4. Move the reference horn physically to the commanded angle while keeping AERIS at broadside. Record the power level when horn is at broadside and when at the commanded angle for each phase setting. Cross-check that maximum is at the commanded angle.

**Pass Criteria:** Beam peak direction within ±5° of commanded angle at ±30° steering. Beam steering loss ≤3 dB compared to broadside (theoretical for element pattern × array factor).

---

### PT-053 — Velocity Measurement Verification

**Objective:** Verify Doppler velocity measurement using a rotating target (motor-driven corner reflector or moving vehicle at controlled speed).

**Procedure:**
1. Configure system for CPI of 100 chirps (100 ms), enabling Doppler processing.
2. Use a target moving at a known radial velocity (e.g., a vehicle traveling at a measured speed on a straight road in front of the radar). GPS-derived ground speed of the target provides reference.
3. Measure the Doppler frequency shift in the range-Doppler map.
4. Convert: v_radial = f_Doppler × λ / 2, where λ = 0.03 m.
5. Velocity resolution: Δv = λ / (2 × T_cpi) = 0.03 / (2 × 0.1) = 0.15 m/s.

**Pass Criteria:** Measured velocity within ±0.5 m/s of GPS reference. Minimum detectable velocity: ≤0.3 m/s (2 resolution cells).

---

### PT-054 — CFAR Detection Test

**Objective:** Verify the CFAR (Constant False Alarm Rate) detection algorithm performance.

**Procedure:**
1. Process recorded datasets from PT-051 through the CFAR detection chain (CA-CFAR, guard cells = 2, reference cells = 16, PFA = 10⁻⁴).
2. Verify that the corner reflector is detected at all ranges with Pd ≥ 0.9.
3. Count false alarms in range bins without targets over 10 minutes of data.
4. Compute empirical PFA = false alarms / (total range bins × total chirps).

**Pass Criteria:** Corner reflector detected in ≥90% of range-Doppler maps. Empirical PFA ≤ 10⁻³ (one decade relaxed from design PFA to account for clutter environment).

---

### PT-055 — Software Integration and Display Test

**Objective:** Verify that the complete software pipeline (STM32 data capture → SPI → Raspberry Pi 5 → FFT processing → display) functions end-to-end.

**Procedure:**
1. Start the AERIS software on the Raspberry Pi 5. Verify all services start without error (check system log: `journalctl -u aeris-radar`).
2. Verify live range-Doppler display updates at ≥5 Hz frame rate.
3. Move hand target (hand-wave) in front of radar at 1–3 m. Verify detection in live display.
4. Run the automated self-test routine (`aeris-selftest --full`). Verify all checks PASS.
5. Verify that station identification is displayed and logged every 10 minutes.

**Pass Criteria:** All software services start without error. Display frame rate ≥5 Hz. Hand-wave detectable at 1–3 m. Self-test returns PASS on all checks. Station ID logged correctly.

---

## 9. Acceptance Criteria Summary

The following table summarises the acceptance criteria for system-level delivery. The system is accepted only when all criteria are PASS.

| Test ID | Parameter | Minimum Requirement | Pass / Fail |
|---------|-----------|---------------------|-------------|
| PT-001 | Supply regulation over 22–28 V | All rails in tolerance | |
| PT-002 | Rail voltage accuracy | See tolerance table | |
| PT-003 | Rail ripple | ≤50 mV p-p on +5 V | |
| PT-005 | Thermal at rated load | T_case ≤ 85°C | |
| PT-010 | PLL lock detect | HIGH within 5 ms | |
| PT-011 | Frequency accuracy | ±1 MHz | |
| PT-012 | Chirp linearity | ≤1% RMS deviation | |
| PT-013 | Phase noise at 100 kHz | ≤ −95 dBc/Hz | |
| PT-014 | Sweep rate | 100 GHz/s ± 1% | |
| PT-020 | TX output power | +29 dBm ± 1 dB | |
| PT-021 | 2nd harmonic | ≤ −30 dBc | |
| PT-022 | P1dB | ≥ +28 dBm | |
| PT-023 | Phase shifter range | ≥ 350° | |
| PT-023 | Phase shifter error | ≤ 1° RMS/step | |
| PT-030 | LNA gain | ≥ 17 dB | |
| PT-031 | System NF | ≤ 8 dB | |
| PT-040 | Element S11 | ≥ 15 dB return loss | |
| PT-041 | TX-RX isolation | ≥ 30 dB | |
| PT-042 | Phase coherence | ≤ ±5° RMS | |
| PT-043 | Beam steering accuracy | ±5° at ±30° | |
| PT-050 | Loopback beat SNR | ≥ 20 dB | |
| PT-051 | Range accuracy | ±3 m at 10–100 m | |
| PT-051 | Detection range | ≥ 100 m (corner reflector) | |
| PT-053 | Velocity accuracy | ±0.5 m/s | |
| PT-055 | Display frame rate | ≥ 5 Hz | |

---

## 10. Test Data Sheets

### Data Sheet: PT-002 Rail Voltage Accuracy

| Rail | Nominal (V) | Min (V) | Max (V) | Measured (V) | Pass/Fail | Date | Technician |
|------|-------------|---------|---------|--------------|-----------|------|-----------|
| +5 V | 5.000 | 4.900 | 5.100 | | | | |
| +3.3 V | 3.300 | 3.251 | 3.350 | | | | |
| +5 V_RF | 5.000 | 4.850 | 5.150 | | | | |
| −5 V_RF | −5.000 | −5.150 | −4.850 | | | | |

### Data Sheet: PT-011 Frequency Accuracy

| Programmed (GHz) | Measured (GHz) | Error (MHz) | Pass/Fail |
|------------------|----------------|-------------|-----------|
| 10.000 | | | |
| 10.025 | | | |
| 10.050 | | | |
| 10.075 | | | |
| 10.100 | | | |

### Data Sheet: PT-013 Phase Noise

| Offset Frequency | Limit (dBc/Hz) | Measured (dBc/Hz) | Pass/Fail |
|------------------|----------------|-------------------|-----------|
| 10 kHz | ≤ −80 | | |
| 100 kHz | ≤ −95 | | |
| 1 MHz | ≤ −110 | | |

### Data Sheet: PT-020 TX Output Power vs Frequency

| Frequency (GHz) | Measured Power (dBm) | Cable Loss Correction (dB) | Corrected Power (dBm) | Pass/Fail |
|-----------------|---------------------|----------------------------|----------------------|-----------|
| 10.000 | | | | |
| 10.010 | | | | |
| 10.020 | | | | |
| 10.030 | | | | |
| 10.040 | | | | |
| 10.050 | | | | |
| 10.060 | | | | |
| 10.070 | | | | |
| 10.080 | | | | |
| 10.090 | | | | |
| 10.100 | | | | |

### Data Sheet: PT-040 Antenna Element S11

| Element # | Array | Return Loss at 10.050 GHz (dB) | Resonant Frequency (GHz) | Pass/Fail |
|-----------|-------|-------------------------------|--------------------------|-----------|
| TX-01 | TX | | | |
| TX-02 | TX | | | |
| TX-03 | TX | | | |
| TX-04 | TX | | | |
| TX-05 | TX | | | |
| TX-06 | TX | | | |
| TX-07 | TX | | | |
| TX-08 | TX | | | |
| TX-09 | TX | | | |
| TX-10 | TX | | | |
| TX-11 | TX | | | |
| TX-12 | TX | | | |
| TX-13 | TX | | | |
| TX-14 | TX | | | |
| TX-15 | TX | | | |
| TX-16 | TX | | | |
| RX-01 | RX | | | |
| RX-02 | RX | | | |
| RX-03 | RX | | | |
| RX-04 | RX | | | |
| RX-05 | RX | | | |
| RX-06 | RX | | | |
| RX-07 | RX | | | |
| RX-08 | RX | | | |
| RX-09 | RX | | | |
| RX-10 | RX | | | |
| RX-11 | RX | | | |
| RX-12 | RX | | | |
| RX-13 | RX | | | |
| RX-14 | RX | | | |
| RX-15 | RX | | | |
| RX-16 | RX | | | |

### Data Sheet: PT-051 Range Measurement Accuracy

| Target Distance (m) | Measured Range (m) | Error (m) | SNR (dB) | Pass/Fail |
|--------------------|--------------------|-----------|----------|-----------|
| 10 | | | | |
| 50 | | | | |
| 100 | | | | |

---

## 11. Calibration Schedule and Ongoing Calibration Procedure

### 11.1 Calibration Intervals

| Item | Interval | Method |
|------|----------|--------|
| VNA (port calibration) | Before each test session | SOL or TOSM using calibration kit |
| Power meter sensor | Annually (external lab) | NIST-traceable calibration |
| Power meter offset | Before each use | Zeroing procedure per HP 437B / E4418B manual |
| Noise source ENR | Annually (external lab) | NIST-traceable calibration |
| Spectrum analyzer frequency reference | Before each session | Check against OCXO reference or GPS-disciplined source |
| AERIS-10P frequency reference (OCXO-10) | Quarterly | Compare against GPS-disciplined OCXO (e.g., Jackson Labs CSAC or Z3805A) |
| AERIS-10P TX power | Monthly | Power meter with calibrated path |
| AERIS-10P phase shifter table | Annually or after firmware update | Repeat PT-023 for all 16 × 64 states |

### 11.2 VNA Port Calibration Procedure

1. Connect calibration kit (Keysight 85052D or 85056D) to VNA port 1 at the measurement reference plane.
2. Perform OPEN, SHORT, LOAD (OSL) calibration per VNA instrument procedure. For 2-port measurements, perform TOSM (OPEN, SHORT, LOAD, THRU) on both ports simultaneously.
3. Verify calibration quality: connect the OPEN standard; S11 phase should be 0° ± 0.1° at DC, rolling linearly. Connect the THRU; S21 should be 0.0 dB ± 0.05 dB.
4. Save the calibration state. Calibration is valid for the current cable/connector configuration for up to 8 hours in a temperature-stable environment (ambient temperature variation ≤5°C).
5. If cables are disconnected and reconnected, recalibrate from step 1.

### 11.3 TX Power Calibration Procedure

1. Connect power sensor (8485A) to the TX output port via a characterised 30 dB attenuator. Record the attenuator's insertion loss at 10.050 GHz from its calibration certificate.
2. Apply the nominal bias settings. Command the system to CW mode at 10.050 GHz.
3. Zero the power meter with the RF off. Enable RF. Record power reading.
4. Correct for attenuator insertion loss and cable losses. Record corrected TX output power.
5. If measured power deviates more than ±1 dB from the nominal +30 dBm, investigate (check PA bias, PA temperature, feed connections) before proceeding to radiated tests.

### 11.4 Records Retention

All completed test data sheets must be:
- Signed and dated by the technician performing the test
- Countersigned by the project engineer
- Scanned to PDF and stored in the project documentation repository under `/Documentation/Test_Records/`
- Retained for a minimum of 5 years

---

*End of AERIS-10P Test and Measurement Procedures Rev 1.0*

*Document controlled. Check repository for latest revision before use.*
