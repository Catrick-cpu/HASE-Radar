# AERIS-10P Complete Wiring Diagram
## System Interconnect Documentation — Rev 1.0
**Date:** 2026-07-14

---

## 1. System-Level Wiring Overview

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                        AERIS-10P SYSTEM WIRING                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

  ┌─────────────┐    24V/8A     ┌──────────────────────────────────────────┐
  │  24V DC     │══════════════▶│            AERIS POWER BOARD              │
  │  Supply     │    XT60       │  ┌─────┐  ┌─────┐  ┌──────┐  ┌────────┐ │
  │  (Battery   │               │  │LT   │  │LT   │  │TPS   │  │LM7812  │ │
  │  or AC/DC)  │               │  │8612 │  │8607 │  │65133 │  │+12V    │ │
  └─────────────┘               │  │5V/5A│  │3.3V │  │±5V   │  │/1A PA  │ │
                                │  └──┬──┘  └──┬──┘  └──┬───┘  └───┬────┘ │
                                │     │         │         │           │       │
                                └─────┼─────────┼─────────┼───────────┼───────┘
                                      │         │         │           │
                              5V/5A   │  3.3V   │  ±5V   │    12V   │
                              (red)   │  (org)  │  (yel) │   (wht)  │
                                      │         │         │           │
  ┌───────────────────────────────────▼─────────▼─────────▼───────────▼────────┐
  │                          AERIS MAIN CONTROL BOARD                            │
  │                                                                               │
  │  ┌──────────────────┐   ┌────────────┐   ┌───────────┐   ┌───────────────┐  │
  │  │ STM32H743ZIT6    │   │ ADF4159    │   │ HMC733    │   │ ADS8661       │  │
  │  │ (480 MHz MCU)    │   │ FMCW PLL   │   │ 10 GHz    │   │ 16-bit ADC    │  │
  │  │                  │◀──│ chirp gen  │──▶│ VCO       │   │ 1 MSPS        │  │
  │  │ SPI1 ────────────┼──▶│            │   │+17 dBm    │   │               │  │
  │  │ SPI2 ─────────┐  │   └────────────┘   └─────┬─────┘   └───────┬───────┘  │
  │  │ SPI3 ──────┐  │  │                          │RF              │IF(ADC)    │
  │  │ SPI4 ───┐  │  │  │   ┌────────────┐         │               │           │
  │  │ USB ────┼──┼──┼──┼──▶│ USB CDC    │         │               │           │
  │  │ GPIO ───┼──┼──┼──┘   │ to PC/RPi5 │         │               │           │
  │  └─────────┼──┼──┼──────┴────────────┘         │               │           │
  │            │  │  │                              │               │           │
  └────────────┼──┼──┼──────────────────────────────┼───────────────┼───────────┘
               │  │  │                              │               │
               │  │  │ SPI1 (to TX phase shifters)  │ RF (10 GHz)  │ IF (<5kHz)
               │  │  │ SPI2 (to RX phase shifters)  │              │
               │  │  │                              │               │
               ▼  ▼  ▼                              ▼               ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │                        AERIS RF FRONTEND BOARD                                │
  │                                                                                │
  │  TRANSMIT PATH:                                                                │
  │                                                                                │
  │  VCO RF ──▶ ┌──────────┐  +29 dBm  ┌────────────────┐                        │
  │  input      │ HMC451   │──────────▶│ 1:16 Wilkinson │──▶ to Phase Shifters   │
  │  (+14 dBm)  │ X-band PA│           │ Power Divider  │   (see below)          │
  │             └──────────┘           │ (-13 dB split) │                        │
  │                                    └────────────────┘                        │
  │                                                                                │
  │  Phase Shifter Array (TX) — 16× HMC647ALP5E:                                  │
  │  ┌────────────────────────────────────────────────────────────────────┐       │
  │  │ SPI chain: STM32 SPI1 → PSH_TX[0] → PSH_TX[1] → ... → PSH_TX[15] │       │
  │  │ CS pin: GPIO PA_CS (active low, all 16 devices share CS)           │       │
  │  │ Each output: SMA 2.92mm → TX patch antenna element                 │       │
  │  └────────────────────────────────────────────────────────────────────┘       │
  │                                                                                │
  │  RECEIVE PATH:                                                                 │
  │                                                                                │
  │  16× RX antennas → 16× ┌──────────┐ → Phase Shifters → ┌──────────┐          │
  │                         │ HMC1040  │   (RX, SPI2)       │ 16:1     │          │
  │                         │ LNA      │                     │ Combiner │          │
  │                         │ NF 1.5dB │                     └────┬─────┘          │
  │                         └──────────┘                          │                │
  │                                                               ▼                │
  │                                                          ┌──────────┐          │
  │                                              LO (10GHz)─▶│ HMC213B  │          │
  │                                                          │ Mixer    │──▶ IF    │
  │                                                          └──────────┘  output  │
  │                                                                         to ADC │
  └──────────────────────────────────────────────────────────────────────────────┘
               │ USB-A                              │ SMA RF
               ▼                                    ▼
  ┌────────────────────┐              ┌────────────────────────┐
  │ Raspberry Pi 5     │              │ ANTENNA PANEL          │
  │ (Processing PC)    │              │ (200mm × 120mm RO4003C)│
  │                    │              │                        │
  │ Runs: Python FMCW  │              │ TX Array: 4×4 patches  │
  │ aeris_control.py   │              │ ┌──┬──┬──┬──┐         │
  │ visualization.py   │              │ │P │P │P │P │         │
  │ data_logger.py     │              │ ├──┼──┼──┼──┤  TX     │
  │                    │              │ │P │P │P │P │  side   │
  │ USB to laptop for  │              │ ├──┼──┼──┼──┤         │
  │ display (HDMI or   │              │ │P │P │P │P │         │
  │ Ethernet for SSH)  │              │ ├──┼──┼──┼──┤         │
  └────────────────────┘              │ │P │P │P │P │         │
                                      │ └──┴──┴──┴──┘         │
                                      │ ←  45mm  →            │
                                      │                        │
                                      │ RX Array: 4×4 patches  │
                                      │ ┌──┬──┬──┬──┐         │
                                      │ │P │P │P │P │         │
                                      │ ├──┼──┼──┼──┤  RX     │
                                      │ │P │P │P │P │  side   │
                                      │ ├──┼──┼──┼──┤         │
                                      │ │P │P │P │P │         │
                                      │ ├──┼──┼──┼──┤         │
                                      │ │P │P │P │P │         │
                                      │ └──┴──┴──┴──┘         │
                                      └────────────────────────┘
