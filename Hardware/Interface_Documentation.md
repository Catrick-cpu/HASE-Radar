# AERIS-10P Interface Documentation
## Rev 1.0 — 2026-07-14

---

## 1. External Interfaces

| Connector | Type | Location | Signal | Notes |
|---|---|---|---|---|
| J_PWR_IN | XT60 Male | Front panel | +24V DC, max 8A | AWG12 wire from battery or AC adapter |
| J_TX_RF | SMA Female | Front panel | RF TX test point (+27 dBm nominal) | Use 20 dB attenuator before connecting instruments |
| J_RX_RF | SMA Female | Front panel | RF RX input (direct antenna bypass) | For alignment only |
| J_IF_MON | SMA Female | Front panel | IF beat signal monitor (0–5 kHz) | Safe to connect spectrum analyzer directly |
| J_USB | Micro-USB B | Front panel | CDC-ACM control interface | USB 2.0 FS, 12 Mbps |
| J_ETH | RJ45 | Front panel | Ethernet 100 Mbps | Optional, for SSH access to RPi5 |
| J_DEBUG | 2.54mm 4-pin | Internal | UART debug, 115200 baud, 3.3V | Pin 1: GND, 2: RX, 3: TX, 4: 3V3 |
| J_SWD | 2×5 1.27mm | Internal | ST-Link SWD debug/program | SWDIO, SWDCLK, GND, VCC, NRST |

---

## 2. Internal Board-to-Board Interfaces

### Power Board → Main Control Board

| Connector | J2 (DF13-6P-1.25H) |
|---|---|
| Pin 1 | +5V, 3A max |
| Pin 2 | +5V, 2A (duplicate) |
| Pin 3 | +3.3V, 1.5A max |
| Pin 4 | GND |
| Pin 5 | GND (duplicate, high current) |
| Pin 6 | +12V, 0.5A (for PA bias via RF board) |

### Power Board → RF Frontend Board

| Connector | J3 (Molex 8-pin, 2.54mm) |
|---|---|
| Pin 1 | +5V PA (HMC451 drain), 1A |
| Pin 2 | +5V RF (HMC647A), 2A |
| Pin 3 | +3.3V (HMC1040 drain), 0.8A |
| Pin 4 | +5V RF bias (HMC647A duplicate) |
| Pin 5 | +5V negative bias (inverted via TPS65133) |
| Pin 6 | -5V (gate bias for PA HMC451 VGG) |
| Pin 7 | GND |
| Pin 8 | GND |

### Main Board → RF Frontend (SPI/Control)

| Connector | J4 (FPC 20-pin, 0.5mm pitch) |
|---|---|
| Pin 1 | SPI1_SCK (TX phase shifter clock) |
| Pin 2 | SPI1_MOSI (TX PS data) |
| Pin 3 | SPI1_MISO |
| Pin 4 | SPI1_NSS (TX PS chip select) |
| Pin 5 | SPI2_SCK (RX phase shifter clock) |
| Pin 6 | SPI2_MOSI (RX PS data) |
| Pin 7 | SPI2_MISO |
| Pin 8 | SPI2_NSS (RX PS chip select) |
| Pin 9 | PA_EN (GPIO PC0, 3.3V CMOS) |
| Pin 10 | LNA_EN (GPIO PC1) |
| Pin 11–16 | GND |
| Pin 17–20 | +3.3V logic supply for level translation |

---

## 3. SPI Protocol Specifications

### Phase Shifter SPI (SPI1 = TX, SPI2 = RX)
- Mode: CPOL=0, CPHA=0 (Mode 0)
- Clock: 10 MHz
- Word size: 8 bits
- CS: active LOW, shared by all 16 elements (daisy-chain)
- Data format: MSB first
- Transaction: 16 bytes sent while CS is LOW, then CS goes HIGH to latch
- Byte order: first byte → last element in chain (PSH[15]), last byte → PSH[0]
- Settling time: 2 µs after CS rising edge before phase is valid

### ADF4159 SPI (SPI3)
- Mode: CPOL=0, CPHA=0 (Mode 0)
- Clock: 1 MHz (conservative, allows time for VCO settling)
- Word size: 32 bits (sent as 4× 8-bit)
- LE (Latch Enable): active HIGH pulse after each 32-bit word
- Programming order: R7 first, R0 last (per ADF4159 datasheet)
- After writing all registers: VCO lock time 10–50 ms

