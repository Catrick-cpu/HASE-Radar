# AERIS-10P Maintenance Documentation
## Rev 1.0 — AERIS-10P Affordable Experimental Radar Intelligence System, 10 GHz Phased Array

**Document Number:** AERIS-MNT-001  
**Revision:** 1.0  
**Date:** 2026-07-14  
**Author:** RF Systems Engineering  
**Status:** Released  

---

## 1. Scope

This document defines all maintenance requirements for the AERIS-10P phased-array FMCW radar system, including scheduled preventive maintenance, calibration procedures, fault diagnosis, component replacement, storage, and disposal. Maintenance must be performed only by technicians familiar with RF systems and ESD-safe handling. Any radiated testing during maintenance activities requires a valid amateur radio licence (Klasse A) in accordance with AFuG 2017 and AFuV 2017.

---

## 2. Maintenance Schedule

### 2.1 Maintenance Interval Summary

| Interval | Activity | Reference |
|----------|----------|-----------|
| Pre-operation (every use) | Pre-operation checklist | Section 3 |
| Monthly | RF connector inspection, software version check, TX power verification, fan inspection | Sections 4.1, 4.2, 5.3 |
| Quarterly | OCXO frequency calibration against GPS reference, phase noise spot check, PCB visual inspection | Section 5.1 |
| Annually | Full calibration verification (all PT-0xx), phase shifter recalibration, thermal paste replacement, fan replacement (if required), deep PCB inspection for corrosion, spare parts inventory review | Sections 5.2, 6.1, 4.3 |
| After any hard impact or weather exposure | Mechanical inspection, connector integrity check, antenna panel inspection | Sections 4.1, 4.4 |

### 2.2 Maintenance Log

A maintenance log must be kept for the AERIS-10P system. Each entry must include:
- Date and time
- Operator (callsign and name)
- Activity performed
- Results / observations
- Corrective actions taken (if any)
- Signature

The maintenance log is stored with the system documentation in `/Documentation/Maintenance_Log/`. A paper copy may be kept in the system case for field use.

---

## 3. Pre-Operation Checklist

Perform this checklist before every operational use of the AERIS-10P system. The checklist takes approximately 5–10 minutes. Do not operate the system if any item fails.

| Item | Check | Action if Failed |
|------|-------|-----------------|
| 3.1 | RF connectors: visually inspect all SMA connectors for obvious damage, bent centre pins, cracked bodies | Do not operate; see Section 6.2 |
| 3.2 | RF connectors: verify all SMA connectors are finger-tight, then tightened to 0.9 Nm with torque wrench | Tighten; re-inspect |
| 3.3 | Antenna panel: no physical damage, no contamination on patch elements | Clean with dry lint-free cloth; do not use IPA on Rogers surface without a separate cleaning verification |
| 3.4 | 24 V power cable: inspect for damage, check fuse continuity | Replace fuse or cable |
| 3.5 | Cooling fan: power on system, verify fan spins within 5 s; hold hand near exhaust — airflow felt | See fault diagnosis; do not operate without working fan if ambient >20°C |
| 3.6 | Software version: boot system, check AERIS software version in startup screen or `aeris-status --version` | Update if behind current release |
| 3.7 | Calibration date: check last calibration date in maintenance log | Schedule calibration if overdue |
| 3.8 | PLL lock: verify PLL_LOCK indicator is GREEN in the software status panel within 10 s of startup | See fault diagnosis PT-010 fault tree |
| 3.9 | TX power indicator: verify software shows TX power within ±2 dB of nominal | See fault diagnosis |
| 3.10 | Station identification: confirm callsign is entered correctly in system settings; verify auto-ID timer is active (10-minute interval) | Enter callsign per AFuV 2017 requirements before any radiated operation |
| 3.11 | Tripod mounting: verify 3/8-16 UNC thread engagement is ≥6 turns; verify the system is level | Re-mount; do not operate if mount is insecure |

---

## 4. Routine Maintenance Tasks

### 4.1 RF Connector Inspection and Cleaning

