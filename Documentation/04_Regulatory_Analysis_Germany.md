# AERIS-10P German Regulatory Analysis
## Amateur Radio Operation at 10 GHz
### Rev 1.0 — 2026-07-14

**Project:** AERIS-10P (Affordable Experimental Radar Intelligence System, 10 GHz Phased Array)
**Prepared by:** HASE-Radar Project Team
**Date:** 2026-07-14
**Classification:** Internal Technical Documentation

---

## Table of Contents

1. Executive Summary
2. German Amateur Radio Legal Framework
3. DARC Band Plan for 3 cm (10 GHz)
4. Power Limits and EIRP Analysis
5. Emission Type Analysis
6. Station Identification Requirements
7. Non-Interference Obligation
8. Radar-Specific Regulatory Considerations
9. Legal Risk Assessment
10. Comparison with Other Countries
11. Compliance Checklist
12. Recommended Operational Procedure for Legal Compliance
13. BNetzA Contact Information and Application Process
14. Conclusion

---

## 1. Executive Summary

The AERIS-10P is an experimental FMCW (Frequency Modulated Continuous Wave) phased-array radar system operating in the X-band at 10.0–10.1 GHz with a transmit power of +30 dBm (1 W) into a 4×4 patch array providing approximately 22 dBi of practical gain, yielding an Effective Isotropic Radiated Power (EIRP) of approximately 52 dBm (158 W EIRP).

**Core Regulatory Finding:** Operation of the AERIS-10P radar under a German Klasse A amateur radio license (Amateurfunklizenz Klasse A) is technically and legally feasible under existing German amateur radio law, subject to the conditions and caveats described in this document.

**Key Findings:**

- The operating frequency range of 10.000–10.100 GHz falls within the German amateur secondary allocation at 10.000–10.500 GHz, which is designated for all modes in the DARC band plan.
- The transmit power of 1 W (+30 dBm) is far below the maximum permitted power of 75 W PEP under the Klasse A license.
- The FMCW emission type is not explicitly prohibited under the AFuG 2017 or AFuV 2017 and is consistent with wideband amateur experimentation.
- Station identification obligations (callsign every 10 minutes) can be implemented via CW burst or digital identifier between measurement sessions.
- As a secondary user of the 10 GHz band, the AERIS-10P must not cause harmful interference to primary users (satellite, fixed, and mobile services) and must accept interference from primary users.

**Recommendation:** Before commencing field operations, the project team should contact the Bundesnetzagentur (BNetzA), specifically Referat 221 (Amateurfunk und Bürgerrufanlagen), to obtain informal written confirmation that the planned radar-type FMCW operation is within the scope of amateur experimentation. An application for a supplementary experimental permit under § 67 TKG should be considered as additional legal protection. Laboratory-only operation is advised until BNetzA clarification has been received.

---

## 2. German Amateur Radio Legal Framework

### 2.1 Amateurfunkgesetz (AFuG 2017)

The primary German statute governing amateur radio operation is the **Gesetz über den Amateurfunk (AFuG)** in its 2017 revision (BGBl. I S. 1614). The following sections are directly relevant to the AERIS-10P project:

**§ 1 AFuG — Zweck und Anwendungsbereich (Purpose and Scope)**

Section 1 defines amateur radio as a technical hobby that serves self-training, intercommunication among amateur radio operators, and technical investigations using radio techniques. This definition is broadly interpreted and encompasses experimental use of radio technology, including novel waveform experimentation. The AERIS-10P's FMCW radar modality constitutes a technical investigation into radar signal processing, beam-forming, and phased-array antenna control — all activities consistent with the statutory purpose of amateur radio experimentation.

**§ 3 AFuG — Zulassung zur Teilnahme am Amateurfunk (Licensing)**

Section 3 establishes the requirement for a valid amateur radio license and callsign. A Klasse A license grants access to all amateur radio frequency allocations and all power levels up to the maxima prescribed in the AFuV. The AERIS-10P operator must hold a valid Klasse A license and must operate the system under their personal callsign. Operation by an unlicensed person is not permitted without direct supervision by the licensee.

**§ 15 AFuG — Sendeverbot und Betriebseinschränkungen (Transmission Prohibitions and Operational Restrictions)**

Section 15 establishes the general prohibition on transmitting outside allocated amateur frequencies, on causing harmful interference to other radio services, and on operating without proper identification. All three prohibitions are addressable through proper operational procedures as described in this document.

