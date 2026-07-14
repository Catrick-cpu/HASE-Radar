# AERIS-10P STEP Model Documentation
## 3D CAD Reference for Manufacturing — Rev 1.0

---

## Overview

This document describes all 3D CAD models in the AERIS-10P mechanical design.
STEP files (.step / .stp) can be opened in: FreeCAD (free), Fusion 360, SOLIDWORKS, CATIA, OpenSCAD.

The `generate_stl.py` script (in this directory) generates STL files for 3D printing.
For CNC machining or professional manufacturing, convert STL→STEP using FreeCAD or Fusion 360.

---

## File Index

| Filename | Description | Dimensions | Material |
|---|---|---|---|
| `main_enclosure.step` | Electronics enclosure | 300×200×100 mm | 6061-T6 Al or PETG |
| `antenna_panel.step` | Antenna array mount plate | 200×120×5 mm | FR4 / Aluminium |
| `tripod_mount_adapter.step` | Camera-tripod interface | 100×80×68 mm | 6061-T6 Al |
| `electronics_tray.step` | PCB mounting tray | 280×180×12 mm | 6061-T6 Al or PETG |
| `cooling_fan_bracket.step` | 80mm fan mount | 80×80×4 mm | PETG |
| `front_panel.step` | Front panel with cutouts | 300×100×5 mm | 6061-T6 Al |

---

## 1. Main Enclosure

```
┌──────────────────────────────────────────────────────────────────────┐
│                         MAIN ENCLOSURE                                │
│                    300mm × 200mm × 100mm                              │
│                                                                        │
│  Front face (300×100mm):                                              │
│  ┌────────────────────────────────────────────────────┐               │
│  │ [ANT ●] [TX ●] [RX ●] [IF ●]  [USB □] [RJ45 □]  │               │
│  │  SMA×4   debug        monitor                       │               │
│  │                                              [PWR○] │               │
│  │  [POWER XT60]                                [LED○] │               │
│  └────────────────────────────────────────────────────┘               │
│  ↑ 100mm                                              ↑               │
│                                                                        │
│  Bottom face: 4× rubber feet (M5 stud, 10mm diameter)                │
│  Side faces: ventilation slots (machined or 3D printed)              │
│  Rear face: blank (or cable gland for 24V input alternative)          │
│  Top face: removable lid, 4× M3 fasteners at corners                 │
│                                                                        │
└──────────────────────────────────────────────────────────────────────┘
```

### Detailed Dimensions

```
Outer dimensions:    W=300mm, D=200mm, H=100mm
Wall thickness:      3mm (aluminium) or 4mm (PETG)
Lid thickness:       2mm (aluminium) or 3mm (PETG)

Front panel cutouts:
  SMA female (×4):   D=6.2mm through-hole, on 15mm grid
  USB micro-B:       rectangular 8.0mm×3.5mm, centered at H=20mm from bottom
  RJ45:              rectangular 16.0mm×14.5mm
  XT60 female:       rectangular 12.5mm×7.5mm
  LED indicators:    D=5.1mm through-hole (×2, green/red)
  Power switch:      rectangular 20mm×13mm (rocker switch)

Electronics tray mounting: 4× M3 threaded inserts, 5mm deep, at 250×160mm grid
Lid hinge: none — lift-off lid with 4× M3 countersunk screws at corners
  (or alternative: continuous hinge on rear edge)

Ventilation:
  Side wall slots: 5× slots, 60mm×3mm, spaced 15mm apart, centered vertically
  Fan mounting: 80mm circular opening on rear face (for push-through airflow)

Weight (aluminium): ~320g
Weight (PETG 30% infill): ~180g

Tripod mount interface: 1/4"-20 UNC blind hole, 8mm deep, at center of bottom face
  Alternative: 3/8"-16 UNC (for heavier tripods) with 1/4"-20 adaptor insert
```

### FreeCAD Modeling Instructions

To create this part in FreeCAD:
1. Open FreeCAD → Part Design workbench
2. Create a new sketch on XY plane: rectangle 300×200mm
3. Pad: 100mm
4. Shell: 3mm (removes inner material)
5. Create pocket for front panel cutouts using further sketches
6. Fillet all outer edges: R=2mm
7. Add M3 threaded hole features (M3×0.5, 8mm depth) at corner positions
8. Export: File → Export → .STEP (ISO 10303-214)

---

## 2. Antenna Panel

