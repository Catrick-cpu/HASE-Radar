# AERIS-10P Phased Array Radar — Project Specification Rev 1.0

**Document Number:** AERIS-10P-SPEC-001  
**Revision:** 1.0  
**Date:** 2026-07-14  
**Author:** AERIS-10P Engineering Team  
**Status:** Released  
**Classification:** Open / Amateur Radio Research

---

## Table of Contents

1. Executive Summary
2. Project Objectives
3. Scope
4. System Overview
5. Performance Specifications
6. Physical Specifications
7. Operational Concept
8. Regulatory Framework
9. Constraints and Design Philosophy
10. Risk Summary
11. Glossary
12. References

---

## Executive Summary

The AERIS-10P (Affordable Experimental Radar Intelligence System, 10 GHz Phased Array) is a ground-based, portable, continuous-wave phased-array radar system designed for experimental and educational use within the German amateur radio service at 10 GHz. The system implements Frequency-Modulated Continuous Wave (FMCW) modulation with a 100 MHz chirp bandwidth over the 10.0–10.1 GHz X-band allocation and employs a 4×4 transmit plus 4×4 receive patch antenna array with analogue phase shifters for real-time electronic beam steering across a ±45° field of view.

The project targets a total build cost below USD 7,500 using commercially available RF monolithic microwave integrated circuits (MMICs), a Rogers RO4003C microstrip antenna substrate, an STM32H743 microcontroller for real-time chirp sequencing and phase-shifter control, and a Raspberry Pi 5 or NVIDIA Jetson Nano single-board computer for range-Doppler signal processing. All hardware is designed to be field-portable, tripod-mounted, and battery-operable from a 24 V DC supply.

Regulatory operation is governed by the German Amateurfunkgesetz (AFuG 2017), Amateurfunkverordnung (AFuV 2017), and the DARC 3 cm band plan. The system operates well within the permitted 75 W PEP power limit with a transmit power of +30 dBm (1 W) at the array feed point. The AERIS-10P serves as a research and demonstration platform for phased-array beamforming, FMCW signal processing, and radar fundamentals education, and is intended for licensed Klasse A amateur radio operators.

---

## 1. Project Objectives

### 1.1 Primary Objectives

**O-1 — Phased Array Beamforming Demonstration:** Demonstrate real-time electronic beam steering across ±45° in both azimuth and elevation using 16 HMC647ALP5E 6-bit analogue phase shifters on the transmit array and 16 independent phase-shifted receive channels combined into a single IF output. The system shall achieve a steered beam within the theoretical 22° 3 dB beamwidth of a 4-element, half-wavelength-spaced linear array.

**O-2 — FMCW Radar Signal Processing Research:** Provide a complete, instrumented FMCW radar chain that allows researchers to examine every stage from chirp generation through range-Doppler map formation. The system shall achieve 1.5 m range resolution and approximately 0.15 m/s velocity resolution with a coherent processing interval of 100 chirps at 1 kHz PRF.

**O-3 — Educational Platform:** Serve as a hands-on educational platform for advanced amateur radio operators, university students, and radar engineers studying phased-array principles, MMIC integration, microstrip antenna design, and digital signal processing for radar. All design files, firmware, and processing software shall be released under an open-source licence.

**O-4 — Amateur Radio Compatibility:** Operate legally and safely within the German amateur radio service on the 3 cm band (10.0–10.5 GHz) under a Klasse A licence, complying with all BNetzA technical requirements including the 75 W PEP power limit, mandatory station identification, and non-interference obligations.

**O-5 — Affordability and Reproducibility:** Achieve a complete system build cost below USD 7,500 (hard ceiling USD 8,000 with contingency) using components available from standard distributors (Mouser, Digi-Key, RFMW). The design shall use no custom ASICs, no controlled-technology export-restricted parts, and no discontinued components.

### 1.2 Secondary Objectives

**O-6 — Hardware Openness:** Publish full PCB schematics, Gerber files, BOM, and firmware source code under the CERN-OHL-S or equivalent licence, enabling independent replication.

**O-7 — Modular Architecture:** Design subsystems (antenna panel, RF front-end module, MCU board, processing computer) as separately testable and replaceable modules.