**§ 16 AFuG — Rufzeichen (Callsign)**

Section 16 mandates that every amateur radio transmission must be identifiable by the operator's assigned callsign. The callsign must be transmitted at the beginning and end of a communication and at intervals not exceeding 10 minutes during continuous operation. Implementation for the AERIS-10P is discussed in Section 6.

### 2.2 Amateurfunkverordnung (AFuV 2017)

The **Amateurfunkverordnung (AFuV)** (BGBl. I S. 1617) provides the implementing regulations for the AFuG. Key sections include:

**§ 1–3 AFuV — Definitions and Scope**

These sections define technical terms and confirm that the Klasse A license encompasses operation on all amateur bands, including millimeter-wave allocations.

**§ 5 AFuV — Frequenzzuweisungen und technische Parameter (Frequency Allocations and Technical Parameters)**

Section 5 incorporates by reference the Frequency Allocation Plan (Frequenzbereichszuweisungsplan, FreqBZPl) of the BNetzA and empowers the BNetzA to issue additional technical conditions for specific bands or emission types. At 10 GHz, no additional conditions have been published for amateur use.

**§ 8 AFuV — Sendeleistung (Transmitter Output Power)**

Section 8 and Annex 1 of the AFuV specify maximum permissible transmitter output power. For the 10 GHz band (3 cm band), the maximum power for Klasse A is **75 W PEP** at the antenna connector. The AERIS-10P operates at +30 dBm (1 W), which represents less than 1.4% of the permitted maximum power. This provides an enormous compliance margin.

**§ 13 AFuV — Rufzeichenkennung (Callsign Identification)**

Section 13 mirrors § 16 AFuG and adds the requirement that identification be made in a technically recognizable form — for non-voice modes, this typically means Morse code (CW) or a digital mode identifier. FMCW radar operation interspersed with CW identification bursts satisfies this requirement.

**Annex 1 (Anlage 1) AFuV — Frequenznutzung und Leistungsgrenzen**

Annex 1 tabulates permitted frequency ranges, maximum power levels, and permitted emission classes for each amateur license class. For Klasse A at 10.000–10.500 GHz: all emission types are permitted, maximum power 75 W PEP.

### 2.3 Telekommunikationsgesetz (TKG) — Experimental Permit

**§ 67 TKG (Experimentierklausel — Experimental Clause)** provides a mechanism by which the BNetzA may issue special permits for experimental use of radio frequencies outside the normal allocation framework, or with relaxed conditions, for a defined period. Although the AERIS-10P operates within the amateur allocation and does not strictly require a § 67 permit, obtaining one provides additional legal certainty and documents the BNetzA's awareness and approval of the specific operation. Applications are submitted in writing to BNetzA Referat 221.

### 2.4 Frequenzbereichszuweisungsplan (FreqBZPl)

The BNetzA Frequency Allocation Plan (current version: 2021, with annual updates) assigns the following status to the 10.000–10.500 GHz band in Germany:

| Service | Allocation Status |
|---|---|
| Fixed Satellite Service (Earth-to-Space) | Primary |
| Mobile except aeronautical mobile | Primary |
| Radiolocation | Primary |
| Amateur | Secondary |
| Amateur-Satellite | Secondary |

As a **secondary user**, amateur stations including the AERIS-10P must not cause harmful interference to primary service users and have no protection from interference caused by primary service users. This is a critical constraint analyzed in Section 7.

---

## 3. DARC Band Plan for 3 cm (10 GHz)

The **Deutscher Amateur-Radio-Club (DARC)** publishes a voluntary band plan that subdivides the amateur allocation within each band to promote efficient coexistence among different amateur operating modes. The 3 cm band plan is as follows:

| Frequency Range | Designation | Permitted Modes |
|---|---|---|
| 10.000–10.125 GHz | General use | All modes |
| 10.125–10.225 GHz | Wideband preferred | All modes, wideband preferred segment |
| 10.225–10.300 GHz | General use | All modes |
| 10.300–10.400 GHz | General use + Beacons | All modes; beacon segment |
| 10.400–10.450 GHz | EME (Earth-Moon-Earth) | All modes, EME operations |
| 10.450–10.500 GHz | Narrowband | SSB, CW; calling frequency 10.368 GHz |

**AERIS-10P Operating Segment: 10.000–10.100 GHz**

