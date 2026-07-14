# AERIS-10P — Affordable Experimental Radar Intelligence System
## 10 GHz Phased Array Radar Platform

**Version:** 1.0 | **Status:** Design Phase Complete | **Date:** 2026-07-14  
**Budget Target:** < $8,000 USD | **Operating Frequency:** 10.0–10.1 GHz (X-band)

---

## What Is This?

AERIS-10P is a complete open-source engineering design for a 10 GHz FMCW phased-array radar, inspired by the AERIS-10 N project. It is designed to be:

- **Legal in Germany** under a Klasse A amateur radio license (10.000–10.500 GHz band)
- **Affordable** at under $8,000 USD for a complete system
- **Educationally valuable** for learning radar engineering, phased arrays, and RF systems
- **Real hardware** — not a simulation; designed to actually be built and operated

**Target performance:**
- Range: 2–5 km (car-sized targets, σ = 10 m²)
- Range resolution: 1.5 m
- Beam width: ~22° (4×4 array)
- Beam steering: ±45° azimuth and elevation
- TX power: 1 W (+30 dBm) — well within 75 W PEP legal limit

---

## Repository Structure

```
HASE-Radar/
├── Documentation/          # All engineering documents (specs, regs, procedures)
│   ├── 01_Project_Specification.md
│   ├── 02_Engineering_Requirements.md
│   ├── 03_System_Design_Document.md
│   ├── 04_Regulatory_Analysis_Germany.md
│   ├── 05_Safety_Documentation.md
│   ├── 06_Test_Procedures.md
│   ├── 07_Assembly_Documentation.md
│   └── 08_Maintenance_Documentation.md
│
├── Hardware/               # Hardware architecture and component selection
│   ├── System_Architecture.md
│   ├── Electronics_Documentation.md
│   ├── Component_Research.md
│   └── Interface_Documentation.md
│
├── RF_System/              # RF design: architecture, antenna, array, components
│   ├── RF_Architecture.md
│   ├── Antenna_Concept.md
│   ├── Array_Design.md
│   └── RF_Component_Analysis.md
│
├── PCB/                    # EasyEDA schematic files + manufacturing notes
│   ├── EasyEDA_Projects/
│   │   ├── AERIS_MainBoard/        schematic.json
│   │   ├── AERIS_RF_Frontend/      schematic.json
│   │   ├── AERIS_Power_Board/      schematic.json
│   │   └── AERIS_PhaseShifter_Board/ schematic.json
│   ├── Manufacturing_Notes.md
│   └── Assembly_Notes.md
│
├── Mechanical/             # 3D models + CAD scripts
│   ├── STL/
│   │   ├── main_enclosure.stl      (300×200×100mm electronics box)
│   │   ├── antenna_panel.stl       (200×120×5mm antenna mount)
│   │   ├── tripod_mount_adapter.stl
│   │   ├── electronics_tray.stl
│   │   ├── cooling_fan_bracket.stl
│   │   └── front_panel.stl
│   ├── CAD/generate_stl.py         (parametric STL generator)
│   ├── dimensions.md
│   └── Assembly_Instructions.md
│
├── Software/
│   ├── Embedded/firmware/          # STM32H743 C firmware
│   │   ├── main.c
│   │   ├── phase_shifter.c / .h
│   │   ├── adf4159.c / .h
│   │   └── Makefile
│   ├── Control/                    # PC-side Python control app
│   │   ├── aeris_control.py
│   │   ├── config.yaml
│   │   ├── requirements.txt
│   │   └── README.md
│   └── Signal_Processing/          # FMCW DSP pipeline
│       ├── fmcw_processing.py
│       ├── visualization.py
│       ├── data_logger.py
│       └── calibration.py
│
├── Spreadsheets/
│   ├── BOM.csv                     (70+ components with prices)
│   ├── Budget.csv                  (cost breakdown by category)
│   ├── Timeline.csv                (24-week project schedule)
│   └── generate_spreadsheets.py    (generates .xlsx from CSV data)
│
├── Testing/
│   ├── Calibration_Procedures.md
│   ├── Measurement_Plans.md
│   └── Validation_Methods.md
│
└── AI_Context/             # Handover documents for future sessions
    ├── PROJECT_MEMORY.md   ← START HERE if you're resuming this project
    ├── DESIGN_HISTORY.md
    ├── TODO.md
    └── FUTURE_AI_INSTRUCTIONS.md
```

