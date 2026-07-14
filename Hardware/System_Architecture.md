# AERIS-10P Hardware System Architecture
## Rev 1.0 — 2026-07-14

---

## 1. Overview

The AERIS-10P hardware consists of four PCBs, an antenna panel, and a processing computer in a single field-deployable unit.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AERIS-10P SYSTEM BLOCK DIAGRAM                    │
│                                                                       │
│  ┌──────────────┐     ┌──────────────────────────────────────────┐  │
│  │ OCXO 10MHz   │────▶│        AERIS MAIN CONTROL BOARD           │  │
│  │ ±0.01 ppm    │     │                                            │  │
│  └──────────────┘     │  ┌───────────┐  ┌──────────────────────┐ │  │
│                        │  │ ADF4159   │  │  STM32H743ZIT6       │ │  │
│  ┌──────────────┐     │  │ FMCW PLL  │  │  480 MHz MCU         │ │  │
│  │  24V Battery │────▶│  │ (chirp    │  │  SPI1: TX PS array   │ │  │
│  │  or AC/DC    │     │  │  gen)     │  │  SPI2: RX PS array   │ │  │
│  └──────────────┘     │  └──────┬────┘  │  SPI3: ADF4159       │ │  │
│                        │         │VTUNE  │  SPI4: ADS8661 ADC   │ │  │
│  ┌──────────────┐     │  ┌──────▼────┐  │  USB: to RPi5/PC     │ │  │
│  │ Raspberry Pi │◀────│  │ HMC733    │  └──────────────────────┘ │  │
│  │ 5 (8GB)      │ USB │  │ VCO       │                            │  │
│  │ (FMCW DSP)   │     │  │ 10GHz     │  ┌──────────────────────┐ │  │
│  └──────────────┘     │  └──────┬────┘  │  ADS8661 16-bit ADC  │ │  │
│                        │         │RF out │  (beat note capture)  │ │  │
│                        └─────────┼───────┴──────────────────────┘─┘  │
│                                  │                                      │
│                                  │ RF (10 GHz, +14 dBm)                │
│                                  ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                   AERIS RF FRONTEND BOARD                        │  │
│  │                                                                   │  │
│  │  TX PATH:                                                         │  │
│  │  RF in ──▶ HMC451 PA ──▶ 1:16 Wilkinson ──▶ 16x HMC647A ──▶    │  │
│  │           (+28dB gain) (-13dB split)  (6-bit PS)  to TX array    │  │
│  │                                                                   │  │
│  │  RX PATH:                                                         │  │
│  │  16x LNA ◀── RX array    LO──▶ HMC213B Mixer ──▶ IF ──▶ ADC     │  │
│  │  (HMC1040, NF 1.5dB)          (convert to IF)   (beat note)      │  │
│  │                                                                   │  │
│  │  CONTROL: SPI1/SPI2 from STM32 ──▶ 32x HMC647A phase shifters  │  │
│  └──────────────────────┬──────────────────────────────────────────┘  │
│                          │ 32x 2.92mm RF cables (phase-matched)        │
│                          ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │              AERIS ANTENNA PANEL (Rogers RO4003C PCB)            │  │
│  │                                                                   │  │
│  │   TX Array (4×4 patches)          RX Array (4×4 patches)         │  │
│  │   ┌─────────────────────┐         ┌─────────────────────┐        │  │
│  │   │ P  P  P  P          │         │  P  P  P  P         │        │  │
│  │   │ P  P  P  P          │         │  P  P  P  P         │        │  │
│  │   │ P  P  P  P          │         │  P  P  P  P         │        │  │
│  │   │ P  P  P  P          │         │  P  P  P  P         │        │  │
│  │   └─────────────────────┘         └─────────────────────┘        │  │
│  │   45mm × 45mm aperture              45mm × 45mm aperture          │  │
│  │   λ/2 = 15mm element spacing        λ/2 = 15mm element spacing    │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Board Descriptions

### Board 1: AERIS Main Control Board (160×100 mm, 4-layer FR4)
Primary digital control and data acquisition board.

**Key ICs:** STM32H743ZIT6, ADF4159CCPZ, HMC733LP6CE, ADS8661IRGAT, OCXO module

**Functions:**
- Generates 10 GHz FMCW chirp (ADF4159 + HMC733 VCO)
- Controls 32 phase shifters via SPI daisy-chain (SPI1 for TX, SPI2 for RX)
- Digitizes IF beat signal via ADS8661 (16-bit, 1 MSPS)
- Communicates with Raspberry Pi 5 via USB CDC-ACM
- Temperature monitoring and PA enable/disable control
- Station identification beacon (Morse CW callsign)

