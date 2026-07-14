# AERIS-10P Assembly Documentation
## Rev 1.0 — AERIS-10P Affordable Experimental Radar Intelligence System, 10 GHz Phased Array

**Document Number:** AERIS-ASY-001  
**Revision:** 1.0  
**Date:** 2026-07-14  
**Author:** RF Systems Engineering  
**Status:** Released  

---

## 1. Scope

This document provides complete assembly instructions for the AERIS-10P radar system. It covers all printed circuit board assemblies, the Rogers RO4003C antenna panel, chassis integration, RF cabling, power wiring, and software installation. The document is intended for use by a technician with experience in SMD assembly and RF system integration.

Read this document in its entirety before commencing any assembly. The sequence of steps is mandatory; components installed in the wrong order may damage parts or make later assembly steps impossible.

---

## 2. Required Tools

| Tool | Specification | Purpose |
|------|--------------|---------|
| Soldering station | Weller WX2 or JBC DDSE, 350°C set point, fine conical tip | SMD and through-hole soldering |
| Hot air rework station | Hakko FR-872B or Metcal MFR-H1-DS, 350–380°C, 30–50 L/min airflow | QFN rework, component removal |
| SMD stencil | Laser-cut stainless steel, 0.12 mm thick, matched to each PCB paste layer | Solder paste application |
| Stencil printer (manual) | DEK or manual alignment jig | Consistent paste application |
| Microscope | Stereo, 10–40× magnification, LED illumination | Solder joint inspection |
| Digital multimeter | Fluke 87V or equivalent, 4.5-digit | Continuity, voltage measurement |
| Torque screwdriver | 0.1–1.0 Nm range, 1/4" drive with Torx and Phillips bits | M3 fasteners at correct torque |
| SMA torque wrench | 5/16" (8 mm) hex, calibrated to 0.9 Nm (8 in-lb) | SMA connector tightening |
| Nylon spanner / wrench | 5/16" (SMA), no-mar jaw | SMA connector tightening without PCB damage |
| Anti-static mat and wrist strap | Certified ESD workstation, <1 MΩ resistance | ESD protection |
| Reflow oven | Puhui T-962A or equivalent, 260°C peak profile | PCB reflow |
| X-ray (recommended) | Nordson DAGE Quadra 7 or equivalent | Verify QFN solder joints |
| Tweezers | Stainless, non-magnetic, fine tip (SS-SA or equivalent) | SMD component placement |
| Flux pen | Kester 951 or MG Chemicals 8341 | Touch-up soldering |
| Desoldering wick | 2.0 mm and 3.0 mm braid | Solder removal and rework |
| Pin header jig | Alignment fixture for connectors | Header placement |

---

## 3. Required Materials

| Material | Specification | Use |
|----------|--------------|-----|
| Solder paste | Kester R256 Sn63Pb37 (−20°C storage) or Kester SAC305 lead-free, Type 4 powder | PCB assembly |
| Solder wire | Kester 44 Sn63Pb37, 0.5 mm diameter, or SAC305 equivalent | Touch-up, connectors |
| IPA flux remover | MG Chemicals 99.9% isopropyl alcohol | Post-solder board cleaning |
| Flux remover brush | ESD-safe bristle brush, 1" wide | Board cleaning |
| Kapton (polyimide) tape | 25 mm width, 68 µm total thickness | Masking, connector protection |
| Thermal interface material | Bergquist GP3000 pad or Shin-Etsu X-23-7921-5 paste, >3 W/m·K | IC-to-heatsink/chassis |
| Thread locker | Loctite 243 (medium strength, blue) | M3 fasteners in aluminium |
| M3 fastener kit | M3 × 6 mm, M3 × 8 mm, M3 × 10 mm cap-head, M3 × 5 mm BHCS, M3 nyloc nut, M3 flat washer | All structural fasteners |
| M5 ring terminal | Crimp, insulated, 10 mm lug, for 2.5 mm² cable | 24 V power input |
| AWG 18 wire | Silicone insulation, 600 V, 15 A rated | Internal power wiring |
| AWG 24 wire | PTFE, 0.1 mm² stranded | Signal and low-current wiring |
| Cable ties | 2.5 mm × 100 mm, nylon | Cable management |
| Heat shrink | 3:1 ratio, adhesive-lined, 3 mm and 6 mm diameter | Wire protection |
| Conformal coating | Humiseal 1B31 or MG Chemicals 419C (selective application to non-RF areas) | Environmental protection |
| Anti-static bags | Component-safe, pink or metallic shielding | Component storage |
| Desiccant | Silica gel sachets, 5 g | Storage |
| Polyimide label stock | Brady THT-170-499-2.5 or equivalent | Connector labelling |

