# AERIS-10P Project Memory
## Complete Engineering Handover Document for Future AI Systems and Engineers
**Created:** 2026-07-14 | **Status:** Design-phase complete, hardware not yet built

---

## SECTION 1: PROJECT IDENTITY

| Field | Value |
|---|---|
| Project Name | AERIS-10P (Affordable Experimental Radar Intelligence System, 10 GHz Phased Array) |
| Version | 1.0 — Initial Design |
| Created | 2026-07-14 |
| Author | AERIS-10P Engineering Team (AI-assisted) |
| Repository | C:\Users\patri\Projects\HASE-Radar\ |
| Status | **Design phase complete.** All documentation, PCB schematics (EasyEDA JSON), STL files, firmware, control software, and spreadsheets created. **Hardware has NOT been built or tested.** |
| Budget | $4,451 base (well under $8,000 limit, $3,104 margin available for upgrades) |

---

## SECTION 2: AUTHORITATIVE TECHNICAL SPECIFICATIONS

> **These are the canonical specs. Do not change without documenting why.**

### RF / Waveform
| Parameter | Value | Unit | Notes |
|---|---|---|---|
| Modulation | FMCW | | Not pulse — chosen for low peak power (amateur license compatible) |
| Center frequency | 10.05 | GHz | Within 10.000–10.100 GHz chirp band |
| Chirp start | 10.000 | GHz | |
| Chirp stop | 10.100 | GHz | |
| Chirp bandwidth | 100 | MHz | Range resolution = 1.5 m |
| Chirp duration | 1 | ms | Sweep time T_chirp |
| PRF | 1000 | Hz | Pulses per second |
| Chirps per CPI | 100 | | Coherent processing interval = 100 ms |
| Waveform shape | Sawtooth | | ADF4159 continuous sawtooth ramp |

### Array
| Parameter | Value | Unit |
|---|---|---|
| TX elements | 16 (4×4) | patches |
| RX elements | 16 (4×4) | patches |
| Total elements | 32 | |
| Element spacing | 15 | mm = λ/2 at 10 GHz |
| TX aperture | 45 × 45 | mm |
| RX aperture | 45 × 45 | mm |
| Antenna substrate | Rogers RO4003C | 0.508 mm thickness |
| Patch dimensions | 13.8 × 8.0 | mm (L × W) |
| Element gain | 6 | dBi |
| Array gain (theoretical) | 24 | dBi = 10·log10(16) + 6 dBi element |
| Array gain (practical) | 22 | dBi (accounting for losses) |
| Beam width | ~22° | both azimuth and elevation |
| Max steering angle | ±45° | azimuth and elevation |

### Key Components
| Component | Part Number | Manufacturer | Function |
|---|---|---|---|
| Phase Shifter | HMC647ALP5E | Analog Devices | 6-bit, 0–360°, 10–14 GHz, QFN-32 |
| VCO | HMC733LP6CE | Analog Devices | 9.5–11 GHz, +17 dBm |
| PLL/FMCW | ADF4159CCPZ | Analog Devices | FMCW ramp generator, 13 GHz max |
| TX PA | HMC451LS6GE | Analog Devices | +29 dBm P1dB, 28 dB gain |
| RX LNA | HMC1040LP4E | Analog Devices | NF 1.5 dB, gain 18 dB |
| Mixer | HMC213B | Analog Devices | Double-balanced, 8–26 GHz |
| MCU | STM32H743ZIT6 | ST Micro | 480 MHz, 6× SPI, USB, LQFP-144 |
| Processing | Raspberry Pi 5 8GB | RPi Foundation | Python FMCW DSP |
| ADC | ADS8661IRGAT | Texas Instruments | 16-bit, 1 MSPS, SPI |
| Reference | AOCJY-10.000MHZ | Abracon | OCXO ±0.01 ppm |

### Performance (Predicted)
| Parameter | Value | Condition |
|---|---|---|
| TX power | +27 to +30 | dBm (PA output) |
| TX EIRP | ~52 | dBm |
| Range (car, σ=10 m²) | 2–5 | km theoretical |
| Range resolution | 1.5 | m |
| Velocity resolution | ~0.15 | m/s (100 chirps @ 1ms) |
| System noise figure | ~2 | dB (LNA-dominated) |
| IF noise bandwidth | 10 | Hz (for Nc=100 chirps) |
| SNR at 3 km (car) | ~+25 | dB (>15 dB threshold → detected) |