```

---

## 2. Power Wiring Detail

### 2.1 24V Input to Power Board

```
  24V Battery/PSU                    AERIS Power Board
  ┌──────────────┐                   ┌──────────────────────────────────┐
  │ (+) ─────────┼──── AWG 12 ──────▶│ F1 (8A Fuse) ─▶ D1 (SS36, RPP) │
  │              │    red wire        │              ─▶ C1 (1000µF/35V) │
  │ (-) ─────────┼──── AWG 12 ──────▶│ GND bus                         │
  │              │    black wire      │                                 │
  └──────────────┘                   │  LT8612: 24V→5V/5A              │
   XT60 Female                       │  ├── L1 (4.7µH)                 │
   on supply side                    │  ├── C2 (100µF output)          │
                                     │  └── feedback R1=100k, R2=22k   │
  NOTE: XT60 connector                                                  │
  Male on power board                │  LT8607: 5V→3.3V/3A            │
  Female on supply                   │  ├── L2 (2.2µH)                 │
  (prevents accidental               │  └── C3 (47µF output)           │
  polarity reversal)                 │                                  │
                                     │  TPS65133: ±5V/1A              │
                                     │  (for RF bias rails)             │
                                     │                                  │
                                     │  LM7812: 24V→12V/1A            │
                                     │  (for HMC451 PA supply)          │
                                     └──────────────────────────────────┘
