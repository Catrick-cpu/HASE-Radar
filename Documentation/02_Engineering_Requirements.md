# AERIS-10P Engineering Requirements Specification Rev 1.0

**Document Number:** AERIS-10P-REQ-001  
**Revision:** 1.0  
**Date:** 2026-07-14  
**Author:** AERIS-10P Engineering Team  
**Status:** Released  
**Parent Document:** AERIS-10P-SPEC-001 (Project Specification Rev 1.0)

---

## Table of Contents

1. Introduction and Purpose
2. System Requirements (REQ-SYS)
3. RF Requirements (REQ-RF)
4. Antenna Requirements (REQ-ANT)
5. Digital and Control Requirements (REQ-DIG)
6. Power Requirements (REQ-PWR)
7. Mechanical Requirements (REQ-MEC)
8. Software Requirements (REQ-SW)
9. Regulatory Requirements (REQ-REG)
10. Safety Requirements (REQ-SAF)
11. Requirements Traceability Matrix
12. Revision History

---

## 1. Introduction and Purpose

### 1.1 Purpose

This Engineering Requirements Specification (ERS) defines all measurable, testable requirements for the AERIS-10P phased-array radar system. Each requirement is assigned a unique identifier, a verification method, and a reference to the design element responsible for satisfying it. This document serves as the binding technical reference for all design, fabrication, integration, and acceptance testing activities.

### 1.2 Requirement Conventions

Requirements are expressed using the word **shall** for mandatory requirements and **should** for recommended but non-mandatory targets. Each requirement is accompanied by:

- **Rationale:** Explains why the requirement exists.
- **Verification Method:** Analysis (A), Inspection (I), Demonstration (D), or Test (T).
- **Design Element:** The subsystem or component responsible for compliance.

### 1.3 Requirement Status Levels

| Status | Meaning |
|---|---|
| Open | Requirement not yet addressed in design |
| In Progress | Design activity underway |
| Closed | Requirement satisfied and verified |
| Deferred | Moved to future revision |

All requirements in this Rev 1.0 document have status **Open** pending completion of detailed design.

---

## 2. System Requirements (REQ-SYS)

### REQ-SYS-001 — Operating Frequency Band

**Requirement:** The AERIS-10P system shall operate in the frequency range 10.000–10.100 GHz.

**Rationale:** The German amateur radio service has secondary allocation of the 10.000–10.500 GHz band under AFuV 2017 Anlage 1. The DARC band plan designates 10.000–10.150 GHz for wideband experimental modes. Restricting operation to 10.000–10.100 GHz provides 100 MHz of usable chirp bandwidth while remaining within the DARC allocation.

**Verification Method:** T — Spectrum analyser measurement of VCO output swept frequency across one complete chirp ramp.

**Design Element:** ADF4159CCPZ PLL + HMC733LP6CE VCO.

---

### REQ-SYS-002 — Radar Modulation

**Requirement:** The system shall implement Frequency-Modulated Continuous Wave (FMCW) modulation with a sawtooth frequency ramp. The chirp bandwidth shall be 100 MHz ±1 MHz. The chirp repetition period shall be 1 ms ±10 μs (1 kHz PRF ±10 Hz).

**Rationale:** FMCW provides simultaneous range and velocity measurement with low peak transmit power, making it suitable for amateur radio use. A 100 MHz bandwidth gives 1.5 m range resolution. A 1 kHz PRF gives a 10 Hz update rate when processing 100-chirp CPIs.

**Verification Method:** T — Measurement of instantaneous frequency vs. time using a spectrum analyser in zero-span or a phase-coherent ADC measurement of a down-converted chirp reference.

**Design Element:** ADF4159CCPZ chirp ramp configuration registers; STM32H743 SPI initialisation firmware.

---

### REQ-SYS-003 — Range Resolution

**Requirement:** The system shall achieve a range resolution of ≤1.5 m after matched-filter (FFT) processing, measured as the 3 dB width of the point-spread function of a single tone target at close range.

**Rationale:** Range resolution is determined by the chirp bandwidth: δR = c/(2B) = 3×10⁸/(2×10⁸) = 1.5 m. This is derived from REQ-SYS-002.

**Verification Method:** T — Corner reflector at known range; measure FFT bin width of peak return.

**Design Element:** FMCW chirp bandwidth (100 MHz); range FFT processing on RPi5.

---

### REQ-SYS-004 — Velocity Resolution

**Requirement:** The system shall achieve a velocity resolution of ≤0.15 m/s with a coherent processing interval of 100 chirps at 1 kHz PRF.

**Rationale:** Velocity resolution = λ/(2·T_CPI) = 0.03/(2×0.1) = 0.15 m/s. This allows detection of slow-moving targets (pedestrians at ~1 m/s, vehicles at highway speeds).

**Verification Method:** A — Calculated from CPI length and wavelength; D — demonstration using a rotating reflector at known angular rate to produce known Doppler frequency.

**Design Element:** CPI length (100 chirps); Doppler FFT processing on RPi5.

---

### REQ-SYS-005 — Maximum Unambiguous Range

**Requirement:** The system shall provide an unambiguous range interval of at least 75 m for targets producing IF beat frequencies within the ADC Nyquist bandwidth.

**Rationale:** The beat frequency for a target at range R is f_beat = 2BR/(cT). At R = 75 m, f_beat = 2×10⁸×75/(3×10⁸×10⁻³) = 50 kHz, well within the 500 kHz Nyquist frequency of the 1 MSPS ADC. Longer ranges up to 150 m (f_beat = 100 kHz) are resolvable with the full ADC bandwidth.

**Verification Method:** A — Calculation from FMCW equations; T — retroreflector test at known ranges.

**Design Element:** ADS8661 ADC sample rate; IF filter bandwidth in analog chain.

---

### REQ-SYS-006 — Receiver Noise Figure

**Requirement:** The system receiver noise figure shall be ≤8 dB referred to the RX antenna port under nominal operating conditions.

**Rationale:** System NF of 8 dB gives sufficient sensitivity for a 2–5 km practical detection range against a 10 m² RCS target. The LNA NF of 1.5 dB dominates if sufficient gain precedes the mixer; however, combining losses and RF interconnect losses raise the cascaded NF to approximately 4–8 dB.

**Verification Method:** T — Y-factor noise figure measurement at the combined RX port using a calibrated noise source.

**Design Element:** HMC1040LP4E LNA; 16:1 combiner insertion loss; HMC213B mixer conversion loss.

---

### REQ-SYS-007 — Transmit Power

**Requirement:** The transmitter output power at the PA output shall be +30 dBm ±1 dB under all operating conditions over the temperature range −10°C to +50°C.

**Rationale:** +30 dBm (1 W) is within the capability of the HMC451LS6GE PA (P1dB = +29 dBm) with drive level set to avoid compression. This power level is well below the 75 W PEP legal limit.

**Verification Method:** T — Power meter measurement at PA output port over temperature.

**Design Element:** HMC451LS6GE PA; VCO drive level; input attenuator if required.

---

### REQ-SYS-008 — Beam Steering Range

**Requirement:** The system shall electronically steer the transmit and receive beams over a range of ±45° in azimuth and ±45° in elevation from boresight, using the phased-array antenna and digital phase shifters.

**Rationale:** ±45° provides useful field of view for surveillance and tracking applications. Beyond ±45° the array scan loss (cos³ θ for a planar array with ohmic loss) becomes prohibitive and the phase shifter settles into grating lobe territory.

**Verification Method:** D — Antenna pattern measurement by rotating the antenna panel on a positioner while measuring received signal strength from a fixed CW source at boresight distance.

**Design Element:** HMC647ALP5E phase shifters; beamforming algorithm in STM32H743 firmware.

---

### REQ-SYS-009 — Operating Temperature

**Requirement:** The system shall operate within all specified performance parameters over an ambient temperature range of −10°C to +50°C. Key parameters to maintain are transmit power (REQ-SYS-007) and frequency accuracy (REQ-SYS-001).

**Rationale:** Field operation in Germany spans −10°C (winter) to +40°C ambient (summer direct sun on equipment). The electronics box provides partial thermal buffering.

**Verification Method:** T — Environmental chamber test cycling from −10°C to +50°C while monitoring TX power and VCO centre frequency.

**Design Element:** OCXO thermal stabilisation; PA thermal management; PCB conformal coating for condensation protection.