### ADS8661 ADC SPI (SPI4)
- Mode: CPOL=0, CPHA=0 (Mode 0)
- Clock: 1 MHz (ADC supports up to 25 MHz, use conservative for first bring-up)
- Word size: 24 bits (8-bit command + 16-bit data response)
- CS: active LOW during full 24-bit transaction
- Conversion trigger: CS falling edge starts conversion; BUSY goes HIGH during conversion
- Data ready: BUSY falling edge signals data ready (or poll BUSY)
- Read back: 16-bit result in bits [23:8] of response word

---

## 4. USB CDC-ACM Protocol

**Physical:** USB 2.0 Full Speed, Micro-USB B connector
**Logical:** Virtual COM port (CDC-ACM class, no driver needed on Linux/Mac, uses USB CDC driver on Windows)

**Packet format:**
```
Byte 0: 0xAA (sync 1)
Byte 1: 0x55 (sync 2)
Byte 2: LENGTH_HIGH (payload length, MSB)
Byte 3: LENGTH_LOW  (payload length, LSB)
Byte 4: CMD         (command byte)
Byte 5..N: PAYLOAD  (command-specific)
Byte N+1: CHECKSUM  (XOR of all preceding bytes)
```

**Commands:**

| CMD | Direction | Payload | Response |
|---|---|---|---|
| 0x01 PING | PC→Radar | none | 0x02 PONG |
| 0x10 SET_BEAM | PC→Radar | [float32 az][float32 el] | none |
| 0x11 SET_CHIRP | PC→Radar | [uint64 f_start][uint64 f_stop][uint32 t_us] | none |
| 0x20 START_CAPTURE | PC→Radar | [uint32 n_samples] | streams 0x21 packets |
| 0x21 DATA_PACKET | Radar→PC | [uint32 seq][uint16[] samples] | none (streaming) |
| 0x30 GET_STATUS | PC→Radar | none | 0x31 STATUS |
| 0x31 STATUS | Radar→PC | [uint8 flags][float32 az][float32 el][float32 temp] | none |
| 0x40 SET_PA_ENABLE | PC→Radar | [uint8 0=off 1=on] | none |
| 0x50 REBOOT | PC→Radar | none | none (firmware reboots) |

---

## 5. RF Connector Torque Specifications

| Connector Type | Torque | Notes |
|---|---|---|
| SMA (male/female) | 0.56 N·m (5 lb·in) | Use calibrated torque wrench |
| 2.92mm (K connector) | 0.45 N·m (4 lb·in) | Lower torque than SMA — do NOT overtighten |
| N-type | 1.36 N·m (12 lb·in) | For test equipment adapters |

⚠️ **Never tighten 2.92mm connectors by hand without torque wrench — overtightening destroys the connector.**

---

## 6. GPIO Assignment Table (STM32H743ZIT6)

| GPIO | Function | Direction | Notes |
|---|---|---|---|
| PA4 | SPI1_NSS | Output | TX phase shifter CS (active LOW) |
| PA5 | SPI1_SCK | Output | TX phase shifter clock |
| PA6 | SPI1_MISO | Input | TX phase shifter data out |
| PA7 | SPI1_MOSI | Output | TX phase shifter data in |
| PA9 | USART1_TX | Output | Debug UART TX |
| PA10 | USART1_RX | Input | Debug UART RX |
| PA11 | USB_DM | Bidirectional | USB Data Minus |
| PA12 | USB_DP | Bidirectional | USB Data Plus |
| PA15 | SPI3_NSS | Output | ADF4159 LE (Latch Enable) |
| PB12 | SPI2_NSS | Output | RX phase shifter CS |
| PB13 | SPI2_SCK | Output | RX phase shifter clock |
| PB14 | SPI2_MISO | Input | RX phase shifter data out |
| PB15 | SPI2_MOSI | Output | RX phase shifter data in |
| PC0 | PA_EN | Output | PA enable (HIGH=on) |
| PC1 | LNA_EN | Output | LNA enable (HIGH=on) |
| PC2 | RAMP_EN | Output | ADF4159 TX_DATA / ramp trigger |
| PC3 | LED_OK | Output | Green status LED |
| PC4 | LED_TX | Output | Red TX active LED |
| PC10 | SPI3_SCK | Output | ADF4159 CLK |
| PC11 | SPI3_MISO | Input | (not used for ADF4159) |
| PC12 | SPI3_MOSI | Output | ADF4159 DATA |
| PD0 | TEMP_ADC | Input | NTC thermistor (analog, ADC3 CH0) |
| PE11 | SPI4_NSS | Output | ADS8661 CS |
| PE12 | SPI4_SCK | Output | ADS8661 SCLK |
| PE13 | SPI4_MISO | Input | ADS8661 SDO |
| PE14 | SPI4_MOSI | Output | ADS8661 SDI |
| PE15 | ADC_BUSY | Input | ADS8661 BUSY (interrupt) |
