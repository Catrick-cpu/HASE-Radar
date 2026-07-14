# AERIS-10P PCB Manufacturing Notes
## Rev 1.0 — 2026-07-14

---

## Board Specifications Summary

| Board | Size | Layers | Substrate | Min Trace | Copper | Finish | Supplier |
|---|---|---|---|---|---|---|---|
| Main Control | 160×100 mm | 4 | FR4 | 0.15 mm | 1 oz | ENIG | JLCPCB |
| RF Frontend | 100×60 mm | 4 | Rogers RO4003C | 0.10 mm | 1 oz | ENIG | PCBWay |
| Power Board | 100×80 mm | 2 | FR4 | 0.20 mm (power) | 2 oz | HASL | JLCPCB |
| Phase Shifter | 120×80 mm | 4 | Rogers/FR4 hybrid | 0.10 mm | 1 oz | ENIG | PCBWay |
| Antenna Panel | 200×120 mm | 2 | Rogers RO4003C | 1.08 mm | 1 oz | ENIG | PCBWay |

---

## 1. AERIS Main Control Board (160×100 mm)

**Stackup (4-layer FR4):**
- Layer 1: Signal (components top)
- Layer 2: Ground (solid copper, RF shield)
- Layer 3: Power (+3.3V, +5V planes)
- Layer 4: Signal (bottom, digital routes)

**Specifications:**
- Board thickness: 1.6 mm
- Copper weight: 1 oz (35 µm)
- Min trace/space: 0.15/0.15 mm
- Min hole drill: 0.25 mm
- Min annular ring: 0.15 mm
- Surface finish: ENIG (immersion gold)
- Solder mask: green, both sides
- Silkscreen: white, both sides
- IPC Class 2

**Critical layout rules:**
- USB D+/D- traces: differential pair, 90Ω impedance (2.5 mm separation), max 50 mm length
- SPI traces: match length within group ±5 mm
- Crystal traces (OCXO): keep short (<20 mm), no other signals crossing underneath
- Decoupling caps: place within 0.5 mm of IC power pins
- Thermal relief: use solid connections on ground plane for RF ICs

**Test points:** Add test point pads (1mm) for: 5V, 3.3V, GND, SPI_SCK, USB_DP, USB_DM, NRST, ADF4159_LOCK

---

## 2. AERIS RF Frontend Board (100×60 mm)

**Stackup (4-layer Rogers RO4003C):**
- Layer 1: RF signal + components
- Layer 2: Ground (solid copper, RF ground plane)
- Layer 3: Power (5V, 3.3V supplies)
- Layer 4: Signal (SPI, control)

**Substrate specification:**
- Rogers RO4003C, 0.508 mm
- εr = 3.55 ± 0.05
- tan δ = 0.0027 at 10 GHz
- Copper: 1 oz (35 µm) electrodeposited
- Board thickness with prepreg: ~1.0 mm

**Critical RF specifications:**
- 50Ω microstrip trace width: 1.08 mm (on 0.508 mm RO4003C, εr=3.55)
- Tolerance on trace width: ±0.05 mm (controlled impedance order!)
- All RF traces must be 50Ω microstrip — specify controlled impedance 50Ω ±10%
- Minimum bend radius: 2× trace width (2.2 mm)
- Via fence: ground vias every 3 mm along all RF traces, 0.3 mm drill, 0.6 mm pad
- No 90° bends — use 45° or radius bends only
- Keep RF traces on Layer 1 only; no RF signals on other layers
- SMA connector footprints: verify manufacturer pad dimensions before layout

**Ordering notes:**
- Supplier: PCBWay (supports Rogers RO4003C, impedance control)
- Specify: "Controlled impedance 50Ω ±10% on layer 1"
- Specify: "Rogers RO4003C 0.508mm substrate, not FR4"
- Lead time: 2–4 weeks
- Price: ~$120 per board, order minimum 2