---

### REQ-SYS-010 — System Update Rate

**Requirement:** The system shall produce and display a range-Doppler map with a minimum update rate of 10 Hz under nominal operation (100-chirp CPI, 1 kHz PRF).

**Rationale:** A 10 Hz update rate (100 ms per frame) is perceptually real-time and sufficient for tracking targets moving at typical vehicle speeds.

**Verification Method:** T — Timestamp processing loop on RPi5; verify ≥10 complete range-Doppler maps per second.

**Design Element:** RPi5 signal processing pipeline; USB/Ethernet data transfer bandwidth.

---

## 3. RF Requirements (REQ-RF)

### REQ-RF-001 — Reference Frequency Accuracy

**Requirement:** The 10 MHz reference oscillator shall maintain a frequency accuracy of ≤±0.01 ppm over the temperature range −10°C to +50°C.

**Rationale:** The PLL multiplies the reference by ~1000 to reach 10 GHz. A ±0.01 ppm reference error corresponds to ±10 kHz at 10 GHz, which is negligible compared to the 100 MHz chirp bandwidth.

**Verification Method:** T — Frequency counter measurement of OCXO output at temperature extremes.

**Design Element:** ABRACON AOCJY-10 OCXO.

---

### REQ-RF-002 — VCO Phase Noise

**Requirement:** The VCO phase noise within the PLL loop bandwidth shall not exceed −80 dBc/Hz at 100 kHz offset from the carrier. Free-running phase noise outside the loop bandwidth shall not exceed −110 dBc/Hz at 1 MHz offset.

**Rationale:** Phase noise sets the radar noise floor for nearby clutter and determines the minimum detectable velocity for slow targets. The HMC733LP6CE specifies −110 dBc/Hz at 1 MHz offset free-running; in-loop noise depends on ADF4159 charge pump and loop filter design.

**Verification Method:** T — Phase noise analyser (R&S FSWP or equivalent) measurement at VCO output.

**Design Element:** HMC733LP6CE VCO; ADF4159 PLL loop filter.

---

### REQ-RF-003 — Chirp Linearity

**Requirement:** The instantaneous frequency deviation from an ideal linear ramp shall not exceed ±500 kHz (0.5% of 100 MHz bandwidth) over the central 90% of the chirp ramp duration.

**Rationale:** Chirp non-linearity causes range sidelobe elevation and range resolution degradation. The ADF4159 uses a digital ramp engine that provides inherently linear frequency steps; the VCO Kv non-linearity must be compensated by the PLL loop.

**Verification Method:** T — Time-frequency analysis of chirp using a fast spectrum analyser or phase-coherent downconversion and spectrogram.

**Design Element:** ADF4159 ramp step size and delay; VCO Kv characterisation; loop filter bandwidth tuning.

---

### REQ-RF-004 — TX Output Power Flatness

**Requirement:** The transmit power at the PA output shall be flat to within ±1 dB across the 10.000–10.100 GHz chirp bandwidth.

**Rationale:** Power variation across the chirp creates amplitude-modulated range sidelobes. The HMC451 gain variation must be characterised and compensated.

**Verification Method:** T — Swept CW power measurement across 10.0–10.1 GHz at PA output.

**Design Element:** HMC451LS6GE PA gain flatness; input power level control.

---

### REQ-RF-005 — TX/RX Isolation

**Requirement:** The isolation between the transmit output and the receive input at the antenna panel shall be ≥50 dB to prevent TX leakage from saturating the RX LNA.

**Rationale:** TX power is +30 dBm. The LNA input compression point is approximately −15 dBm (18 dB gain, output P1dB ~+3 dBm). Isolation ≥45 dB brings TX leakage at LNA input to −15 dBm; ≥50 dB provides 5 dB margin. This isolation is achieved by the spatial separation of TX and RX arrays plus the PE8316 circulator/isolator in the TX path.

**Verification Method:** T — CW injection at TX port; measure power at RX port with VNA.

**Design Element:** PE8316 circulator (20 dB isolation); physical TX/RX array separation (additional ≥30 dB spatial isolation estimated from aperture geometry at 10 GHz).

---

### REQ-RF-006 — LNA Noise Figure

**Requirement:** Each receive chain LNA shall have a noise figure of ≤2.0 dB at the operating frequency 10.0–10.1 GHz and at temperatures up to +50°C.

**Rationale:** The HMC1040LP4E specifies 1.5 dB NF at room temperature; a 0.5 dB margin is allowed for temperature degradation and PCB trace losses ahead of the LNA input.

**Verification Method:** T — Noise figure analyser (Y-factor method) measurement of each LNA chain.

**Design Element:** HMC1040LP4E LNA; PCB layout (minimal trace between antenna feed and LNA input).

---

### REQ-RF-007 — LNA Gain

**Requirement:** The receive chain LNA shall provide ≥16 dB gain at 10.0–10.1 GHz to ensure the LNA noise figure dominates the cascaded system noise figure ahead of the combiner and mixer.

**Rationale:** The HMC1040 specifies 18 dB gain. Friis formula: F_sys = F_LNA + (F_combiner − 1)/G_LNA. At G_LNA = 63 (18 dB), even a combiner loss of 16 dB (Factor 40) contributes only 40/63 ≈ 0.6 to F_sys, well controlled.

**Verification Method:** T — Gain measurement using VNA or signal generator/power meter.

**Design Element:** HMC1040LP4E LNA; bias circuitry.

---

### REQ-RF-008 — Mixer Conversion Loss

**Requirement:** The RX mixer (HMC213B) conversion loss shall be ≤8 dB at LO power of +10 dBm ±2 dB over the 10.0–10.1 GHz RF input range, with IF output at frequencies ≤1 MHz.

**Rationale:** The HMC213B specifies 6 dB typical conversion loss with 10 dBm LO. The IF beat frequency for targets within 150 m ranges is below 100 kHz, well within the 5 GHz IF bandwidth of the HMC213B.

**Verification Method:** T — Two-tone measurement with VNA port 1 as RF (10 GHz), port 2 as LO (10 GHz), spectrum analyser on IF port.

**Design Element:** HMC213B mixer; LO power splitter from VCO/PA chain.

---

### REQ-RF-009 — Spurious Emissions

**Requirement:** Spurious emissions from the transmitter, measured at the TX antenna port, shall be ≤−50 dBc at any frequency other than the intended chirp carrier and its harmonics below −30 dBc.

**Rationale:** German amateur radio station operation must not cause harmful interference to other services. PLL reference spurs and VCO harmonics must be filtered. The 2nd harmonic at 20 GHz is outside amateur allocations; a low-pass filter after the PA is required.

**Verification Method:** T — Spectrum analyser measurement at TX antenna port, bandwidth 1–20 GHz.

**Design Element:** Low-pass filter after PA (fc ≈ 12 GHz); ADF4159 charge pump spur optimisation.

---

### REQ-RF-010 — Phase Shifter Resolution

**Requirement:** The phase shifter shall provide 6-bit resolution (64 discrete phase states) with an LSB phase step of 5.625° ±0.5° per bit, allowing phase settings from 0° to 354.375° in 5.625° increments.

**Rationale:** 6-bit phase resolution produces quantisation sidelobes of approximately −26 dB in the array pattern (20·log10(1/64) ≈ −36 dBc, reduced by statistical effects to approximately −26 dB for practical arrays), acceptable for this experimental application.

**Verification Method:** T — VNA measurement of insertion phase vs. SPI control word for each of 64 states for representative sample of HMC647A devices.

**Design Element:** HMC647ALP5E phase shifter; SPI control from STM32H743.

---

### REQ-RF-011 — Phase Shifter Settling Time

**Requirement:** The phase shifter shall settle to the commanded phase state within 50 ns of the SPI latch signal falling edge, allowing chirp-to-chirp beam steering updates at 1 kHz PRF.

**Rationale:** The HMC647A specifies a switching speed of <10 ns. At 1 ms chirp period and 50 ns settling, the effective duty cycle loss for beam reconfiguration is <0.005%, negligible.

**Verification Method:** T — Time-domain measurement of RF phase step response using a phase discriminator and oscilloscope.

**Design Element:** HMC647ALP5E phase shifter; SPI clock rate ≥10 MHz from STM32H743.

---

### REQ-RF-012 — Phase Shifter Insertion Loss