---

## 4. PCB Assembly Sequence

### 4.1 General PCB Assembly Rules

- All PCB assembly must be performed at an ESD-safe workstation with technician wearing a grounded wrist strap.
- Inspect all PCBs for mechanical damage (cracked vias, scratched traces) before applying solder paste.
- Verify component orientation before and after placement. Pay particular attention to polarised components (capacitors, diodes, ICs).
- Use the correct solder profile for the solder paste chosen. SAC305 requires a higher peak temperature (245–260°C) than Sn63Pb37 (183–210°C peak).
- Perform visual inspection (10× minimum magnification) of all solder joints after reflow and before applying power.

### 4.2 AERIS_Power_Board — Assembly Sequence

The AERIS_Power_Board contains the LT8612 (5 V / 5 A buck converter), LT8607 (3.3 V / 3 A buck converter), and TPS65133 (±5 V / 1 A inverting/boost for RF bias rails). Power board must be assembled and verified before installation into the main chassis.

**Step 1 — Board Inspection**
Inspect the bare PCB for correct layer stack-up (4-layer), correct silkscreen designators, via quality. The LT8612 and LT8607 are in QFN-16 packages with exposed thermal pads; the PCB must have a matching thermal land with solder mask-defined (SMD) pads.

**Step 2 — Stencil Paste Application**
1. Align the stencil over the PCB using the alignment jig or corner pin registration.
2. Apply Sn63Pb37 Type 4 paste across all pads using the squeegee in a single smooth pass at approximately 30° angle with 0.5–1 kg pressure. A 0.12 mm stencil produces approximately 70–80 µm paste height for this package size.
3. Lift the stencil straight up. Inspect paste deposits under the microscope: all pads should show uniform, well-defined deposits. The thermal pad aperture for QFN packages must show paste covering ≥70% of the pad area with window-pane aperture relief.

**Step 3 — Component Placement**
Place components in this order (smallest first to avoid disturbing placed parts):
1. Decoupling capacitors: 100 nF 0402 X5R (place all per schematic).
2. Bulk capacitors: 22 µF 0805 X5R on input and output rails.
3. Bootstrap capacitors: 100 nF 0402 on BST pins.
4. Enable resistors, feedback resistors: 0402.
5. Inductors: Bourns SRR6038 or equivalent (4.7 µH for LT8612, 10 µH for LT8607). These are large and can be placed with tweezers.
6. LT8612 QFN-16: align pin 1 indicator. Place carefully — thermal pad is under the IC.
7. LT8607 QFN-12.
8. TPS65133 QFN-24.

**Step 4 — Reflow**
Profile for Sn63Pb37: Preheat 150°C for 90 s, soak 150–170°C for 60 s, ramp to 210°C peak over 30 s, dwell at peak ≤10 s, cool at ≤3°C/s. Do not allow peak temperature to exceed 230°C; LT8612 has a maximum soldering temperature of 260°C, but lower is preferred.

**Step 5 — Through-Hole and Connector Assembly**
After reflow and cleaning: hand-solder the screw terminal blocks (Phoenix Contact or equivalent, 5.08 mm pitch, 3-way for 24 V in, 4-way for output distribution), electrolytic bulk capacitors (Panasonic FR series, 100 µF 35 V), and LED indicator.