### German Regulatory Status
| Parameter | Status |
|---|---|
| Band | 10.000–10.500 GHz (amateur 3 cm) ✓ |
| License | Klasse A (full amateur radio license) ✓ |
| TX power | 1 W vs 75 W limit → -18.75 dB margin ✓ |
| Emission type | FMCW ≈ F3E/F7X — permitted ✓ |
| Station ID | Required every 10 min → implemented in software ✓ |
| BNetzA consultation | RECOMMENDED before field operation ⚠️ |
| Field operation | Wait for BNetzA response ⚠️ |

---

## SECTION 3: DESIGN DECISIONS

### Why FMCW (not Pulse Radar)?
- **Chosen:** FMCW — continuous wave with linear frequency sweep
- **Why:** Lower peak power (1 W vs potentially kW for pulse); more compatible with amateur radio license; no range blind zone; simpler ADC (low-rate: 8 kSPS vs GHz for pulse); better average SNR per watt
- **Rejected:** Pulse radar — high peak power needed for range, may conflict with amateur license constraints, requires fast ADC (GHz)

### Why 10 GHz (not 5.8, 24, or 77 GHz)?
- **Chosen:** 10.0–10.1 GHz (X-band)
- **Why:** Full German amateur allocation (10.000–10.500 GHz); affordable X-band components available; λ/2 = 15 mm → manageable array size; reasonable atmospheric attenuation; good range/resolution trade-off
- **Rejected:** 5.8 GHz (no full amateur allocation in Germany, ISM only); 24 GHz (higher cost, smaller allocation window, components harder to source); 77 GHz (automotive radar band, not amateur, extremely expensive)

### Why 4×4 Array (not 8×8)?
- **Chosen:** 4×4 = 16 elements per TX/RX
- **Why:** Budget ($8k limit); manageable PCB size; 32 phase shifters = 2 SPI buses on STM32; 22° beam width acceptable for experimental use; 24 dBi gain gives 2–5 km range
- **Rejected:** 8×8 (64 elements per array = 128 phase shifters → 8 SPI buses, much higher cost ~$4k just for phase shifters, larger PCB)
- **Path forward:** MIMO operation possible — TX and RX 4×4 arrays give virtual 8×8 = 64 elements → 11° beam width

### Why Analog Beamforming (not Digital)?
- **Chosen:** Analog beamforming (phase shifters at RF)
- **Why:** Cost — single ADC vs 32 ADCs; simpler architecture; real-time beam steering; sufficient for research purposes
- **Rejected:** Digital beamforming (per-element ADC would cost ~$30k+ and require FPGA)

### Why HMC647ALP5E?
- Only 6-bit digital MMIC phase shifter available at 10 GHz from distributors in small quantity; good enough precision (5.625° LSB); QFN-32 solderable with hot air; ~$35/pc

### Why ADF4159?
- Built-in hardware FMCW sawtooth ramp generator → no CPU-generated chirp needed; excellent phase noise; supports 10 GHz easily; SPI programmable; ~$28

### Why STM32H743?
- 6 SPI buses needed for 32 phase shifters (2 buses) + ADF4159 + ADS8661 + future expansion; 480 MHz for real-time control; USB FS built-in; abundant GPIO; affordable (~$18); STM32CubeIDE ecosystem

### Why Raspberry Pi 5?
- Best price/performance for Python DSP (~80$); USB3 for ADC streaming; quad-core A76 handles 100k-point FFT; large software ecosystem; GPIO for future hardware control
- Upgrade path: NVIDIA Jetson Nano for GPU-accelerated processing

---

## SECTION 4: CURRENT PROJECT STATUS