**Requirement:** The HMC647ALP5E insertion loss shall not exceed 8 dB at 10 GHz, and the insertion loss variation across all 64 phase states shall not exceed ±1.5 dB (amplitude ripple).

**Rationale:** Amplitude ripple across phase states causes beam pattern asymmetry and sidelobe elevation. The HMC647A specifies 6 dB typical insertion loss and ±1 dB amplitude variation.

**Verification Method:** T — VNA S21 measurement for all 64 states on 5 representative devices; record max variation.

**Design Element:** HMC647ALP5E phase shifter.

---

### REQ-RF-013 — Impedance Matching

**Requirement:** All RF ports (VCO output, PA input/output, LNA input/output, mixer RF/LO/IF, phase shifter input/output) shall be matched to 50 Ω with return loss ≥10 dB (VSWR ≤1.92:1) across the 10.0–10.1 GHz operating band.

**Rationale:** Impedance mismatches cause signal reflections, power loss, and potential oscillation in cascaded amplifiers. Each MMIC datasheet specifies 50 Ω matching conditions.

**Verification Method:** T — VNA S11 measurement at each port under operational bias conditions.

**Design Element:** PCB microstrip matching networks; MMIC bias circuits.

---

### REQ-RF-014 — Beam Steering Scan Loss

**Requirement:** The array gain reduction at ±45° scan angle relative to boresight shall not exceed 6 dB.

**Rationale:** For a uniform planar array, gain reduction at scan angle θ is approximately −10·log10(cos(θ)) per axis for element pattern effects, plus grating lobe and impedance mismatch contributions. At ±45°, cos(45°) = 0.707, yielding approximately −3 dB per axis or −6 dB combined for 2D scan.

**Verification Method:** A — Array factor calculation; D — antenna range measurement at ±45° scan.

**Design Element:** Antenna array element pattern (patch); phase shifter settings.

---

### REQ-RF-015 — Cross-Port Isolation of PA

**Requirement:** The HMC451LS6GE PA shall maintain output-to-input isolation ≥20 dB across the 10.0–10.1 GHz band to prevent oscillation via the PCB layout feedback path.

**Rationale:** High-gain amplifiers (28 dB) can oscillate if the reverse isolation (S12) is insufficient and board layout provides a feedback path. The HMC451 specifies >20 dB isolation.

**Verification Method:** T — VNA S12 measurement of assembled PA circuit on PCB.

**Design Element:** HMC451LS6GE; PCB layout ground via isolation.

---

## 4. Antenna Requirements (REQ-ANT)

### REQ-ANT-001 — Element Type and Substrate

**Requirement:** Antenna elements shall be rectangular microstrip patch radiators fabricated on Rogers RO4003C substrate, thickness 0.508 mm, relative permittivity εr = 3.55 ±0.05, loss tangent tan δ ≤ 0.0027 at 10 GHz.

**Rationale:** RO4003C is an industry-standard, low-loss, stable microwave laminate available in standard panel sizes. Its well-characterised electrical properties allow accurate antenna design using analytical models and EM simulation.

**Verification Method:** I — Manufacturer certificate of conformance; T — dielectric property measurement by resonator method.

**Design Element:** Antenna PCB fabrication; Rogers RO4003C laminate.

---

### REQ-ANT-002 — Patch Resonant Frequency

**Requirement:** Each patch antenna element shall resonate at 10.050 GHz ±50 MHz (S11 ≤ −15 dB at 10.050 GHz), as the centre of the 10.000–10.100 GHz chirp sweep.

**Rationale:** Patch dimensions of 13.8 mm × 13.8 mm on RO4003C (0.508 mm, εr = 3.55) give a resonant frequency of approximately 10.05 GHz based on the effective permittivity and fringing field model.

**Verification Method:** T — VNA S11 measurement of individual patch element with reference ground plane.

**Design Element:** Patch dimensions (13.8 mm × 13.8 mm); substrate thickness (0.508 mm).

---

### REQ-ANT-003 — Element Spacing

**Requirement:** The element spacing in both row and column directions shall be 15 mm ±0.2 mm (λ/2 at 10 GHz, where λ = 30 mm).

**Rationale:** Half-wavelength spacing is the standard design point for phased arrays, providing a 3 dB beamwidth consistent with REQ-SYS-008 (22° per axis for 4 elements) without grating lobes for scan angles up to ±90°.

**Verification Method:** I — Optical measurement of fabricated PCB element centres; gerber file inspection.

**Design Element:** Antenna PCB layout; KiCad footprint placement.

---

### REQ-ANT-004 — Array Size and Configuration

**Requirement:** Each of the TX and RX antenna arrays shall be configured as a 4×4 planar array (4 elements per row, 4 rows). The total TX aperture shall be 45 mm × 45 mm (3 element spacings per axis). The same dimensions apply to the RX array.

**Rationale:** A 4×4 array provides 16×16 = 256 two-way array factor, corresponding to approximately 48 dBi combined two-way gain (24 dBi each way), giving adequate EIRP for multi-kilometre detection range.

**Verification Method:** I — PCB layout inspection; T — antenna pattern measurement.

**Design Element:** Antenna PCB layout; feed network topology.

---

### REQ-ANT-005 — TX Array Gain

**Requirement:** The TX antenna array shall achieve a realised gain of ≥20 dBi at boresight at 10.050 GHz, accounting for impedance mismatch, ohmic loss in feed network, and patch radiation efficiency.

**Rationale:** Theoretical gain of a 4×4 array with λ/2 spacing is 10·log10(16·4π/λ²·0.01×0.01) ≈ 10·log10(16) + 10·log10(4π·A/λ²) for directivity ≈ 24 dBi. Deducting 2 dB for ohmic and mismatch losses gives a minimum requirement of 22 dBi (design target) with 20 dBi as the minimum passing criterion.

**Verification Method:** T — Antenna range gain measurement using calibrated gain standard horn at 10 GHz.

**Design Element:** 4×4 TX patch array; corporate feed Wilkinson divider network.

---

### REQ-ANT-006 — RX Array Gain

**Requirement:** The RX antenna array shall achieve a realised gain of ≥20 dBi at boresight at 10.050 GHz, under the same conditions as REQ-ANT-005.

**Verification Method:** T — Same method as REQ-ANT-005, applied to RX array.

**Design Element:** 4×4 RX patch array; corporate feed Wilkinson combiner network.

---

### REQ-ANT-007 — Antenna Beamwidth

**Requirement:** The 3 dB one-way beamwidth of each array (TX or RX) shall be 20°–25° in both azimuth and elevation at boresight, consistent with a 4-element, half-wavelength-spaced uniform linear array.

**Rationale:** Theoretical 3 dB beamwidth = 0.886·λ/(N·d) = 0.886/(4·0.5) = 0.443 rad ≈ 25.4° for a 4-element ULA at λ/2 spacing. In practice the patch element pattern narrows this slightly.

**Verification Method:** T — Antenna pattern measurement in azimuth and elevation planes.

**Design Element:** Antenna array geometry; element pattern.

---

### REQ-ANT-008 — Port Impedance

**Requirement:** The corporate feed network port impedance (at the SMA connector feeding each array) shall be 50 Ω ±5 Ω at 10.050 GHz, with return loss ≥15 dB.

**Rationale:** The RF chain is designed around 50 Ω transmission line impedance throughout. The Wilkinson divider output impedance is transformed to 50 Ω at each stage.

**Verification Method:** T — VNA S11 measurement at antenna SMA port.

**Design Element:** Wilkinson divider microstrip line dimensions; substrate εr.

---

### REQ-ANT-009 — TX/RX Cross-Panel Isolation

**Requirement:** The isolation between the TX array SMA feed port and the RX array SMA feed port, measured on the antenna panel with both arrays present, shall be ≥30 dB across 10.0–10.1 GHz.

**Rationale:** Combined with the PA-to-LNA isolation from PE8316 circulator (20 dB) and the combiner/divider network insertion losses, total TX-to-LNA-input isolation needs to be ≥50 dB (REQ-RF-005). The antenna panel contributes ≥30 dB from the physical separation and cross-polar orientation of TX and RX patches.

**Verification Method:** T — VNA S21 measurement from TX SMA port to RX SMA port on assembled antenna panel.

**Design Element:** TX and RX array physical separation (≥50 mm between array edges); absorber barrier between arrays if needed.

---

### REQ-ANT-010 — Cross-Polarisation Isolation