**Inspection requirements:**
- Impedance test coupon on board edge (order extra space for TDR coupon)
- Visual inspection of copper voids under QFN pads
- X-ray inspection of HMC647A, HMC1040, HMC213B solder joints recommended

---

## 3. AERIS Power Board (100×80 mm)

**Stackup (2-layer FR4):**
- Layer 1: Power supply components, wide traces
- Layer 2: Ground plane (solid copper)

**Critical layout rules:**
- Input 24V trace: minimum 3 mm width for 8A
- Output 5V trace: minimum 2 mm for 5A
- Star ground: all supply returns meet at single point near input capacitor
- LT8612 switching node (SW pin): minimize loop area between SW, L1, C_out
- LT8612 bootstrap cap: within 1 mm of BST pin
- LM7812: large copper thermal pad on layer 1 and 2, add external heatsink mount hole
- LED current resistors: near LEDs (reduce stray current in small traces)
- Bulk capacitor C1 (1000µF): as close to XT60 input as possible

**DRC rules:** 0.2 mm min clearance (power board has high currents, wider clearance safer)

---

## 4. AERIS Phase Shifter Board (120×80 mm)

**Stackup (4-layer hybrid Rogers/FR4):**
- Layer 1: Rogers RO4003C 0.508 mm (RF signal)
- Core 1: FR4 prepreg (structural)
- Layer 2: Ground (solid copper)
- Core 2: FR4 prepreg
- Layer 3: Power (+5V plane)
- Core 3: FR4 prepreg
- Layer 4: FR4 (SPI control signals)

Note: Ask PCBWay for Rogers/FR4 hybrid stackup. They offer this as "Rogers mixed" option. Layer 1 uses Rogers, remaining layers FR4.

**Critical specifications:**
- 50Ω on Layer 1 (Rogers): trace width 1.08 mm
- Component vias through all 4 layers: 0.3 mm drill
- RF via fence: 0.3 mm drill, 0.6 mm pad, every 5 mm
- HMC647A (5×5mm QFN-32): thermal pad must be soldered to ground plane via multiple vias
- Power distribution: 2mm trace for 5V supply line feeding all 16 ICs (1.44A total)

---

## 5. AERIS Antenna Panel (200×120 mm)

**Construction:**
- Rogers RO4003C, 0.508 mm, 2-layer
- Layer 1: Patch antennas, feed lines, Wilkinson dividers
- Layer 2: Continuous ground plane (no cuts)

**Patch element specifications:**
- Patch dimensions: L=13.8 mm, W=8.0 mm (verify with EM simulation)
- Feed point: inset microstrip at y0=3.4 mm from patch edge
- Feed line width: 1.08 mm (50Ω)
- Element spacing: 15 mm center-to-center (λ/2)
- Patch copper: 1 oz electrodeposited
- Ground plane: 1 oz, solid copper

**Ordering:**
- Surface finish: ENIG (immersion gold) — important for RF performance
- Do NOT use HASL (bumps on pads affect patch resonance)
- Via fencing on ground plane perimeter
- Supplier: PCBWay, specify "Rogers RO4003C 0.508mm, ENIG"

---

## 6. Gerber File Export from EasyEDA

1. Open schematic → click PCB view
2. Complete layout, run DRC
3. File → Export → Gerber (PCB Fabrication File)
4. Select: Include Drill File, Copper layers (all), Soldermask, Silkscreen, Board outline
5. Verify: Open Gerber in GerbView or KiCad Gerber Viewer before ordering
6. Check: All component footprints present, board outline closed, drill file matches pads
7. Upload to PCBWay or JLCPCB as .zip archive

---

## 7. Component Ordering Notes for PCB Assembly

If ordering with SMT assembly (PCBWay assembly service or JLCPCB):
- Export BOM from EasyEDA as CSV
- Match Mouser/LCSC part numbers in BOM
- Flag QFN packages as "difficult — requires X-ray inspection"
- Specify "no-clean flux" for RF boards
- RF connectors (SMA, 2.92mm): order separately, install after reflow