**O-8 — Data Logging:** Implement raw IF data capture for post-processing research, including time-stamped storage of I/Q samples at up to 1 MSPS for offline analysis in Python/NumPy/SciPy.

---

## 2. Scope

### 2.1 In Scope

The AERIS-10P project specification covers the following subsystems and activities:

- **RF Front-End:** VCO, PLL/chirp generator, power amplifier, low-noise amplifier, mixers, phase shifters, circulators, and all RF interconnects from 10 GHz signal generation to IF output.
- **Phased-Array Antenna:** 4×4 TX and 4×4 RX microstrip patch arrays on Rogers RO4003C substrate, corporate feed networks, element spacing, and mechanical integration into the antenna panel.
- **Digital Control System:** STM32H743ZIT6 microcontroller firmware for SPI-based phase-shifter programming, ADF4159 chirp ramp configuration, ADC data acquisition, and real-time control loop.
- **Signal Processing:** Raspberry Pi 5 or Jetson Nano-based processing pipeline implementing range FFT, Doppler FFT, CFAR detection, and range-Doppler map visualisation.
- **Power System:** 24 V DC input, LT8612/LT8607/TPS65133 DC-DC converter tree supplying all subsystem rails.
- **Mechanical Enclosure:** 300 mm × 200 mm × 100 mm aluminium electronics box with antenna panel mounting frame and 3/8-16 UNC tripod interface.
- **Regulatory Compliance:** Demonstration of compliance with AFuG 2017, AFuV 2017, and DARC 3 cm band plan requirements.
- **Software and Firmware:** Real-time control firmware, Python-based processing software, graphical user interface.

### 2.2 Out of Scope

- Moving-target indicator (MTI) clutter cancellation (future work).
- Synthetic aperture radar (SAR) modes.
- Full EMC pre-compliance testing to ETSI EN 301 783 or similar (recommended before any public demonstration).
- Integration with external tracking systems or command-and-control networks.
- Series production; this is a one-off experimental prototype.

---

## 3. System Overview

### 3.1 Top-Level Architecture

The AERIS-10P implements a classical pulsed-equivalent FMCW homodyne radar architecture with separated TX and RX apertures, analogue phase-shifted beamforming, and a homodyne (self-mixing) receiver. The chirp generator uses the ADF4159 fractional-N PLL to ramp the HMC733LP6CE VCO linearly from 10.0 GHz to 10.1 GHz in 1 ms, generating a 100 MHz bandwidth sawtooth FMCW chirp at a 1 kHz pulse repetition frequency. Transmit power is amplified by the HMC451LS6GE PA to +30 dBm, then distributed through a 1:16 Wilkinson divider corporate feed network to each of 16 TX patch elements, each preceded by an HMC647ALP5E 6-bit phase shifter. On receive, 16 patch elements feed 16 phase-shifted paths through HMC647A phase shifters and HMC1040LP4E LNAs before combination in a 16:1 corporate combiner. The combined RX signal and a sample of the TX signal are mixed in an HMC213B double-balanced mixer, producing an intermediate frequency (IF) beat signal whose frequency is proportional to target range. The IF signal is digitised by a 16-bit ADS8661IRGAT ADC at 1 MSPS and streamed via SPI to the STM32H743, which forwards data over USB or Ethernet to the Raspberry Pi 5 for FFT-based range and Doppler processing.

### 3.2 ASCII Block Diagram