**Requirement:** The co-polar to cross-polar isolation of each patch element shall be ≥20 dB at boresight, measured at 10.050 GHz.

**Rationale:** Low cross-polarisation ensures clean beam pattern and reduces ambiguous target returns from cross-pol reflections.

**Verification Method:** T — Pattern measurement with co-polar and cross-polar reference horn; record null-to-peak ratio.

**Design Element:** Patch geometry; symmetric feed point placement.

---

## 5. Digital and Control Requirements (REQ-DIG)

### REQ-DIG-001 — ADC Resolution

**Requirement:** The analogue-to-digital converter shall provide ≥14 effective number of bits (ENOB) at the IF signal input frequency range of DC to 500 kHz, with a full-scale input range of ±4.096 V (configurable).

**Rationale:** The ADS8661IRGAT is a 16-bit SAR ADC with specified ENOB of ≥14.5 bits at low input frequencies. 14 ENOB provides a noise floor of 6.02×14 + 1.76 = 86.04 dBFS, sufficient to resolve target returns at −60 dBFS above noise.

**Verification Method:** T — FFT test: apply single-tone sine wave at 10 kHz; compute SINAD from FFT output.

**Design Element:** ADS8661IRGAT ADC; anti-aliasing filter on IF input.

---

### REQ-DIG-002 — ADC Sample Rate

**Requirement:** The ADC shall operate at a sample rate of 1 MSPS ±1% (1,000,000 samples per second ±10,000 sps), synchronised to the STM32H743 SPI clock.

**Rationale:** 1 MSPS provides a Nyquist bandwidth of 500 kHz, sufficient to capture beat frequencies corresponding to targets within 150 m at 100 MHz chirp bandwidth. Synchronisation with the chirp ramp timing ensures coherent processing.

**Verification Method:** T — Logic analyser measurement of SPI CLK frequency with ADS8661 in continuous conversion mode.

**Design Element:** ADS8661IRGAT; STM32H743 SPI peripheral clock divider configuration.

---

### REQ-DIG-003 — MCU Clock Speed

**Requirement:** The STM32H743ZIT6 shall operate at its maximum rated CPU frequency of 480 MHz using the external 25 MHz crystal or internal PLL, with all performance-critical peripherals (SPI, DMA, USB) enabled.

**Rationale:** 480 MHz provides sufficient DMIPS throughput to manage 6 SPI buses for 32 phase shifters plus ADC data, PLL control, and USB data forwarding simultaneously in a real-time RTOS context.

**Verification Method:** T — Oscilloscope measurement of SysTick timer period; verify CPU clock via debugger register.

**Design Element:** STM32H743ZIT6; external 25 MHz crystal oscillator; PLL configuration in STM32CubeIDE.

---

### REQ-DIG-004 — SPI Bus Speed for Phase Shifters

**Requirement:** The SPI interfaces controlling the HMC647ALP5E phase shifters shall operate at ≥10 Mbit/s to ensure all 32 phase shifters (TX and RX arrays) can be updated within 100 μs (one-tenth of the chirp period).

**Rationale:** Each HMC647A requires a 6-bit SPI word plus 2 bits framing = 8 bits. 32 phase shifters × 8 bits = 256 bits. At 10 Mbit/s, 256 bits requires 25.6 μs. With overhead, update time ≤100 μs is achievable. The STM32H743 SPI peripheral supports up to 150 Mbit/s.

**Verification Method:** T — Logic analyser measurement of SPI CLK frequency during phase-shifter update routine.

**Design Element:** STM32H743 SPI1–SPI6 configuration; SPI daisy-chain or parallel bus topology for phase shifters.

---

### REQ-DIG-005 — Phase Shifter Update Latency

**Requirement:** The time from issuance of a new beam direction command by the processing computer to completion of phase-shifter latch on all 32 devices shall be ≤200 μs, including SPI transfer time and GPIO latch pulse generation.

**Rationale:** At 1 kHz PRF (1 ms chirp period), a 200 μs update latency allows beam direction change between consecutive chirps, enabling electronically scanned operation.

**Verification Method:** T — Logic analyser trace from Ethernet command receipt to last phase shifter LE (latch enable) pulse assertion.

**Design Element:** STM32H743 firmware; SPI DMA configuration; phase shifter SPI topology.

---

### REQ-DIG-006 — ADC DMA Buffer

**Requirement:** The STM32H743 shall implement double-buffered DMA transfer of ADC samples, each buffer holding exactly 1000 samples (one chirp period), allowing the CPU to process one buffer while the DMA fills the other.

**Rationale:** Double-buffering prevents DMA buffer overruns at 1 MSPS. Buffer size of 1000 samples corresponds to exactly one 1 ms chirp at 1 MSPS.

**Verification Method:** T — Debugger observation of DMA buffer fill; verify no overrun flag in STM32 DMA status register over 10,000 consecutive chirps.

**Design Element:** STM32H743 DMA2 or MDMA controller; SRAM buffer allocation.

---

### REQ-DIG-007 — Data Transfer to Processing Computer

**Requirement:** Raw ADC data shall be transferred from STM32H743 to the RPi5 at a sustained rate of ≥2 MB/s to support 1 MSPS × 16-bit = 2 MB/s raw data throughput. The interface shall be USB 2.0 High Speed (480 Mbit/s) or 100BASE-TX Ethernet.

**Rationale:** USB 2.0 HS provides 480 Mbit/s theoretical maximum; practical CDC or bulk transfer rates of 25–40 MB/s are well above the 2 MB/s requirement.

**Verification Method:** T — Sustained data transfer test; measure throughput with `iperf` (Ethernet) or USB bulk transfer benchmark.

**Design Element:** STM32H743 USB HS peripheral (with ULPI PHY) or Ethernet MAC; RPi5 USB 3.0 or Ethernet port.

---

### REQ-DIG-008 — Chirp Synchronisation

**Requirement:** The start of each chirp ramp (ADF4159 ramp trigger) shall be synchronised to the ADC sampling start with a jitter of ≤100 ns to ensure coherent processing across the CPI.

**Rationale:** Chirp-to-ADC timing jitter causes phase errors across the CPI, elevating Doppler sidelobes and degrading velocity resolution. 100 ns jitter at 10 GHz corresponds to 1 rad phase error, which is tolerable with digital compensation.

**Verification Method:** T — Oscilloscope measurement of ADF4159 TXDATA pin (ramp start) vs. ADC CS (conversion start) edge timing across 1000 chirps.

**Design Element:** STM32H743 timer-based synchronisation; TXDATA GPIO to ADF4159; ADC CS GPIO.

---

### REQ-DIG-009 — Firmware Update Mechanism

**Requirement:** The STM32H743 firmware shall be updateable over USB using the STM32 built-in DFU (Device Firmware Upgrade) bootloader without requiring a JTAG/SWD debugger connection in the field.

**Rationale:** Field firmware updates are required for bug fixes and parameter changes without disassembly of the electronics box.

**Verification Method:** D — Demonstrate firmware update via USB DFU using STM32CubeProgrammer on a field laptop.

**Design Element:** STM32H743 USB FS peripheral; BOOT0 pin accessible from front panel; DFU bootloader activation logic.

---

### REQ-DIG-010 — Real-Time Operating System

**Requirement:** The STM32H743 firmware shall run under FreeRTOS with task priorities assigned to ensure ADC DMA interrupt handling and SPI phase-shifter update complete with deterministic latency ≤50 μs from interrupt to execution.

**Rationale:** Deterministic timing is essential for coherent radar operation. FreeRTOS priority scheduling prevents lower-priority tasks (USB data forwarding, configuration parsing) from blocking time-critical ADC and SPI operations.

**Verification Method:** T — FreeRTOS trace (Tracealyzer or SystemView) measurement of interrupt-to-task-run latency distribution over 10,000 events.

**Design Element:** STM32H743 FreeRTOS port; task priority configuration in main.c.

---

## 6. Power Requirements (REQ-PWR)

### REQ-PWR-001 — Input Voltage

**Requirement:** The system shall operate from a 24 V DC input voltage in the range 22.0–26.0 V DC, representing ±10% around the nominal 24 V.

**Rationale:** 24 V is a standard vehicle auxiliary and industrial DC power voltage. The ±10% range accommodates discharged (22 V LiFePO4) and fully charged (29.2 V LiFePO4 at 4-cell) battery states; the 26 V upper limit is set by DC-DC converter ratings.