RF connector integrity is the single most common source of performance degradation in field-operated RF systems. Clean connectors at every monthly maintenance and whenever the system has been operated in dusty or humid conditions.

**Procedure:**
1. Disconnect all SMA connectors from mating parts.
2. Inspect the centre pin of each SMA male connector: it must be straight, undamaged, and protrude the correct distance (SMA male pin protrusion: 3.02 mm ±0.05 mm from the reference plane). A bent or retracted pin must be replaced (see Section 6.2).
3. Inspect the SMA female socket: threads must be clean and sharp; the dielectric must be white/beige PTFE with no cracks.
4. Apply a few drops of 99.9% IPA to a lint-free swab. Insert the swab into the female SMA socket and rotate to clean the inner conductor and socket. Do not apply IPA to the Rogers RO4003C patch surfaces directly — apply to a lint-free cloth and gently wipe if cleaning is required.
5. Allow 2–3 minutes for IPA to evaporate before reconnecting.
6. Inspect the mating surfaces under 5× magnification if available. Any pitting, arcing damage, or contamination that persists after cleaning warrants connector replacement.

**Torque on reassembly:** 0.9 Nm (8 in-lb) using the calibrated SMA torque wrench. Do not over-torque — SMA connectors on Rogers PCBs can crack the PCB copper around the connector tabs if over-torqued.

### 4.2 Software Version Verification

1. SSH into the Raspberry Pi 5: `ssh pi@aeris-radar.local`
2. Check current version: `aeris-status --version`
3. Check for updates: `cd /home/pi/aeris-software && git fetch origin && git status`
4. If behind, update: `git pull origin main && pip3 install -r requirements.txt && sudo systemctl restart aeris-radar`
5. After update, run the self-test: `aeris-selftest --basic`
6. STM32 firmware version: visible in the serial console boot banner, or query via `aeris-status --fw-version`. Update STM32 firmware via ST-LINK per the assembly documentation (Section 9.1) if a new release is available.

### 4.3 Thermal Paste Refresh (Annual)

The HMC451LS6GE PA and the LT8612/LT8607 DC-DC converters use thermal interface material to the chassis. Thermal paste dries and cracks over 12–18 months, increasing junction temperatures.

**Procedure:**
1. Power off the system and disconnect 24 V.
2. Remove the electronics tray from the chassis (4× M3 screws).
3. Use a plastic spudger to separate the PA and DC-DC ICs from the thermal pad or paste contact with the tray.
4. Remove old thermal paste with IPA on a lint-free cloth. Remove thoroughly — do not leave residue.
5. Apply a fresh, thin bead (approximately 0.1 mm thickness, rice-grain amount for QFN packages) of Shin-Etsu X-23-7921-5 or equivalent ≥6 W/m·K paste to the IC thermal pad.
6. Replace the electronics tray. Torque screws to 0.35 Nm.
7. Run the system for 30 minutes and measure IC temperatures as per PT-005. Compare to baseline.

### 4.4 Fan and Filter Cleaning

The 80 mm fan draws air through the chassis. Dust accumulation on the fan blades and any inlet mesh increases thermal resistance and reduces fan life.

**Procedure (Monthly):**
1. Power off the system.
2. Open the chassis or access the fan from the rear panel.
3. Use a dry compressed air blast (ESD-safe can duster) to clear dust from the fan blades and any inlet grille. Direct the airflow backwards through the grille to push dust out.
4. Do not use water or IPA on the fan motor.
5. Check that the fan rotates freely by hand. Any bearing roughness or wobble indicates the fan should be replaced (annual or on condition).

**Fan Replacement:**
If the fan tachometer reading falls below 80% of rated speed (typically 1800–2400 RPM for a 5 V 80 mm ball-bearing fan) or exhibits audible bearing noise, replace the fan. Use a ball-bearing type only (not sleeve bearing) for reliability in tilted or inverted orientations on the tripod. Replace with: Noctua NF-A8 (5 V fan with JST adaptor) or Delta FFB0812EHE (12 V, with voltage converter if needed).

