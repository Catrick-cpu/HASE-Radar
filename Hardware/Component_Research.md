# AERIS-10P Component Research and Selection
## Rev 1.0 — 2026-07-14

Complete research document for all major ICs. Each entry: selected part, rationale, alternatives, pricing, availability.

---

## 1. Phase Shifter — HMC647ALP5E (Selected)

**Selected:** HMC647ALP5E (Analog Devices, formerly Hittite Microwave)
- 6-bit digital phase shifter, 10–14 GHz
- Insertion loss: 4 dB typical at 10 GHz
- Phase range: 0–360° in 64 steps (5.625° LSB)
- Phase accuracy: ±1.5° RMS
- Switching time: <2 µs
- Supply: +5V, 90 mA
- Package: QFN-32, 5×5 mm
- Mouser: 597-HMC647ALP5E, ~$35/unit

**Why selected:** Only 6-bit MMIC digital phase shifter available at 10 GHz from stock distributors in 2025–2026. The 6-bit resolution (5.625° LSB) matches our 4-element array beam width (22°) — one LSB corresponds to 22°/4 ≈ 5.5°, which is well matched.

**Alternative 1: MAPS-010144 (Macom, 5-bit)**
- 5 bits = 11.25° LSB — coarser control than HMC647A
- Cheaper (~$18/unit) but less phase resolution
- Rejected: 5-bit insufficient for precise beam control

**Alternative 2: Custom GaAs MMIC**
- Better specs (lower insertion loss) but minimum order quantity 100+ units, 16-week lead time, $50k NRE
- Rejected: impractical for research prototype

---

## 2. VCO — HMC733LP6CE (Selected)

**Selected:** HMC733LP6CE (Analog Devices)
- Frequency: 9.5–11.0 GHz
- Output power: +17 dBm
- Phase noise: -120 dBc/Hz @ 100 kHz
- Tuning sensitivity: 40 MHz/V typical
- Supply: +5V, Vtune 0–12V
- Package: LP-6 (5×5 mm)
- Mouser: 597-HMC733LP6CE, ~$45/unit

**Why selected:** Best phase noise at 10 GHz in LCC package. Critical for FMCW clutter rejection — VCO phase noise limits ability to detect slow targets in clutter.

**Alternative: HMC-SXX112 (integrated PLL+VCO)**
- All-in-one but less flexibility, worse phase noise
- Rejected: phase noise is critical; separate VCO+PLL gives better control

---

## 3. PLL — ADF4159CCPZ (Selected)

**Selected:** ADF4159CCPZ (Analog Devices)
- Fractional-N PLL, up to 13 GHz
- Built-in FMCW sawtooth/triangular ramp generator
- Reference: up to 110 MHz
- PFD: up to 110 MHz
- Charge pump: 0.3–4.77 mA programmable
- SPI programmable (32-bit registers)
- Package: CP-40-3, 6×6 mm
- Mouser: 584-ADF4159CCPZ, ~$28/unit

**Why selected:** The ADF4159 is one of the few PLLs with a built-in hardware FMCW ramp generator. This eliminates the need for software-generated chirps (which would require real-time MCU intervention at high rates). The ramp runs autonomously in hardware after programming.

**ADF4159 register programming tool:** ADIsimPLL (free from analog.com) can compute all register values from desired frequency and ramp parameters.

---

## 4. TX PA — HMC451LS6GE (Selected)

**Selected:** HMC451LS6GE (Analog Devices)
- Frequency: 8–15 GHz
- Gain: 28 dB
- P1dB: +29 dBm (0.8 W)
- PAE: 20% @ P1dB
- Supply: VDD1=+5V (300 mA), VDD2=+5V (200 mA), VGG1/2 = 0 to -1V
- Package: SMT LS-6 (6-pin, 4×4 mm)
- Mouser: 597-HMC451LS6GE, ~$65/unit

**Why selected:** Available in stock at Mouser/DigiKey, covers 10 GHz well, +29 dBm is significantly above 75 W PEP legal limit concern (we operate at +27 dBm, 2W, far below 75W). Good efficiency (20%).

**Thermal note:** At +27 dBm output with 20% PAE, supply power = 10W output / PAE = 10·(10^(27/10)/1000)/0.20 = 0.5/0.2 = 2.5W supply. Dissipation = 2.5 - 0.5 = 2W heat. Heatsink required.

---

## 5. LNA — HMC1040LP4E (Selected)

**Selected:** HMC1040LP4E (Analog Devices)
- Frequency: 8–12 GHz
- Noise Figure: 1.5 dB
- Gain: 18 dB
- P1dB: +18 dBm
- OIP3: +30 dBm
- Supply: VDD = +3.3V, 15 mA per device
- Package: QFN-24, 4×4 mm
- Mouser: 597-HMC1040LP4E, ~$45/unit

**Why selected:** Lowest NF available at 10 GHz in distributor stock. NF is the most important parameter for the LNA since it directly adds to system NF. Even 0.1 dB improvement in LNA NF reduces total system NF by nearly 0.1 dB.