**Verification Method:** T — Power supply test at 22 V, 24 V, and 26 V; verify system operation and measure output rail voltages.

**Design Element:** LT8612 and LT8607 DC-DC converters; input undervoltage protection circuit.

---

### REQ-PWR-002 — Input Current Limit

**Requirement:** The maximum input current drawn from the 24 V supply shall not exceed 8.0 A DC under any operational condition, including worst-case duty cycle with all RF stages active.

**Rationale:** The total power budget is 192 W (24 V × 8 A). Breakdown: PA at +30 dBm (HMC451, ~400 mA at 5 V drain = 2 W), VCO (HMC733, ~180 mA at 5 V = 0.9 W), 32 × HMC647A phase shifters (~50 mA at 5 V each = 8 W total), 16 × HMC1040 LNAs (~180 mA at 5 V = 14.4 W), MCU + RPi5 (~25 W combined). Total ≈ 80–120 W typical; 192 W is the hard ceiling.

**Verification Method:** T — Clamp meter measurement at 24 V input connector during maximum load operation.

**Design Element:** System power budget; DC-DC converter sizing.

---

### REQ-PWR-003 — 5 V Rail

**Requirement:** The 5 V output rail (generated by LT8612) shall maintain 5.0 V ±2% (4.9–5.1 V) at output currents up to 5 A. Output voltage ripple shall not exceed 50 mV peak-to-peak at 1 MHz switching frequency.

**Rationale:** The 5 V rail powers all RF MMICs (VCO, PA, LNA, phase shifters). Excessive ripple couples into the VCO tune voltage via the RF power supply, causing frequency modulation and elevated phase noise.

**Verification Method:** T — DMM voltage measurement at 5 A load; oscilloscope measurement of ripple with 20 MHz bandwidth.

**Design Element:** LT8612 DC-DC converter; output LC filter; bulk capacitance (470 μF electrolytic + 10 μF MLCC per RF device).

---

### REQ-PWR-004 — 3.3 V Rail

**Requirement:** The 3.3 V output rail (generated by LT8607) shall maintain 3.3 V ±2% (3.234–3.366 V) at output currents up to 3 A. Ripple shall not exceed 30 mV peak-to-peak.

**Rationale:** 3.3 V powers the STM32H743 I/O and logic, ADF4159, and ADS8661 ADC. ADC accuracy is sensitive to supply ripple; 30 mV corresponds to 30 mV/4096 mV ≈ 7.3 LSB at 16-bit full-scale, which must be reduced by decoupling at the ADC VCC pin.

**Verification Method:** T — Same measurement method as REQ-PWR-003.

**Design Element:** LT8607 DC-DC converter; ADC power supply decoupling (100 nF + 10 μF MLCC at AVDD pin).

---

### REQ-PWR-005 — ±5 V RF Bias Rail

**Requirement:** The ±5 V rails (generated by TPS65133) shall maintain ±5.0 V ±5% at currents up to ±1 A. Ripple shall not exceed 20 mV peak-to-peak on either rail.

**Rationale:** Some MMIC bias circuits require a negative supply for gate voltage. The TPS65133 provides regulated ±5 V from a single inductor charge pump architecture. The RF bias rails require exceptionally low ripple to avoid frequency pulling of the VCO.

**Verification Method:** T — Oscilloscope measurement at TPS65133 VOUT+ and VOUT− pins under nominal load.

**Design Element:** TPS65133 regulator; RF bias filter network (ferrite bead + MLCC Pi filter on each supply to each MMIC).

---

### REQ-PWR-006 — Power Sequencing

**Requirement:** At system power-on, the 5 V rail shall be stable before 3.3 V logic rails power-up. The RF MMICs shall be biased (gate/drain) only after the STM32H743 has completed initialisation and asserted a PA_ENABLE GPIO signal. At power-down, the PA_ENABLE signal shall be de-asserted before removing the 5 V supply.

**Rationale:** Out-of-sequence biasing can destroy GaAs pHEMT devices (HMC451 PA). The gate must be biased before the drain voltage is applied; the STM32H743 controls the drain enable via GPIO-controlled load switch.

**Verification Method:** T — Oscilloscope multi-channel capture of 5 V, 3.3 V, PA drain voltage, and STM32 PA_ENABLE GPIO at power-on and power-off transitions.

**Design Element:** STM32H743 GPIO PA_ENABLE; TPS2110 load switch for PA drain; power-on reset sequencer.

---

### REQ-PWR-007 — Input Protection

**Requirement:** The 24 V input shall be protected against reverse polarity (−24 V) and overvoltage up to +30 V transients without permanent damage to any system component.

**Rationale:** Field power connections (Anderson PowerPole) can be reversed by untrained users. Vehicle alternator load-dump transients can exceed 30 V for tens of milliseconds.

**Verification Method:** T — Apply −24 V for 5 seconds; remove and verify system powers up correctly. Apply 30 V transient (100 ms) via surge generator; verify no damage.

**Design Element:** P-channel MOSFET reverse-polarity protection; TVS diode (SMAJ30A) across input for overvoltage clamping.

---

### REQ-PWR-008 — Conversion Efficiency

**Requirement:** The combined DC-DC conversion efficiency from 24 V input to all regulated output rails (5 V, 3.3 V, ±5 V) shall be ≥85% under nominal load conditions.

**Rationale:** At 120 W typical load with 85% efficiency, input power is 141 W; 21 W is dissipated as heat in the converters and must be removed by the aluminium enclosure. Efficiency below 85% would require additional heatsinking.

**Verification Method:** T — Measure input power (V_in × I_in) and output powers (sum of V_out × I_out for each rail); compute η = P_out/P_in.

**Design Element:** LT8612, LT8607, TPS65133 converter selection; inductor and capacitor quality (DCR, ESR).

---

## 7. Mechanical Requirements (REQ-MEC)

### REQ-MEC-001 — Enclosure Dimensions

**Requirement:** The electronics enclosure (excluding antenna panel) shall not exceed 300 mm (L) × 200 mm (W) × 100 mm (H) external dimensions, fabricated from 3 mm wall aluminium alloy (6061-T6 or equivalent).

**Rationale:** This envelope fits in a standard field case (Pelican 1510 or equivalent) alongside the antenna panel, cabling, and accessories, allowing single-person transport.

**Verification Method:** I — Dimensional measurement with calipers.

**Design Element:** Mechanical enclosure design; PCB stack planning.

---

### REQ-MEC-002 — Antenna Panel Dimensions

**Requirement:** The antenna panel shall not exceed 200 mm (W) × 120 mm (H) × 5 mm (D, including connectors and standoffs). The panel shall be flat within 0.5 mm across its full area.

**Rationale:** Flatness is critical for antenna pattern integrity; a 0.5 mm bow at 10 GHz corresponds to λ/60 variation, negligible for the 22° beamwidth application.

**Verification Method:** I — Flatness measurement on surface plate; caliper measurement.

**Design Element:** Rogers RO4003C PCB; aluminium backing plate.

---

### REQ-MEC-003 — Tripod Mount

**Requirement:** The system shall include a standard 3/8-16 UNC threaded female insert (stainless steel, minimum depth 10 mm) located at the centre of mass of the electronics box ±25 mm, for direct attachment to a standard photo-tripod head.

**Rationale:** Standard 3/8-16 UNC is universal for tripods supporting loads over 3 kg, compatible with heavy-duty video heads and survey tripods.

**Verification Method:** I — Thread gauge measurement; load test with 10 kg (2× design margin).

**Design Element:** Enclosure base plate; stainless steel threaded insert (M8-to-3/8-16 adapter available as alternative).

---

### REQ-MEC-004 — System Weight

**Requirement:** The total system weight (electronics box + antenna panel + interconnect cables) shall not exceed 6 kg.

**Rationale:** Single-operator deployment requires a manageable carry weight. The 5 kg design target has a 1 kg margin to 6 kg requirement.

**Verification Method:** I — Weigh assembled system on calibrated scale.

**Design Element:** Aluminium enclosure wall thickness; PCB material choice; cable selection.

---

### REQ-MEC-005 — Connector Types and Locations