| Area | Status | Notes |
|---|---|---|
| Documentation (8 docs) | ✅ Complete | All in Documentation/ folder |
| Hardware docs (4 docs) | ✅ Complete | System_Architecture, Electronics, Components, Interface |
| RF System docs (4 docs) | ✅ Complete | RF_Architecture, Antenna, Array, Components |
| PCB schematics (4 JSON) | ✅ Complete | EasyEDA Standard JSON — import and route |
| STL files (6 files) | ✅ Complete | Basic solid models — refine in FreeCAD for production |
| STL generator script | ✅ Complete | Mechanical/CAD/generate_stl.py |
| Firmware (main.c) | ✅ Complete | STM32H743, tested only by code review |
| Firmware (phase_shifter) | ✅ Complete | phase_shifter.c/h |
| Firmware (adf4159) | ✅ Complete | adf4159.c/h |
| Firmware (Makefile) | ✅ Complete | arm-none-eabi-gcc |
| Control software | ✅ Complete | aeris_control.py, config.yaml, requirements.txt |
| Signal processing | ✅ Complete | fmcw_processing.py, visualization.py, data_logger.py, calibration.py |
| Demo (no hardware) | ✅ Complete | demo_no_hardware.py — test processing without hardware |
| OpenEMS simulation | ✅ Complete | openems_antenna_simulation.py |
| Link budget calculator | ✅ Complete | link_budget_calculator.py |
| BOM spreadsheet | ✅ Complete | BOM.csv (60 line items with prices) |
| Budget spreadsheet | ✅ Complete | Budget.csv |
| Timeline spreadsheet | ✅ Complete | Timeline.csv (24-week schedule) |
| Excel generator | ✅ Complete | generate_spreadsheets.py |
| Testing docs (3 docs) | ✅ Complete | Calibration, Measurement Plans, Validation |
| AI Context | ✅ Complete | This file + DESIGN_HISTORY, TODO, FUTURE_AI_INSTRUCTIONS |
| Wiring diagram | ✅ Complete | Hardware/Wiring_Diagram.md |
| STEP model docs | ✅ Complete | Mechanical/CAD/STEP_Model_Description.md |
| **Hardware built** | ❌ NOT STARTED | All above is design only |
| **Hardware tested** | ❌ NOT STARTED | |
| **BNetzA consulted** | ❌ NOT DONE | Contact before field operation |
| **EM simulation run** | ❌ NOT DONE | Run openems_antenna_simulation.py |
| **PCB layouts done** | ❌ NOT DONE | Schematics done, layouts need EasyEDA work |

---

## SECTION 5: COMPLETE FILE INVENTORY

```
HASE-Radar/
├── README.md                                     Project overview and quick start
│
├── Documentation/
│   ├── 01_Project_Specification.md               Full project spec (2000+ words)
│   ├── 02_Engineering_Requirements.md            Requirements with IDs (2500+ words)
│   ├── 03_System_Design_Document.md              System design with block diagrams
│   ├── 04_Regulatory_Analysis_Germany.md         German amateur radio legal analysis
│   ├── 05_Safety_Documentation.md                RF safety, electrical safety
│   ├── 06_Test_Procedures.md                     Complete test procedures
│   ├── 07_Assembly_Documentation.md              Assembly steps
│   └── 08_Maintenance_Documentation.md           Maintenance and fault diagnosis
│
├── Hardware/
│   ├── System_Architecture.md                    Hardware block diagram and subsystems
│   ├── Electronics_Documentation.md              PCB stack, grounding, SPI map
│   ├── Component_Research.md                     Component selection rationale
│   ├── Interface_Documentation.md                Connector pinouts, protocols
│   └── Wiring_Diagram.md                         Complete ASCII wiring diagrams
│
├── RF_System/
│   ├── RF_Architecture.md                        RF signal chain, link budget
│   ├── Antenna_Concept.md                        Patch antenna design
│   ├── Array_Design.md                           Phased array mathematics
│   ├── RF_Component_Analysis.md                  NF, phase noise analysis
│   ├── openems_antenna_simulation.py             OpenEMS EM simulation script
│   └── link_budget_calculator.py                 Radar range equation calculator
│
├── PCB/
│   ├── EasyEDA_Projects/
│   │   ├── AERIS_MainBoard/schematic.json        STM32H743 + ADF4159 + HMC733 board
│   │   ├── AERIS_RF_Frontend/schematic.json      PA + Phase shifters + LNA + Mixer
│   │   ├── AERIS_Power_Board/schematic.json      24V → 5V/3.3V/±5V/12V
│   │   └── AERIS_PhaseShifter_Board/schematic.json 16x HMC647A array board
│   ├── Manufacturing_Notes.md                    PCB fab specifications
│   └── Assembly_Notes.md                         PCB assembly instructions
│
├── Mechanical/
│   ├── STL/
│   │   ├── main_enclosure.stl                    300×200×100 mm box (ASCII STL)
│   │   ├── antenna_panel.stl                     200×120×5 mm panel
│   │   ├── tripod_mount_adapter.stl              100×80×68 mm L-bracket
│   │   ├── electronics_tray.stl                  280×180×12 mm tray
│   │   ├── cooling_fan_bracket.stl               80×80×4 mm fan plate
│   │   └── front_panel.stl                       300×100×5 mm front panel
│   ├── CAD/
│   │   ├── generate_stl.py                       Parametric STL generator (Python)
│   │   └── STEP_Model_Description.md             Dimensions and manufacturing notes
│   ├── dimensions.md                             All mechanical dimensions
│   └── Assembly_Instructions.md                  Mechanical assembly steps
│
├── Software/
│   ├── Embedded/firmware/
│   │   ├── main.c                                STM32H743 main firmware
│   │   ├── phase_shifter.c / .h                  HMC647A driver
│   │   ├── adf4159.c / .h                        ADF4159 FMCW PLL driver
│   │   └── Makefile                              arm-none-eabi-gcc build system
│   ├── Control/
│   │   ├── aeris_control.py                      PC-side radar control application
│   │   ├── config.yaml                           System configuration
│   │   ├── requirements.txt                      Python dependencies
│   │   └── README.md                             Control software user guide
│   └── Signal_Processing/
│       ├── fmcw_processing.py                    FMCW DSP pipeline (range/Doppler/CFAR)
│       ├── visualization.py                      Radar display (range profile, RDM, PPI)
│       ├── data_logger.py                        HDF5 data logging
│       ├── calibration.py                        Phase + amplitude calibration
│       └── demo_no_hardware.py                   Full demo with synthetic data
│
├── Spreadsheets/
│   ├── BOM.csv                                   60+ line item BOM with prices
│   ├── Budget.csv                                Cost breakdown by category
│   ├── Timeline.csv                              24-week project schedule
│   └── generate_spreadsheets.py                  Generates .xlsx from CSV data
│
├── Testing/
│   ├── Calibration_Procedures.md                 Step-by-step calibration
│   ├── Measurement_Plans.md                      Test measurement plans
│   └── Validation_Methods.md                     Validation criteria and methods
│
└── AI_Context/
    ├── PROJECT_MEMORY.md                         ← THIS FILE — start here
    ├── DESIGN_HISTORY.md                         Design decision log
    ├── TODO.md                                   Prioritized task list
    └── FUTURE_AI_INSTRUCTIONS.md                 Instructions for future AI sessions
```

