# AERIS-10P PCB Assembly Notes
## Rev 1.0 — 2026-07-14

---

## Assembly Sequence

**Critical rule:** Never power a board until ALL assembly and inspection is complete for that board.

1. Power Board → test all voltage rails → pass
2. Main Control Board → test digital interfaces → pass
3. RF Frontend Board → test RF connectivity → pass
4. Phase Shifter Boards (×2) → test SPI and RF → pass
5. Antenna Panel → test S11 → pass
6. Integration: interconnect all boards → full system test

---

## 1. Power Board Assembly

**Tools:** Hot-air rework station (350°C, 5 L/min), fine-tip soldering iron, flux paste, IPA

1. Apply solder paste with stencil (SMD components, 0.5mm openings for 0402)
2. Place components with tweezers: start with ICs (LT8612, LT8607, TPS65133, LM7812)
3. Place inductors and electrolytic capacitors
4. Place XT60 connector (through-hole — solder last by hand)
5. Place indicator LEDs and resistors
6. Reflow: ramp 2°C/s, preheat 150°C for 90s, peak 250°C for 30s, cool 3°C/s
7. **Inspect:** Check no solder bridges under LT8612 (MSOP-16). Use 10× magnifier.
8. Solder XT60 connector by hand: liquid flux, large iron tip, 60s solder time
9. **Test before connecting to anything:**
   - Connect 24V bench supply (current limit: 0.5A initially)
   - Measure TP1 (+5V): expect 5.0 ± 0.15V
   - Measure TP2 (+3.3V): expect 3.3 ± 0.1V
   - If rail is wrong: disconnect immediately, check component placement
10. Load test: connect 1A dummy load to 5V rail, verify regulation holds

---

## 2. Main Control Board Assembly

**Note:** STM32H743ZIT6 in LQFP-144 has 0.5mm pitch — use solder paste stencil.

1. Apply paste via laser-cut stencil
2. Place STM32H743ZIT6: align pin 1 marker, center in footprint
3. Place ADF4159CCPZ (CP-40-3 package): 0.5mm pitch, use vacuum pickup
4. Place HMC733LP6CE (LP-6): RF component, handle carefully
5. Place ADS8661IRGAT (QFN-20): small package, check orientation
6. Place OCXO module (through-hole or SMD mount): last before reflow
7. Place all passives: 0402 caps and resistors
8. Place USB connector: SMD type, verify pad alignment before reflow
9. Reflow: standard SAC305 profile (250°C peak)
10. Post-reflow inspection:
    - LQFP-144 under microscope: check for solder bridges at all 144 pins
    - Check pad coverage on QFN components (X-ray recommended if available)
11. Hand solder: debug header, SWD connector, XT60-style power connector
12. **First power-on sequence:**
    - Connect power board, measure 3.3V on Main Board
    - Attach ST-Link V3 via SWD header
    - Flash minimal blinky firmware
    - Verify LED blinks at 1 Hz → STM32 running

---

## 3. RF Frontend Board Assembly

**Most critical board. Rogers RO4003C substrate — handle carefully.**

⚠️ **CAUTION:** Rogers substrate is fragile at PCB edges. Do not snap or flex.
⚠️ **ESD:** All HMC components are ESD-sensitive. Ground yourself with ESD strap before handling.

1. Clean Rogers PCB with IPA to remove any contamination
2. Apply solder paste — only SAC305 paste for this board (HASL forbidden on Rogers)
3. Place HMC647A phase shifters (×16, QFN-32 5×5mm):
   - These are the most critical components to place correctly
   - Use vacuum pickup tool, verify orientation (pin 1 marker)
   - Place in two rows: TX group (8) and RX group (8)
4. Place HMC1040 LNAs (×16, QFN-24 4×4mm)
5. Place HMC213B mixer (QFN-16, 4×4mm)
6. Place HMC451 PA (LS-6 package)
7. Place all passive components
8. Reflow: 260°C peak, 30s, 2°C/s cool (SAC305 profile)
9. **Post-reflow (critical):**
   - Inspect all QFN solder joints: look for bridging and voiding
   - X-ray inspection strongly recommended for QFN components
   - Clean with ultrasonic IPA bath or spray flux remover
10. **Install SMA/2.92mm connectors AFTER reflow:**
    - These are not reflow-compatible — solder by hand
    - 2.92mm connector: use fixture to align perpendicular to board
    - Solder the ground flange first (4 ground pads around connector)
    - Then solder center pin: use small iron tip, minimal flux
    - Verify: measure S11 with VNA at connection point
11. **First RF test:**
    - Apply +5V RF and +3.3V to board
    - Connect VNA to PA input port, verify 50Ω S11 match
    - Connect signal generator at 10 GHz to RX port
    - Verify signal passes through LNA → measure gain ~18 dB with VNA

---

## 4. Phase Shifter Board Assembly

**Note:** This is similar to RF Frontend but simpler (no PA/mixer).**

1. Same process as RF Frontend but focus on HMC647A placement
2. **Critical: SPI daisy-chain routing** — verify during layout that U16 DATA_OUT connects to U15 DATA_IN, etc.
3. **Test SPI communication before installing in system:**
   - Connect SPI to STM32 Nucleo eval board (easier access)
   - Send SPI transaction: 16 bytes = [0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10]
   - This sets all 16 shifters to code 0x10 = 90°
   - Verify with VNA that phase changes at each output
4. Build two identical boards: one for TX, one for RX

---

## 5. Common Assembly Issues and Solutions

| Issue | Symptom | Solution |
|---|---|---|
| QFN bridge | Short circuit between adjacent pins | Hot air rework, add flux, reflow gently. Wick excess solder. |
| QFN opens | IC doesn't respond to SPI | X-ray to check solder voids under pad. Hot air reflow with more paste if possible. |
| LQFP bridge | Two adjacent pins shorted | Fine-tip iron with flux. Cut solder ball between pins with scalpel. |
| Component tombstone | Passive component standing up on one end | Usually means paste imbalance. Reflow at higher temperature or more balanced paste. |
| Rogers PCB warped | Substrate not flat | Bake at 120°C for 30 min before assembly. Use fixture during reflow. |
| SMA misaligned | High return loss after installation | Remove and reinstall with better fixture. Torque to spec (0.45 N·m for 2.92mm). |

---

## 6. Torque Specifications

| Connector | Torque | Wrench size |
|---|---|---|
| SMA female-female | 0.56 N·m (5 lb·in) | 5/16" open-end |
| 2.92mm K-connector | 0.45 N·m (4 lb·in) | 7/16" open-end |
| SMA to SMA (inline) | 0.56 N·m | 5/16" |
| XT60 mounting screws | 0.50 N·m | M3 hex key |

⚠️ **NEVER** overtighten 2.92mm connectors. They are machined to fine tolerance and easily destroyed.