The AERIS-10P chirp sweeps from 10.000 GHz to 10.100 GHz (100 MHz bandwidth). This entire range falls within the **10.000–10.125 GHz general-use, all-modes** segment. FMCW operation in this segment is fully consistent with the DARC band plan.

**Practical Implications:**

1. The AERIS-10P should not transmit into the narrowband segment (10.450–10.500 GHz) or near the SSB/CW calling frequency (10.368 GHz), to avoid interfering with conventional amateur communication on that portion of the band. The AERIS-10P's 100 MHz chirp centered around 10.05 GHz is 318 MHz below the calling frequency — an ample spectral separation.

2. The wideband preferred segment (10.125–10.225 GHz) is adjacent to the AERIS-10P operating range. If bandwidth is extended in future revisions, operation should stay within the lower all-modes segment and avoid encroaching into beacon allocations at 10.300–10.400 GHz.

3. DARC band plan compliance is voluntary but strongly recommended as evidence of good amateur practice. Operating outside the band plan's intent — for example, causing wideband interference to the narrowband segment — could invite complaints and regulatory scrutiny even if technically within the legal allocation.

---

## 4. Power Limits and EIRP Analysis

### 4.1 Transmitted Power

Under AFuV Annex 1, Klasse A licenses permit a maximum transmitter output power of **75 W PEP (48.75 dBm)** at the antenna connector at 10 GHz. The AERIS-10P transmits at **+30 dBm (1 W)** at the output of the HMC451LS6GE power amplifier, well below this limit. The compliance margin is:

```
Margin = 75 W / 1 W = 75x (18.75 dB headroom)
```

This extraordinary margin means that even with component drift, calibration errors, or PA harmonic content at unexpected levels, the system cannot approach the legal power limit in normal operation.

### 4.2 EIRP Analysis

German amateur radio law (AFuG/AFuV) does not impose an explicit EIRP limit for terrestrial operation. EIRP limits apply in certain specific scenarios (satellite uplinks, band-sharing agreements), but no such limits are documented in German amateur allocations at 10 GHz for terrestrial use.

**AERIS-10P EIRP Calculation:**

```
P_TX = +30 dBm (1 W)
G_TX (practical) = +22 dBi (4×4 patch array, with feed and mismatch losses)
Cable/connector losses = -2 dB (estimated, PCB traces to connector)
---
EIRP = 30 + 22 - 2 = +50 dBm ≈ 100 W EIRP

Conservative (no cable loss subtracted):
EIRP = 30 + 22 = +52 dBm ≈ 158 W EIRP
```

For regulatory purposes, the conservative figure of **52 dBm EIRP (158 W EIRP)** is used. While this is a large EIRP value, it is characteristic of directional antenna systems and is fully consistent with amateur microwave operation. Many amateur EME (moonbounce) stations at 10 GHz operate with substantially higher EIRP using dish antennas (e.g., 3 m dish = 48 dBi gain, +73 dBm EIRP at 75 W).

The directional nature of the EIRP means that the actual power density at any given point (other than along the beam axis) is much lower than the EIRP figure suggests. This is relevant to the interference analysis in Section 7.

---

## 5. Emission Type Analysis

### 5.1 ITU Emission Designator for FMCW

The International Telecommunication Union (ITU) Radio Regulations define standardized emission designators. For the AERIS-10P FMCW waveform:

- **Chirp type:** Frequency modulation with a sawtooth ramp (generated by the ADF4159CCPZ PLL/FMCW generator)
- **Modulating signal:** A deterministic linear frequency ramp (no external information content — pure ranging waveform)
- **Closest ITU designator:** `F7X` — Frequency modulation, multiple signals, other types
- **Alternative designator:** `F3E` — FM with single analog modulating signal (the ramp can be considered an analog sweep)

Neither of these emission types is excluded or prohibited under the AFuG or AFuV for the amateur service. The emission designators serve primarily to categorize interference potential and are not gatekeeping criteria for amateur operation.

### 5.2 Comparison with Spread-Spectrum

FMCW radar is functionally similar to spread-spectrum transmissions, which are explicitly permitted in the amateur service under ITU Radio Regulations. The AERIS-10P's 100 MHz chirp bandwidth is comparable to many spread-spectrum amateur emissions. The key difference is that spread-spectrum typically has a random or pseudo-random frequency hopping pattern, whereas FMCW uses a deterministic linear sweep. This distinction does not affect the regulatory status — both are wideband modulations within the allocated band.