---

## SECTION 6: OPEN QUESTIONS AND UNRESOLVED ISSUES

1. **BNetzA Consultation** (CRITICAL): Contact Bundesnetzagentur before any field operation. Email: poststelle@bnetza.de, Phone: +49 228 14-0. Reference: §67 TKG experimental station permit. Ask about: FMCW radar operation under Klasse A license, power level 1W, frequency 10.000–10.100 GHz.

2. **PCB Layout** (HIGH): EasyEDA JSON schematics are complete and importable. PCB layout (component placement and routing) has NOT been done. This is the most time-consuming next step. Priority: start with Power Board (simplest), then Main Board, then Phase Shifter Board, then RF Frontend (most complex).

3. **EM Simulation** (HIGH): Patch antenna dimensions (L=13.8mm, W=8.0mm) are analytically computed but NOT verified with EM simulation. Run `python openems_antenna_simulation.py --mode analytical` first, then set up full EM simulation. Expected: S11 < -15 dB at 10.05 GHz ± 50 MHz bandwidth.

4. **HMC647A Availability** (HIGH): Check Mouser stock immediately. These parts can have 8-16 week lead times. Order early.

5. **ADF4159 Register Calculation** (MEDIUM): The register values in adf4159.c are computed but not verified on hardware. Use Analog Devices ADIsimPLL tool to verify register values before ordering PCBs. The DEV_WORD calculation produces 10.05 GHz → 10.100 GHz in ~1 ms but may have small errors.

6. **PA Heatsink Design** (MEDIUM): HMC451LS6GE dissipates ~5W. Heatsink design not fully detailed. Need: 50 cm² Cu heatsink or forced-air cooled finned heatsink. Calculate: Rth_heatsink = (70°C - 40°C ambient) / 5W = 6 °C/W required.

7. **Cable Phase Matching** (MEDIUM): The 32 antenna feed cables must be phase-matched within ±3° at 10 GHz. Physical trimming process described in Wiring_Diagram.md but requires VNA to execute.

8. **STM32 HAL Initialization** (LOW): main.c calls MX_GPIO_Init(), MX_SPI1_Init(), etc. These functions are generated by STM32CubeMX and are NOT included in the firmware files. Use STM32CubeMX to generate the project, then add aeris firmware files.

9. **EasyEDA JSON Compatibility** (LOW): JSON files are in EasyEDA Standard 6.x format. EasyEDA Pro (new version) may need different format. Test by importing into EasyEDA at easyeda.com.

---

## SECTION 7: NEXT STEPS (PRIORITIZED)

### IMMEDIATE (This week)
1. Check Mouser stock for HMC647ALP5E — if in stock, place order immediately
2. Import EasyEDA JSON files into EasyEDA Standard (easyeda.com) and verify import
3. Run `python RF_System/link_budget_calculator.py --sweep --plot` to verify range predictions
4. Run `python Software/Signal_Processing/demo_no_hardware.py --scenario default` to test processing

