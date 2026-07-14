# AERIS-10P Project TODO
**Last updated:** 2026-07-14 | **Status:** Design complete, hardware phase starting

---

## CRITICAL (Do First)

- [ ] **Check HMC647ALP5E stock on Mouser** — 32 units needed. If stock < 50, order immediately. Long lead time (8-16 weeks) possible. Run `link_budget_calculator.py` first to confirm no design changes needed before ordering.
- [ ] **Import EasyEDA JSON files** — Open easyeda.com, File > Import > EasyEDA JSON, import all 4 files from PCB/EasyEDA_Projects/. Verify components appear correctly. Fix any format issues.
- [ ] **Contact BNetzA before field operation** — Email poststelle@bnetza.de. Subject: "Anfrage: FMCW-Radar unter Amateurfunklizenz Klasse A bei 10 GHz". Reference §67 TKG.

---

## HIGH PRIORITY

- [ ] **Generate STM32CubeMX project** — Open STM32CubeMX, select STM32H743ZIT6, configure: HSE 25 MHz crystal, PLL → 480 MHz HCLK, SPI1 (10 MHz AF5), SPI2 (10 MHz AF5), SPI3 (1 MHz AF6), SPI4 (1 MHz AF5), USB_FS (PA11/PA12), USART1 (PA9/PA10 115200 baud), ADC1 (for NTC). Generate HAL project, then merge with existing firmware files.

- [ ] **Run antenna EM simulation** — Install OpenEMS (conda install -c conda-forge openems). Run: `python RF_System/openems_antenna_simulation.py --mode analytical` (no hardware needed). Then `--mode setup` for full EM sim. Verify S11 < -15 dB at 10.05 GHz. If resonance is off, adjust L_patch by ±0.5 mm.

- [ ] **PCB layout — Power Board** (START HERE — simplest board)
  - Board: 100×80 mm, 2-layer FR4
  - Place LT8612 with L1, C3-C6 first
  - Place LT8607 with L2, C8-C9
  - Place TPS65133 with L3-L4
  - Place XT60 connector, fuse, reverse polarity MOSFET
  - Route 2mm power traces for 5A paths
  - Star ground at input capacitor
  - Export Gerbers and order from JLCPCB

- [ ] **PCB layout — Main Control Board**
  - Board: 160×100 mm, 4-layer FR4
  - Place STM32H743 centrally (144-pin)
  - Place ADF4159 near SPI3 pins
  - Place HMC733 VCO at corner with RF clearance
  - Place ADS8661 near SPI4 pins
  - Place OCXO module at corner
  - USB connector on board edge
  - Decouple all supply pins with 100nF 0402
  - Export Gerbers

- [ ] **Order RF components from Mouser** — Prioritize:
  1. HMC647ALP5E ×32+ (Mouser 597-HMC647ALP5E)
  2. HMC1040LP4E ×18 (Mouser 597-HMC1040LP4E)
  3. HMC213B ×2 (Mouser 597-HMC213B)
  4. HMC451LS6GE ×2 (Mouser 597-HMC451LS6GE)
  5. HMC733LP6CE ×2 (Mouser 597-HMC733LP6CE)
  6. ADF4159CCPZ ×2 (Mouser 584-ADF4159CCPZ)

- [ ] **Verify ADF4159 register values** — Use ADIsimPLL (free from Analog Devices website) to verify chirp register calculation in adf4159.c. Input: f_ref=10MHz, f_start=10.000GHz, f_stop=10.100GHz, sweep_time=1ms. Compare DEV_WORD and CLK_DIV with software output.

---

## MEDIUM PRIORITY

- [ ] **PCB layout — RF Frontend** (Most complex, save for last)
  - Board: 100×60 mm, 4-layer Rogers RO4003C
  - Impedance-controlled: 50Ω microstrip = 1.08 mm trace width
  - Place HMC451 PA at RF input with heatsink slug area
  - Place Wilkinson divider tree (PCB trace based)
  - Place 16× HMC647A in 4×4 grid pattern
  - Place 16× HMC1040 LNA in 4×4 pattern
  - Place HMC213B mixer
  - RF via fence along all RF traces
  - Add ground plane stitching vias every 5 mm
  - Order from PCBWay (specify RO4003C, controlled impedance)