```

### 2.2 Power Distribution from Power Board to Main Board

```
  Power Board Output          Cable              Main Board Input
  ┌────────────────┐          DF13               ┌────────────────────┐
  │ J1 (6-pin)     │          6-pin              │ J2 (6-pin)         │
  │ Pin 1: 5V      │──AWG18──▶│ Pin 1: 5V       │                    │
  │ Pin 2: 5V      │──AWG18──▶│ Pin 2: 5V (x2)  │ → STM32, RPi USB  │
  │ Pin 3: 3.3V    │──AWG18──▶│ Pin 3: 3.3V     │ → Logic devices    │
  │ Pin 4: GND     │──AWG18──▶│ Pin 4: GND      │                    │
  │ Pin 5: GND     │──AWG18──▶│ Pin 5: GND (x2) │                    │
  │ Pin 6: 12V     │──AWG18──▶│ Pin 6: 12V      │ → PA supply        │
  └────────────────┘          └─────────────────┘└────────────────────┘

  Power Board to RF Frontend:
  ┌────────────────┐          Molex 8-pin          ┌────────────────────┐
  │ J3 (8-pin)     │                               │ J4 (8-pin)         │
  │ Pin 1: +5V PA  │──AWG18──────────────────────▶│ → HMC451 Vd supply │
  │ Pin 2: +5V RF  │──AWG18──────────────────────▶│ → HMC647A supply   │
  │ Pin 3: +3.3V   │──AWG18──────────────────────▶│ → LNA logic supply  │
  │ Pin 4: +5V RF  │──AWG18──────────────────────▶│ → LNA drain supply  │
  │ Pin 5: +5V RFB │──AWG18──────────────────────▶│ → Bias circuits     │
  │ Pin 6: -5V RFB │──AWG18──────────────────────▶│ → Gate bias neg.   │
  │ Pin 7: GND     │──AWG18──────────────────────▶│ GND (×2)            │
  │ Pin 8: GND     │──AWG18──────────────────────▶│                     │
  └────────────────┘                               └────────────────────┘
```

---

## 3. RF Signal Wiring (SMA / 2.92 mm Connectors)

### 3.1 TX Path RF Connections

```
  Main Board                   RF Frontend Board
  ┌─────────────┐              ┌──────────────────────────────────────┐
  │             │              │                                        │
  │ J_VCO_OUT   │──RG405──────▶│ J_PA_IN     (SMA, +14 dBm input)     │
  │ (SMA female)│  10cm semi   │                                        │
  │             │  rigid       │  PA HMC451: +14 dBm → +29 dBm        │
  │ J_LO_OUT    │──RG405──────▶│ J_LO_IN     (SMA, +10 dBm LO)        │
  │ (SMA female)│  10cm        │ (feeds mixer for IF generation)       │
  └─────────────┘              │                                        │
                               │  PA OUT (J_PA_OUT, SMA)               │
                               │   └──▶ 1:16 Wilkinson Divider         │
                               │         (internal PCB trace network)   │
                               │                                        │
                               │  16× TX Phase Shifter Outputs:         │
                               │  J_TX[0]..J_TX[15]  (2.92mm female)   │
                               └──────────────────────────────────────┘
                                  ↓ 16× RG405 flexible, 80mm each, ↓
                                  ↓ PHASE-MATCHED to ±5° at 10 GHz  ↓
                               ┌──────────────────────────────────────┐
                               │ ANTENNA PANEL (Rogers RO4003C PCB)   │
                               │                                        │
                               │  TX patch elements:                    │
                               │  ┌─────────────────────────────────┐  │
                               │  │ P[0,0] P[0,1] P[0,2] P[0,3]   │  │
                               │  │ P[1,0] P[1,1] P[1,2] P[1,3]   │  │
                               │  │ P[2,0] P[2,1] P[2,2] P[2,3]   │  │
                               │  │ P[3,0] P[3,1] P[3,2] P[3,3]   │  │
                               │  └─────────────────────────────────┘  │
                               │  Element spacing: 15mm × 15mm          │
                               │  Each fed via 2.92mm SMA launch pad    │
                               └──────────────────────────────────────┘