**Step 6 — Power Board Verification**
Before installing the power board in the main chassis:
1. Connect 24 V bench supply (current limited to 0.5 A).
2. Measure all output voltages at the output headers. Refer to Phase 1 power tests (PT-001 through PT-005) in the test procedures document.
3. If any output is incorrect, debug before proceeding.
4. Apply correct resistive loads and verify thermal stability for 10 minutes before declaring the board ready for installation.

---

### 4.3 AERIS_RF_Frontend — Assembly Sequence

The RF Frontend board carries the following ICs: 16× HMC647ALP5E (5×5 QFN, 32 pads + thermal), 4× HMC1040LP4E (4×4 QFN, 24 pads + thermal), 4× HMC213B (4×4 QFN, 16 pads + thermal), and associated passives, SMA edge connectors, and SMA surface-mount connectors. This is the most demanding PCB to assemble due to the density and the RF performance requirements of the HMC devices.

**Substrate and Trace Preparation**
The RF Frontend board is on Rogers RO4003C (for the antenna) or on FR4 with RF-grade impedance control for the IC board. Inspect for board warpage; warpage ≥0.5 mm will affect stencil printing and must be corrected with a flat platen or stencil printer.

**Step 1 — Substrate Cleaning**
Clean the board surface with IPA and a lint-free cloth before applying paste. Allow 5 minutes to dry fully. Any flux or organic contamination will cause paste adhesion failures.

**Step 2 — Stencil Paste Application**
Use the 0.12 mm stencil designed for the HMC647A pad pattern. The HMC647ALP5E has 5×5 mm package with 0.5 mm pitch pads on four sides and a large exposed thermal pad underneath. Stencil apertures for the thermal pad must be segmented (window-pane pattern) to prevent paste bridging.

Step through each IC location. For the HMC647A thermal pad, confirm ≥70% paste coverage. Any paste bridging between adjacent pads must be corrected with a flux pen and brass mesh before placement.

**Step 3 — Pick-and-Place**
If a pick-and-place machine is available, use the centroid file for this board. For manual placement:

1. HMC647ALP5E (16 pieces): Using fine-tip vacuum tweezer. Align pin 1 marker (dot or chamfered corner on package) to the pin 1 pad on the PCB silkscreen. Do not press down hard — paste compression will cause bridging. After placement, verify alignment with the microscope at 20× before moving to the next component.
2. HMC1040LP4E (4 pieces): Similarly align pin 1. These are the RX LNAs. Handle with ESD precautions; these GaAs PHEMT devices are highly ESD-sensitive (HBM Class 1B).
3. HMC213B (4 pieces): These are the double-balanced mixers. The package is 4×4 QFN. Align per silkscreen.
4. Passive components: 0402 resistors and capacitors.

**Step 4 — Reflow**
For SAC305 solder paste: Preheat to 175°C for 90 s, soak 175–200°C for 60 s, ramp to 245°C peak over 45 s, dwell ≤15 s at peak, cool ≤3°C/s. Do not exceed 260°C at any point (GaAs IC maximum reflow temperature).

**Step 5 — X-Ray Inspection (Recommended)**
After reflow, perform X-ray inspection on all QFN components. Verify:
- No solder bridging between any pads
- Uniform solder joint height under the thermal pad (thermal pad voiding ≤25% acceptable; >25% requires rework)
- No solder balls

If X-ray is not available, perform the following continuity test as a functional substitute: with no power applied, use a precision capacitance meter to verify the bypass capacitors on each IC power pin read the expected capacitance value (indicating the IC is connected to its supply rail through the bypass). Bridged pads will cause obvious shorts measurable with the DMM.

**Step 6 — SMA Connector Soldering (Hand)**
SMA edge-launch connectors (2.92 mm male, Johnson 142-0761-851 or equivalent) must be soldered by hand using the soldering station. These connectors are through-hole or edge-mount; the body is held by 4× PCB mount tabs on the edge of the board.