```
 10 MHz OCXO
(ABRACON AOCJY)
      |
      v
 ADF4159CCPZ         SPI config from STM32H743
 PLL/Chirp Gen  <------------------------------------+
      |                                              |
      | 10.0–10.1 GHz ramp (1 ms, 100 MHz BW)       |
      v                                              |
 HMC733LP6CE                                         |
 VCO (+17 dBm)                                       |
      |                                              |
      +------------------+                           |
      |                  |                           |
      v                  v (reference sample)        |
 HMC451LS6GE       HMC213B                           |
 TX PA (+30 dBm)   MIXER                             |
      |                  ^                           |
      v                  |                           |
 1:16 Wilkinson    16:1 Wilkinson                    |
 Power Divider     Power Combiner                    |
      |                  ^                           |
      |                  |                           |
 [x16 TX paths]    [x16 RX paths]                   |
 HMC647ALP5E       HMC647ALP5E                       |
 Phase Shifters    Phase Shifters  <-----------------+
      |                  ^         (SPI from STM32)  |
      v                  |                           |
 4x4 TX Patch      4x4 RX Patch                     |
 Array (RO4003C)   Array (RO4003C)                   |
                         |                           |
                    HMC1040LP4E                      |
                    LNA (x16 or post-combine)        |
                         |                           |
                    HMC213B IF output                |
                         |                           |
                         v                           |
                   ADS8661IRGAT                      |
                   16-bit ADC (1 MSPS)               |
                         |                           |
                         v SPI                       |
                   STM32H743ZIT6 -------------------+
                   MCU (480 MHz)
                         |
                         | USB 2.0 HS or Ethernet
                         v
                   Raspberry Pi 5 8GB
                   (or NVIDIA Jetson Nano)
                   FFT | CFAR | Range-Doppler Map
                         |
                         v
                   Display / Data Logger
                   (Laptop via Ethernet/WiFi)
```

### 3.3 Data Flow Summary

Each 1 ms chirp produces 1,000 ADC samples (at 1 MSPS) representing the IF beat signal. A coherent processing interval (CPI) of 100 chirps (100 ms) provides 100 × 1,000 = 100,000 samples, from which a 2D range-Doppler FFT is computed. The Raspberry Pi 5 processes one CPI in real time (10 Hz update rate), displaying a range-Doppler power map on the operator laptop via Ethernet.

---

## 4. Performance Specifications

| Parameter | Specification | Notes |
|---|---|---|
| Operating Frequency | 10.0–10.1 GHz | X-band, German 3 cm amateur band |
| Chirp Bandwidth | 100 MHz | FMCW sawtooth |
| Chirp Duration | 1 ms | Ramp-up; 10% guard time |
| Pulse Repetition Frequency | 1000 Hz (1 kHz PRF) | One chirp per ms |
| Coherent Processing Interval | 100 chirps (100 ms) | 10 Hz update rate |
| Range Resolution | 1.5 m | c/(2B) = 3×10⁸/(2×10⁸) |
| Maximum Unambiguous Range | 75 m (IF BW limited to 50 kHz) / 150 m at 100 kHz | Beat freq = 2BR/cT |
| Velocity Resolution | ~0.15 m/s | λ/(2×T_CPI) at 100 chirps |
| Maximum Unambiguous Velocity | ±7.5 m/s | PRF limited: λ·PRF/4 |
| TX Output Power | +30 dBm (1 W) | At PA output; EIRP 52 dBm |
| TX Array Gain | 22 dBi (practical) | 4×4 patch, λ/2 spacing |
| RX Array Gain | 22 dBi (practical) | 4×4 patch, λ/2 spacing |
| EIRP | 52 dBm | 30 dBm + 22 dBi TX gain |
| Regulatory Power Limit | 75 W PEP (48.75 dBm) | AFuV 2017, 3 cm band |
| Noise Figure (system) | ~8 dB | LNA NF 1.5 dB, combiner and mixer losses |
| Beamwidth (one axis) | ~22° (3 dB) | 0.886/4 elements at λ/2 |
| Maximum Steering Angle | ±45° | Phase shifter limited |
| Phase Shifter Resolution | 5.625° (6-bit, 64 states) | HMC647ALP5E LSB |
| Theoretical Detection Range (car, σ=10 m²) | 8 km | SNR=15 dB, NF=8 dB, IF BW=2 kHz |
| Practical Detection Range | 2–5 km | With real-world losses and clutter |
| ADC Resolution | 16 bits | ADS8661IRGAT |
| ADC Sample Rate | 1 MSPS | SPI output to STM32H743 |
| Frequency Reference Accuracy | ±0.01 ppm | ABRACON AOCJY-10 OCXO |

---

## 5. Physical Specifications