```
┌──────────────────────────────────────────────────────────────────────┐
│                       ANTENNA PANEL                                   │
│                    200mm × 120mm × 5mm                                │
│                                                                        │
│  Front face (mounted outward, toward target):                         │
│                                                                        │
│  TX Array (4×4 patches)   |   RX Array (4×4 patches)                 │
│  ┌───────────────────────┐│┌───────────────────────┐                 │
│  │ ○  ○  ○  ○           │││           ○  ○  ○  ○ │                 │
│  │                        │││                        │                 │
│  │ ○  ○  ○  ○           │││           ○  ○  ○  ○ │                 │
│  │   (patch elements)     │││   (patch elements)     │                 │
│  │ ○  ○  ○  ○           │││           ○  ○  ○  ○ │                 │
│  │                        │││                        │                 │
│  │ ○  ○  ○  ○           │││           ○  ○  ○  ○ │                 │
│  └───────────────────────┘│└───────────────────────┘                 │
│         45mm × 45mm array │   45mm × 45mm array                       │
│         (3λ/2 × 3λ/2)     │                                          │
│  ←    90mm TX section     │   90mm RX section      →                 │
│                                                                        │
│  Back face: 16× 2.92mm SMA launch pads per array section             │
│             = 32 total connector pads                                  │
│             Mount holes: 6× M3 through-holes at periphery             │
│                                                                        │
└──────────────────────────────────────────────────────────────────────┘
```

### Detailed Dimensions

```
Total panel: 200mm (W) × 120mm (H) × 5mm (substrate)
  Note: "panel" is actually the Rogers RO4003C PCB itself + aluminium backing plate

Rogers RO4003C PCB: 200mm × 120mm × 0.508mm (substrate)
Aluminium backing plate: 200mm × 120mm × 4.5mm (for rigidity)

TX array center: at X=45mm, Y=60mm (from left edge, centered vertically)
RX array center: at X=155mm, Y=60mm

Element positions (TX, element [row,col]):
  [0,0]: X=22.5mm, Y=37.5mm
  [0,1]: X=37.5mm, Y=37.5mm
  [0,2]: X=52.5mm, Y=37.5mm
  [0,3]: X=67.5mm, Y=37.5mm
  [1,0]: X=22.5mm, Y=52.5mm
  ... (15mm step in each direction)
  [3,3]: X=67.5mm, Y=82.5mm

SMA feed connector positions: on rear face, aligned with each element feed point
  2.92mm SMA edge-launch connectors with 1.2mm hole diameter

Mount holes: 6× M3 through-holes
  At (10,10), (100,10), (190,10), (10,110), (100,110), (190,110) mm
```

---

## 3. Tripod Mount Adapter

```
Side view:                          Front view:
                                    
     ┌─────────────────────┐        ┌──────────────────────┐
     │    Base Plate       │        │     80mm × 68mm      │
     │    100mm × 8mm      │        │                      │
     │                     │        │    ○         ○       │
     └──────────┬──────────┘        │      (M5 holes)     │
                │                   │    ○         ○       │
                │ 8mm × 60mm        │                      │
                │ upright           └──────────────────────┘
                │
     ┌──────────┴──────────┐
     │   Enclosure mount   │
     │   80mm × 8mm × 60mm │
     │                     │
     │   M5 bolt here      │
     │   (to enclosure     │
     │    bottom)          │
     │                     │
     │   1/4"-20 nut       │
     │   recessed 5mm deep │
     │   (tripod thread)   │
     └─────────────────────┘
```

### Detailed Dimensions

```
Base plate:   100mm (L) × 80mm (W) × 8mm (H)
Upright:      80mm (W) × 8mm (D) × 60mm (H)
Total height: 68mm (8mm base + 60mm upright)

Tripod interface: 1/4"-20 UNC hex nut pressed into recess at base center
  Recess depth: 5mm, hex across-flats: 11.1mm
  Alternatively: 3/8"-16 UNC insert option

Enclosure attachment:
  4× M5 through-holes in base plate, at 80×60mm grid (matching enclosure bottom)
  M5 hex button-head socket screws from below

Upright-to-enclosure attachment:
  4× M3 through-holes in upright, at 60×40mm grid
  M3 hex socket screws → threaded inserts in enclosure bottom

Tilt mechanism (optional upgrade):
  Center pivot hole D=8mm for M8 bolt, allows ±30° tilt
  Clamping nut on M8 bolt locks angle

Material: 6061-T6 aluminium, 2.5mm anodize coat (black)
Weight: ~120g

3D Print alternative (PETG):
  Print upright and base as separate parts, join with M3 bolts
  Add steel M5 threaded inserts for durability
```

---

## 4. Electronics Tray

```
Top view (inside enclosure):

  ┌──────────────────────────────────────────────────────────────────┐
  │                     ELECTRONICS TRAY                              │
  │                   280mm × 180mm × 12mm                            │
  │                                                                    │
  │  ●    ●    ●    ●   ← M3 PCB standoffs (4mm height)             │
  │  [  Power Board  ]   [    Main Control Board    ]                 │
  │   100×80mm           160×100mm                                    │
  │                                                                    │
  │  ●    ●    ●    ●                                                 │
  │  [RF Frontend Bd]   [ Phase Shifter Board ]                       │
  │   100×60mm           120×80mm                                     │
  │                                                                    │
  │  ●    ●    ●    ●   ← M3 PCB standoffs                          │
  │                                                                    │
  │   [Fan mount ●]      [Raspberry Pi 5   ]                         │
  │                       85×56mm (standard Pi)                       │
  │                                                                    │
  └──────────────────────────────────────────────────────────────────┘
  
  Overall tray: 280mm × 180mm × 12mm base + 4mm standoffs = 16mm total height
  Tray mounting: 4× M3 screws into enclosure walls at 270×170mm grid
  PCB mounting: M3 threaded inserts in tray, 4mm brass standoffs
  Cable management: 6× cable routing slots (5×20mm) around perimeter
```