### 5.3 Distinction from Pulse Radar

Traditional pulse radar transmits short, very high-power pulses (megawatts of peak power in military systems). The AERIS-10P is explicitly NOT a pulse radar. FMCW transmits continuously at a constant low power level, which:

1. Avoids the spectral splatter associated with very short pulses
2. Produces no RF interference spikes that would affect adjacent services
3. Is generally considered less interference-prone than pulse radar
4. Has no high peak-power regulatory implications (pulse radar peak power might exceed 75 W PEP even at low average power)

This distinction is important when explaining the system to regulatory authorities. The AERIS-10P should be described as a **continuous waveform frequency sweep** rather than as a "radar" in the traditional pulse sense, as the term "radar" may trigger reflexive concern among non-technical regulators.

### 5.4 Harmonic Emissions

The AFuV requires that spurious emissions (harmonics, intermodulation products) be suppressed to the levels specified in ITU-R SM.329. At 10 GHz, the second harmonic would fall at 20 GHz and the third at 30 GHz — both in frequency ranges with no adjacent sensitive amateur or primary services. Nevertheless, the AERIS-10P design should include adequate filtering to suppress harmonics by at least 40 dB below the carrier power, yielding harmonic power below -10 dBm (0.1 mW). This is achievable with standard microstrip low-pass filter design on the Rogers RO4003C substrate.

---

## 6. Station Identification Requirements

### 6.1 Legal Basis

Under § 16 AFuG and § 13 AFuV, every amateur radio transmission must be identified with the operator's assigned callsign at the following intervals:

- At the beginning of transmission
- At the end of transmission
- At intervals not exceeding **10 minutes** during continuous operation

The identification must be in a technically recognizable form. For digital/non-voice emissions, CW (Morse code) identification is the standard method, though digital identification modes (e.g., FSK, PSK) are also accepted.

### 6.2 Implementation for AERIS-10P

The AERIS-10P operates continuously during a measurement session, which may last anywhere from a few minutes to several hours. The following identification scheme is proposed:

**Method A — Interleaved CW Burst:**
At intervals not exceeding 9 minutes (providing 1 minute of safety margin), the STM32H743ZIT6 MCU interrupts the FMCW chirp sequence and commands the ADF4159CCPZ to switch to a fixed CW frequency (e.g., 10.001 GHz). The MCU then modulates the PA enable line to key Morse code at 12 WPM. A 4-character callsign takes approximately 6 seconds at 12 WPM. After the CW burst completes, the MCU resumes the FMCW chirp sequence.

**Method B — Out-of-Band CW on Separate Transmitter:**
A separate low-power CW transmitter (e.g., 2.4 GHz amateur band) identifies the station continuously in parallel with FMCW operation. This method does not interrupt radar measurements but requires a second licensed transmitter and frequency.

**Method C — Embedded Digital Identifier:**
The FMCW chirp waveform is periodically interrupted by a brief FM-CW identifier packet encoded in a digital protocol at a fixed frequency offset. This method is technically elegant but may be unfamiliar to monitoring stations. BNetzA pre-approval is recommended if this method is used.

**Recommended approach:** Method A is the simplest to implement reliably and has clear precedent in amateur radio practice. The 6-second interruption every 9 minutes represents a data collection gap of approximately 1% of total operating time — negligible for most measurement applications.

### 6.3 Logging Requirements

The AFuV does not mandate a formal station log (Stationsjournal) for casual amateur operation, but one is strongly recommended for experimental radar operation. The log should record:

- Date and time of each operating session (UTC)
- Frequencies used
- Transmit power
- Location (GPS coordinates or address)
- Callsign identification times
- Any anomalies or interference events

---

## 7. Non-Interference Obligation

### 7.1 Secondary Status of Amateur Allocation at 10 GHz

The 10.000–10.500 GHz band is allocated to the amateur service on a **secondary basis** in Germany. This has the following legal implications under the ITU Radio Regulations and the FreqBZPl:

1. **Amateur stations must not cause harmful interference** to stations of primary services (Fixed, Mobile, Radiolocation, Satellite) operating in the same or adjacent bands.
2. **Amateur stations must accept interference** from primary service stations and have no right to protection from such interference.
3. **Harmful interference** is defined by the ITU as interference that endangers the functioning of a radionavigation service or of other safety services or seriously degrades, obstructs, or repeatedly interrupts a radiocommunication service operating in accordance with Radio Regulations.