**Requirement:** The following connectors shall be provided on the enclosure rear panel in the positions shown in the mechanical drawing: (a) 1× Anderson PowerPole PP45 for 24 V DC input, (b) 2× SMA female (TX and RX RF test ports), (c) 1× USB Type-C (STM32H743 USB), (d) 1× RJ-45 Ethernet (RPi5), (e) 1× 4-pin M8 circular (CAN bus / spare digital I/O). Front panel shall have: 1× rocker power switch rated 15 A 30 V DC, 3× LED indicators (Power, RF Active, Fault/Status).

**Rationale:** All external connections on the rear panel prevent accidental disconnection when the unit is mounted on a tripod. LEDs on the front panel are visible to the operator standing in front of the system.

**Verification Method:** I — Visual inspection; connector mating test.

**Design Element:** Rear panel machining drawing; front panel silk-screen legend.

---

### REQ-MEC-006 — Ingress Protection

**Requirement:** The electronics enclosure shall achieve a minimum IP54 rating (dust protected, splash resistant from all directions) per IEC 60529. The antenna panel, mounted externally, shall be coated with a conformal coat rated for outdoor exposure (IPC-CC-830B compliant).

**Rationale:** Field use in Germany includes operation in rain and dusty environments. IP54 provides adequate protection without the cost and complexity of a fully sealed IP67 enclosure.

**Verification Method:** T — IP54 water spray test per IEC 60529 §14.2.3; verify no ingress into electronics cavity.

**Design Element:** Enclosure O-ring seal; cable gland for umbilical; conformal coating of antenna PCB.

---

### REQ-MEC-007 — Thermal Management

**Requirement:** The PA (HMC451LS6GE) junction temperature shall not exceed 125°C at +50°C ambient with maximum continuous TX operation. The enclosure internal temperature shall not exceed +70°C under any operating condition.

**Rationale:** The HMC451 maximum junction temperature is 150°C. At 28 dB gain and +30 dBm output, the PA dissipates approximately 3 W. With a 3 W device-to-case thermal resistance of 15°C/W and case-to-ambient of 5°C/W, junction temperature at 50°C ambient is 50 + 3×(15+5) = 110°C, within limit.

**Verification Method:** T — Thermal camera measurement of PA package at +50°C ambient during 30-minute continuous operation.

**Design Element:** PA PCB thermal via array; aluminium chassis heatsink contact; thermal interface pad (Bergquist GP3000).

---

### REQ-MEC-008 — Cable Management

**Requirement:** The umbilical cable bundle connecting the electronics box to the antenna panel shall be ≤1.5 m in length, terminated with SMA connectors (RF) and a multi-pin connector (power, SPI, control) at each end. Minimum bend radius shall be 30 mm for SMA cables at 10 GHz.

**Rationale:** Excessive cable length introduces insertion loss (0.5 dB/m for RG-405 semi-rigid at 10 GHz). 1.5 m is sufficient for tripod deployment without excessive loss.

**Verification Method:** I — Physical measurement; VNA insertion loss measurement of assembled cable set.

**Design Element:** RF cable selection (RG-405 or Flexiform 047); cable harness design.

---

## 8. Software Requirements (REQ-SW)

### REQ-SW-001 — Real-Time Control Firmware (STM32)

**Requirement:** The STM32H743 firmware shall implement all radar control functions including: ADF4159 SPI initialisation and chirp ramp configuration, HMC647A phase-shifter SPI update, ADS8661 ADC SPI sampling at 1 MSPS, chirp start/stop synchronisation, and USB/Ethernet data forwarding to RPi5.

**Verification Method:** D — Functional demonstration of all control outputs while monitoring with logic analyser.

**Design Element:** STM32H743 firmware; FreeRTOS task design.

---

### REQ-SW-002 — FMCW Signal Processing Pipeline

**Requirement:** The processing software on RPi5 shall implement the following signal chain: (1) receive raw ADC samples from STM32, (2) apply Hann window per chirp, (3) compute 1024-point range FFT per chirp, (4) stack 100 range FFT outputs into a 100×512 range-Doppler matrix, (5) apply Hann window along slow-time axis, (6) compute 128-point Doppler FFT across slow-time, producing a range-Doppler map.

**Verification Method:** T — Inject synthetic target signal; verify correct range bin and Doppler bin detection.

**Design Element:** Python signal processing module (numpy.fft); data receiver thread.

---

### REQ-SW-003 — CFAR Detection

**Requirement:** The software shall implement Cell-Averaging CFAR (CA-CFAR) detection in the range-Doppler map with configurable guard cells (default 2) and reference cells (default 16), and a configurable probability of false alarm (PFA, default 10⁻⁴).

**Verification Method:** T — Inject simulated target at SNR = 13 dB; verify detection rate ≥90% and false alarm rate ≤0.01% in 10,000 test frames.

**Design Element:** Python CFAR module; configurable parameters in config.yaml.

---

### REQ-SW-004 — Graphical User Interface

**Requirement:** The processing software shall provide a real-time GUI displaying: (a) range-Doppler power map (colour-mapped dB scale), (b) detected target list (range, velocity, bearing), (c) beam direction indicator, (d) system status (RF active, temperature, power rails status), and (e) controls for beam steering direction, CFAR threshold, and display range scale.

**Verification Method:** D — Visual demonstration of GUI with live data or replay of recorded data file.

**Design Element:** Python/PyQt6 GUI; Matplotlib/pyqtgraph range-Doppler plot widget.

---

### REQ-SW-005 — Data Logging

**Requirement:** The software shall log raw ADC samples (or processed range-Doppler maps, selectable) to disk in HDF5 format with timestamps, system configuration, and GPS coordinates (if external GPS receiver is connected via USB). Log file size shall not exceed 2 GB per hour at 1 MSPS full-raw logging.

**Rationale:** Raw data logging enables offline reprocessing with improved algorithms without requiring a new measurement campaign.

**Verification Method:** T — Run system for 1 hour in raw logging mode; verify file size ≤2 GB and correct data format using h5py.

**Design Element:** Python logging module; h5py library; configurable logging mode in config.yaml.

---

### REQ-SW-006 — Beamforming Control

**Requirement:** The software shall provide a beamforming control API that accepts a target direction (azimuth, elevation in degrees) and computes the required 32 phase-shifter control words using the planar array steering vector equation, then transmits the control words to the STM32H743 over the control interface.

**Verification Method:** T — Command beam to known angles (0°, ±22.5°, ±45°); verify received signal strength peaks at expected angles using a fixed CW test source.

**Design Element:** Python beamforming module; TCP socket command interface to STM32.

---

### REQ-SW-007 — Calibration Routine

**Requirement:** The software shall include an antenna array calibration routine that: (a) sweeps beam directions in 5° steps, (b) measures received signal strength from a known calibration reflector or CW source at a fixed known location, (c) computes per-element amplitude and phase correction coefficients, and (d) stores coefficients in a calibration file applied during normal operation.

**Verification Method:** D — Run calibration routine with corner reflector at 50 m range; verify beam pattern improvement vs. uncalibrated.

**Design Element:** Python calibration module; calibration coefficient storage (JSON or HDF5).

---

### REQ-SW-008 — Configuration Management

**Requirement:** All system operating parameters (frequency, chirp bandwidth, PRF, CPI length, CFAR thresholds, beam scan pattern, logging options) shall be stored in a human-readable YAML configuration file loadable at startup and modifiable without recompiling firmware or software.

**Verification Method:** I — Inspect config.yaml; D — modify parameter and verify changed behaviour.

**Design Element:** config.yaml; Python configparser module; STM32 parameter upload command.

---

### REQ-SW-009 — Station Identification Automation

**Requirement:** The firmware shall implement an automated station identification interrupt: at every 10-minute interval, the system shall briefly (≤5 seconds) transmit the operator's callsign in Morse code (CW) at the current operating frequency, then resume radar operation.

**Rationale:** AFuV 2017 §14 requires station identification at maximum 10-minute intervals. Automating this ensures compliance without operator action.

**Verification Method:** D — Run system for 15 minutes; verify CW identification burst transmitted at minute 10; verify callsign is correct (configurable in config.yaml).

**Design Element:** STM32H743 FreeRTOS timer task; CW keyer function; callsign string in config.

---

### REQ-SW-010 — Remote Control Interface

**Requirement:** The RPi5 shall expose a TCP/IP control interface (port 5555) allowing a remote laptop to send beam steering commands, request system status, start/stop recording, and query the detected target list. The interface shall use a simple JSON command-response protocol.