```

### 3.2 RX Path RF Connections

```
  ANTENNA PANEL (RX side)      RF Frontend Board
  ┌───────────────────────┐    ┌──────────────────────────────────────┐
  │ 16× RX patch elements │    │                                        │
  │ P[0,0]..P[3,3]        │    │  16× LNA inputs:                      │
  │                        │    │  J_RX[0]..J_RX[15]  (2.92mm female)  │
  │  ↑ 15mm spacing ↑     │    │                                        │
  │                        │    │  LNA HMC1040LP4E (×16):               │
  │ 2.92mm SMA launch pads│    │  ┌──────────────────────────────────┐ │
  └──────┬─────────────────┘   │  │ Each: NF 1.5 dB, Gain 18 dB     │ │
         │  16× RG405           │  │ VDD = +3.3V (drain)              │ │
         │  flexible            │  │ VGG = +0.3V (gate, from DAC)    │ │
         │  80mm each           │  └──────────────────────────────────┘ │
         │  phase-matched       │                                        │
         ▼                      │  16× RX Phase Shifters (HMC647A):     │
  ┌──────────────────────────── │  SPI2 chain control                   │
  │  J_RX_IN[0..15]             │                                        │
  └──────────────────────────── │  16:1 Wilkinson Combiner (PCB trace)  │
                                 │   (-13 dB split loss + +12 dB comb.) │
                                 │                                        │
                                 │  Combined RX signal → Mixer input:     │
                                 │  J_MIX_RF  (SMA, ~-35 dBm received)  │
                                 │                                        │
                                 │  HMC213B Mixer:                        │
                                 │  RF in: from combiner                  │
                                 │  LO in: from VCO (+10 dBm, internal)   │
                                 │  IF out: J_IF_OUT (SMA, 0–5 kHz)      │
                                 │   └──▶ IF Amplifier (+20 dB)          │
                                 │   └──▶ Low-pass filter (fc = 10 kHz) │
                                 │   └──▶ J_ADC_IN (SMA or BNC)         │
                                 └──────────────────────────────────────┘
                                           │ BNC or SMA
                                           ▼
                               ┌─────────────────────┐
                               │ Main Board: ADS8661  │
                               │ 16-bit ADC, 1 MSPS   │
                               │ SPI4 → STM32H743     │
                               └─────────────────────┘
```

---

## 4. Digital Control Wiring (SPI Buses)

### 4.1 SPI Bus Map

```
  STM32H743ZIT6                          Devices
  ┌─────────────────────────────────┐
  │                                 │
  │  SPI1 (AF5, 10 MHz)             │
  │  ├── SCK:  PA5  ─────────────────────────────────▶ TX Phase Shifter chain
  │  ├── MOSI: PA7  ─────────────────────────────────▶ HMC647A × 16 (TX array)
  │  ├── MISO: PA6  ◀────────────────────────────────  (readback if needed)
  │  └── CS:   PA4  ─────────────────────────────────▶ All TX shifters (shared)
  │                                                       ┌─────┐   ┌─────┐
  │  Daisy chain: Data in → PSH_TX[15] → PSH_TX[14] → ... → PSH_TX[0] → Data out
  │                                                       └─────┘   └─────┘
  │  SPI2 (AF5, 10 MHz)
  │  ├── SCK:  PB13 ─────────────────────────────────▶ RX Phase Shifter chain
  │  ├── MOSI: PB15 ─────────────────────────────────▶ HMC647A × 16 (RX array)
  │  ├── MISO: PB14 ◀────────────────────────────────  
  │  └── CS:   PB12 ─────────────────────────────────▶ All RX shifters (shared)
  │
  │  SPI3 (AF6, 1 MHz)
  │  ├── SCK:  PC10 ─────────────────────────────────▶ ADF4159 CLK
  │  ├── MOSI: PC12 ─────────────────────────────────▶ ADF4159 DATA
  │  ├── MISO: PC11 (not used for ADF4159)
  │  └── CS:   PA15 ─────────────────────────────────▶ ADF4159 LE (Latch Enable)
  │
  │  SPI4 (AF5, 1 MHz)
  │  ├── SCK:  PE12 ─────────────────────────────────▶ ADS8661 SCLK
  │  ├── MOSI: PE14 ─────────────────────────────────▶ ADS8661 SDI
  │  ├── MISO: PE13 ◀────────────────────────────────  ADS8661 SDO
  │  └── CS:   PE11 ─────────────────────────────────▶ ADS8661 /CS
  │
  │  GPIO CONTROL
  │  ├── PC0  (PA_EN)  ──────────────────────────────▶ HMC451 PA Enable
  │  ├── PC1  (LNA_EN) ──────────────────────────────▶ HMC1040 LNA bias enable
  │  ├── PC2  (RAMP_EN)──────────────────────────────▶ ADF4159 TXDATA (ramp trigger)
  │  ├── PC3  (LED_OK) ──────────────────────────────▶ System OK LED (green)
  │  ├── PC4  (LED_TX) ──────────────────────────────▶ TX active LED (red)
  │  ├── PD0  (TEMP_INT)◀─────────────────────────────  NTC thermistor on PA (analog)
  │  └── PA0  (ADC_BUSY)◀────────────────────────────  ADS8661 BUSY signal
  │
  │  USB FS (PA11/PA12)
  │  ├── USB_DP: PA12 ────────────────────────────────▶ USB micro-B connector pin 3
  │  └── USB_DM: PA11 ────────────────────────────────▶ USB micro-B connector pin 2
  │              (VBUS detection on PA9)
  │
  │  UART1 (debug, 115200 baud)
  │  ├── TX: PA9  ─────────────────────────────────────▶ Debug UART header pin 1
  │  └── RX: PA10 ◀───────────────────────────────────  Debug UART header pin 2
  │
  └─────────────────────────────────┘