### 7.2 Primary Users at 10 GHz

The principal primary services at 10 GHz in Germany and their interference sensitivity:

| Service | Frequency Range | Interference Sensitivity | Proximity Risk |
|---|---|---|---|
| FSS Earth-to-Space (uplinks) | 9.5–10.0 GHz, 10.7–12.75 GHz | Very high (satellite receivers) | Low (AERIS-10P operates 10.0–10.1 GHz) |
| Mobile (terrestrial) | 10.0–10.5 GHz | Moderate | Low (directional beam) |
| Radiolocation (radar) | 9.0–10.0 GHz, 10.0–10.5 GHz | Moderate | Low (FMCW vs. pulse radar) |
| Meteorological radar | ~5.6 GHz, ~9.7 GHz | High (scientific data) | Low (frequency separation) |

The AERIS-10P's key interference mitigation factors are:

- **Very low transmit power:** 1 W at antenna vs. 75 W permitted maximum
- **Highly directional beam:** 22 dBi antenna gain means the beam is approximately 22° wide. At angles beyond the main beam, transmit power density drops dramatically (typically 20–25 dB sidelobe suppression for a well-designed patch array).
- **FMCW waveform:** The 100 MHz bandwidth is spread over a continuous sweep, reducing peak spectral density compared to a narrowband CW transmission of equal power.

### 7.3 Avoidance Zones

The following operational avoidances are recommended:

1. **Satellite Earth Station sites:** Do not point the beam toward known satellite uplink installations. A list of German satellite earth stations is available from the BNetzA. Minimum separation distance: 5 km from licensed satellite earth station facilities.

2. **Radio Astronomy Observatories:** While 10 GHz is not a primary radio astronomy allocation, observatories may conduct observations in this range. Minimum separation: 10 km from known radio telescope facilities (e.g., Effelsberg 100m telescope, which operates across multiple bands).

3. **Airport approach zones:** X-band is used for precision approach radar (PAR) and air traffic control radar at airports. Do not operate within 3 km of airport boundaries without prior coordination with the airport's frequency management.

4. **Military installations:** Germany has active military radar operations. Avoid operation near military bases.

### 7.4 Power Density Analysis

At a distance R from the AERIS-10P in the direction of the main beam:

```
S(R) = (P_TX × G_TX) / (4π × R²)

With P_TX = 1 W, G_TX = 158 (linear, 22 dBi practical):
S(R) = 158 / (4π × R²) = 12.57 / R² [W/m²]
```

At representative distances:
- R = 1 m: S = 12.6 W/m² (significant — within near-field transition)
- R = 10 m: S = 0.126 W/m²
- R = 100 m: S = 0.00126 W/m²
- R = 1 km: S = 0.0000126 W/m² = 12.6 µW/m²

These power densities are far below any threshold that would constitute harmful interference to ground-based receivers, which typically have antenna gains of 30–50 dBi pointing toward their intended signal sources (satellites, fixed links), not toward the AERIS-10P.

---

## 8. Radar-Specific Regulatory Considerations

### 8.1 Absence of Explicit Radar Prohibition

Neither the AFuG 2017, the AFuV 2017, nor any BNetzA ruling published to date contains an explicit prohibition on radar-type operation by licensed amateur stations. The amateur service is broadly defined to encompass technical experimentation, and FMCW ranging and imaging are established amateur activities (amateur radar has a long history, particularly at 10 GHz and 24 GHz, with active amateur radar clubs operating throughout Europe).

### 8.2 Distinction from Professional/Military Radar Licensing

Professional radar systems (air traffic control, weather radar, maritime radar) require specific type approvals and operational licenses under the TKG and separate aviation/maritime regulations. These requirements do NOT apply to experimental amateur radar operating within the amateur allocation at the power levels permitted by the Klasse A license. The AERIS-10P is categorically different from licensed professional radar because:

1. It operates at a fraction of the power level of professional systems
2. It uses a different waveform (FMCW vs. pulse)
3. It operates in the amateur secondary allocation
4. It is operated by a licensed amateur operator for experimental purposes

### 8.3 German Amateur Radar Practice

