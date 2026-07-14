# AERIS-10P Design History and Decision Log
**Format:** [Date] [Phase] [Decision]: Rationale. Alternatives considered.

---

## 2026-07-14 — Initial Design Session

**[2026-07-14] [Concept] [Project Name]:** Named AERIS-10P (Affordable Experimental Radar Intelligence System, 10 GHz Phased Array). Name chosen to reflect: experimental nature (important for regulatory context), budget constraint (affordable), and technical spec (10 GHz phased array). The "10P" distinguishes it from hypothetical future variants at other frequencies.

**[2026-07-14] [Concept] [Inspired by AERIS-10 N]:** Design inspired by the open-source AERIS-10 N radar project. Key differences: this design targets German amateur radio operation (different regulatory framework than US-based AERIS-10 N), adds phased-array capability, and targets 2-3 km range vs shorter-range demonstrations.

**[2026-07-14] [Regulatory] [German Band Selection]:** Selected 10.000–10.100 GHz after researching German amateur radio band plan (DARC). Key finding: 10.000–10.500 GHz (3 cm band) has full amateur secondary allocation in Germany. Klasse A license permits up to 75 W PEP. Our 1 W design has 18.75 dB margin. Alternative bands rejected: 5.8 GHz (no German amateur allocation outside ISM), 24 GHz (limited allocation, expensive components), 2.4 GHz (overcrowded, no good radar components).

**[2026-07-14] [Waveform] [FMCW Selected Over Pulse]:** FMCW chosen because: (1) low peak power — amateur license is power-limited, FMCW averages power over chirp time; (2) no range blind zone; (3) simpler receiver (low-rate ADC vs GHz-rate for pulse); (4) better spectral compatibility with amateur operations. Pulsed radar would need much higher peak power for same range, potentially requiring special permits.

**[2026-07-14] [RF] [10.0-10.1 GHz Chirp Band]:** 100 MHz bandwidth gives 1.5m range resolution (c/2B = 3e8/(2×100e6)). Wider bandwidth would give better resolution but would require more PCB layout care and possibly exceed amateur band allocation. 100 MHz was determined to be a good trade-off: achievable with ADF4159 + HMC733, stays within amateur band, gives useful resolution.

**[2026-07-14] [Architecture] [4×4 Array Size]:** 16 elements chosen after budget analysis. 8×8 would give better performance (11° beam width vs 22°, +6 dB gain) but costs nearly 4× more in phase shifters alone (64 × $35 = $2,240 vs 32 × $35 = $1,120). Budget constraint ($8,000 total) made 4×4 the practical choice. Future upgrade path: 4×4 + MIMO processing gives virtual 8×8.

**[2026-07-14] [Architecture] [Analog Beamforming]:** Analog phase shifters chosen over digital beamforming (per-element ADC) for cost. Digital beamforming with 32 elements would need 32 ADCs + FPGA → estimated cost $15,000+. Analog beamforming with HMC647A costs ~$1,120 for all 32 shifters. Trade-off: analog is less flexible (can only form one beam at a time, no post-processing beam agility) but sufficient for research purposes.

**[2026-07-14] [Components] [HMC647ALP5E Phase Shifter]:** Only 6-bit X-band MMIC phase shifter in stock at distributors in 2026. Alternatives reviewed: MAPS-010144 (5-bit, less resolution), UMS CHU2140 (obsolete/hard to source), custom GaAs (impractical for small quantity). HMC647A is the best available choice. 6-bit = 5.625° LSB → adequate for 4-element array where beam width is 22° (LSB = 22°/4 ≈ 5.5°, well matched).

**[2026-07-14] [Components] [ADF4159 FMCW PLL]:** Selected for built-in sawtooth ramp generator — eliminates need for real-time CPU-generated chirp (which would require DDS or DAC at high speed). ADF4159 generates the FMCW chirp autonomously in hardware once programmed. Alternative: ADF4355 (integrated PLL+VCO but worse phase noise at 10 GHz), ADF5355 (similar). ADF4159 + external HMC733 VCO gives better phase noise than integrated solutions.

**[2026-07-14] [Components] [HMC733 VCO]:** Selected for best in-class phase noise (-120 dBc/Hz @ 100 kHz offset) at 10 GHz in small quantity. This is critical for FMCW radar: VCO phase noise becomes range-dependent clutter floor. Alternative: HMC-SXX112 (integrated PLL+VCO, lower phase noise control, not as good for FMCW), custom DRO (better phase noise but impractical to source).