| Parameter | Specification |
|---|---|
| Electronics Enclosure | 300 mm × 200 mm × 100 mm, 3 mm wall aluminium |
| Antenna Panel Dimensions | 200 mm × 120 mm × 1.6 mm |
| Antenna Substrate | Rogers RO4003C, εr = 3.55, tan δ = 0.0027, 0.508 mm thick |
| TX Array Aperture | 45 mm × 45 mm |
| RX Array Aperture | 45 mm × 45 mm |
| Patch Element Dimensions | 13.8 mm × 13.8 mm |
| Element Spacing | 15 mm (λ/2 at 10 GHz) |
| Tripod Mount | 3/8-16 UNC standard photo-tripod thread |
| Total System Weight | ~5 kg (electronics box + antenna panel + cabling) |
| Power Input Connector | Anderson PowerPole PP45 or XLR 4-pin, 24 V DC, max 8 A |
| RF Interconnects | SMA female (all RF test ports), SMA-to-2.92 mm adapters for VNA access |
| Data/Control Connectors | USB Type-C (MCU programming/data), RJ-45 Ethernet (RPi5 to laptop) |
| Operating Temperature Range | −10°C to +50°C |
| Storage Temperature Range | −40°C to +70°C |
| Power Consumption (maximum) | 192 W (24 V × 8 A) |
| Typical Power Consumption | ~120 W (nominal operational) |
| Power Supply Voltages | 24 V (main), 5 V/5 A, 3.3 V/3 A, ±5 V/1 A (RF bias) |

---

## 6. Operational Concept

### 6.1 Deployment Scenario

The AERIS-10P is designed for semi-permanent field deployment by a licensed Klasse A amateur radio operator. Typical deployment scenarios include:

- **Open field or rooftop:** Elevated location to maximise radar line-of-sight. The antenna panel is mounted on a standard 3/8-16 UNC photo-tripod or survey tripod at operator-adjustable height (1.5–3 m AGL). The electronics box is placed on a field table or directly on the tripod platform.
- **Vehicle-side deployment:** The system can be operated from a 24 V vehicle auxiliary battery (e.g., 100 Ah LiFePO4) providing approximately 45 minutes of continuous operation at maximum power.
- **Indoor laboratory use:** For development and calibration, the system operates from a 24 V bench power supply (Meanwell RSP-200-24 or equivalent) with the antenna connected via SMA coaxial cables to absorber-terminated test loads or an anechoic chamber setup.

### 6.2 Setup Procedure (Summary)

1. Erect tripod; torque antenna panel mounting bracket to 3/8-16 UNC thread.
2. Run coaxial umbilical (RF) and power/data cable bundle from electronics box to antenna panel.
3. Connect 24 V power supply or battery to PowerPole connector; verify LED power-good indicators on all DC-DC converter rails.
4. Connect operator laptop to RJ-45 Ethernet port on electronics box (RPi5 provides DHCP server).
5. Power on system via main power switch; STM32H743 initialises within 500 ms, configuring ADF4159 chirp ramp and loading default phase-shifter coefficients.
6. Open radar processing GUI on laptop (Python/PyQt6 application); verify live range-Doppler map display.
7. Adjust antenna azimuth and elevation manually; use GUI beam-steering controls for electronic fine-pointing.
8. Transmit station identification (callsign) via voice or CW at least every 10 minutes as required by AFuV 2017.

### 6.3 Operator Requirements

The operator must hold a valid German amateur radio licence Klasse A (covering the 10 GHz band) issued by the Bundesnetzagentur. Experimental radar permits beyond normal amateur radio authority should be obtained from BNetzA prior to any operation that may illuminate third-party aircraft, vessels, or persons, or that is conducted at locations other than the licensed station address.

### 6.4 Maintenance

Field-replaceable units include: the antenna panel (SMA coaxial connectors), the RF front-end module (SMA bracket), and the processing computer (RPi5 on standoff header). Firmware updates are loaded over USB DFU from the operator laptop. Calibration of phase-shifter offsets is performed using the built-in calibration routine with a reference reflector at known range.

---

## 7. Regulatory Framework

### 7.1 Applicable German Regulations

The AERIS-10P is designed to comply with the following legal instruments:

| Document | Title | Relevance |
|---|---|---|
| AFuG 2017 | Amateurfunkgesetz — German Amateur Radio Act | Overall legal basis for amateur radio operation |
| AFuV 2017 | Amateurfunkverordnung — Amateur Radio Ordinance | Technical parameters, power limits, identification |
| DARC 3 cm Band Plan | DARC e.V. 3 cm (10 GHz) band plan | Frequency allocation, permitted modes |
| TKG 2021 | Telekommunikationsgesetz | Spectrum management framework |
| BNetzA Vfg 17/2010 | EMF exposure decree | RF human exposure limits |