### Detailed Dimensions

```
Base plate: 280mm × 180mm × 3mm (aluminium or PETG)
Rim: 12mm total height (9mm side walls on 3 sides, open front)
PCB standoffs: M3×0.5 threaded, 4mm height, positions per board layout

PCB mounting positions:
  Power Board (100×80mm):     Bottom-left, PCB at (10,10) to (110,90)
  Main Control Board (160×100mm): Top area, PCB at (120,10) to (280,110)
  RF Frontend (100×60mm):     Bottom-center, PCB at (10,100) to (110,160)
  Phase Shifter (120×80mm):   Bottom-right, PCB at (140,100) to (260,180)
  Raspberry Pi (85×56mm):     Right area, PCB at (185,50) to (270,106)

Standoff positions: 4 per board, M3×0.5 threaded insert in tray
  3D printed version: print M3 hex holes, press in M3 threaded inserts

Material: 6061-T6 aluminium (preferred) or PETG (prototype)
```

---

## 5. Front Panel

```
┌──────────────────────────────────────────────────────────────────────┐
│              FRONT PANEL    300mm × 100mm × 5mm                      │
│                                                                        │
│  [═══════════ AERIS-10P ══════════════════════════════════════════]   │
│  │                                                                  │  │
│  │  SMA×4           USB-B  ETH    XT60   PWR-SW  LED1  LED2       │  │
│  │  (RF ports)                    (24V)                            │  │
│  │  ○○○○          □      □□□□   [==]   (○)   (●)   (●)          │  │
│  │                                                                  │  │
│  │  ← 10 → ← 30 → ← 20 → ← 20 → ← 25 → ← 20 → ← 20 → (mm)    │  │
│                                                                        │
└──────────────────────────────────────────────────────────────────────┘
```

### Cutout Dimensions

```
Overall: 300mm × 100mm × 5mm
Mount holes: 4× M3 through-holes at corners (5mm from edge each)

Connector cutouts (from left edge, centered at H=50mm):
  SMA female (×4):   4× D=6.35mm holes, spaced 15mm, first at X=25mm
  USB micro-B:       at X=110mm, 11mm×8mm rectangle
  RJ45:              at X=150mm, 17mm×15mm rectangle
  XT60 female:       at X=185mm, 13mm×8mm rectangle
  Power switch:      at X=220mm, 22mm×15mm rectangle
  LED green (OK):    at X=255mm, D=5.2mm hole
  LED red (TX):      at X=275mm, D=5.2mm hole
  
Label engraving (or printed label):
  "AERIS-10P" centered at top
  Each connector labeled below cutout
  "10 GHz FMCW RADAR" below main label
  "RF RADIATION HAZARD" warning triangle near SMA ports

Finish:
  Aluminium: black anodize, white silk-screen labels
  PETG: black filament, heat-press label insert
```

---

## Manufacturing Notes

### Option A: CNC Machined Aluminium (Production Quality)

- Material: 6061-T6 aluminium
- Finish: Type II anodize, black (for RF shielding and aesthetics)
- Tolerance: ±0.1mm general, ±0.05mm for RF connector holes
- Supplier: Proto Labs, Fictiv, or local machine shop
- Estimated cost per piece: $120–$250 depending on complexity
- Lead time: 5–10 business days

### Option B: 3D Printed PETG (Prototype Quality)

- Material: PETG, 30% infill, 0.2mm layer height, 4 perimeters
- Print orientation: largest flat face down (minimize supports)
- Threaded features: use M3 heat-set inserts (press in with soldering iron at 200°C)
- Finish: optional spray paint (Krylon Fusion, black)
- Estimated cost per piece: $5–$15 (material)
- Lead time: 4–8 hours per piece on FDM printer (Prusa MK4, Bambu X1)

### Option C: Laser-Cut Sheet Metal (Panel Version)

- Material: 1.5mm or 2mm steel sheet
- Process: laser cut + CNC bend
- Coating: powder coat, black
- Good for: front panel, simple brackets
- Not suitable for: enclosure (too many features)

### STEP File Generation from FreeCAD

To generate STEP files from scratch:
```python
# In FreeCAD's Python console:
import FreeCAD
import Part

# Create main enclosure box
box = Part.makeBox(300, 200, 100)  # W×D×H in mm
shell_offset = 3  # wall thickness

# Create inner void
inner = Part.makeBox(
    300 - 2*shell_offset,
    200 - 2*shell_offset, 
    100 - shell_offset,
    FreeCAD.Vector(shell_offset, shell_offset, 0)
)

# Shell the box
enclosure = box.cut(inner)

# Export STEP
Part.export([enclosure], "main_enclosure.step")
```

For full parametric modeling, use the FreeCAD Part Design workbench with 
the Spreadsheet workbench for dimensions management.

---

*End of STEP Model Documentation — AERIS-10P Rev 1.0*