### 4.5 PCB Inspection for Corrosion

Annually or after any moisture exposure, inspect all PCBs for corrosion signs:

1. Remove all PCBs from the chassis.
2. Inspect under 10× magnification:
   - Green or white powdery deposits indicate flux residue contamination (not corrosion) — clean with IPA.
   - Blue/green staining on copper pads indicates copper oxide corrosion from moisture ingress.
   - Brown/black staining on SMA connector threads indicates oxidation — clean and assess structural integrity.
3. Apply a thin coat of Humiseal 1B31 conformal coating to non-RF areas (power board, digital sections of MainBoard) if regular humidity exposure is expected. Do not apply conformal coating to the RF Frontend board or antenna panel.

---

## 5. Calibration Procedures

### 5.1 Frequency Reference Calibration (Quarterly)

The AERIS-10P uses an ABRACON AOCJY-10 OCXO as the 10 MHz master reference. While this oscillator is specified at ±0.01 ppm stability, it can drift at the extremes of its temperature range. Calibration verifies that the frequency reference is within specification.

**Equipment required:** GPS-disciplined OCXO (e.g., Jackson Labs CSAC, Z3805A, or a GPS reference receiver with 10 MHz output such as a u-blox LEA-M8F development board), frequency counter (Keysight 53230A or HP 53131A, 10-digit, 10 MHz or higher timebase).

**Procedure:**
1. Allow the AERIS-10P OCXO to warm up for 15 minutes in a stable-temperature environment.
2. Connect the GPS-disciplined reference to the frequency counter's reference input.
3. Connect the AERIS OCXO output (10 MHz) to the frequency counter's measurement input.
4. Gate time: 10 seconds. Record 10 consecutive 10-second frequency measurements.
5. Compute mean frequency: f_mean. Compute offset from 10 MHz: Δf = f_mean − 10,000,000 Hz.
6. Frequency accuracy in ppm: accuracy = Δf / 10 × 10⁻⁶ ppm.

**Pass Criterion:** |accuracy| ≤ 0.01 ppm (|Δf| ≤ 0.1 Hz). If outside this range, the OCXO calibration trimmer (if available) may be adjusted. Otherwise, the OCXO must be replaced.

**Logging:** Record mean frequency and offset in the maintenance log.

### 5.2 Phase Shifter Recalibration (Annual)

The HMC647ALP5E phase shifters are factory-calibrated at manufacture, but the phase vs. code relationship can shift with temperature cycling and component ageing. Annual recalibration updates the phase correction table stored in the STM32 firmware.

**Equipment required:** Vector Network Analyzer with 2-port calibration, calibrated cables.

**Procedure:**
1. Execute the recalibration command from the AERIS software: `aeris-cal --phase-shifters`
2. The system automatically:
   a. Steps each of the 16 TX and 16 RX phase shifters through all 64 phase codes.
   b. Measures the S21 phase at each code using the system's internal feedback path (or an external VNA port if connected in calibration mode).
   c. Stores the measured phase-vs-code table in the STM32 non-volatile flash.
3. After calibration, verify beam steering performance (abbreviated version of PT-043): steer to 0°, ±15°, ±30°. Confirm peaks within ±3°.

**Alternative (VNA-based, more accurate):**
1. Connect VNA port 1 to the common TX feed. Connect VNA port 2 to the output of each phase shifter in turn.
2. Step through all 64 codes for each phase shifter and record measured phase at 10.050 GHz.
3. Upload the measured calibration table to the STM32 via USB serial command.

### 5.3 TX Power Verification (Monthly)

**Equipment required:** Power meter (HP 437B + 8485A sensor), 30 dB, 5 W in-line SMA attenuator, calibrated cable.

**Procedure:**
1. Connect 30 dB attenuator and calibrated cable to the TX output SMA port.
2. Connect power meter sensor to the cable output.
3. Zero the power meter with RF off.
4. Enable CW at 10.050 GHz via the AERIS software maintenance menu (`aeris-maint --cw-mode 10050`).
5. Record power meter reading. Correct for attenuator loss and cable loss (from the cable loss log).
6. Compare to nominal value (+30 dBm ±1 dB at the TX SMA port).