- [ ] **PCB layout — Phase Shifter Boards** (2 identical boards: TX and RX)
  - Board: 120×80 mm, 4-layer hybrid Rogers/FR4
  - 16× HMC647A in 4×4 layout matching antenna element positions
  - SPI daisy-chain routing (U16→U15→...→U1)
  - RF distribution network (Wilkinson 1:4 + 4× 1:4)
  - 16× 2.92mm SMA edge-launch on board edge

- [ ] **Test firmware on Nucleo-H743ZI eval board** — Cheaper than custom PCB for firmware validation. Adapt GPIOs to Nucleo pinout. Test: USB CDC enumeration, SPI communication (use logic analyzer), ADF4159 lock detect.

- [ ] **Run `demo_no_hardware.py` tests** — `python Software/Signal_Processing/demo_no_hardware.py --scenario highway`. Verify processing pipeline, CFAR detection, visualization. Test with `--no-display --frames 50` for headless/CI testing.

- [ ] **Design PA heatsink** — HMC451LS6GE dissipates ~5W. Need heatsink with Rth < 6°C/W. Options: (a) Copper slug under PCB in Rogers board, (b) External TO-3 heatsink bonded with thermal paste, (c) Forced air from 80mm fan. Finalize design before PCB layout.

- [ ] **Install required software tools**:
  - STM32CubeIDE: st.com/stm32cubeide
  - OpenEMS: conda install -c conda-forge openems
  - Python deps: pip install -r Software/Control/requirements.txt
  - EasyEDA: easyeda.com (browser-based)
  - STM32CubeMX: st.com/stm32cubemx

---

## LOW PRIORITY

- [ ] **Refine STL models** — Current STL files are simple solid boxes. For production: (a) Add ventilation slots to enclosure, (b) Add connector cutouts to front panel, (c) Add PCB mounting bosses to electronics tray, (d) Use FreeCAD for parametric design.

- [ ] **Calibration software test** — Run `python Software/Signal_Processing/calibration.py` with test data. Verify calibration table generation and file format (.npy).

- [ ] **Excel spreadsheet generation** — Install openpyxl: `pip install openpyxl`. Run `python Spreadsheets/generate_spreadsheets.py` to generate formatted .xlsx files. Open in Excel and verify.

- [ ] **GitHub repository setup** — Create public repo at github.com. Include: all source files, README.md, LICENSE (CC BY-SA 4.0), .gitignore (exclude build artifacts), releases (firmware .bin files).

- [ ] **Write DARC community article** — Document the project for the DARC journal (Funkamateur or CQ DL). Share design files with amateur radio community. Contact DARC OV for possible club project support.

- [ ] **Amateur radio station identification** — Implement callsign beacon in firmware: every 600s, transmit CW callsign (Morsetext) as brief interrupt to normal FMCW operation. Command: CMD_SEND_ID in main.c.

- [ ] **Corner reflector fabrication** — Build trihedral corner reflector from 0.3m aluminum sheet (σ = ~133 m² = 21 dBsm). Use for range calibration test at 25 m. Dimensions: 3 equilateral triangles, 30cm edge.

- [ ] **Update PROJECT_MEMORY.md** after each major milestone (hardware assembly, first power-on, first detection).

---

## QUICK COMMANDS

```bash
# Test signal processing (no hardware needed):
python Software/Signal_Processing/demo_no_hardware.py --scenario highway

# Compute link budget:
python RF_System/link_budget_calculator.py --range-km 3 --rcs 10 --sweep

# Run antenna design calculations:
python RF_System/openems_antenna_simulation.py --mode analytical

# Generate Excel spreadsheets:
pip install openpyxl
python Spreadsheets/generate_spreadsheets.py

# Build STM32 firmware (requires arm-none-eabi-gcc):
cd Software/Embedded/firmware
make all

# Flash firmware (requires ST-Link):
make flash
```