### SHORT TERM (2-4 weeks)
5. Contact BNetzA for pre-consultation
6. Generate STM32CubeMX project for STM32H743ZIT6 (clock config, SPI config, USB)
7. Run OpenEMS antenna simulation to verify patch dimensions
8. Begin PCB layout in EasyEDA (start with Power Board)

### MEDIUM TERM (1-3 months)
9. Complete all 4 PCB layouts and order from PCBWay/JLCPCB
10. Order all components (see BOM.csv, focus on HMC647A first)
11. Test firmware on STM32 Nucleo-H743ZI eval board first
12. Assemble Power Board, test voltage rails

### LONG TERM (3-6 months)
13. Complete hardware assembly and integration
14. Phase calibration
15. Range measurements in lab
16. Field testing (after BNetzA clearance)
17. Open-source publication on GitHub

---

## SECTION 8: INSTRUCTIONS FOR FUTURE AI SYSTEMS

When you receive this project in a future session:

1. **Read this file first**, then `Documentation/03_System_Design_Document.md`
2. **Do not change the system architecture** without documenting a compelling technical reason
3. **Do not change component selections** without checking Component_Research.md alternatives
4. **Always check regulatory compliance** for any frequency or power changes
5. **The canonical specs are in SECTION 2 of this file** — not scattered through other files
6. **EasyEDA JSON format** is EasyEDA Standard 6.x — do NOT convert to EasyEDA Pro format without testing
7. **STM32 firmware** targets STM32H743ZIT6, HAL library, build with arm-none-eabi-gcc via Makefile
8. **Python software** targets Python 3.10+ on both Windows and Linux (Raspberry Pi OS)
9. **Budget constraint** is $8,000 USD total — current base design is $4,451 — $3,549 margin
10. **German regulatory constraint** — operation must comply with AFuG 2017, AFuV 2017, DARC band plan

**Fixed parameters (do not change):**
- Frequency: 10.000–10.100 GHz (amateur band, FMCW chirp)
- Array: 4×4 TX + 4×4 RX (32 elements total)
- Phase shifter: HMC647ALP5E (6-bit)
- MCU: STM32H743ZIT6
- Antenna substrate: Rogers RO4003C, 0.508 mm
- Element spacing: 15 mm (λ/2)

---

## SECTION 9: GLOSSARY

| Term | Meaning in This Project |
|---|---|
| AERIS-10P | Project name: Affordable Experimental Radar Intelligence System, 10 GHz Phased Array |
| FMCW | Frequency Modulated Continuous Wave — our radar waveform |
| PLL | Phase-Locked Loop — ADF4159 controls VCO for precise frequency |
| VCO | Voltage-Controlled Oscillator — HMC733, generates 10 GHz |
| PA | Power Amplifier — HMC451, amplifies TX signal to +29 dBm |
| LNA | Low-Noise Amplifier — HMC1040, amplifies received signal |
| Phase Shifter | HMC647A — digital control of RF signal phase for beam steering |
| Wilkinson | Wilkinson power divider/combiner — splits or combines RF signals |
| SPI | Serial Peripheral Interface — how STM32 controls phase shifters and ADF4159 |
| CDC-ACM | USB Communication Device Class — how STM32 talks to PC |
| CFAR | Constant False Alarm Rate — adaptive radar detection threshold |
| RDM | Range-Doppler Map — 2D plot of detected targets vs range and velocity |
| PPI | Plan Position Indicator — top-down radar display |
| CPI | Coherent Processing Interval — block of chirps processed together (100 chirps = 100 ms) |
| EIRP | Effective Isotropic Radiated Power = TX power × antenna gain |
| PEP | Peak Envelope Power — how German law measures TX power limit (75 W) |
| Klasse A | German amateur radio full license (Amateurfunkklasse A) |
| BNetzA | Bundesnetzagentur — German telecommunications regulator |
| AFuG | Amateurfunkgesetz — German Amateur Radio Act |
| DARC | Deutscher Amateur-Radio-Club — German amateur radio organization (band plan) |
| RO4003C | Rogers RO4003C — RF PCB substrate (εr=3.55, low loss) |
| QFN | Quad Flat No-lead — IC package type used by many HMC parts |
| LQFP | Low-Profile Quad Flat Package — STM32H743 package (144 pins) |
| SWD | Serial Wire Debug — programming/debugging interface for STM32 |
| HMC | Hittite Microwave Corporation — now Analog Devices, makes many RF ICs used here |