1. Apply flux (Kester 951 pen) to all four tabs and the centre pin landing pad.
2. Tack one tab first to hold the connector square.
3. Verify squareness with a steel rule against the PCB edge. The connector flange must be flush with the PCB edge within ±0.1 mm.
4. Solder remaining tabs. Use sufficient solder to fill each tab completely.
5. Solder the centre pin to the trace landing pad: brief 1 s contact, 350°C tip, rosin-core solder.

**Step 7 — Board Cleaning**
Wash the populated board with IPA using a brush, then rinse with fresh IPA. Use compressed nitrogen to remove liquid from under components. Inspect under bright light for remaining flux residue; repeat cleaning if visible.

**Step 8 — RF Frontend Functional Test**
Before installing the RF Frontend board, perform a basic bias test:
1. Apply +5 V and −5 V RF bias rails.
2. Measure quiescent current on each rail. Compare to expected values (HMC647A: ~50 mA per IC; HMC1040: ~60 mA per IC; HMC213B: ~80 mA per IC).
3. An unexpectedly high or low current indicates a damaged device or assembly error. Identify and correct before proceeding.

---

### 4.4 AERIS_MainBoard — Assembly Sequence

The MainBoard carries: STM32H743ZIT6 (LQFP-144, 0.5 mm pitch), ADF4159CCPZ (CP-40-3, 0.5 mm pitch), HMC733LP6CE (LP-6 QFN/SMD), ADS8661IRGAT (QFN-20), ABRACON AOCJY-10 OCXO module (through-hole or SMD footprint), USB connectors, Ethernet PHY (if separate from STM32), SPI headers, and JTAG/SWD debug connector.

**Step 1 — Stencil and Paste**
Apply paste. The STM32H743 in LQFP-144 at 0.5 mm pitch requires a finely aligned stencil; use a precision stencil printer if possible. The ADF4159 in CP-40-3 (QFN-style, 40 pads on 6×6 mm package) requires window-pane thermal pad aperture.

**Step 2 — Component Placement**
1. All 0402 and 0603 passives.
2. ADS8661IRGAT (QFN-20, 4×4 mm).
3. ADF4159CCPZ (CP-40-3, 6×6 mm). Pin 1 orientation is critical for PLL operation.
4. HMC733LP6CE: this is in a 40-lead QFN/SMD laminate carrier package. Verify the land pattern matches the footprint. Ground paddle must make solid thermal contact with the PCB copper.
5. STM32H743ZIT6 (LQFP-144, 20×20 mm): use a placement tool for the large package if available. Align carefully — all 144 leads must register over their pads. The pin 1 marker is on the corner of the IC. Inspect alignment at 40× before reflow; a misplaced STM32 at 0.5 mm pitch will cause all leads on one side to bridge.
6. OCXO module (ABRACON AOCJY-10): follow manufacturer recommendation for placement — the OCXO requires controlled thermal environment. Place last, after all SMD components are reflowed.

**Step 3 — Reflow**
Standard profile. Inspect STM32 leads at 40× after reflow for any bridges. If bridges are found, apply flux pen and drag solder with a fine tip (0.3 mm chisel); use desoldering wick to remove excess.

**Step 4 — Post-Reflow Assembly**
By hand, after reflow:
- Install 2×20 pin GPIO header (for RPi5 connection or SPI bus)
- Install USB Type-A connector (host)
- Install USB Micro-B or USB-C connector (device/programming)
- Install RJ-45 Ethernet jack
- Install SWD debug header (2×5, 1.27 mm pitch, Tag-Connect or standard)
- Install screw terminal for 24 V input sense

**Step 5 — MainBoard Verification**
1. With 3.3 V applied, verify STM32 is not consuming excess current (nominal: 50–150 mA at 480 MHz with peripherals active).
2. Connect SWD probe (STM32 ST-LINK V3 Mini or J-Link). Attempt to read device ID. STM32H743 device ID = 0x450. If not readable, check SWD connections and 3.3 V supply.

---

## 5. Antenna Panel Assembly

### 5.1 PCB Procurement

The antenna panel is a single-layer Rogers RO4003C PCB with the following specifications:

| Parameter | Value |
|-----------|-------|
| Substrate | Rogers RO4003C |
| Thickness | 0.508 mm |
| εr | 3.55 |
| tan δ | 0.0027 |
| Copper | 1 oz (35 µm) electro-deposited on signal side, 1 oz on ground plane |
| Finish | Electroless Nickel Immersion Gold (ENIG) — do NOT specify HASL; HASL on Rogers is not compatible with 10 GHz patch performance |
| Dimensions | 200 mm × 120 mm |
| Drill | Vias for feed probe if used; otherwise microstrip feed line on top copper |
| Silkscreen | Top only, for element numbering |
| Solder mask | None on RF patch elements and feed lines; solder mask on connector pads only |

The patch dimensions are 13.8 mm × 13.8 mm, resonant at 10.05 GHz on this substrate. Element spacing is 15 mm (λ/2 at 10 GHz, λ = 30 mm). TX array: 4×4 elements, aperture 45 mm × 45 mm. RX array: 4×4 elements, aperture 45 mm × 45 mm. Total antenna panel dimensions: 200 mm × 120 mm.

### 5.2 Connector Soldering

The antenna panel uses 2.92 mm (K-connector) end-launch SMA connectors for the feed point connections to the RF Frontend board.

1. Verify connector footprint alignment with the antenna feed line on the copper layer.
2. Apply flux to the centre pin landing and body pads.
3. Solder with soldering station at 350°C. Apply minimum solder — excess solder on the centre conductor changes the characteristic impedance of the feed point.
4. Allow to cool 30 s before handling.
5. Mark each connector with a polyimide label: TX-01 through TX-16, RX-01 through RX-16, matching the element numbering on the silkscreen.

### 5.3 Antenna Panel Inspection

Before mounting, inspect the antenna panel:
- All 32 patch elements visible and undamaged
- Feed lines unbroken
- No copper contamination between feed lines and ground plane
- ENIG surface uniformly gold-coloured (no dark spots indicating dewetting)
- All SMA connectors seated flush and square

Perform a visual continuity check: the centre pin of each SMA connector should show continuity to the patch feed point trace. No continuity between centre pin and ground plane (ground plane is on the back side).

### 5.4 Antenna Panel Mounting

1. Place the antenna panel against the front face of the aluminium chassis. Align the 6× M3 mounting holes.
2. Install M3 × 6 mm cap-head screws with M3 flat washers and Loctite 243.
3. Tighten to 0.4 Nm with torque screwdriver. Over-tightening will bow the thin Rogers substrate.
4. Verify that the panel is flat against the chassis face (maximum gap 0.2 mm measured with feeler gauge at centre and corners).

---

## 6. Chassis Assembly

### 6.1 Chassis Specification

The AERIS-10P chassis is a custom aluminium enclosure: 300 mm × 200 mm × 100 mm. Material: 6061-T6 aluminium alloy, 2 mm wall thickness, anodised black. The chassis serves as the RF ground reference, thermal spreader, and structural frame. It includes:

- Front face: 200 mm × 100 mm, with 200 mm × 120 mm aperture for the antenna panel and M3 standoff inserts
- Rear face: M5 screw terminal for 24 V input, USB panel-mount connector, Ethernet panel-mount RJ-45, SMA bulkhead (for diagnostic port)
- Bottom: 3/8-16 UNC threaded insert (standard photo-tripod thread) for tripod mounting
- Internal: M3 threaded inserts (brass heat-set) for PCB tray, fan mount, cable management

### 6.2 Threaded Insert Installation

Install all brass M3 heat-set inserts before PCB installation:
1. Heat insert with the tip of the soldering iron at 200°C.
2. Press insert into the plastic bracket (if 3D-printed) or tighten screw-in inserts into aluminium chassis.
3. For the aluminium chassis, M3 threads are machined directly; verify threads with a thread gauge (M3×0.5) before assembly.

### 6.3 Electronics Tray Mounting

The electronics tray holds the three PCBs (Power Board, RF Frontend, MainBoard) on a 3 mm thick aluminium tray:

1. Mount AERIS_Power_Board to the tray with 4× M3×6 mm screws. Apply a 0.3 mm Bergquist thermal pad between the LT8612 and LT8607 packages and the aluminium tray surface (these ICs generate heat that must be conducted to the chassis).
2. Mount AERIS_RF_Frontend to the tray. Apply thermal paste (Shin-Etsu X-23-7921-5, sparingly — 0.1 mm layer) between the HMC451 PA exposed paddle and the tray. The PA is the primary heat source in the RF section.
3. Mount AERIS_MainBoard. STM32H743 and the OCXO module require moderate thermal management; use a thermal pad on the STM32 exposed paddle.
4. Apply Loctite 243 to all M3 screws before torquing to 0.35 Nm.

### 6.4 Cable Management and Routing

Cable routing sequence — always route in this order to avoid inaccessibility:

**RF Cables (First)**
Install all SMA RF cables before power or signal cables. Tight RF bends degrade signal quality and shorten cable life.
1. TX feed cables from HMC647A phase shifter outputs to the antenna feed SMA connectors.
2. RX feed cables from RX antenna SMA connectors to HMC1040 LNA inputs.
3. VCO output to ADF4159 reference / PLL input.
4. PA output cable (RG-405 semi-rigid from PA output to TX antenna panel distribution network).
5. Loop-back / calibration cable (internal 30 dB attenuator path).

Label each RF cable end with a polyimide heat-shrink label before installing the connector.

**Power Cables (Second)**
1. Run AWG 18 silicone wire from the 24 V screw terminal block on the power board to the chassis rear panel terminal.
2. Route power distribution cables from the power board output headers to the MainBoard and RF Frontend power input connectors.
3. Secure all power wires with cable ties at 50 mm intervals.

**Digital Signal Cables (Third)**
1. Flat flex cable (FFC) or ribbon cable from STM32 SPI headers to HMC647A phase shifter SPI bus.
2. USB cable from STM32 USB-HS port to Raspberry Pi 5 USB-A port.
3. SPI cable from STM32 to ADS8661 ADC input (keep short, ≤100 mm, to minimise capacitive loading).
4. GPIO cable for synchronisation signals (chirp trigger, frame sync) from STM32 to RPi5.

### 6.5 Cooling Fan Installation

Mount the 80 mm × 80 mm × 25 mm DC fan (5 V, ball-bearing, minimum 30 CFM) in the fan bracket on the rear of the chassis:
1. Orient fan to exhaust air out of the chassis (airflow: front → rear, across the PCB tray).
2. Mount with 4× M3×20 mm screws and rubber anti-vibration grommets (supplied with fan).
3. Connect fan to the +5 V rail via a 2-pin JST-XH connector. Wire with AWG 24 silicone.
4. Optionally connect fan tachometer output to STM32 GPIO for software fan speed monitoring.

### 6.6 Raspberry Pi 5 Installation

The Raspberry Pi 5 8GB mounts to a purpose-built bracket on the rear of the electronics tray:
1. Mount RPi5 to bracket with 4× M2.5 × 5 mm standoffs and M2.5 screws.
2. Apply a thermal pad (0.5 mm, 6 W/m·K) between the BCM2712 SoC and the bracket for heat spreading.
3. Connect: USB-A (RPi5) to USB-HS (STM32) data link; MicroHDMI to panel-mount HDMI (optional, for local display); USB-A (RPi5) to USB keyboard/mouse (for configuration, can be removed after commissioning).

---

## 7. RF Cabling

### 7.1 Semi-Rigid Coax (PA Output)