The German amateur radio community has a well-established tradition of X-band radar experimentation. The DARC's UKW-Referat and the relevant working groups (e.g., those focused on VHF/UHF/SHF experimentation) have documented amateur radar projects at 10 GHz and 24 GHz. These projects have operated without adverse regulatory action, establishing a practical precedent for amateur FMCW radar in Germany.

### 8.4 BNetzA Informal Opinion Process

Before commencing field operation, the project team should contact BNetzA Referat 221 (Amateurfunk) to:

1. Describe the AERIS-10P system (frequency, power, waveform, antenna, intended use)
2. Request confirmation that the planned operation falls within the scope of the Klasse A license
3. Ask whether any additional permit conditions apply

This informal consultation is not legally required but is strongly recommended. BNetzA officials are generally cooperative with licensed amateurs conducting legitimate technical experiments. The written response provides legal protection in the event of a complaint from a neighboring service.

### 8.5 Experimental Permit Under § 67 TKG

If the BNetzA informal opinion raises concerns, or if the project team wishes to operate with additional legal certainty, an application for an experimental permit under § 67 TKG is the appropriate path. This permit:

- Grants specific authorization for the described experimental operation
- May include conditions (geographic area, operating hours, power limits)
- Is typically valid for 1–3 years and can be renewed
- Demonstrates regulatory compliance to any third party

The application process is described in Section 13.

---

## 9. Legal Risk Assessment

### 9.1 Risk Categorization

| Scenario | Legal Risk Level | Basis | Mitigation |
|---|---|---|---|
| Laboratory operation only, below 1 W | Very Low | Well within amateur license; no third-party exposure | Standard amateur license compliance |
| Field operation, open rural area, no primary users nearby | Low | Secondary allocation use; low power; directional beam | Station ID; prior BNetzA notification; log keeping |
| Field operation near airport or satellite earth station | Medium | Potential interference to primary users; BNetzA enforcement possible | Pre-coordination; avoid avoidance zones; reduce power further |
| Operation without callsign identification | Medium-High | Violation of § 16 AFuG / § 13 AFuV; potential fine | Implement Method A identification |
| Operation on primary-only frequency (outside 10.0–10.5 GHz) | High | Illegal use of non-amateur frequency | Verify frequency calibration before each session |
| Operation exceeding 75 W PEP | High | Direct violation of AFuV Annex 1 | Monitor PA output; implement hardware power limit |
| Causing actual interference to primary service | High | TKG § 67 enforcement; potential license suspension | Observe avoidance zones; keep power minimal |

### 9.2 Probability Assessment

Given the AERIS-10P's conservative design parameters (1 W transmit power, directional antenna, FMCW waveform, proper callsign ID implementation), the probability of any adverse regulatory action is assessed as **very low** under normal operating conditions. The system's EIRP is moderate by amateur microwave standards, and the FMCW waveform is relatively benign in terms of interference potential.

### 9.3 Consequence Assessment

The AFuG provides for administrative fines (Bußgelder) for violations of amateur radio regulations. Under § 18 AFuG, violations can result in fines up to €50,000 in severe cases. However, for minor technical violations by otherwise compliant licensed amateurs, practical consequences are typically limited to a warning letter or requirement to modify operation. License suspension is reserved for serious or repeated offenders.

---

## 10. Comparison with Other Countries

### 10.1 United Kingdom (Ofcom)

The UK's **Office of Communications (Ofcom)** regulates amateur radio under the Wireless Telegraphy Act 2006 and the Amateur Radio Licence terms. The Full Licence (equivalent to Klasse A) permits operation at 10 GHz with up to 400 W EIRP in some configurations. Ofcom has not issued any prohibition on amateur FMCW radar and has granted experimental licenses under Section 8 of the WT Act to amateur radar experimenters. UK amateur radar groups (e.g., the Royal Signals Amateur Radio Society) have operated X-band amateur radar systems without regulatory difficulty.

### 10.2 Netherlands (Agentschap Telecom)

The Netherlands' Agentschap Telecom regulates amateur radio under the Telecommunicatiewet. The Dutch FMCW amateur radar regulatory environment is essentially equivalent to Germany's: secondary allocation at 10 GHz, no explicit radar prohibition, identification required. Several Dutch amateur groups have operated FMCW radar systems at 10 GHz and have published results through the VERON (Dutch amateur radio association). No adverse regulatory actions have been reported.

### 10.3 Austria (RTR-GmbH)