**Pass Criterion:** Corrected TX output power: +29 to +31 dBm. If outside this range, proceed to the PA fault diagnosis (Section 6.3).

---

## 6. Common Fault Diagnosis

### 6.1 No PLL Lock

**Symptom:** PLL_LOCK indicator is red or absent in the AERIS software status panel. The ADF4159 lock detect (MUXOUT) GPIO reads LOW on the STM32.

**Fault tree:**

1. **Check OCXO power and output.** Measure the OCXO supply voltage (should be +5 V ±0.1 V). Measure OCXO output level at the ADF4159 REF_IN pin with an oscilloscope: expect a 10 MHz sine wave, 0.5–1 V peak, or a clipped near-square wave. If no signal: OCXO may have failed; replace the ABRACON AOCJY-10.

2. **Check SPI communication.** Using the STM32 serial console, run `aeris-diag --spi-loopback`. This verifies that the SPI bus to the ADF4159 is functional. If SPI loopback fails, inspect the SPI cable connection and board connector. If SPI is working but PLL does not lock, the ADF4159 may have been programmed with incorrect register values. Re-run `aeris-init --pll` to reload the default register set.

3. **Check VCO supply voltage.** Measure the HMC733LP6CE supply pins: Vd should be +5 V ±0.25 V; Vs (source bias) should be at the designed operating point. If supply is out of range, trace back to the TPS65133 ±5 V_RF rails (PT-002).

4. **Check VCO tuning range.** In CW mode, sweep the ADF4159 N-divider to step the VCO from its minimum to maximum frequency (9.5–11 GHz per HMC733 datasheet). A PLL that locks at some frequencies but not others may indicate the VCO is operating outside its range for the chosen N-divider values. Verify N-divider and reference divider settings against the ADF4159 configuration spreadsheet.

5. **Replace ADF4159 or HMC733.** If all above steps are inconclusive, the IC may have been damaged by ESD or over-voltage. Replace with a spare (see Section 8).

### 6.2 Low TX Output Power

**Symptom:** TX power >2 dB below nominal (+30 dBm).

**Fault tree:**

1. **Check PA bias.** Measure the HMC451LS6GE gate and drain voltages. The PA requires specific gate bias voltage (from datasheet, typically negative gate voltage for pHEMT depletion-mode devices). If bias is incorrect, check the gate bias circuit (often a DAC output from the STM32 or a fixed resistor divider from the −5 V_RF rail).

2. **Check PA supply voltage.** Vd for the HMC451 should be +5 V ±0.25 V. Measure directly at the PA drain pin. If supply sags under load, the TPS65133 +5 V_RF rail has insufficient current capacity — inspect for a shorted bypass capacitor.

3. **Check cable connections.** Inspect the SMA connections from the phase shifters to the PA input, and from the PA output to the TX feed. A partially mated SMA connector can introduce 3–6 dB of attenuation. Tighten all connectors and re-measure.

4. **Check PA temperature.** The HMC451LS6GE has a thermal shutdown or significant gain roll-off if the die temperature exceeds 150°C. Measure PA case temperature. If above 80°C, check thermal paste and chassis cooling. Allow the PA to cool and re-measure output power.

5. **PA failure.** If bias is correct, supply is correct, connections are correct, and temperature is within range, the PA may have failed (degraded output stage). Replace HMC451LS6GE per Section 6.5.

### 6.3 High Noise Floor on IF Output

**Symptom:** The software noise floor in the range-FFT is elevated (worse than expected based on the system NF budget of 8 dB), reducing detection range.

**Fault tree:**

1. **Check LNA bias.** Measure the HMC1040LP4E drain voltage and current. Operating point must be within the specified range (typically 3 V drain, ~60–80 mA). Incorrect bias shifts the noise figure and gain away from the optimum.