```

### 4.2 Phase Shifter SPI Daisy-Chain Detail

```
  STM32 SPI1 (TX array control):
  ┌──────────┐
  │  STM32   │ MOSI ──▶ DATA_IN[PSH_TX_15]
  │  SPI1    │ SCK  ──▶ CLK (all shifters, parallel)
  │          │ CS   ──▶ LE (Latch Enable, all shifters, parallel)
  └──────────┘

  Data flow for one SPI transaction (update all 16 phase shifters):
  
  1. Assert CS LOW
  2. Send 16 bytes, one per shifter, MSB to LSB order:
     Byte[0] = phase word for PSH_TX[15]  (6 bits used, bit[5:0])
     Byte[1] = phase word for PSH_TX[14]
     ...
     Byte[15] = phase word for PSH_TX[0]
  3. De-assert CS HIGH → all 16 shifters latch simultaneously
  4. Wait 2 µs for phase to settle
  
  HMC647A Phase Word Encoding:
  Bit 5 (MSB) = 180° bit  (0=bypass, 1=insert 180° shift)
  Bit 4       = 90° bit
  Bit 3       = 45° bit
  Bit 2       = 22.5° bit
  Bit 1       = 11.25° bit
  Bit 0 (LSB) = 5.625° bit
  
  Total phase = sum of active bits
  Example: 90° = bit4 set → byte = 0b00010000 = 0x10 = 16 decimal
  Example: 45° = bit3 set → byte = 0b00001000 = 0x08 = 8 decimal
```

---

## 5. USB Connection to Raspberry Pi 5

```
  Main Board (STM32H743)       Cable              Raspberry Pi 5
  ┌─────────────────────┐                          ┌─────────────────────┐
  │                     │                          │                     │
  │ USB micro-B         │──USB-A to Micro-B───────▶│ USB3 Type-A port    │
  │ J_USB1              │  (0.3m, shielded)        │                     │
  │ (CDC-ACM device)    │                          │ /dev/ttyACM0        │
  │                     │                          │ (CDC-ACM serial)    │
  │ Also: Ethernet RJ45 │──Ethernet Cat6──────────▶│ Ethernet port       │
  │ (for faster data if │  (optional, for          │ (SSH access,        │
  │ USB is insufficient)│  high-bandwidth mode)    │ higher throughput)  │
  │                     │                          │                     │
  └─────────────────────┘                          │ HDMI: to monitor    │
                                                   │ USB: keyboard/mouse │
                                                   │ (for on-site use)   │
                                                   └─────────────────────┘
  
  USB Protocol:
  - CDC-ACM serial at 2 Mbaud
  - Packet format: [0xAA][0x55][uint16 length][uint8 cmd][payload][uint8 checksum]
  - Data rate for ADC streaming: 16-bit × 8 kSPS = 128 kbps → well within USB FS limit
  - Command round-trip latency: <5 ms typical
```

---

## 6. Cooling System Wiring

```
  Main Board                   Fan Bracket (80mm fan)
  ┌────────────────┐           ┌──────────────────────────────┐
  │ J_FAN (2-pin)  │           │ Fan (5V, 0.2A, 80mm × 25mm) │
  │ Pin 1: 5V (red)│──AWG26───▶│ Red wire (+5V)               │
  │ Pin 2: GND(blk)│──AWG26───▶│ Black wire (GND)             │
  └────────────────┘           │ Yellow wire (tach): NC       │
                               └──────────────────────────────┘
  
  Thermal Protection:
  ┌────────────────┐
  │ NTC Thermistor │──── Kapton tape adhesive mount on PA heatsink
  │ (10kΩ @ 25°C) │──▶ Main Board ADC input (PA0/PD0)
  │                │     STM32 reads every 100ms
  │                │     Shutdown threshold: 70°C
  └────────────────┘     Warning threshold: 60°C