Austria's telecommunications regulator, the RTR-GmbH (Rundfunk und Telekom Regulierungs-GmbH), implements amateur radio regulation under the Austrian Amateurfunkgesetz. The Austrian framework closely mirrors the German AFuG/AFuV, including the same frequency allocations and power limits at 10 GHz. The ÖVSV (Österreichischer Versuchssenderverband, Austrian amateur radio association) maintains a band plan equivalent to DARC's, and amateur radar experimentation at 10 GHz is practiced without regulatory constraint.

### 10.4 European Harmonization (CEPT/ERC)

The CEPT (European Conference of Postal and Telecommunications Administrations) ERC Recommendation 25-10 and the associated CEPT/ERC Report provide harmonized conditions for amateur radio in Europe. CEPT member states (including Germany, UK, Netherlands, and Austria) apply broadly consistent regulatory frameworks at 10 GHz. Operation legal in Germany is generally legal in all CEPT member states, subject to local variations in power limits and frequency use.

---

## 11. Compliance Checklist

The following checklist summarizes all regulatory requirements for AERIS-10P operation under a German Klasse A amateur license. All items must be confirmed before commencing any transmission.

| # | Requirement | Regulatory Basis | AERIS-10P Status | Action Required |
|---|---|---|---|---|
| 1 | Valid Klasse A amateur license held by operator | § 3 AFuG | Operator must confirm | Verify license validity |
| 2 | Valid callsign assigned by BNetzA | § 3 AFuG | Operator must confirm | Verify callsign currency |
| 3 | Operating frequency within 10.000–10.500 GHz | AFuV Annex 1 | Compliant (10.0–10.1 GHz) | Verify VCO/PLL calibration |
| 4 | Transmit power ≤ 75 W PEP at antenna connector | AFuV Annex 1 | Compliant (+30 dBm = 1 W) | Monitor PA output power |
| 5 | Callsign identification every ≤ 10 minutes | § 16 AFuG, § 13 AFuV | Implement Method A CW burst | Software implementation required |
| 6 | No harmful interference to primary services | § 15 AFuG, ITU RR | Low risk; compliant if avoidance zones observed | Observe avoidance zones |
| 7 | Spurious emissions suppressed per ITU-R SM.329 | AFuV § 10 | Design requirement | Harmonic filter on PA output |
| 8 | Station log maintained | Recommended practice | Not yet implemented | Implement logging in software |
| 9 | DARC band plan observed | Voluntary | Compliant (10.0–10.1 GHz all-modes segment) | Verify chirp start/stop frequencies |
| 10 | BNetzA notification (informal opinion) | Recommended | Not yet done | Contact Referat 221 before field ops |
| 11 | Field operation avoidance zones respected | § 15 AFuG | Not yet verified | Site survey before each field session |
| 12 | Operator physically present during operation | § 3 AFuG | Required | No unmanned autonomous operation |
| 13 | Emergency stop capability | Safety/legal | Hardware E-stop required | Implement hardware TX inhibit |

---

## 12. Recommended Operational Procedure for Legal Compliance

The following procedure should be followed for each operating session of the AERIS-10P:

### Pre-Operation Checklist

1. **Verify license and callsign:** Confirm that the operating amateur's Klasse A license is valid and the callsign is current.
2. **Frequency calibration check:** Verify that the ADF4159CCPZ chirp start frequency is within the 10.000–10.100 GHz range using a calibrated frequency counter or spectrum analyzer.
3. **Power level check:** Measure PA output power with a calibrated power meter. Confirm power is +30 dBm ± 2 dB (0.63–1.58 W).
4. **Site survey (field operation only):** Confirm no primary service facilities (airports, satellite earth stations, radio observatories) are within the avoidance distances specified in Section 7.3.
5. **Callsign ID timer set:** Enable the automatic callsign identification timer in the AERIS-10P control software. Verify CW output is audible and correctly encodes the callsign.
6. **Station log entry:** Record date, time (UTC), location, frequency range, and transmit power in the station log.

### During Operation

7. **Monitor for interference:** Observe the IF spectrum for unexpected signals that might indicate interference to or from the AERIS-10P. If a primary service operator contacts you (e.g., by radio or in person), immediately cease transmission and investigate.
8. **Callsign ID compliance:** Confirm that the callsign identification occurs at least every 9 minutes (the 9-minute software interval plus 1-minute safety margin equals ≤ 10-minute legal maximum).
9. **Power monitor:** The STM32H743ZIT6 MCU should continuously monitor the PA supply current and forward power coupler output. If power deviates above the expected level by more than 3 dB, automatically inhibit the PA and log the anomaly.