2. **Check mixer LO drive level.** The HMC213B requires nominally +7 to +10 dBm LO drive. Measure LO level at the mixer LO port with a directional coupler and SA. Under-driven LO increases conversion loss and noise figure.

3. **Check mixer supply.** The HMC213B requires DC bias on its IF port (+5 V_RF) for proper operation. Verify bias is present and within tolerance.

4. **Check IF amplifier chain.** If the system has IF amplifier stages between the mixer output and the ADC, verify each stage gain and supply. A failed IF amplifier can reduce signal level and cause the ADC to be dominated by quantisation noise.

5. **Check for interference.** Operate the system with the TX disabled. Measure the IF noise floor with TX off. If the noise floor is normal with TX off but elevated with TX on, there is TX-to-RX leakage (insufficient isolation) creating self-jamming. Check the MASWSS0179 T/R switch operation and TX-to-RX isolation (PT-041).

6. **Check ADC reference.** The ADS8661 uses an internal or external voltage reference. An incorrect or noisy reference voltage increases ADC noise floor. Measure the reference voltage at the ADS8661 REF pin (nominal 4.096 V internal or as configured externally).

### 6.4 Beam Steering Not Working

**Symptom:** The radar beam does not steer to the commanded angle; the pattern remains at broadside regardless of phase shifter commands, or the beam is erratic.

**Fault tree:**

1. **Check SPI communication to HMC647A.** From the AERIS software diagnostic menu: `aeris-diag --phase-shifter 1`. This commands phase shifter #1 through all 64 codes and reads back the code via the SPI DOUT line (if the HMC647A SPI read-back is supported). If communication fails, trace the SPI CS, CLK, and MOSI lines from the STM32 to the HMC647A.

2. **Check phase shifter supply voltage.** The HMC647ALP5E requires VDD (digital, typically 3.3 V) and VCC (phase shifter bias, typically from the +5 V or −5 V_RF rail, depending on the application circuit). Measure each supply at the IC power pins.

3. **Verify with VNA.** Connect the VNA to one phase shifter input and output. Command the phase shifter through codes 0x00, 0x10, 0x20, 0x30, 0x3F via the STM32 serial command interface. Verify that S21 phase changes in the expected direction and magnitude on the VNA. If no phase change is seen despite correct SPI signalling, the HMC647A IC has likely failed and must be replaced.

4. **Check phase control word in firmware.** Verify that the beam-steering algorithm is computing the correct phase gradient for the commanded angle. The required inter-element phase shift for angle θ is: Δφ = 360° × (d/λ) × sin(θ) = 360° × 0.5 × sin(θ). For θ = 30°: Δφ = 90° per element. This value, divided by the phase step (5.625° per bit for the 6-bit shifter) gives 16 bits per element — verify this calculation in the firmware source.

---

## 7. Component Replacement Procedures

### 7.1 General ESD Precautions

All component replacement must be performed at an ESD-safe workstation with wrist strap and ESD mat grounded. The HMC647A, HMC1040, and HMC213B are GaAs devices with HBM ESD ratings as low as 500 V. Handle with care; never touch pins directly.

### 7.2 HMC647ALP5E Rework with Hot Air

The HMC647ALP5E is in a 5×5 mm QFN package with an exposed thermal pad. Replacement requires a hot air rework station and proper stencil or syringe paste application.

**Tools required:** Hot air rework station (Hakko FR-872B or Metcal MFR-H1-DS), fine-tip iron 350°C, flux pen (Kester 951), desoldering wick 2.0 mm, tweezers, 0.12 mm stencil (or syringe paste for individual pad application), new HMC647ALP5E in ESD-safe packaging.

**Removal:**
1. Apply flux pen generously to all four sides of the HMC647A package.
2. Set hot air: 360°C, 30 L/min airflow, round nozzle 5 mm diameter.
3. Hover the nozzle 5–8 mm above the package. Move in slow circles. Observe the solder — when reflowed, the package will float very slightly.
4. After approximately 30–60 s, gently lift the package with tweezers from one corner. Do not force; if it does not lift freely, continue heating.
5. Place removed component in an ESD tray (do not discard — may be tested and reused).