### 7.2 Frequency Allocation

The German amateur radio service has secondary allocation of the 10.000–10.500 GHz band (3 cm band). The AERIS-10P operates on 10.000–10.100 GHz, within the DARC-recommended segment for narrowband/wideband experimental modes. This segment is also allocated to radiolocation (primary) and Earth-exploration satellite services, placing additional obligation on the amateur operator not to cause harmful interference.

### 7.3 Power Limits

AFuV 2017, Anlage 1, allocates 75 W PEP (peak envelope power) to Klasse A licensees on the 3 cm band. The AERIS-10P transmits a maximum of +30 dBm (1 W) at the PA output. With 22 dBi TX array gain, the EIRP is 52 dBm (158 W EIRP). Although EIRP exceeds 75 W, the German regulatory framework (consistent with ITU Radio Regulations) applies the power limit to the transmitter output power, not to EIRP, for high-gain antenna applications in the amateur service. The operator should confirm this interpretation with BNetzA before deployment with high-gain antenna.

### 7.4 Station Identification

Under AFuV 2017 §14, the amateur station must identify itself with its callsign at the beginning and end of each transmission and at intervals not exceeding 10 minutes during continuous operation. For a radar system, this identification is typically implemented as a brief CW or voice ID burst transmitted on the assigned radar frequency or an adjacent voice frequency. The AERIS-10P firmware implements an automated 10-minute identification interrupt that briefly keys a CW identification sequence into the radar transmit chain.

### 7.5 Experimental Radar Permit

Any operation of an active radar — even within amateur radio frequency allocations — may require an additional experimental radar permit from BNetzA under §55 TKG, particularly if the system illuminates airspace or is operated at locations other than the licensed station address. The operator is strongly advised to apply for a BNetzA Experimentallizenz before commencing field operations. Contact: Bundesnetzagentur, Referat 225, Tulpenfeld 4, 53113 Bonn.

### 7.6 RF Exposure (EMF)

The AERIS-10P at +30 dBm TX power and 22 dBi gain produces a far-field power density at 1 m boresight of approximately 158 W/m² EIRP equivalent (note: far-field only applies beyond 2D²/λ ≈ 1.35 m for this aperture). BNetzA Vfg 17/2010 specifies an occupational exposure limit of 50 W/m² and general public limit of 10 W/m² at 10 GHz (averaged over 6 minutes). Operators must maintain a minimum safe distance of approximately 4 m from the boresight of the transmitting antenna during operation. Safety interlocks and warning labels are required on the enclosure.

---

## 8. Constraints and Design Philosophy

### 8.1 Budget Constraint

The total procurement budget is USD 7,500, with a contingency ceiling of USD 8,000. This drives selection of commercial off-the-shelf (COTS) MMICs and development boards rather than custom ASICs or military-grade components. PCB fabrication is budgeted at two four-layer boards from JLC PCB or equivalent ($200–$400 total).

### 8.2 Open-Source Requirement

All hardware design files (KiCad schematics, PCB layouts, mechanical drawings), firmware source (STM32 HAL-based C project), and processing software (Python 3 with NumPy/SciPy/Matplotlib) shall be published on a public version-controlled repository (GitHub or GitLab) under open licences (CERN-OHL-S for hardware, GPL-3.0 or MIT for software).

### 8.3 Repairability

The design shall avoid BGA packages with pitch below 0.5 mm wherever possible to allow rework with standard hot-air tools. All MMIC devices are in exposed-pad QFN or flat-pack packages accessible to a skilled amateur with a hot-air rework station.

### 8.4 Component Availability

All selected components must be available from mainstream distributors with stock levels exceeding 50 units at time of BOM freeze. Alternative second-source components shall be identified for all critical RF MMICs.

### 8.5 No Controlled Technology

The design exclusively uses components available without US Export Administration Regulations (EAR) licence requirements for the intended application. All RF MMICs from Analog Devices/Hittite are commercial parts available to non-US persons.

---

## 9. Risk Summary