The PA output to the TX feed network uses RG-405 (0.086" semi-rigid, 50 Ω, SMA fittings):

1. Cut semi-rigid cable to the exact required length (measure with a string, then transfer to semi-rigid cutter or score-and-break tool).
2. Install SMA (m) connectors at each end using the crimp or solder attachment method per the connector manufacturer's assembly instructions.
3. Form any bends using a hand-bending tool or mandrel. Minimum bend radius for RG-405: 5 mm. Do not kink.
4. Measure insertion loss with VNA at 10 GHz. Maximum acceptable: 0.5 dB for a 100 mm length.

### 7.2 Phase Matching of TX Feed Cables

TX feed cables from the common TX source to the 16 phase shifter inputs must be electrically identical in length to within ±5° at 10 GHz (±1.4 mm physical length for solid PTFE cables).

**Phase matching procedure:**
1. Cut 16 TX feed cables to the same nominal physical length plus 5 mm excess.
2. Install connectors on all cables.
3. Using the VNA, measure S21 phase of each cable at 10.050 GHz relative to the reference cable (cable #1 or a reference airline).
4. Sort cables by measured electrical length. Cables within ±2.5° phase are matched pairs.
5. For cables outside ±2.5°, trim the physical length by 0.14 mm per degree and re-measure.
6. Record the measured electrical length of each cable on a cable record log. Install cables with their labels attached.

### 7.3 Flexible Coax (SMA)

For connections to the phase shifter board and ADC, use flexible SMA cables (086-equivalent, e.g., Huber+Suhner Sucoflex 104 or Times Microwave LMR-100A with SMA):
- Keep lengths ≤200 mm wherever possible.
- Dress all flexible cables with a minimum 50 mm bend radius.
- Label both ends of every cable before installation.
- Secure cables with cable ties — do not allow cables to press against sharp chassis edges.

---

## 8. Power Wiring

### 8.1 24 V Input Wiring

1. Install a chassis-mount screw terminal block (Phoenix Contact GMKD 3 or equivalent) on the rear panel for the 24 V input.
2. Wire the 24 V+ line with AWG 18 silicone, terminated at the chassis terminal with an M5 ring crimp terminal (0.5 Nm torque).
3. Install a 10 A inline automotive blade fuse holder in the 24 V+ line, within 100 mm of the input terminal. Use a 10 A fast-blow fuse (system maximum 8 A).
4. Connect 24 V return (GND) similarly; use AWG 18 green/yellow wire (or black per convention) with an M5 ring terminal.
5. Label the chassis terminal with a polyimide label: "24 V DC IN, 10 A MAX".

### 8.2 Internal Distribution

Run AWG 18 silicone wire from the power board output screw terminals to each consumer board:
- Use red for +V and black for GND consistently.
- Keep power wires away from RF cable routing by at least 10 mm.
- Install a ferrite bead on each power feed at the board entry connector (Fair-Rite 2643002402 or equivalent) to prevent RF from coupling onto the power wiring.

---

## 9. Software Installation

### 9.1 STM32 Firmware Installation

1. Install STM32CubeProgrammer (v2.14 or later) on the host PC.
2. Connect ST-LINK V3 Mini to the AERIS MainBoard 10-pin SWD header. Connect ST-LINK USB to the host PC.
3. In STM32CubeProgrammer: select "ST-LINK" interface, SWD mode, 4 MHz SWD frequency. Click "Connect". Verify device detected (STM32H743ZIT6, 2 MB flash).
4. Click "Open file" and select `AERIS_STM32_firmware_vX.X.X.bin` from the firmware release package.
5. Set start address: 0x08000000 (beginning of flash).
6. Click "Download". Programming takes approximately 15 seconds.
7. After completion, click "Disconnect". Remove ST-LINK.
8. Cycle power. Verify the heartbeat LED on the MainBoard flashes at 1 Hz, indicating firmware has started.
9. Open a serial terminal (115200 baud, 8N1) on the STM32 USB COM port. Verify the startup banner is printed: "AERIS-10P STM32 Firmware vX.X.X — READY".

### 9.2 Raspberry Pi 5 OS and Software Installation

**OS Installation:**
1. Using Raspberry Pi Imager (v1.8 or later) on a host PC, write "Raspberry Pi OS 64-bit (Bookworm)" to a 32 GB Class 10 microSD card or 64 GB USB SSD.
2. In the Imager advanced options: set hostname `aeris-radar`, enable SSH (public key authentication preferred), configure Wi-Fi or leave disabled.
3. Install the microSD or USB SSD in the RPi5. Boot.
4. After first boot, SSH into the RPi5: `ssh pi@aeris-radar.local`

**System Configuration:**
```
sudo raspi-config
# Interface Options → SPI → Enable
# Interface Options → I2C → Enable (if used)
# Interface Options → SSH → Enable
# Performance → GPU Memory → 128 MB
# Finish and Reboot
```

**Dependency Installation:**
```
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-numpy python3-scipy python3-matplotlib \
    python3-pyqt5 python3-serial python3-spidev \
    git build-essential cmake
```

**AERIS Software Package:**
```
cd /home/pi
git clone https://github.com/aeris-radar/aeris-software.git
cd aeris-software
pip3 install -r requirements.txt
sudo cp aeris-radar.service /etc/systemd/system/
sudo systemctl enable aeris-radar
sudo systemctl start aeris-radar
```

**SPI Bus Configuration:**
Add to `/boot/firmware/config.txt`:
```
dtparam=spi=on
dtoverlay=spi1-1cs
core_freq=250
```

Verify SPI bus is operating: `ls /dev/spidev*` should show `/dev/spidev0.0` and `/dev/spidev1.0`.

---

## 10. Initial Power-On Checklist

Complete this checklist in order before the first full-power-on of the assembled system.

| Step | Action | Expected Result | Check |
|------|--------|-----------------|-------|
| 1 | Visually inspect all RF connections — all SMA connectors fully tightened to 0.9 Nm | All connectors seated and tight | |
| 2 | Verify no short circuits: measure 24 V input impedance with DMM (Ohmmeter) | >100 Ω (not a dead short) | |
| 3 | Verify +5 V rail at test point TP1 | 4.9–5.1 V | |
| 4 | Verify +3.3 V at TP2 | 3.25–3.35 V | |
| 5 | Verify +5 V_RF at TP3 | 4.85–5.15 V | |
| 6 | Verify −5 V_RF at TP4 | −4.85 to −5.15 V | |
| 7 | Apply 24 V from bench supply, current limited to 1 A | Power LED illuminates; current <1 A | |
| 8 | Increase current limit to 5 A. Verify heartbeat LED on MainBoard | LED flashes at 1 Hz | |
| 9 | Verify fan operating | Fan spins, audible airflow | |
| 10 | Verify RPi5 boots (activity LED pattern) | Activity LED flashing during boot | |
| 11 | Connect to RPi5 via SSH | SSH login successful | |
| 12 | Start AERIS software (`aeris-selftest --basic`) | All basic checks PASS | |
| 13 | Verify PLL locks (check status LED on MainBoard or software status) | PLL_LOCK indicator green | |
| 14 | Verify no unexpected heat on PA board (check by touch after 2 min) | PA warm to touch, not burning hot | |

---

## 11. Post-Assembly Verification Checklist

After the initial power-on checklist is complete, proceed to the test procedures document (06_Test_Procedures.md) and execute Phase 1 through Phase 6 in order. The following abbreviated checklist confirms basic functionality before formal testing:

| Check | Procedure | Pass Criterion |
|-------|-----------|---------------|
| Power rails in tolerance | Measure with DMM at each rail test point | Per PT-002 limits |
| PLL lock at 10.050 GHz | Software status display | Lock detect HIGH |
| TX output detectable | SA at TX port (via 30 dB attenuator) | Signal present at 10.050 GHz |
| RX IF present | SA at IF output port | Signal present at IF frequency |
| SPI to phase shifters functional | Command all phase shifters to 0x3F, verify S21 phase changes | Phase changes on VNA |
| ADC reading | Software FFT display with loopback | Beat note visible |
| Beam steering at 0° | Boresight measurement with reference horn | Peak within ±2° of normal |
| Range detection | Corner reflector at 10 m | Detected within ±3 m |

---

*End of AERIS-10P Assembly Documentation Rev 1.0*

*Document controlled. Check repository for latest revision before use.*