**Pad Cleanup:**
1. Apply fresh flux to the PCB pads.
2. Using desoldering wick 2.0 mm and the iron at 350°C, remove all solder from each exposed pad. Work methodically around all four sides, then the thermal pad (apply heat for 3–4 s per section; the thermal pad is large and requires longer dwell).
3. Inspect under 10× magnification: all pads should be clean, flat copper with ENIG finish (gold colour). No solder bridges, no lifted pads.

**Installation:**
1. Apply solder paste to pads using a mini-stencil (cut from the full stencil for this IC footprint) or with a syringe applying paste to each pad manually. The thermal pad receives a segmented paste deposit (window-pane pattern).
2. Place the new HMC647ALP5E. Align pin 1 dot to silkscreen mark.
3. Set hot air: 350°C, 25 L/min. Approach from the side first to preheat the board for 15 s. Then move nozzle over the component for 30–45 s until solder is seen to reflow (slight movement of component as surface tension centres it).
4. Remove heat. Allow to cool with no airflow for 2 minutes.
5. Inspect under 10× microscope. Perform continuity checks.

### 7.3 STM32H743 Replacement

The STM32H743ZIT6 in LQFP-144 at 0.5 mm pitch can be replaced with hot air, but requires significant skill due to the 144 leads. Consider sending the board to a professional rework facility for this operation.

If performing in-house: use a large round nozzle (12–15 mm), 350°C, 20 L/min, hover over the entire package, preheat the board from below with a pre-heater plate at 150°C, then reflow from above. Lead-frame IC packages often require more heat than QFN packages due to the gull-wing leads dissipating heat to the board.

---

## 8. Spare Parts List

Maintain the following minimum spare parts inventory. Suggested stocking quantity reflects the estimated failure rate over a 2-year operational period.

| Part | Description | Quantity | Notes |
|------|-------------|---------|-------|
| HMC647ALP5E | 6-bit phase shifter, 10–14 GHz, QFN | 4 | Most likely RF IC to require replacement; 16 installed |
| HMC1040LP4E | LNA 8–12 GHz, NF 1.5 dB | 2 | 4 installed; critical for RX sensitivity |
| HMC213B | Double-balanced mixer 8–26 GHz | 2 | 4 installed |
| HMC451LS6GE | TX PA, +29 dBm, 28 dB gain | 2 | 1 installed; PA most stressed component |
| HMC733LP6CE | VCO 9.5–11 GHz | 1 | 1 installed |
| ADF4159CCPZ | FMCW PLL synthesiser | 1 | 1 installed |
| STM32H743ZIT6 | Microcontroller LQFP-144 | 1 | 1 installed |
| ADS8661IRGAT | 16-bit 1 MSPS ADC | 2 | 1 installed; ESD-sensitive |
| ABRACON AOCJY-10 | 10 MHz OCXO reference | 1 | 1 installed |
| LT8612EFE | 5 V DC-DC converter | 1 | 1 installed |
| LT8607PMSE6 | 3.3 V DC-DC converter | 1 | 1 installed |
| PE8316 | 9.5–10.5 GHz circulator/isolator | 1 | As installed |
| SMA female, PCB mount | Panel SMA connector | 6 | Connectors are field-replaceable; highest wear item |
| SMA m-m barrel | Loopback adaptor | 2 | |
| 30 dB SMA attenuator, 5 W | In-line attenuator for TX measurements | 2 | |
| M3 × 6, cap-head, SS | Stainless M3 fasteners | 20 | Various lengths |
| 10 A blade fuse | AGX or ATO automotive blade | 5 | For 24 V input fuse |
| 80 mm ball-bearing fan, 5 V | Noctua NF-A8 5V or equivalent | 1 | Annual replacement on condition |
| Shin-Etsu X-23-7921-5 thermal paste | 7 g syringe | 1 | Annual replacement |
| Kester 44 solder wire 0.5 mm | Sn63Pb37 | 1 spool | Field touch-up |
| IPA 99.9% | 500 mL spray bottle | 2 | Connector cleaning |