| Risk ID | Risk Description | Probability | Severity | Mitigation |
|---|---|---|---|---|
| R-01 | VCO chirp non-linearity degrades range resolution | Medium | High | ADF4159 digital ramp compensation; post-processing dechirp correction algorithm |
| R-02 | Mutual coupling between TX/RX arrays causes self-interference | Medium | High | Physical separation of TX and RX panels by 50 mm; PE8316 circulator on TX port |
| R-03 | Phase shifter quantisation sidelobes limit angular resolution | Low | Medium | 6-bit (64 level) resolution gives <−26 dB quantisation sidelobes; acceptable for experimental use |
| R-04 | MMIC supply chain disruption (HMC647A, HMC733) | Low | High | Order 20% excess quantities at project start; identify substitute parts (MACOM MAPS-010164 for phase shifter) |
| R-05 | Regulatory non-compliance (BNetzA radar permit) | Medium | High | Consult BNetzA Referat 225 before field operations; initial testing in shielded lab environment |
| R-06 | RF PCB manufacturing defects on RO4003C | Low | Medium | Order 3 sets of antenna panels; specify impedance control (50 Ω ±10%) in Gerber notes |
| R-07 | Power consumption exceeds 24 V/8 A budget | Low | Medium | Thermal/power simulation in LTspice before build; measure each rail with bench supply |
| R-08 | RPi5 processing throughput insufficient for real-time 1 MSPS FFT | Low | Low | Benchmarked at 10 Hz update rate; fallback to Jetson Nano with CUDA FFT if needed |
| R-09 | Antenna gain lower than predicted (element matching loss) | Medium | Medium | EM simulation in ANSYS HFSS or openEMS; trimming patches ±0.3 mm for resonance tuning |
| R-10 | Thermal runaway in PA at high duty cycle | Low | High | PA mounted to aluminium enclosure wall (heatsink); thermal pad and thermal via array; measure PA temperature in field |

---

## 10. Glossary

| Term | Definition |
|---|---|
| ADC | Analogue-to-Digital Converter. Converts continuous analogue signal to discrete digital values. |
| AFuG | Amateurfunkgesetz. German federal law governing the amateur radio service. |
| AFuV | Amateurfunkverordnung. German regulatory ordinance implementing AFuG. |
| BNetzA | Bundesnetzagentur. Federal Network Agency of Germany; national radio spectrum regulator. |
| Chirp | A signal whose frequency changes linearly over time. In FMCW radar, a sawtooth frequency ramp from f_start to f_stop. |
| CPI | Coherent Processing Interval. The block of consecutive coherent pulses (chirps) processed together for Doppler analysis. |
| CFAR | Constant False Alarm Rate. Adaptive threshold algorithm for radar target detection in clutter. |
| DARC | Deutscher Amateur-Radio-Club e.V. German national amateur radio organisation; publishes the German band plan. |
| dBi | Decibels relative to an isotropic radiator. Unit of antenna gain. |
| dBm | Decibels relative to 1 milliwatt. Unit of power level. |
| DDS | Direct Digital Synthesis. Method of generating waveforms from a digital clock and lookup table (not used in AERIS-10P; ADF4159 uses fractional-N PLL instead). |
| EIRP | Equivalent Isotropically Radiated Power. Transmitter output power multiplied by the antenna gain relative to an isotropic radiator. |
| FMCW | Frequency-Modulated Continuous Wave. Radar modulation where the carrier is continuously transmitted with a linearly swept frequency. |
| FFT | Fast Fourier Transform. Efficient algorithm for computing the Discrete Fourier Transform; used for range and Doppler processing. |
| IF | Intermediate Frequency. In FMCW radar, the difference frequency between the TX chirp and the reflected RX signal. Proportional to target range. |
| LNA | Low-Noise Amplifier. First active stage in the receive chain; minimises added noise figure. |
| MMIC | Monolithic Microwave Integrated Circuit. An integrated circuit designed for microwave frequency operation, typically GaAs or GaN process. |
| NF | Noise Figure. Measure of noise added by a receiver component, in decibels. |
| OCXO | Oven-Controlled Crystal Oscillator. A frequency reference with thermally stabilised crystal for low ageing and low phase noise. |
| PA | Power Amplifier. Final stage in the transmit chain; boosts signal to the required transmit power level. |
| PEP | Peak Envelope Power. The average power supplied to the antenna during one RF cycle at the crest of the modulation envelope. Regulatory power limit basis in German amateur radio. |
| PLL | Phase-Locked Loop. Feedback control circuit that locks an oscillator's phase and frequency to a reference signal. |
| PRF | Pulse Repetition Frequency. Number of chirps transmitted per second. Determines unambiguous velocity range. |
| Range-Doppler Map | A 2D image with range on one axis and radial velocity (Doppler) on the other, showing detected target returns. |
| RPi5 | Raspberry Pi 5. Single-board computer used as the AERIS-10P processing platform. |
| SMA | SubMiniature version A. 50 Ω coaxial connector standard used for RF connections up to 18 GHz. |
| SPI | Serial Peripheral Interface. Synchronous serial communication protocol used to program phase shifters, PLL, and ADC. |
| SNR | Signal-to-Noise Ratio. Ratio of signal power to noise power, usually in decibels. |
| VCO | Voltage-Controlled Oscillator. An oscillator whose frequency is controlled by an input voltage. In AERIS-10P, the HMC733LP6CE covering 9.5–11 GHz. |
| Wilkinson Divider | A passive microwave power divider/combiner providing equal power split with port isolation. Used in the corporate feed network of the TX and RX arrays. |