### Post-Operation

10. **Station log closure:** Record session end time and any anomalies noted.
11. **Equipment shutdown:** Follow the safe shutdown procedure (Section 9 of Safety Documentation): disable PA, disable VCO, disconnect DC supply.

---

## 13. BNetzA Contact Information and Application Process

### 13.1 Primary Contact

**Bundesnetzagentur für Elektrizität, Gas, Telekommunikation, Post und Eisenbahnen**
**Referat 221 — Amateurfunk und Bürgerrufanlagen**
Tulpenfeld 4
53113 Bonn, Germany

Telephone: +49 228 14-0 (main) / extension for Referat 221 available on BNetzA website
Email: amateurfunk@bundesnetzagentur.de
Web: www.bundesnetzagentur.de > Funkfrequenzen > Amateurfunk

### 13.2 Informal Opinion Request

For an informal opinion, submit a written inquiry (preferably by email to the address above) including:

1. Operator's full name and callsign
2. License class (Klasse A) and license number
3. Description of the planned experimental system (frequency, power, waveform, antenna, intended purpose)
4. Specific question: confirmation that the operation falls within the scope of the Klasse A license and the amateur secondary allocation at 10 GHz
5. Proposed operating location(s) (general area, not GPS coordinates required at this stage)
6. Contact information for follow-up

Response time is typically 2–6 weeks. A written response (email or letter) from BNetzA Referat 221 confirming permission constitutes informal authorization and should be kept with the station records.

### 13.3 § 67 TKG Experimental Permit Application

If an experimental permit is desired, the application must include:

1. All information from the informal opinion request (Section 13.2 above)
2. Detailed technical specifications (this document and the AERIS-10P Technical Specifications document serve as supporting attachments)
3. Proposed duration of the experimental period (recommend 12–24 months, renewable)
4. Proposed geographic area of operation
5. Description of interference mitigation measures
6. Description of monitoring and logging procedures
7. Emergency contact information

The application is submitted to BNetzA Referat 221. There is no fee for amateur experimental permits under § 67 TKG (as of 2026). Processing time is typically 4–12 weeks. The permit, when issued, specifies the authorized frequency range, maximum power, geographic area, and operating conditions.

### 13.4 DARC Regional Group

In addition to the BNetzA, the DARC (Deutscher Amateur-Radio-Club e.V.) can provide technical and legal support. The DARC's SHF (super high frequency) working group maintains expertise in 10 GHz equipment and can provide letters of support for experimental permit applications.

DARC Hauptgeschäftsstelle:
Lindenallee 4, 34225 Baunatal
Email: info@darc.de
Web: www.darc.de

---

## 14. Conclusion

Based on the analysis presented in this document, the AERIS-10P FMCW radar system can be operated legally under a German Klasse A amateur radio license, subject to the following conditions:

1. **The operator holds a valid Klasse A license** and operates under their assigned callsign.
2. **Operation is confined to 10.000–10.100 GHz**, within the amateur secondary allocation and the DARC all-modes segment.
3. **Transmit power is maintained at 1 W (+30 dBm)** or below, well within the 75 W PEP legal maximum.
4. **Callsign identification is implemented** at intervals not exceeding 10 minutes, using the CW burst method or an equivalent technically recognizable format.
5. **Avoidance zones are respected** — no operation within 5 km of satellite earth stations, 10 km of radio observatories, or 3 km of airport boundaries.
6. **BNetzA Referat 221 is contacted** for an informal opinion before commencing field operations.

The legal risk under these conditions is assessed as **low**. The AERIS-10P is a well-designed experimental system operating at a small fraction of the permitted power level in a frequency segment where amateur experimentation has a long and established history. Proactive engagement with the BNetzA and the DARC will provide additional legal certainty and community support for the project.

The project team should revisit this analysis if the operating parameters change significantly (e.g., power increase, frequency change, deployment near sensitive areas) or if the BNetzA issues new guidance on amateur radar operation.

---

*End of Document — AERIS-10P German Regulatory Analysis Rev 1.0 — 2026-07-14*
*For questions, contact the HASE-Radar Project Team.*
