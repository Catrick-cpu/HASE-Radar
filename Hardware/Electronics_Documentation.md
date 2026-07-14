# AERIS-10P Electronics Documentation
## Rev 1.0 — 2026-07-14

---

## 1. PCB Stackup Specifications

### FR4 Boards (Main Control, Power)

**4-layer FR4 stackup (Main Control Board):**
- Layer 1 (top): Signal — component side, digital signals, USB traces
- Prepreg 1 (7628): 0.2mm
- Layer 2: Ground — solid copper pour, RF shield
- Core (FR4): 0.8mm
- Layer 3: Power — +3.3V and +5V planes
- Prepreg 2 (7628): 0.2mm
- Layer 4 (bottom): Signal — additional routing, SPI buses
- Total board thickness: ~1.6mm

**2-layer FR4 stackup (Power Board):**
- Layer 1: Power supply components and routing
- Core FR4: 1.4mm
- Layer 2: Ground plane (solid copper)
- Total: 1.6mm

### Rogers Boards (RF Frontend, Phase Shifter, Antenna)

**4-layer Rogers/FR4 hybrid stackup (Phase Shifter Board):**
- Layer 1 (top): Rogers RO4003C 0.508mm — 50Ω microstrip RF traces
- Bond layer: Rogers RO4403C bondply 0.1mm
- Layer 2: Ground — solid copper, 1oz
- Core FR4: 0.6mm
- Layer 3: Power (+5V) — FR4 prepreg
- Layer 4 (bottom): FR4 — SPI control signals
- Total: ~1.5mm

**Note:** PCBWay calls this "Rogers mixed material board" — specify in order notes.

---

## 2. Grounding Strategy

**Star ground topology:**
- All supply return currents meet at a single star point near the 24V input
- Separate ground planes for: analog RF, digital control, power supply
- Connect planes at single point under each board

**RF board grounding:**
- Solid copper ground plane on layer 2 (no splits)
- Ground via fence along all RF traces (0.3mm drill, 0.6mm pad, every 3mm)
- Exposed pad (thermal) of QFN ICs must connect directly to ground plane via multiple vias
- No digital signals crossing under RF traces on layer 4

**Mixed-signal board (Main Control):**
- Analog section (ADC) on one corner, digital section on other
- Single ground plane, but keep analog and digital routes separated
- Decouple ADC AVDD and DVDD with separate ferrite bead from main supply

---

## 3. Power Distribution

**Decoupling capacitor philosophy:**
- Every IC supply pin: 100nF 0402 X7R within 0.5mm of pin
- Every IC: 1µF 0402 X5R within 2mm of IC
- Bulk supply: 10µF 0805 X5R per functional block
- RF ICs: additional 100pF high-frequency cap (sometimes called "HF bypass")

**Ferrite bead placement:**
- One ferrite bead (e.g., Murata BLM18AG601SN1D, 600Ω@100MHz) on 5V supply entering RF section
- Prevents digital switching noise from coupling into RF supply

**Recommended component values:**
- Local bypass: 100nF 0402, X7R, 16V (Murata GRM155R71C104KA88D or equiv.)
- Mid-range: 1µF 0402, X5R, 6.3V
- Bulk: 10µF 0805, X5R, 6.3V
- RF bypass: 10pF 0402, C0G, 50V

---

## 4. SPI Bus Architecture

```
STM32H743ZIT6 SPI Resource Allocation:

SPI1 (PA4-PA7, AF5) — 10 MHz — TX Phase Shifter Array
  CS:   PA4 (GPIO, push-pull, active LOW)
  SCK:  PA5 (AF5)
  MISO: PA6 (AF5, not used for HMC647A but reserved)
  MOSI: PA7 (AF5)
  Pull-up on CS: 10kΩ to 3.3V (default high = deasserted)
  Level translation: 3.3V → 5V required (HMC647A needs 5V SPI)
  Use TXB0104 bidirectional level translator

SPI2 (PB12-PB15, AF5) — 10 MHz — RX Phase Shifter Array
  Same as SPI1, same level translation

SPI3 (PA15, PC10, PC11, PC12, AF6) — 1 MHz — ADF4159 PLL
  CS/LE: PA15 (GPIO, pulse HIGH for latch)
  SCK:   PC10 (AF6)
  MISO:  PC11 (not used)
  MOSI:  PC12 (AF6)
  Note: ADF4159 uses 32-bit SPI words, MSB first

SPI4 (PE11-PE14, AF5) — 1 MHz — ADS8661 ADC
  CS:   PE11 (GPIO, active LOW)
  SCK:  PE12 (AF5)
  MISO: PE13 (AF5) 
  MOSI: PE14 (AF5)
  Note: ADS8661 is 24-bit SPI transaction

SPI5, SPI6 — Reserved for future expansion
```

**Level translation for phase shifter SPI (3.3V → 5V):**
- IC: TXB0104 (4-bit bidirectional voltage translator, 3.3V → 5V)
- Place one TXB0104 per SPI bus (4 signals: SCK, MOSI, CS, MISO)
- Direction auto-sensing (no DIR pin needed for SPI)
- Propagation delay: <5 ns — negligible at 10 MHz

---

## 5. USB Interface

**USB Full-Speed (12 Mbps) CDC-ACM:**
- STM32H743 has built-in USB FS peripheral on PA11 (DM) and PA12 (DP)
- USB crystal: requires accurate 48 MHz clock (either from PLL or external crystal)
- 48 MHz from PLL: set HSE×4 = 25 MHz × (192/100) = 48 MHz (or use USB PLL)
- USB enumeration: Windows needs no driver (CDC is native), Linux/Mac natively
- Series resistors: 22Ω on D+ and D- (PA12 and PA11 respectively)
- ESD protection: PRTR5V0U2X (SOT-363) on USB lines
- VBUS detection: 100kΩ from VBUS to PA9 (ADC input or comparator)

**USB data rate:**
- Raw USB FS: 12 Mbps
- CDC overhead: ~10% → effective ~11 Mbps
- ADC data: 16-bit × 8000 SPS = 128 kbps → 1% of USB bandwidth
- Sufficient headroom for future higher sample rates

---

## 6. GPIO Assignments (Complete Table)

See Hardware/Interface_Documentation.md for complete GPIO table.

Key highlights:
- PA4, PA5, PA6, PA7: SPI1 (TX array)
- PA11, PA12: USB D-/D+ (reserved, do NOT connect anything else)
- PA15: ADF4159 Latch Enable (must not float — pull to GND with 10kΩ)
- PC0, PC1, PC2: PA_EN, LNA_EN, RAMP_EN (3.3V GPIOs, but 5V tolerant)

---

## 7. Test Points

Required test points for bring-up and calibration:

| TP# | Signal | Type | Location |
|---|---|---|---|
| TP1 | +5V | 1mm pad | Power board output |
| TP2 | +3.3V | 1mm pad | Main board logic supply |
| TP3 | +5V RF | 1mm pad | RF board supply |
| TP4 | GND | 2mm pad | Multiple on each board |
| TP5 | VCO_OUT | SMA | Main board (for spectrum analyzer) |
| TP6 | IF_OUT | SMA | RF board (beat note monitor) |
| TP7 | SPI1_SCK | 0.8mm pad | Main board (for logic analyzer probe) |
| TP8 | ADF4159_LE | 0.8mm pad | Main board |
| TP9 | PA_DRAIN | 1mm pad | RF board (current measurement) |
| TP10 | OCXO_OUT | 1mm pad | Main board (frequency counter) |