**Total RX chain NF (Friis):** NF_sys ≈ NF_LNA + (NF_mixer − 1)/G_LNA = 1.5 + (4.0−1)/63.1 ≈ 1.55 dB

---

## 6. Mixer — HMC213B (Selected)

**Selected:** HMC213B (Analog Devices)
- Type: Double-balanced mixer
- RF/LO range: 8–26 GHz
- IF range: DC to 5 GHz
- Conversion loss: 6 dB
- LO-to-RF isolation: 40 dB
- LO power required: +13 dBm minimum
- Package: QFN-16, 4×4 mm
- Mouser: 597-HMC213B, ~$55/unit

**Why selected:** Handles 10 GHz easily, covers full chirp BW (100 MHz), DC-coupled IF (can receive the very low IF beat note of 0-2 kHz for FMCW). Good isolation prevents TX leakage from saturating IF.

**LO power:** VCO outputs +17 dBm. Tap off -7 dB (directional coupler on PCB) to get +10 dBm for mixer LO. Or use external attenuator.

---

## 7. MCU — STM32H743ZIT6 (Selected)

**Selected:** STM32H743ZIT6 (STMicroelectronics)
- Core: ARM Cortex-M7 @ 480 MHz
- Flash: 2 MB, RAM: 1 MB (SRAM)
- Peripherals: 6× SPI, 4× I2C, 4× USART, USB FS/HS, Ethernet, 2× SDMMC
- GPIO: 114 available (LQFP-144 package)
- Supply: 1.8–3.6V, 150 mA typical
- Package: LQFP-144
- Mouser: 511-STM32H743ZIT6, ~$18/unit (check availability)

**Why selected:** 6 SPI buses is critical — we need SPI1 (TX PS), SPI2 (RX PS), SPI3 (ADF4159), SPI4 (ADS8661), with 2 spares. No other affordable MCU offers this without external SPI expander. 480 MHz gives real-time performance.

**Development tools:** STM32CubeIDE (free), STM32CubeMX (for HAL code generation), arm-none-eabi-gcc (open-source toolchain). ST-Link V3 for programming/debugging (~$20 for Nucleo board which includes ST-Link).

---

## 8. Processing — Raspberry Pi 5 8GB (Selected)

**Selected:** Raspberry Pi 5 8GB
- CPU: BCM2712, quad-core Cortex-A76 @ 2.4 GHz
- RAM: 8 GB LPDDR4X
- USB: 2× USB 3.0, 2× USB 2.0
- Interface: Ethernet, WiFi, Bluetooth
- Price: ~$80
- OS: Raspberry Pi OS 64-bit

**Why selected:** Best price/performance ratio for Python DSP. NumPy FFT on RPi5 is fast: 100k-point complex FFT takes ~5 ms → sufficient for 2 Hz update rate on range-Doppler map.

**Benchmark estimate:**
- chirp_matrix size: 100 × 8 = 800 complex samples (negligible)
- range FFT: 8192-point FFT × 100 chirps = fast
- Doppler FFT: 100-point FFT × 4096 range bins = fast
- Total per CPI: <<100 ms → sufficient for 10 Hz update rate

---

## 9. ADC — ADS8661IRGAT (Selected)

**Selected:** ADS8661IRGAT (Texas Instruments)
- Resolution: 16 bits
- Sample rate: 1 MSPS (maximum)
- Interface: SPI, 4-wire
- Input: differential, ±VREF (±4.096V with external REF5040)
- SNR: 92 dB typical
- Package: VQFN-20
- Mouser: 595-ADS8661IRGAT, ~$12/unit

**Why selected:** 16-bit resolution gives 96 dB dynamic range — important for detecting weak targets in the presence of strong clutter or near-range returns. 1 MSPS is massively oversample for our IF bandwidth (<5 kHz) — decimate by 125 to get 8 kSPS effective rate, dramatically improving SNR through processing gain.

---

## 10. Reference Oscillator — ABRACON AOCJY-10 (Selected)

**Selected:** ABRACON AOCJY-10.000MHZ-T
- Frequency: 10.000000 MHz
- Stability: ±0.01 ppm (OCXO — oven-controlled)
- Phase noise: -140 dBc/Hz @ 1 kHz
- Output: CMOS square wave
- Supply: +5V, 80 mA (during warm-up), 40 mA steady state
- Warm-up: 5 minutes to stability
- Mouser: 815-AOCJY10.000MHZ, ~$25/unit

**Why selected:** OCXO frequency stability ensures long coherent integration time without phase drift. A 1 ppm TCXO would drift 1 cycle in 100 µs, limiting integration to <100 µs. Our OCXO at 0.01 ppm allows integration >>100 ms without correction.

**Upgrade path:** GPS-disciplined OCXO (e.g., Trimble Thunderbolt, ~$200 used) would give sub-Hz accuracy for long-range coherent SAR-mode operation.
