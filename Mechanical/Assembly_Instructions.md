# AERIS-10P Mechanical Assembly Instructions
## Rev 1.0 — 2026-07-14

---

## Required Tools

| Tool | Specification | Use |
|---|---|---|
| Allen key set | M2, M3, M4, M5 hex | Fasteners |
| Torque screwdriver | 0.2–2 N·m | Calibrated tightening |
| SMA torque wrench | 5/16", 7/16" | RF connectors |
| Soldering iron | 350°C fine tip | Thread inserts (PETG) |
| 3D printer | PETG compatible | Print prototype parts |
| Drill press | 5–7mm bits | Front panel holes |
| File | Fine metal file | Deburring |

---

## Step 1: Prepare Electronics Tray

1. Print `electronics_tray.stl` in PETG (30% infill, 0.2mm layers)
   — OR machine from 2mm aluminium sheet
2. Install M3 threaded heat-set inserts at all 20 standoff positions:
   - Heat soldering iron to 200°C
   - Place insert on hole
   - Press gently with iron tip for 5–8 seconds until flush
   - Allow 30 seconds to cool before disturbing
3. Install M3 brass standoffs (4mm height) at PCB positions
4. Verify all standoffs are vertical using a right-angle gauge

---

## Step 2: Install PCBs on Tray

1. **Power Board first:**
   - Lower board onto 4 standoffs at (15,15), (105,15), (15,85), (105,85)
   - Fasten with M3×8 button-head hex screws
   - Verify: no board flex, all corners seated flat
2. **Main Control Board:**
   - Lower onto standoffs at (120,15), (270,15), (120,105), (270,105)
   - Fasten with M3×8 screws
3. **Phase Shifter Boards (RX then TX):**
   - Mount at (145,100)–(255,100)–(145,170)–(255,170)
   - Label TX board with "TX" marker pen before installing
4. **RF Frontend Board:**
   - Mount at (15,100)–(105,100)–(15,150)–(105,150)
5. **Raspberry Pi 5:**
   - Use standard RPi mounting holes (85×56mm)
   - Mount at (185,25)–(260,25)–(185,70)–(260,70)

---

## Step 3: Cable Routing — RF Cables

**Critical: RF cables before power cables (easier access).**

1. Connect VCO RF output (SMA on Main Board) → HMC451 PA input (2.92mm on RF Board)
   - Cable: RG-405 semi-rigid, 100mm, SMA one end / 2.92mm other end
   - Bend cable gently (min bend radius 5mm)
   - Torque SMA to 0.56 N·m, 2.92mm to 0.45 N·m

2. Connect LO tap (SMA on Main Board or VCO board) → Mixer LO input
   - Cable: RG-405, 100mm
   - Add 3 dB attenuator pad if LO power is too high

3. Connect TX Phase Shifter Board outputs to RF Frontend TX inputs (×16):
   - 16× RG-405 flexible, 80mm each
   - **Before installing:** label each cable 0–15 at both ends
   - Connect in order: cable 0 → PS output 0 → TX divider input 0, etc.

4. Connect RX antenna outputs to LNA inputs (×16):
   - 16× RG-405, 80mm each
   - Same labeling procedure

5. Connect IF output (SMA on RF Board) → ADC input on Main Board
   - Cable: RG-174 flexible, 150mm, SMA both ends

6. **Phase-match TX cables:**
   - After all cables are installed (but before final tray installation)
   - Measure S21 phase on VNA for each cable at 10.05 GHz
   - Record phases in a table: φ₀, φ₁, ..., φ₁₅
   - Target: all within ±5° of mean
   - If any cable is out of spec: trim slightly (shorten by 1–2mm) and remeasure

---

## Step 4: Cable Routing — Power and Digital

1. Connect Power Board output (J2, DF13-6P) → Main Board power input (J2)
   - Use supplied cable assembly or make custom: AWG18, 150mm
   - Pin 1 and 2 to 5V rail on both boards
   - Verify: no reversed polarity

2. Connect Power Board RF output (J3, Molex 8-pin) → RF Frontend power input
   - AWG18 multi-conductor cable, 150mm
   - Label each wire (use colored wire or shrink-wrap labels)

3. Route USB cable (Main Board USB Micro-B → RPi5 USB3 port):
   - Cable length: 300mm
   - Use a cable with a 90° connector if space is tight

4. Connect cooling fan (J_FAN on Main Board) → 80mm fan
   - AWG26, 200mm, JST 2-pin
   - Fan should be oriented to push air toward PA heatsink

5. Secure all cables with cable ties to internal mounting points
   - Never bundle RF cables with power cables (EMI interference)
   - Keep RF cables as short as practical
   - Maintain SMA bend radius ≥ 5mm

---

## Step 5: Install Electronics Tray in Enclosure

1. Lower tray assembly into enclosure from top
2. Route front-panel cables (USB, RF connectors) through front panel cutouts before securing tray
3. Fasten tray with 4× M3×12 countersunk screws through enclosure walls
4. Check: tray is level, no RF connectors pinched or strained

---

## Step 6: Mount Antenna Panel

1. Connect 32× 2.92mm SMA cables from Phase Shifter Boards to Antenna Panel
   - Connect TX cables to TX patch array (left side of panel)
   - Connect RX cables to RX patch array (right side)
   - All cables exit front of enclosure through slots before panel is attached
2. Mount antenna panel to front face of enclosure:
   - Use 6× M3×8 screws through panel mounting holes into front panel threaded holes
   - Torque to 0.5 N·m
3. Verify: panel is flush with enclosure, no gaps, all SMA connections accessible

---

## Step 7: Install Front Panel

1. Install external RF connectors (SMA female panel mount) in front panel cutouts
2. Install USB Micro-B panel-mount connector
3. Install RJ45 panel-mount (optional)
4. Install XT60 female panel-mount for 24V input
5. Install power switch (rocker, SPST 10A)
6. Install LED bezels and LEDs (connect internal cables before installing)
7. Mount front panel to enclosure: 4× M3 screws, torque 0.4 N·m

---

## Step 8: Install Lid

1. Verify all internal connections are complete
2. Take thermal infrared photo of all ICs with brief 5-minute power-on (check hotspots)
3. Apply foam gasket to lid perimeter (optional IP43 sealing)
4. Lower lid onto enclosure
5. Fasten with 4× M3×10 countersunk screws at corners

---

## Step 9: Mount on Tripod Adapter

1. Attach tripod adapter to enclosure bottom:
   - 4× M5×12 button-head hex screws through adapter into enclosure
   - Torque: 1.0 N·m
2. Thread camera tripod into 1/4"-20 UNC hole on adapter
3. Tilt and lock at desired elevation angle
4. Verify: radar does not tip on tripod, center of gravity is stable

---

## Step 10: Final Inspection Checklist

- [ ] All RF connectors torqued to spec (0.45 N·m for 2.92mm, 0.56 N·m for SMA)
- [ ] No cable kinks or minimum bend radius violations
- [ ] Fan spinning (verify with brief power-on)
- [ ] All PCBs secured with no flex
- [ ] Antenna panel flush and secure
- [ ] USB, Ethernet, and 24V connectors accessible from front
- [ ] RPi5 accessible (or Ethernet SSH configured)
- [ ] XT60 input connector is female (cannot accidentally mate wrong polarity)
- [ ] Ground connection: chassis ground to enclosure wall
- [ ] Warning label installed: "RF RADIATION HAZARD — MAINTAIN 2m CLEARANCE"