**Verification Method:** T — Connect via `netcat` from remote laptop; send JSON command {"cmd": "beam", "az": 30.0, "el": 0.0}; verify system responds with {"status": "ok"} and beam updates.

**Design Element:** Python asyncio TCP server on RPi5; JSON command parser.

---

### REQ-SW-011 — Software Licence

**Requirement:** All processing software and firmware source code shall be released under an OSI-approved open-source licence. Firmware shall be licensed under GPL-3.0 or MIT. Processing software shall be licensed under MIT or Apache-2.0.

**Verification Method:** I — SPDX licence header in all source files; LICENSE file in repository root.

**Design Element:** GitHub/GitLab repository; SPDX header template.

---

### REQ-SW-012 — Software Build Reproducibility

**Requirement:** The processing software shall have a reproducible build environment specified by a requirements.txt (Python pip) and a Dockerfile (for RPi5 deployment), ensuring consistent library versions across installations.

**Verification Method:** D — Fresh build in Docker container from repository; verify all tests pass.

**Design Element:** requirements.txt; Dockerfile; GitHub Actions CI pipeline.

---

## 9. Regulatory Requirements (REQ-REG)

### REQ-REG-001 — Frequency Band Compliance

**Requirement:** The transmitter shall operate exclusively in the 10.000–10.100 GHz range as specified in REQ-SYS-001. Spurious emissions outside the 10.000–10.500 GHz amateur band shall be suppressed per REQ-RF-009.

**Verification Method:** T — Spectrum analyser measurement.

**Design Element:** ADF4159 frequency limits programmed in firmware; output low-pass filter.

---

### REQ-REG-002 — Transmitter Output Power Compliance

**Requirement:** The transmitter output power at the PA output shall not exceed +47.75 dBm (75 W PEP) under any operating condition, in compliance with AFuV 2017 Anlage 1 for the 3 cm band.

**Rationale:** The design target of +30 dBm (1 W) is 47.75 dB below the 75 W legal limit, providing 17.75 dB regulatory headroom.

**Verification Method:** T — Calibrated power meter at TX port.

**Design Element:** PA drive level; ADF4159 output power setting.

---

### REQ-REG-003 — Station Identification

**Requirement:** The system shall transmit the operator's callsign in CW or voice at the beginning of each operational session and at intervals not exceeding 10 minutes, as required by AFuV 2017 §14.

**Verification Method:** D — Verify automated 10-minute CW ID from REQ-SW-009.

**Design Element:** STM32H743 firmware CW ID timer.

---

### REQ-REG-004 — Operator Licence Verification

**Requirement:** The system configuration file shall require entry of a valid Klasse A callsign before activating the transmitter. The software shall not enable the RF stages (PA_ENABLE) without a non-empty callsign string in config.yaml.

**Verification Method:** D — Attempt to start system with empty callsign field; verify transmitter does not activate.

**Design Element:** STM32H743 firmware callsign validation; RPi5 software pre-flight check.

---

### REQ-REG-005 — Non-Interference Declaration

**Requirement:** System operating procedures shall include a statement that the AERIS-10P operates on a non-interference basis as a secondary user of the 10 GHz band, and the operator shall immediately cease transmission if interference to a primary user is detected.

**Verification Method:** I — Inspection of operating procedure document included in user documentation.

**Design Element:** User documentation; operating procedure SOP-001.

---

### REQ-REG-006 — Experimental Radar Permit Documentation

**Requirement:** Field operation of the AERIS-10P outside the operator's licensed station address shall be preceded by submission of a Frequenznutzungsantrag or Experimentallizenz application to BNetzA Referat 225. The system documentation shall include a template application letter.

**Verification Method:** I — Template letter present in documentation package.

**Design Element:** Regulatory documentation package.

---

## 10. Safety Requirements (REQ-SAF)

### REQ-SAF-001 — RF Exposure Safety Distance

**Requirement:** A minimum safety exclusion distance of 4 m from the boresight of the transmitting antenna shall be maintained during operation, enforced by physical barriers (safety tape, cones) or supervision during any measurement session.

**Rationale:** At +30 dBm TX power, 22 dBi gain, and 4 m distance: far-field power density S = EIRP/(4πR²) = 158/(4π×16) = 0.79 W/m², below the BNetzA general public limit of 10 W/m² at 10 GHz. Note: at distances below the Rayleigh distance (2D²/λ = 2×0.045²/0.03 = 0.135 m), near-field analysis is required; at 4 m, far-field formula applies.

**Verification Method:** T — Power density measurement at 4 m range using a calibrated EMF probe (Narda NBM-550 or equivalent).

**Design Element:** Safety procedure SOP-001; physical site preparation.

---

### REQ-SAF-002 — RF Interlock

**Requirement:** The system shall include a hardware RF kill switch accessible from the operator position that immediately de-asserts PA_ENABLE and disables the VCO ramp, cutting transmit power within 10 ms of actuation.

**Verification Method:** T — Actuate kill switch during transmission; measure power at TX port; verify ≤10 ms to −40 dBm or lower.

**Design Element:** Front panel emergency stop button; STM32H743 external interrupt on kill switch GPIO; PA drain load switch.

---

### REQ-SAF-003 — Electrical Safety

**Requirement:** The 24 V DC input wiring shall use wire gauge ≥12 AWG rated for ≥10 A. All high-current connections shall use approved crimp terminals. The enclosure shall be bonded to chassis ground. A resettable polyfuse or automotive-type fuse (10 A) shall be installed in the 24 V positive input line within 15 cm of the power connector.

**Verification Method:** I — Visual inspection of wiring and fuse; measurement of chassis-to-earth continuity ≤0.1 Ω.

**Design Element:** Power wiring harness; enclosure grounding lug.

---

### REQ-SAF-004 — Warning Labels

**Requirement:** The following labels shall be affixed to the antenna panel and electronics box: (a) "CAUTION: RF RADIATION — Do not stand within 4 m of antenna aperture during operation," (b) "ACTIVE RADAR — Licensed amateur radio use only," (c) Operator callsign and contact information.

**Verification Method:** I — Inspect labels on assembled system.

**Design Element:** Enclosure labelling; antenna panel silkscreen or adhesive label.

---

### REQ-SAF-005 — Thermal Protection

**Requirement:** The PA (HMC451) shall be equipped with a thermistor (NTC, 10 kΩ at 25°C) mounted on the PCB within 5 mm of the PA package. If the thermistor reading corresponds to a temperature ≥100°C, the STM32H743 shall de-assert PA_ENABLE and set the Fault LED.

**Verification Method:** T — Simulate overtemperature by heating thermistor to 100°C equivalent resistance; verify PA disable occurs.

**Design Element:** NTC thermistor footprint on RF PCB; STM32H743 ADC input for thermistor; firmware thermal protection task.

---

### REQ-SAF-006 — Grounding and ESD Protection

**Requirement:** All SMA RF connectors shall be grounded to the chassis through direct metal contact. All digital I/O lines entering or leaving the enclosure shall be protected with ESD protection diodes (TVS or Zener, VBRL ≤5.5 V) at the PCB connector.

**Verification Method:** I — Inspect connector grounding; measure SMA shell-to-chassis resistance ≤0.1 Ω.

**Design Element:** PCB connector footprints; chassis bonding straps; ESD protection diode placement.

---

## 11. Requirements Traceability Matrix