```

---

## 7. External Connectors Summary

| Connector | Type | Location | Signal | Wire Color | Notes |
|---|---|---|---|---|---|
| J_POWER_IN | XT60 Male | Power Board | 24V DC | Red/Black | 8A rated |
| J_TX_RF | SMA Female | Front Panel | RF TX Out (SMA to VNA for test) | N/A (RF) | For test access |
| J_RX_RF | SMA Female | Front Panel | RF RX In (direct) | N/A (RF) | For test access |
| J_IF_MON | SMA Female | Front Panel | IF output monitor | N/A (RF) | Spectrum analyzer |
| J_USB | Micro-USB B | Front Panel | CDC-ACM to RPi5/PC | USB cable | Primary control |
| J_ETH | RJ45 | Front Panel | Ethernet | Cat6 | Optional |
| J_DEBUG | 2.54mm 4-pin | Internal | UART debug | AWG26 | 3.3V UART |
| J_JTAG | 2.54mm 20-pin | Internal | ST-Link SWD | Ribbon | Firmware flash |
| J_ANT_TX[0..15] | 2.92mm Female | RF Board | TX antenna feeds | Semi-rigid | Phase matched |
| J_ANT_RX[0..15] | 2.92mm Female | RF Board | RX antenna inputs | Semi-rigid | Phase matched |

---

## 8. Cable Specifications

| Cable | Type | Length | Application | Notes |
|---|---|---|---|---|
| 24V power | AWG12, 2-conductor | 0.5m | Battery to Power Board | XT60 connectors |
| Board power | AWG18, multi-conductor | 0.15m | Power Board to Main Board | DF13 connector |
| RF frontend power | AWG18, multi-conductor | 0.15m | Power Board to RF Frontend | Molex 8-pin |
| VCO to PA | RG-405 semi-rigid | 0.10m | Main Board to RF Frontend | 2.92mm both ends |
| LO to Mixer | RG-405 semi-rigid | 0.10m | VCO tap to Mixer LO | 2.92mm both ends |
| TX phase shifter to antenna | RG-405 flexible | 0.08m × 16 | Phase shifters to TX patches | 2.92mm, phase-matched |
| RX antenna to LNA | RG-405 flexible | 0.08m × 16 | RX patches to LNA inputs | 2.92mm, phase-matched |
| IF output to ADC | RG-174 flexible | 0.15m | Mixer IF to ADC input | SMA to SMA |
| USB control | USB-A to Micro-B | 0.30m | STM32 to RPi5 | Standard USB 2.0 |
| Fan power | AWG26, 2-conductor | 0.20m | Main Board to fan | JST 2-pin |

---

## 9. Phase Matching Procedure for RF Cables

Phase matching of the 16 TX and 16 RX antenna cables is critical for proper beam steering.

**Procedure:**
1. Cut all 16 TX cables to the same physical length ±0.5mm
2. Measure S21 phase of each cable with VNA at 10.05 GHz
3. Record phase of each cable: φ₁, φ₂, ..., φ₁₆
4. Compute mean phase: φ_mean = average(φ₁..φ₁₆)
5. Compute error: Δφᵢ = φᵢ - φ_mean
6. If |Δφᵢ| > 5°: trim cable slightly (shorten by δL where δL = Δφᵢ × λ/(360°) = Δφᵢ × 0.03/360)
7. Repeat measurement until all cables within ±3° of mean
8. Store residual errors in calibration table for software correction

**Expected cable electrical length:** 80mm at velocity factor 0.70 (ε_r_eff ≈ 2.04 for RG-405) → electrical length = 80/0.70 = 114.3mm = 3.81λ at 10 GHz → phase = 3.81 × 360° = 1372° ≡ 292° (mod 360°)

---

*End of Wiring Diagram Document — AERIS-10P Rev 1.0*