**[2026-07-14] [Components] [HMC451LS6GE PA]:** +29 dBm P1dB at X-band, 28 dB gain, in distributors. Operated at +27 dBm (back off 2 dB from P1dB for linearity). Alternatives: HMC943 (+33 dBm but $150+), CGY2122UH (cheaper but lower output). Decision: HMC451 gives 1W at antenna with good efficiency, within budget.

**[2026-07-14] [Components] [HMC1040LP4E LNA]:** Best noise figure (1.5 dB) at 10 GHz available from distributors in 2026. NF dominates system noise figure since it's first in the chain. Each 0.1 dB NF improvement adds ~0.4 km to max range. Alternative: TQL9092 (NF 1.7 dB, cheaper) would reduce range by ~10%.

**[2026-07-14] [Components] [STM32H743ZIT6 MCU]:** Selected because: (1) 6 SPI buses needed simultaneously (SPI1: TX PS, SPI2: RX PS, SPI3: ADF4159, SPI4: ADS8661, SPI5: spare, SPI6: spare); (2) USB FS built-in for PC communication; (3) 480 MHz for real-time control; (4) abundant GPIO (144-pin LQFP); (5) STM32Cube ecosystem. Alternatives: STM32F767 (slower), RP2040 (fast PIO but only 2 SPI buses), ESP32 (WiFi but limited SPI count).

**[2026-07-14] [Components] [Raspberry Pi 5 8GB]:** Best performance/cost for Python FMCW DSP. 2.4 GHz quad-core A76 can run 100k-point FFT at >10 Hz update rate. USB3 for ADC data streaming. Alternative: NVIDIA Jetson Nano ($149, CUDA for parallel FFT), Intel NUC ($400, overkill). Upgrade path documented in TODO.md.

**[2026-07-14] [Components] [Rogers RO4003C Substrate]:** Industry standard for X-band PCBs. εr=3.55, tan δ=0.0027, available from PCBWay and Advanced Circuits. Alternative: Rogers RO4350B (similar performance, slightly different εr), Rogers RT/duroid 5880 (lower loss but more expensive), standard FR4 (too lossy at 10 GHz — loss tangent 10× higher). RO4003C is the practical choice for a research project.

**[2026-07-14] [Mechanical] [3D-Printed Prototype]:** PETG chosen for prototype enclosure (vs machined aluminium) because: faster iteration (hours vs weeks), much cheaper ($5 vs $150+), sufficient for initial testing. Machined aluminium planned for field-use version (better RF shielding, durability, IP protection). STL files created for both prototype and final designs.

**[2026-07-14] [Software] [Python for Signal Processing]:** Python chosen for DSP because: numpy/scipy/matplotlib ecosystem; abundant radar signal processing libraries; easier development than C/MATLAB; runs on RPi5. NumPy FFT is fast enough for our update rate (<10 Hz). Alternative: MATLAB (expensive, requires license), GNU Radio (complex for custom FMCW), C++ (faster but more development time). Numba JIT compilation available for bottlenecks.

**[2026-07-14] [Software] [USB CDC-ACM Protocol]:** Custom binary packet protocol chosen over: JSON (too verbose for ADC streaming), UART (slower), SPI/I2C (requires additional hardware), Ethernet (RPi5 has it but adds complexity). Binary packet format is compact and fast. 16-bit ADC at 8 kSPS = 128 kbps → well within USB FS 12 Mbps.

**[2026-07-14] [Budget] [Total $4,451]:** Well under $8,000 target. Breakdown: RF ICs $2,292 (51%), PCBs $626 (14%), cables $512 (11%), mechanical $109 (2%), test equipment $140 (3%), consumables $75 (2%). Largest cost driver: 2.92mm SMA connectors ($358 for 40 units). Possible reduction: use cheaper SMA-type connectors for prototype, reserve 2.92mm for final version.

---

## Future Entries (Template)

When adding new entries, use this format:

**[YYYY-MM-DD] [Phase] [Decision Topic]:** What was decided. Why. What alternatives were considered and rejected. Who made the decision.

Phases: Concept, Research, Regulatory, RF, Architecture, Components, PCB, Mechanical, Software, Testing, Budget, Procurement, Assembly, Integration

---
*This log should be updated whenever a significant design decision is made or revised.*
