# AERIS-10P Mechanical Dimensions
## Rev 1.0 — 2026-07-14 | All dimensions in millimeters unless noted

---

## 1. Main Electronics Enclosure

```
External dimensions:
  Width (X):  300.0 mm
  Depth (Y):  200.0 mm
  Height (Z): 100.0 mm
  
Wall thickness:
  Aluminium: 3.0 mm (machined)
  PETG prototype: 4.0 mm (3D printed)
  
Lid thickness:
  Aluminium: 2.0 mm
  PETG: 3.0 mm

Internal dimensions (aluminium version):
  Width:  294.0 mm (300 - 2×3)
  Depth:  194.0 mm
  Height:  95.0 mm (100 - lid - base)

Front panel area: 300 × 100 mm (front face)
Rear panel area:  300 × 100 mm (rear face)
Side panels:      200 × 100 mm each

Lid fasteners: 4× M3 × 10 countersunk screws
  Positions: at 10mm from each corner (x=10,y=10), (x=290,y=10), (x=10,y=90), (x=290,y=90)

Bottom feet: 4× rubber M5 stud, D=20mm, H=10mm
  Positions: x=20mm, y=20mm from each corner

Tripod thread: M10×1.0 or 1/4"-20 UNC, depth 12mm, at bottom center (x=150, y=100)

Material: 6061-T6 Aluminium (machined, type II anodize black)
Weight (aluminium): 0.8–1.2 kg
Weight (PETG printed at 30%): 0.4 kg
```

---

## 2. Antenna Panel

```
Total panel: 200.0 × 120.0 × 5.0 mm
  (Rogers RO4003C PCB + aluminium backing plate)

Rogers PCB: 200.0 × 120.0 × 0.508 mm
Aluminium backing: 200.0 × 120.0 × 4.5 mm

TX array region (left half):
  Center: x=50mm, y=60mm
  Extends: x=27.5 to 72.5mm, y=37.5 to 82.5mm

RX array region (right half):
  Center: x=150mm, y=60mm
  Extends: x=127.5 to 172.5mm

Element positions (TX, element [row,col], from panel left edge):
  [0,0]: (35.0, 37.5)   [0,1]: (50.0, 37.5)   [0,2]: (65.0, 37.5)   [0,3]: (80.0, 37.5)
  [1,0]: (35.0, 52.5)   [1,1]: (50.0, 52.5)   [1,2]: (65.0, 52.5)   [1,3]: (80.0, 52.5)
  [2,0]: (35.0, 67.5)   [2,1]: (50.0, 67.5)   [2,2]: (65.0, 67.5)   [2,3]: (80.0, 67.5)
  [3,0]: (35.0, 82.5)   [3,1]: (50.0, 82.5)   [3,2]: (65.0, 82.5)   [3,3]: (80.0, 82.5)

RX elements same pattern at x+100mm offset.

Mounting holes: 6× M3 through-holes
  At (10,10), (100,10), (190,10), (10,110), (100,110), (190,110)

SMA connector footprints (rear face): 16 per array = 32 total
  2.92mm edge-launch, pad dimensions per Southwest Microwave 1092-06A-5 datasheet
```

---

## 3. Tripod Mount Adapter

```
Overall bounding box: 100 × 80 × 68 mm

Base plate: 100 × 80 × 8 mm
  Tripod thread: 1/4"-20 UNC, 12mm deep, at center (x=50, y=40) of base
  Alternative: 3/8"-16 UNC insert at same location
  To enclosure: 4× M5 through-holes at (15,20), (85,20), (15,60), (85,60)

Upright: 80 × 8 × 60 mm (rises from base at rear edge)
  To enclosure: 4× M3 through-holes at (10,30), (70,30), (10,50), (70,50) from upright base
  
Material: 6061-T6 aluminium or PETG with M5/M3 thread inserts
Weight: 120g (aluminium), 45g (PETG)

Tilt range (with optional clamping bolt): ±30°
  Pivot: M8 bolt through 8.5mm hole at upright midpoint (x=40, y=30)
```

---

## 4. Electronics Tray