---

## 9. Storage Procedure

### 9.1 Short-Term Storage (Less Than 6 Months)

1. Power off the system and disconnect 24 V input.
2. Install dust caps on all exposed SMA connectors (SMA dust cap, push-on type).
3. Wipe all external surfaces with a dry lint-free cloth to remove moisture and fingerprints.
4. Place 5 g silica gel sachet inside the chassis.
5. Close the chassis and secure all access panels.
6. Store in an indoor environment: temperature +5°C to +40°C, humidity <70% RH non-condensing.
7. Place in a protective carry case with foam cut-outs.

### 9.2 Long-Term Storage (6 Months or Greater)

1. Complete all pre-storage maintenance checks.
2. Remove the antenna panel and wrap in anti-static bubble wrap. Store separately in a flat orientation to prevent the Rogers substrate from warping.
3. Remove the Raspberry Pi 5 microSD card (if used) or USB SSD and store it in an anti-static bag separately from the main chassis.
4. Bag all PCB assemblies individually in metallic anti-static bags (not pink anti-static foam, which does not provide RF shielding).
5. Place desiccant (10 g minimum) inside the sealed chassis.
6. Store at: temperature −20°C to +60°C dry, preferred +15°C to +25°C; humidity <50% RH.
7. Power on and perform the complete pre-operation checklist at least once every 12 months during long-term storage to verify the OCXO maintains calibration and capacitors do not dry out.

### 9.3 Field Transport

Transport the AERIS-10P in the dedicated carry case. Do not leave the system in a vehicle in direct sunlight (interior temperatures can exceed 80°C). Use the original tripod mounting hardware; improvised mounts may not support the 5 kg system weight safely.

---

## 10. End-of-Life and Disposal

### 10.1 RF Integrated Circuit Recycling

The HMC647ALP5E, HMC1040LP4E, HMC213B, and HMC451LS6GE contain gallium arsenide (GaAs) compound semiconductor material. GaAs is classified as a hazardous substance under EU Directive 2011/65/EU (RoHS) and must not be disposed of in general waste. Options for disposal:

- Return to the component distributor (Analog Devices authorised distributors may accept returns under take-back programmes).
- Deliver to a licensed electronic waste recycling facility. In Germany, WEEE (Waste Electrical and Electronic Equipment) regulations (ElektroG, implementing EU Directive 2012/19/EU) require registered take-back. Use a certified WEEE recycling point.

### 10.2 PCB and Electronic Assembly Disposal

All populated PCBs, including the Rogers RO4003C antenna panel, must be disposed of as WEEE (Elektroschrott) in accordance with ElektroG. Do not dispose in household waste. Deliver to a municipal Wertstoffhof (recycling centre) with electronics acceptance, or to a certified WEEE recycler.

The Rogers RO4003C substrate does not contain hazardous halogens (it is a halogen-free material), but the copper layers and solder alloys require separate handling per local regulations.

### 10.3 Battery Disposal

If a lithium coin cell (CR2032 or similar) is used for the STM32 real-time clock battery, it must be disposed of at a battery collection point (Batterie-Rückgabe) per BattG (Batteriegesetz) in Germany. Do not dispose in household waste.

### 10.4 Decommissioning Checklist

Before final disposal:
1. Delete all personal data (callsign, GPS coordinates, station logs) from the Raspberry Pi 5 storage: `sudo shred -vuz /dev/mmcblk0` or perform a secure erase.
2. Remove the microSD card / SSD and destroy physically if it contains sensitive data.
3. Document system serial number and disposal date in the maintenance log.
4. If the system holds a BNetzA experimental radar permit, notify BNetzA that the station is being decommissioned and the permit is being relinquished.

---

*End of AERIS-10P Maintenance Documentation Rev 1.0*

*Document controlled. Check repository for latest revision before use.*