| Requirement ID | Requirement Description (Short) | Design Element | Verification | Status |
|---|---|---|---|---|
| REQ-SYS-001 | Operating frequency 10.0–10.1 GHz | ADF4159 + HMC733 | T | Open |
| REQ-SYS-002 | FMCW, 100 MHz BW, 1 kHz PRF | ADF4159 chirp config | T | Open |
| REQ-SYS-003 | Range resolution ≤1.5 m | Chirp BW + Range FFT | T | Open |
| REQ-SYS-004 | Velocity resolution ≤0.15 m/s | CPI length + Doppler FFT | A+D | Open |
| REQ-SYS-005 | Unambiguous range ≥75 m | ADC sample rate + IF BW | A+T | Open |
| REQ-SYS-006 | System NF ≤8 dB | HMC1040 LNA + combiner | T | Open |
| REQ-SYS-007 | TX power +30 dBm ±1 dB | HMC451 PA | T | Open |
| REQ-SYS-008 | Beam steering ±45° | HMC647A + beamform algo | D | Open |
| REQ-SYS-009 | Operating temp −10°C to +50°C | Full system | T | Open |
| REQ-SYS-010 | Update rate ≥10 Hz | RPi5 processing | T | Open |
| REQ-RF-001 | Reference accuracy ±0.01 ppm | AOCJY-10 OCXO | T | Open |
| REQ-RF-002 | VCO phase noise ≤−80 dBc/Hz @100 kHz | HMC733 + ADF4159 loop | T | Open |
| REQ-RF-003 | Chirp linearity ±500 kHz | ADF4159 ramp + VCO Kv | T | Open |
| REQ-RF-004 | TX power flatness ±1 dB | HMC451 gain flatness | T | Open |
| REQ-RF-005 | TX/RX isolation ≥50 dB | PE8316 + array separation | T | Open |
| REQ-RF-006 | LNA NF ≤2.0 dB | HMC1040LP4E | T | Open |
| REQ-RF-007 | LNA gain ≥16 dB | HMC1040LP4E | T | Open |
| REQ-RF-008 | Mixer conversion loss ≤8 dB | HMC213B | T | Open |
| REQ-RF-009 | Spurious emissions ≤−50 dBc | LPF after PA | T | Open |
| REQ-RF-010 | Phase shifter resolution 5.625°/bit | HMC647ALP5E | T | Open |
| REQ-RF-011 | Phase shifter settling ≤50 ns | HMC647ALP5E | T | Open |
| REQ-RF-012 | Phase shifter IL ≤8 dB, ripple ±1.5 dB | HMC647ALP5E | T | Open |
| REQ-RF-013 | All ports 50 Ω, RL ≥10 dB | PCB matching networks | T | Open |
| REQ-RF-014 | Scan loss ≤6 dB at ±45° | Array element pattern | A+D | Open |
| REQ-RF-015 | PA output-to-input isolation ≥20 dB | HMC451 + PCB layout | T | Open |
| REQ-ANT-001 | RO4003C substrate | Rogers RO4003C PCB | I+T | Open |
| REQ-ANT-002 | Patch resonant at 10.05 GHz | 13.8×13.8 mm patch | T | Open |
| REQ-ANT-003 | Element spacing 15 mm ±0.2 mm | PCB layout | I | Open |
| REQ-ANT-004 | 4×4 TX and 4×4 RX arrays | Antenna PCB | I+T | Open |
| REQ-ANT-005 | TX array gain ≥20 dBi | 4×4 TX array + feed net | T | Open |
| REQ-ANT-006 | RX array gain ≥20 dBi | 4×4 RX array + feed net | T | Open |
| REQ-ANT-007 | Beamwidth 20°–25° | Array geometry | T | Open |
| REQ-ANT-008 | Feed port 50 Ω, RL ≥15 dB | Wilkinson divider | T | Open |
| REQ-ANT-009 | TX/RX panel isolation ≥30 dB | Array separation | T | Open |
| REQ-ANT-010 | Cross-pol isolation ≥20 dB | Patch geometry | T | Open |
| REQ-DIG-001 | ADC ENOB ≥14 bits | ADS8661IRGAT | T | Open |
| REQ-DIG-002 | ADC sample rate 1 MSPS ±1% | ADS8661 + STM32 SPI | T | Open |
| REQ-DIG-003 | MCU clock 480 MHz | STM32H743 PLL | T | Open |
| REQ-DIG-004 | SPI speed ≥10 Mbit/s | STM32H743 SPI config | T | Open |
| REQ-DIG-005 | Phase shift update latency ≤200 μs | STM32 firmware + SPI | T | Open |
| REQ-DIG-006 | ADC double-buffer DMA | STM32 DMA config | T | Open |
| REQ-DIG-007 | Data transfer ≥2 MB/s | USB HS or Ethernet | T | Open |
| REQ-DIG-008 | Chirp sync jitter ≤100 ns | STM32 timer sync | T | Open |
| REQ-DIG-009 | USB DFU firmware update | STM32 DFU bootloader | D | Open |
| REQ-DIG-010 | FreeRTOS, latency ≤50 μs | STM32 RTOS config | T | Open |
| REQ-PWR-001 | Input voltage 22–26 V DC | LT8612/LT8607 | T | Open |
| REQ-PWR-002 | Input current ≤8 A | System power budget | T | Open |
| REQ-PWR-003 | 5 V ±2%, ripple ≤50 mV | LT8612 | T | Open |
| REQ-PWR-004 | 3.3 V ±2%, ripple ≤30 mV | LT8607 | T | Open |
| REQ-PWR-005 | ±5 V ±5%, ripple ≤20 mV | TPS65133 | T | Open |
| REQ-PWR-006 | Power sequencing: 5V before 3.3V, PA last | STM32 GPIO + load switch | T | Open |
| REQ-PWR-007 | Input reverse polarity and OV protection | MOSFET + TVS | T | Open |
| REQ-PWR-008 | DC-DC efficiency ≥85% | LT8612/LT8607 | T | Open |
| REQ-MEC-001 | Enclosure ≤300×200×100 mm aluminium | Mechanical drawing | I | Open |
| REQ-MEC-002 | Antenna panel ≤200×120×5 mm, flat ±0.5 mm | Antenna panel drawing | I | Open |
| REQ-MEC-003 | 3/8-16 UNC tripod mount | Enclosure base plate | I+T | Open |
| REQ-MEC-004 | Total weight ≤6 kg | System assembly | I | Open |
| REQ-MEC-005 | Connector layout per mechanical drawing | Rear/front panel | I | Open |
| REQ-MEC-006 | IP54 enclosure, conformal coat antenna | Enclosure sealing | T+I | Open |
| REQ-MEC-007 | PA Tj ≤125°C at +50°C ambient | PA thermal design | T | Open |
| REQ-MEC-008 | Cable ≤1.5 m, ≥30 mm bend radius | Cable harness | I+T | Open |
| REQ-SW-001 | STM32 radar control firmware | STM32 FW | D | Open |
| REQ-SW-002 | Range-Doppler FFT pipeline | RPi5 Python | T | Open |
| REQ-SW-003 | CA-CFAR detection | Python CFAR module | T | Open |
| REQ-SW-004 | Real-time GUI | PyQt6 GUI | D | Open |
| REQ-SW-005 | HDF5 data logging ≤2 GB/hr | Python logger | T | Open |
| REQ-SW-006 | Beamforming API | Python beamform module | T | Open |
| REQ-SW-007 | Calibration routine | Python calibration | D | Open |
| REQ-SW-008 | YAML configuration | config.yaml | I+D | Open |
| REQ-SW-009 | 10-minute CW station ID | STM32 FW CW keyer | D | Open |
| REQ-SW-010 | TCP/IP JSON control interface | RPi5 asyncio server | T | Open |
| REQ-SW-011 | Open-source licence | Repository SPDX headers | I | Open |
| REQ-SW-012 | Reproducible build (requirements.txt + Docker) | Dockerfile | D | Open |
| REQ-REG-001 | Frequency band compliance | ADF4159 + LPF | T | Open |
| REQ-REG-002 | TX power ≤75 W PEP | PA output power limit | T | Open |
| REQ-REG-003 | Station identification ≤10 min | CW ID firmware | D | Open |
| REQ-REG-004 | Callsign required before TX enable | STM32 FW pre-check | D | Open |
| REQ-REG-005 | Non-interference declaration | Operating procedures | I | Open |
| REQ-REG-006 | BNetzA experimental permit template | Documentation | I | Open |
| REQ-SAF-001 | 4 m RF exclusion zone | Site procedure | T | Open |
| REQ-SAF-002 | Hardware RF kill switch | Front panel E-stop | T | Open |
| REQ-SAF-003 | Electrical safety: wiring, fuse, chassis ground | Power harness | I | Open |
| REQ-SAF-004 | Warning labels on enclosure and antenna | Labels | I | Open |
| REQ-SAF-005 | PA overtemperature protection | NTC + STM32 FW | T | Open |
| REQ-SAF-006 | Grounding and ESD protection | PCB layout + chassis | I | Open |

---

## 12. Revision History

| Revision | Date | Author | Description |
|---|---|---|---|
| 1.0 | 2026-07-14 | AERIS-10P Engineering Team | Initial release of requirements specification. |

---

*End of Document — AERIS-10P-REQ-001 Rev 1.0*