```
Overall: 280 × 180 × 12 mm

Base plate: 280 × 180 × 3 mm
Side rails: 280 × 9 × 9 mm (front and back)
  (open sides for cable routing)

PCB standoff positions (M3, 4mm height):
  Power Board (100×80mm): standoffs at (15,15), (105,15), (15,85), (105,85)
  Main Control Board (160×100mm): standoffs at (120,15), (270,15), (120,105), (270,105)
  RF Frontend (100×60mm): standoffs at (15,100), (105,100), (15,150), (105,150)
  Phase Shifter Board (120×80mm): standoffs at (145,100), (255,100), (145,170), (255,170)
  Raspberry Pi 5 (85×56mm): standoffs at (185,25), (260,25), (185,70), (260,70)

Tray mount to enclosure: 4× M3 countersunk at corners (10,10), (270,10), (10,170), (270,170)
Cable routing slots: 6× 5×20mm slots on front and rear edges

Material: 2mm aluminium or 3mm PETG
Weight: 0.5 kg (aluminium), 0.15 kg (PETG)
```

---

## 5. Front Panel Connector Layout

```
Front panel: 300 × 100 × 5 mm (mounted at Z=0, replaces enclosure front face)

Connector cutouts (from left edge, all centered vertically at Y=50mm):

X=25mm:  4× SMA holes, D=6.35mm, spaced 15mm (X=25, 40, 55, 70)
          Labels: TX, RX, IF_MON, GND_REF
X=110mm: USB Micro-B, 11.0 × 7.5mm rectangle, R=0.5mm corners
X=150mm: RJ45, 16.0 × 14.5mm rectangle (for Ethernet option)
X=185mm: XT60 female, 15.0 × 8.5mm rectangle (24V power input)
X=220mm: Rocker switch, 22.0 × 15.0mm rectangle (power switch)
X=255mm: LED hole, D=5.2mm (green — system OK)
X=275mm: LED hole, D=5.2mm (red — TX active)

Label plate: black anodized, white laser engraving
  Top label: "AERIS-10P" centered
  Below SMA: "RF PORTS — RF CAUTION"
  Below USB: "CTRL"
  Below XT60: "24V 8A"
  
M3 mount holes: at (5,5), (295,5), (5,95), (295,95)
```

---

## 6. Thermal Design

```
PA HMC451LS6GE heat dissipation:
  TX power: 27 dBm = 0.5 W
  PAE: 20%
  Supply power: 0.5/0.20 = 2.5 W
  Heat dissipation: 2.5 - 0.5 = 2.0 W
  
Heatsink requirement (ambient 40°C, max PA junction 150°C, θj-c = 25°C/W):
  Available thermal budget: 150 - 40 = 110°C
  Junction to case: 25°C/W × 2W = 50°C
  Remaining for heatsink: 110 - 50 = 60°C
  Required heatsink θc-a: 60°C / 2W = 30°C/W
  With fan: 15°C/W heatsink sufficient (80mm fan provides 30-50 LFM)
  Without fan: need 30°C/W → 50cm² natural convection heatsink

LM7812 heat dissipation:
  Input: 24V, output: 12V, current: 0.5A
  Dissipation: (24-12) × 0.5 = 6 W (!)
  Heatsink required: TO-220 + 10°C/W heatsink + 80mm forced air
  Recommendation: Replace LM7812 with LT8612 switching regulator for 12V rail
  LT8612 efficiency: ~90% → dissipation: 12×0.5 × (1-0.9)/0.9 = 0.67 W (much better)
```

---

## 7. Weight Budget

| Component | Weight (g) |
|---|---|
| Main enclosure (PETG prototype) | 400 |
| Front panel (aluminium 300×100×5mm) | 400 |
| Electronics tray (PETG) | 150 |
| Main control PCB + components | 80 |
| RF frontend PCB | 50 |
| Power board | 60 |
| Phase shifter boards ×2 | 80 |
| Antenna panel (Rogers PCB + Al backing) | 200 |
| Raspberry Pi 5 | 70 |
| Cables and connectors | 200 |
| Fasteners and misc | 50 |
| **Total** | **~1740 g (~1.7 kg)** |

Note: With aluminium enclosure: add ~500g (aluminium vs PETG). Target total: <3 kg for field use.