---

## 11. References

| Ref | Document |
|---|---|
| [1] | Analog Devices, "ADF4159 Datasheet: Direct Modulation/Fast Waveform Generating, 13 GHz, Fractional-N Frequency Synthesizer," Rev. D, 2020. |
| [2] | Analog Devices (Hittite), "HMC647ALP5E Datasheet: 6-Bit Digital Phase Shifter, 10–14 GHz," 2018. |
| [3] | Analog Devices (Hittite), "HMC733LP6CE Datasheet: VCO with Buffer Amplifier, 9.5–11 GHz," 2017. |
| [4] | Analog Devices (Hittite), "HMC451LS6GE Datasheet: GaAs pHEMT MMIC Power Amplifier, Ku-Band," 2016. |
| [5] | Analog Devices (Hittite), "HMC1040LP4E Datasheet: Low Noise Amplifier, 8–12 GHz," 2019. |
| [6] | Analog Devices (Hittite), "HMC213B Datasheet: Double Balanced Mixer, 8–26 GHz," 2017. |
| [7] | Texas Instruments, "ADS8661IRGAT Datasheet: 16-Bit, High-Speed, Single-Supply, SAR ADC," 2020. |
| [8] | STMicroelectronics, "STM32H743ZIT6 Reference Manual RM0433," Rev. 8, 2023. |
| [9] | Rogers Corporation, "RO4003C Laminates Datasheet," Publication 92-004, 2022. |
| [10] | ABRACON, "AOCJY Series OCXO Datasheet," 2021. |
| [11] | Bundesgesetzblatt, "Amateurfunkgesetz (AFuG) vom 23. Juni 1997, geändert 2017." |
| [12] | Bundesgesetzblatt, "Amateurfunkverordnung (AFuV) vom 15. Februar 2005, geändert 2017." |
| [13] | DARC e.V., "Bandplan 3-cm-Band (10 GHz)," Rev. 2023. |
| [14] | M. I. Skolnik, "Introduction to Radar Systems," 3rd ed., McGraw-Hill, 2001. |
| [15] | G. A. Richards, J. A. Scheer, W. A. Holm, "Principles of Modern Radar," Vol. I, SciTech Publishing, 2010. |
| [16] | Pozar, D. M., "Microwave Engineering," 4th ed., Wiley, 2011. |
| [17] | Balanis, C. A., "Antenna Theory: Analysis and Design," 4th ed., Wiley, 2016. |
| [18] | Bundesnetzagentur, "Vfg 17/2010: Allgemeinzuteilung für Funkanlagen auf der Grundlage der EMF-Richtlinie." |
| [19] | Analog Devices, "LT8612 Datasheet: 6A, 42V, 3MHz Step-Down Regulator," 2019. |
| [20] | Texas Instruments, "TPS65133 Datasheet: Dual-Output, Regulated Charge Pump," 2018. |

---

*End of Document — AERIS-10P-SPEC-001 Rev 1.0*