### Board 2: AERIS RF Frontend Board (100×60 mm, 4-layer Rogers RO4003C)
X-band RF signal chain on low-loss substrate.

**Key ICs:** HMC451LS6GE (PA), 16× HMC647ALP5E (TX phase shifters), 16× HMC1040LP4E (LNA), HMC213B (mixer)

**Functions:**
- Amplifies VCO output (+14 dBm → +29 dBm via HMC451)
- Splits TX signal 1:16 (Wilkinson divider tree on PCB)
- Phase-shifts each TX element individually (HMC647A)
- Amplifies 16 RX elements (HMC1040 LNA)
- Phase-shifts each RX element (HMC647A)
- Combines 16 RX signals (Wilkinson combiner tree)
- Down-converts combined RX signal to IF (HMC213B mixer)

### Board 3: AERIS Power Board (100×80 mm, 2-layer FR4)
Voltage conversion from 24V input to all required rails.

**Key ICs:** LT8612 (24V→5V/5A), LT8607 (5V→3.3V/3A), TPS65133 (±5V/1A), LM7812 (12V/1A)

**Rails:** +5V/5A (MCU, RPi5, logic), +3.3V/3A (MCU IO, ADC), +5V RF/1A (HMC647A), -5V RF/1A (gate bias), +12V/1A (PA drain)

### Board 4: AERIS Phase Shifter Array Board (120×80 mm, 4-layer hybrid Rogers/FR4)
Two identical boards used for TX and RX arrays.

**Key ICs:** 16× HMC647ALP5E

**Functions:** SPI daisy-chain control of 16 phase shifters, RF power distribution to 16 elements, 16 RF output ports (2.92mm SMA edge-launch)

---

## 3. Signal Flow Description

### Transmit Signal Flow
```
OCXO (10 MHz) → ADF4159 PLL (programs chirp ramp)
                      ↓
              HMC733 VCO (10.000–10.100 GHz, +17 dBm)
                      ↓ (semi-rigid cable)
              HMC451 PA (+29 dBm)
                      ↓
              1:16 Wilkinson divider (+16 dBm per element input)
                      ↓ (16 paths)
              16× HMC647A TX phase shifters (+12 dBm per element output)
                      ↓ (16 semi-rigid cables, phase-matched)
              16× TX patch antennas (6 dBi each, +18 dBm EIRP per element)
                      ↓↓↓ RADIATED ↓↓↓
              Total TX EIRP: +18 + 10*log10(16) = +30 dBm = 1W → EIRP with array gain: ~52 dBm
```

### Receive Signal Flow
```
TARGET REFLECTION (σ = 10 m²)
        ↑↑↑ Received by RX Array ↑↑↑
16× RX patch antennas (6 dBi each, received power ~-80 to -100 dBm at 3km)
        ↓ (16 semi-rigid cables)
16× HMC647A RX phase shifters (steer beam for coherent combining)
        ↓
16× HMC1040 LNA (gain +18 dB, NF 1.5 dB)
        ↓
16:1 Wilkinson combiner (+12 dB combining gain, -1 dB total)
        ↓
HMC213B Mixer (LO from HMC733 VCO tap, -6 dB conversion loss)
        ↓
IF Amplifier (+20 dB)
        ↓
Low-pass filter (fc = 10 kHz, passes beat note 0-2 kHz for <3km range)
        ↓
ADS8661 16-bit ADC (1 MSPS, decimated to 8 kSPS for IF)
        ↓ (SPI4 to STM32)
STM32H743 (collects samples, sends via USB)
        ↓ (USB CDC)
Raspberry Pi 5 (FFT, CFAR, display)
```

---

## 4. Key Design Parameters

| Parameter | Value | Justification |
|---|---|---|
| TX power at PA | +27 dBm | 2 dB backoff from P1dB=29 dBm for linearity |
| ADC sample rate | 8 kSPS | Nyquist for 4 km max range (f_beat_max = 2×4000×100e6/(3e8×1e-3) = 2.67 kHz) |
| SPI clock (phase shifters) | 10 MHz | Allows update of all 32 in <13 µs (16 bytes × 8 bits / 10 MHz = 12.8 µs) |
| SPI clock (ADF4159) | 1 MHz | ADF4159 specification, conservative |
| USB baud rate | 115200 (CDC) | Actual USB FS bandwidth 12 Mbps; 16-bit at 8 kSPS = 128 kbps, well within limit |
| Temperature limit | 70°C | PA junction temperature limit; shutdown triggered at heatsink 70°C |
| Ramp time | 1 ms | Gives 10,000 steps (at CLK2 = 10 MHz / CLK_DIV = 4 / 2.5 MHz); 40 kHz frequency step |