---

## Quick Technical Summary

| Parameter | Value |
|---|---|
| Frequency | 10.0–10.1 GHz (FMCW, 100 MHz chirp BW) |
| Array | 4×4 TX + 4×4 RX = 32 patch antennas |
| Phase Shifter | HMC647ALP5E (6-bit, 0–360°) |
| VCO/PLL | HMC733 + ADF4159 FMCW generator |
| TX PA | HMC451LS6GE (+30 dBm / 1 W) |
| RX LNA | HMC1040LP4E (NF 1.5 dB) |
| Antenna Gain | ~22 dBi (TX + RX combined array) |
| MCU | STM32H743ZIT6 (480 MHz) |
| Processing | Raspberry Pi 5 (8 GB) |
| Power | 24 V DC, max 8 A |
| Weight | ~5 kg complete |
| Budget | ~$4,565 base / $8,000 max |

---

## German Amateur Radio Compliance

Operating frequency **10.000–10.100 GHz** falls within the **German 3 cm amateur band (10.000–10.500 GHz)**.

- **License required:** Klasse A (full amateur radio license)
- **Our TX power:** 1 W = +30 dBm (legal limit: 75 W PEP)
- **EIRP:** ~52 dBm (1 W × 22 dBi array gain)
- **Emission type:** FMCW (F3E/F7X equivalent — permitted)
- **Station ID:** required every 10 minutes (implemented in firmware)

⚠️ **Before field operation:** Contact BNetzA (Referat 221) for informal consultation on radar-type experimental operation. See `Documentation/04_Regulatory_Analysis_Germany.md` for full analysis.

---

## Getting Started

### 1. Understand the design
Read `Documentation/03_System_Design_Document.md` for the full system overview.

### 2. Review the BOM
Open `Spreadsheets/BOM.csv` in Excel/LibreOffice to see all components and prices.

### 3. Open PCB schematics
Import `PCB/EasyEDA_Projects/AERIS_MainBoard/schematic.json` into EasyEDA Standard (web app at easyeda.com) using **File → Import → EasyEDA JSON**.

### 4. Print mechanical parts
Open STL files from `Mechanical/STL/` in your slicer (PrusaSlicer, Cura). Print in PETG at 30% infill for prototype. Order machined aluminium for field-use version.

### 5. Set up software development environment
```bash
# On Raspberry Pi 5 (processing computer):
pip install -r Software/Control/requirements.txt

# Test signal processing without hardware:
python Software/Signal_Processing/fmcw_processing.py --demo

# Compile firmware (requires arm-none-eabi-gcc):
cd Software/Embedded/firmware
make all
```

---

## Key Design Choices

| Choice | Selected | Why |
|---|---|---|
| Waveform | FMCW | Low peak power, amateur-legal, simpler ADC |
| Frequency | 10 GHz | Full German amateur allocation, good component availability |
| Beamforming | Analog phase array | 10× cheaper than digital beamforming |
| Array size | 4×4 | Budget/complexity vs performance trade-off |
| Processing | Raspberry Pi 5 | Best price/performance for Python DSP |
| Antenna substrate | Rogers RO4003C | Industry standard, PCB-house available |

Full rationale in `Hardware/Component_Research.md` and `AI_Context/DESIGN_HISTORY.md`.

---

## License

Open-source for educational and amateur radio research use.  
**Not for commercial deployment. Always comply with local telecommunications regulations.**

---

*Generated 2026-07-14 as part of the HASE-Radar experimental radar development project.*
