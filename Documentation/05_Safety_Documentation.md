# AERIS-10P Safety Documentation
## Rev 1.0 — 2026-07-14

**Project:** AERIS-10P (Affordable Experimental Radar Intelligence System, 10 GHz Phased Array)
**Prepared by:** HASE-Radar Project Team
**Date:** 2026-07-14
**Classification:** Internal Technical Documentation — Safety Critical

> **THIS DOCUMENT MUST BE READ IN FULL BY ALL PERSONNEL BEFORE HANDLING OR OPERATING THE AERIS-10P SYSTEM.**

---

## Table of Contents

1. RF Radiation Safety
2. Near-Field Hazards
3. Electrical Safety
4. Safety Interlocks
5. Warning Labels Required
6. Personal Protective Equipment
7. Laboratory Procedures
8. Field Operation Safety
9. Emergency Procedures
10. Chemical Hazards and MSDS References

---

## 1. RF Radiation Safety

### 1.1 Applicable Guidelines

The AERIS-10P transmits RF energy at 10.0–10.1 GHz (X-band, 3 cm wavelength) at a power level of +30 dBm (1 W) into a 4×4 patch array antenna with approximately 22 dBi of practical gain. All RF radiation safety evaluations are based on the **ICNIRP 2020 Guidelines for Limiting Exposure to Electromagnetic Fields** (Health Physics, 2020; https://www.icnirp.org/cms/upload/publications/ICNIRPemfgdl.pdf), which represent the current scientific consensus on safe RF exposure limits and form the basis of German (and EU) RF safety regulation.

At 10 GHz, the dominant mechanism of biological interaction is **superficial tissue heating**. RF energy at this frequency is absorbed primarily in the skin and superficial tissues (penetration depth ~0.4 mm). At exposure levels below the Maximum Permissible Exposure (MPE), no adverse health effects have been demonstrated. The ICNIRP 2020 guidelines are conservative by design, incorporating safety factors that account for individual variation and uncertainty in the scientific evidence.

### 1.2 Maximum Permissible Exposure (MPE) at 10 GHz

ICNIRP 2020 specifies the following MPE values for continuous, localized exposure in the frequency range 6 GHz to 300 GHz (the "above 6 GHz" regime where the metric is power density in W/m²):

| Population | MPE (Power Density) | Averaging Time | Area Averaged Over |
|---|---|---|---|
| Occupational (workers) | **50 W/m²** | 30 minutes | 4 cm² |
| General Public | **10 W/m²** | 30 minutes | 4 cm² |

The **general public** MPE (10 W/m²) is the governing value for any operation in locations where members of the public who have not consented to RF exposure and have no specialist training could be present. The **occupational** MPE (50 W/m²) applies to trained workers who are aware of the RF environment and take appropriate precautions.

For the AERIS-10P project team, trained operators working with full knowledge of the RF environment may apply the occupational MPE. However, for field operations in open areas, the general public MPE must be used as the design criterion.

### 1.3 Near-Field / Far-Field Boundary

The transition from near-field to far-field propagation for the AERIS-10P antenna array occurs at the Fraunhofer distance:

```
R_ff = 2 × D² / λ

Where:
  D = largest dimension of the antenna aperture = 0.045 m (45 mm × 45 mm array)
  λ = wavelength at 10 GHz = 0.03 m (30 mm)

R_ff = 2 × (0.045)² / 0.03
R_ff = 2 × 0.002025 / 0.03
R_ff = 0.00405 / 0.03
R_ff = 0.135 m ≈ 14 cm
```

**The far-field begins at approximately 13.5 cm from the antenna surface.** At distances less than 13.5 cm, the power density distribution is complex and cannot be calculated using the simple far-field formula. Near-field exposure can be higher than the far-field formula would predict. Therefore, **the antenna array surface must be treated as a high-RF-hazard zone during transmission, and physical contact must be prohibited.**

### 1.4 Far-Field Power Density Calculation

In the far-field (R > 0.135 m), the power density along the main beam axis is:

```
S(R) = (P_TX × G_TX) / (4π × R²)

Where:
  P_TX = 1 W (transmit power, +30 dBm)
  G_TX = 158.5 (linear equivalent of 22 dBi practical gain)

S(R) = (1 × 158.5) / (4π × R²)
S(R) = 158.5 / (12.566 × R²)
S(R) = 12.62 / R²   [W/m², with R in metres]
```

Power density at representative distances along the main beam:

| Distance R | Power Density S(R) | vs. Occupational MPE | vs. General Public MPE |
|---|---|---|---|
| 0.135 m (far-field boundary) | 692 W/m² | 13.8× ABOVE | 69× ABOVE |
| 0.50 m | 50.5 W/m² | At limit | 5× ABOVE |
| 1.00 m | 12.6 W/m² | Well below | 1.26× ABOVE |
| 1.12 m | 10.0 W/m² | Well below | AT LIMIT |
| 2.00 m | 3.15 W/m² | Well below | Well below |
| 5.00 m | 0.50 W/m² | Well below | Well below |

### 1.5 Safety Distances

**General Public Safety Distance:**
```
R_safe_GP = sqrt(P_TX × G_TX / (4π × MPE_GP))
R_safe_GP = sqrt(158.5 / (4π × 10))
R_safe_GP = sqrt(158.5 / 125.66)
R_safe_GP = sqrt(1.261)
R_safe_GP ≈ 1.12 m
```

**Occupational Safety Distance:**
```
R_safe_OC = sqrt(158.5 / (4π × 50))
R_safe_OC = sqrt(158.5 / 628.3)
R_safe_OC = sqrt(0.252)
R_safe_OC ≈ 0.50 m
```

**Operational Safety Zone (Conservative Design Criterion):**

To provide a safety margin above the calculated general public MPE distance, the AERIS-10P operational safety zone is defined as:

> **2 metres (2 m) in front of the antenna array during any transmission.**

This provides a factor-of-1.8 safety margin above the calculated MPE distance of 1.12 m, consistent with good engineering practice for experimental systems. The 2 m safety zone applies to all persons, including trained operators.

### 1.6 Off-Axis Exposure

The power density values in Section 1.4 are worst-case, calculated along the main beam axis. Off-axis exposure is lower by the antenna's sidelobe suppression factor. For a well-designed 4×4 patch array:

- First sidelobe level: approximately −13 dB (×0.05) relative to main beam
- At 90° off-axis: −25 dB or more (×0.003) relative to main beam

At 90° off-axis and 1 m distance, the power density is approximately 12.6 × 0.003 ≈ 0.038 W/m², far below any MPE limit. Exposure from the sides or rear of the antenna presents no significant RF hazard at any reasonable distance.

### 1.7 ICNIRP Peak Spatial Exposure

ICNIRP 2020 also specifies a **peak spatial exposure** limit of 200 W/m² (general public) to prevent hotspot effects from localized antenna elements. This limit is relevant to the near-field region. Because the near-field of a 45 mm aperture at 10 GHz extends only 13.5 cm, and because access to within 13.5 cm of the antenna is prohibited during operation, this limit is addressed by the physical access prohibition rather than by calculation.

---

## 2. Near-Field Hazards

### 2.1 Active Transmit Surface

The AERIS-10P antenna panel (200 mm × 120 mm) is an **active RF radiating surface** during all transmission periods. The following prohibitions are mandatory:

- **Do not touch the antenna panel during transmission.** RF current flowing in the patch antenna metallization can cause RF burns to the skin and can couple RF energy into the body.
- **Do not place any object within 5 cm of the antenna panel during transmission.** Metallic objects in the near-field can cause reflections and impedance mismatch, potentially damaging the PA. Flammable objects can be heated by concentrated near-field energy.
- **Do not lean over the antenna panel during transmission.** The face, eyes, and hands are the most vulnerable body regions.

### 2.2 RF Burns

RF burns differ from thermal burns in that tissue damage can occur below the pain threshold at frequencies above 3 GHz. At 10 GHz, surface tissue absorption is rapid. A brief contact (< 1 second) with the antenna radiating at 1 W poses low risk of serious injury, but prolonged contact can cause superficial burns. If skin contact with the antenna surface occurs during transmission, immediately shut off the PA supply and inspect the contact area.

### 2.3 Medical Device Interference

Implanted medical devices (cardiac pacemakers, implanted cardioverter-defibrillators, insulin pumps, cochlear implants, implanted neurostimulators) may be susceptible to RF interference at 10 GHz. Persons with these devices must not enter the 2 m safety zone while the AERIS-10P is transmitting.

**Before any RF testing session, verbally confirm with all present personnel that no implanted medical devices are present.** Post a warning notice at the entrance to the operating area.

### 2.4 Eye Hazards

The lens of the human eye is particularly vulnerable to RF heating because it lacks effective cooling by blood circulation. While the ICNIRP MPE values are set to protect all tissues including the eye, the additional restriction is:

- Do not look directly into the antenna aperture from within 2 m during transmission.
- If the antenna is mounted at eye height, ensure the 2 m safety zone is clearly marked in the forward hemisphere.

---

## 3. Electrical Safety

### 3.1 Power Supply Characteristics

The AERIS-10P operates from a **24 V DC, 8 A maximum** external power supply (total system power up to 192 W). The following DC rails are derived by onboard regulators:

| Rail | Regulator | Voltage | Maximum Current | Hazard Level |
|---|---|---|---|---|
| Main input | External PSU | +24 V | 8 A | Moderate (192 W) |
| Logic/processor | LT8612 | +5 V | 5 A | Low |
| Digital/MCU | LT8607 | +3.3 V | 3 A | Low |
| RF bias (+) | TPS65133 | +5 V | 1 A | Low |
| RF bias (−) | TPS65133 | −5 V | 1 A | Low |

At 24 V DC, the supply voltage is below the 50 V threshold considered immediately dangerous to life under IEC 60479-1 for dry skin contact. However, at 8 A maximum current capability, a short circuit can deliver significant energy (192 W) to a fault point, causing fire, arc flash, or thermal burns from hot conductors and melted insulation.

### 3.2 Overcurrent Protection

All supply rails must be fuse-protected:

| Rail | Fuse Rating | Location |
|---|---|---|
| 24 V input | 10 A fast-blow | At DC input connector |
| 5 V digital | 6 A fast-blow | After LT8612 |
| 3.3 V MCU | 4 A fast-blow | After LT8607 |
| ±5 V RF bias | 2 A fast-blow | After TPS65133 |
| PA supply (24 V to HMC451) | 2 A fast-blow | PA power line |

In addition to fuses, all LT86xx regulators and TPS65133 have built-in current limiting and thermal shutdown. The PA supply should include a hardware current limit circuit (current sense resistor + comparator + MOSFET switch) to immediately cut PA power if current exceeds 1.5× the rated operating value.

### 3.3 Grounding

The electronics enclosure (300 mm × 200 mm × 100 mm aluminium) must be connected to **protective earth (PE)** via the power cable or a separate ground wire. This ensures that any fault current from the 24 V supply to the chassis is routed to earth rather than through an operator who may contact the chassis.

All PCBs within the enclosure should be connected to chassis ground at a single star-ground point to minimize ground loop currents that can introduce noise into RF measurements.

### 3.4 ESD Handling for RF ICs

The AERIS-10P uses numerous RF integrated circuits that are sensitive to electrostatic discharge (ESD):

| Component | ESD Sensitivity | JEDEC Class |
|---|---|---|
| HMC647ALP5E (phase shifters, 16×) | High | Class 1A (< 250 V HBM) |
| HMC733LP6CE (VCO) | High | Class 1B (< 500 V HBM) |
| ADF4159CCPZ (PLL) | Moderate | Class 1C (< 1000 V HBM) |
| HMC451LS6GE (PA) | High | Class 1A |
| HMC1040LP4E (LNA) | Very High | Class 0 (< 125 V HBM) |
| HMC213B (mixer) | High | Class 1A |

The LNA (HMC1040LP4E) is particularly sensitive and can be damaged by static discharge from a human hand or from ungrounded tools. The following ESD precautions are mandatory during PCB assembly and repair:

- Wear a grounded ESD wrist strap (verified with tester before use)
- Work on an ESD-dissipative mat connected to earth ground
- Store all RF ICs in ESD-shielding bags when not in use
- Use ESD-safe tweezers and soldering equipment
- Verify that the PCB is discharged before inserting or removing any IC

### 3.5 Capacitor Discharge Procedure

Before performing any maintenance on the AERIS-10P electronics, the following discharge procedure must be followed:

1. Disconnect the 24 V DC supply at the input connector.
2. Wait 30 seconds for all electrolytic capacitors to discharge through their bleed resistors.
3. If working on the PA power supply section, additionally use a 100Ω / 5 W resistor connected across the PA supply capacitors (measure voltage across capacitors; wait until voltage is below 1 V before proceeding).
4. Verify with a digital multimeter that all supply rails are below 1 V before touching internal components.

---

## 4. Safety Interlocks

### 4.1 Software TX Inhibit

The STM32H743ZIT6 MCU implements a software transmit inhibit that is engaged by default on power-up. Transmission is enabled only after:

1. The control computer (Raspberry Pi 5 or Jetson Nano) has established a valid control link with the MCU
2. The operator has explicitly enabled transmission through the control software UI
3. All self-test checks (power supply voltages, temperature, PLL lock status) have passed

If the control link is lost (timeout > 500 ms), the MCU automatically engages the TX inhibit, disabling the PA and the VCO output. This prevents the system from transmitting without supervision.

### 4.2 Temperature Monitor with Automatic Shutdown

The AERIS-10P MCU continuously reads temperature sensors (NTC thermistors or digital temperature ICs) mounted at the following locations:

- PA heatsink (HMC451LS6GE)
- VCO module (HMC733LP6CE)
- Electronics enclosure internal air temperature

**Automatic shutdown thresholds:**

| Location | Warning Temperature | Shutdown Temperature |
|---|---|---|
| PA heatsink | 65°C | 70°C |
| VCO module | 60°C | 70°C |
| Enclosure internal | 55°C | 65°C |

At the warning threshold, the MCU logs the event and alerts the operator through the control software. At the shutdown threshold, the MCU immediately disables the PA and VCO output and enters a safe state. The system cannot be restarted until temperatures return below the warning threshold AND the operator acknowledges the condition through the control software.

### 4.3 Current Limit Protection on PA Supply

A hardware current limit circuit on the PA (HMC451LS6GE) supply line limits the maximum current to 1.2 A (the PA draws approximately 0.8–1.0 A at +29 dBm output). If current exceeds 1.2 A for more than 10 ms, a hardware comparator trips a P-channel MOSFET, cutting the PA supply. This condition is signaled to the MCU via a GPIO interrupt. The MCU logs the event and requires operator intervention to reset.

### 4.4 Forward Power Monitor with Protection

A directional coupler (e.g., −20 dB coupling factor) on the PA output feeds a power detector (e.g., AD8317 log detector) whose output is digitized by the MCU's ADC. The MCU continuously compares the measured forward power to the expected value (+30 dBm ± 2 dB). If the measured power exceeds +33 dBm (+3 dB over nominal), the MCU immediately disables the PA. This protects against:

- PA oscillation or runaway
- Impedance mismatch causing elevated power levels
- Calibration error causing unexpected power increase

If the measured power falls below +27 dBm (−3 dB below nominal), the MCU logs a warning, as this may indicate a cable fault, connector problem, or component degradation.

---

## 5. Warning Labels Required

The following warning labels must be affixed to the AERIS-10P system before any operation. Labels must be durable (vinyl or aluminium anodized), clearly legible, and positioned so that they are visible from the normal approach direction.

### Label 1 — RF Radiation Hazard (on antenna panel and electronics enclosure front)

```
+-----------------------------------------------+
|  [RF SYMBOL]  RF RADIATION HAZARD              |
|                                                |
|  MAINTAIN 2 METRE CLEARANCE IN FRONT OF       |
|  ANTENNA DURING TRANSMISSION                  |
|                                                |
|  PERSONS WITH IMPLANTED MEDICAL DEVICES       |
|  (PACEMAKERS, ICDs) MUST STAY CLEAR          |
|                                                |
|  10 GHz X-BAND — 1 W (+30 dBm) — 22 dBi      |
+-----------------------------------------------+
```

### Label 2 — Electrical Hazard (on electronics enclosure and power input)

```
+-----------------------------------------------+
|  [LIGHTNING SYMBOL]  HIGH CURRENT             |
|                                                |
|  24 V DC / 8 A MAXIMUM — 192 W               |
|                                                |
|  DO NOT OPEN DURING OPERATION                 |
|  DISCONNECT POWER BEFORE SERVICING           |
|  WAIT 30 SECONDS AFTER POWER-OFF             |
|  BEFORE TOUCHING INTERNAL COMPONENTS         |
+-----------------------------------------------+
```

### Label 3 — ESD Sensitive (on electronics enclosure lid and all PCBs)

```
+-----------------------------------------------+
|  [ESD SYMBOL]  RF SENSITIVE ELECTRONICS       |
|                                                |
|  ESD PROTECTION REQUIRED                      |
|  USE GROUNDED WRIST STRAP AND ESD MAT         |
|  WHEN HANDLING INTERNAL COMPONENTS           |
+-----------------------------------------------+
```

---

## 6. Personal Protective Equipment

### 6.1 Required PPE — RF Testing

The following PPE is required for all persons present during AERIS-10P RF testing (transmitter active):

| PPE Item | Requirement Level | Purpose |
|---|---|---|
| RF awareness training | Mandatory for all operators | Understand hazards and safe zones |
| Verbal confirmation of no implanted medical devices | Mandatory before each session | Prevent medical device interference |
| Adherence to 2 m safety zone | Mandatory for all persons | RF exposure protection |

No specialized RF shielding garments are required because the system operates at 1 W into a directional antenna. The 2 m safety zone is the primary protective measure.

### 6.2 Required PPE — PCB Assembly, Disassembly, and Maintenance

| PPE Item | Requirement Level | Purpose |
|---|---|---|
| ESD wrist strap (verified) | Mandatory | Protect sensitive RF ICs from ESD damage |
| ESD-dissipative work mat | Mandatory | Secondary ESD protection for PCBs |
| Safety glasses | Mandatory for soldering | Protect against solder splash and flux spatter |
| Nitrile gloves | Recommended for flux handling | Protect skin from isopropyl alcohol and flux chemicals |
| Fume extraction / ventilation | Mandatory during soldering | Remove solder flux fumes (potential respiratory irritant) |

### 6.3 Recommended PPE — Connector Work

When mating or unmating SMA and MMCX RF connectors:

- Confirm transmitter is OFF before disconnecting any RF connector
- Use calibrated torque wrench for SMA connectors (5–8 Nm recommended)
- Safety glasses recommended to protect against connector snap-back

---

## 7. Laboratory Procedures

### 7.1 Two-Person Rule for High-Power RF Testing

During any test involving the PA (HMC451LS6GE) transmitting at full output (+30 dBm), **a minimum of two persons must be present.** This rule ensures that:

1. One person can observe the equipment while the other monitors the RF environment and safety zone
2. In the event of an incident (RF exposure, electrical fault, fire), one person can assist the other or call for help

The two-person rule may be relaxed for bench tests where the antenna is replaced with a 50Ω matched termination (RF load) and all RF energy is dissipated internally, with no radiated power.

### 7.2 Antenna Connection and RF Measurement Procedure

The following procedure must be followed when connecting or disconnecting the antenna:

1. **Disable the PA.** Use the control software to engage TX inhibit, or physically disconnect the PA supply fuse.
2. **Verify PA is disabled.** Observe the forward power monitor reading on the control software — it should read < −30 dBm.
3. **Connect or disconnect the antenna RF cable.**
4. **Verify the antenna connection is secure** (torqued SMA connector, no visible cable damage).
5. **Re-enable the PA** and verify forward power reading returns to expected level.

**Never disconnect the antenna from the PA output while the PA is transmitting.** Disconnecting the load causes the PA output impedance to see an open circuit, potentially generating voltage spikes that can destroy the PA or cause arcing at the connector.

### 7.3 Termination of Unused RF Ports

All unused RF connectors must be terminated with a **50Ω matched RF load (termination).** This applies to:

- Unused SMA connectors on the RF distribution board
- Unused mixer IF ports
- Unused LNA inputs (if multiple RX channels are not all connected)
- Test ports on directional couplers during bench testing

Use loads rated for the expected power level: a 1 W (30 dBm) load for any ports that may carry PA output power. For all other ports, a 0.25 W (24 dBm) load is sufficient.

### 7.4 Spectrum Analyzer Measurement Precautions

When connecting a spectrum analyzer to the AERIS-10P:

- Verify the spectrum analyzer input is rated for the power level to be measured (maximum input power is typically +30 dBm for most Keysight/Rohde & Schwarz analyzers — exactly the PA output power)
- Insert a calibrated attenuator (e.g., 20 dB, 2 W) between the AERIS-10P and the spectrum analyzer when measuring PA output
- Never connect the PA output directly to a spectrum analyzer without attenuation

---

## 8. Field Operation Safety

### 8.1 Site Survey Requirements

Before operating the AERIS-10P at any field location, the following site survey must be completed:

1. **Distance from primary service facilities:** Confirm no satellite earth stations within 5 km, radio observatories within 10 km, or airports within 3 km (see Regulatory Analysis document).
2. **Public access:** Identify all paths, roads, and areas where members of the public may approach within the planned transmit arc. If public access within 2 m of the antenna's forward hemisphere cannot be excluded, operation is not permitted without physical barriers.
3. **Overhead hazards:** Identify any overhead power lines, cables, or structures that could contact the antenna tripod or cables.
4. **Weather assessment:** Check weather forecast. Do not operate in lightning conditions (see Section 8.4).
5. **Emergency egress:** Identify the nearest emergency access route and ensure the system can be rapidly powered off and secured.

Document the site survey in the station log (date, location GPS coordinates, survey findings, operator name and callsign).

### 8.2 Warning Signs and Physical Barriers

At field operation sites, the following warning measures must be implemented before commencing RF transmission:

- **Warning signs** posted at a radius of 5 m from the antenna in the forward hemisphere, bearing the text: "ACTIVE RF TRANSMITTER — DO NOT APPROACH WITHIN 2 METRES OF ANTENNA — AUTHORIZED PERSONNEL ONLY"
- For unattended approaches (footpaths, parking areas): physical barriers (cones, tape, or rope) to prevent unintentional entry into the safety zone
- If the site is accessible to the general public, a second operator must be positioned to intercept and redirect any persons approaching the safety zone

### 8.3 Prohibited Operating Areas

Do not operate the AERIS-10P in the following locations without explicit prior coordination with the relevant authority:

| Location Type | Prohibition Basis | Minimum Distance |
|---|---|---|
| Medical facilities (hospitals, care homes) | Medical device interference risk | 500 m |
| Airports and airfields | Air traffic control radar interference; aviation safety | 3 km from boundary |
| Military installations | Military communication interference; access restrictions | 5 km from boundary |
| Satellite earth station facilities | Satellite uplink interference | 5 km from facility |
| Radio astronomy observatories | Scientific observation interference | 10 km from telescope |
| Fuel depots, gas stations | Fire/explosion risk from RF ignition sources | 100 m |

### 8.4 Weather Conditions

**Lightning:** Do not operate the AERIS-10P if lightning is occurring within 10 km or if lightning is forecast within the next 30 minutes. The antenna panel and tripod mast provide an elevated metallic structure that can attract lightning. If lightning approaches during operation:

1. Immediately disable the PA (TX inhibit)
2. Disconnect the antenna cable from the electronics enclosure
3. Move personnel at least 30 m from the antenna system
4. Do not handle the equipment during the storm

**Rain and moisture:** The electronics enclosure is rated for splash resistance (IP54 or equivalent, pending housing design). Do not operate in heavy rain without confirmed housing integrity. Moisture intrusion into the RF connectors or electronics can cause permanent damage to ICs and can create electrical faults.

**Wind:** The antenna panel on a tripod is susceptible to wind loading. In winds above 20 km/h, use sandbag weights on the tripod legs. In winds above 40 km/h, do not operate in the field.

**Temperature:** Operating temperature range for all components: −10°C to +50°C ambient. At ambient temperatures above 35°C, additional cooling may be required for the PA and electronics enclosure.

---

## 9. Emergency Procedures

### 9.1 Emergency Power Cutoff

In any emergency requiring immediate cessation of AERIS-10P operation:

**Fastest method:** Disconnect the 24 V DC power cable at the input connector on the electronics enclosure. This immediately de-energizes all supply rails and ceases all RF transmission. Keep the input connector accessible and un-obstructed at all times during operation.

**Secondary method:** The control software includes an emergency stop (E-STOP) button that simultaneously engages the TX inhibit and commands the MCU to disable all DC-DC converter outputs. This requires the control computer to be operational.

**Hardware emergency stop button:** A panel-mounted normally-closed momentary pushbutton in series with the 24 V input line must be installed before field operation. Pressing this button disconnects the supply without requiring any software action.

### 9.2 RF Exposure First Aid

If a person has been exposed to RF radiation from the AERIS-10P:

**Immediate actions:**
1. Immediately disable the PA (TX inhibit or power cutoff).
2. Remove the affected person from the RF field.
3. Assess for symptoms of RF burns: localized skin redness, pain, warmth, or blistering at the point of contact with the antenna or within the near-field zone.

**RF burn (contact burn):**
- Treat as a thermal burn. Cool the affected area with running water for 10 minutes.
- Cover with a clean, dry dressing. Do not apply ice.
- Seek medical attention if the burn is larger than 1 cm², involves the face or hands, or if blistering occurs.

**Overexposure (no visible burn):**
- If a person was inadvertently in the main beam at close range for a significant period, log the estimated exposure duration and geometry.
- The person should be informed of the exposure and advised to seek medical evaluation if any symptoms develop (headache, localized warmth, visual disturbances).
- Notify the project safety officer and document the incident.

**Eye exposure:**
- If the person was looking directly into the antenna from within 2 m, seek immediate medical evaluation regardless of symptoms. Early ophthalmological assessment is important.

### 9.3 Electrical Incident

**Shock (contact with live conductor):**
1. Do not touch the affected person until power is disconnected.
2. Disconnect the 24 V supply at the source (pull the input cable).
3. If the person is unresponsive, call emergency services (112 in Germany) immediately.
4. Administer CPR if trained and if the person is not breathing.
5. All personnel must have valid first-aid training (Erste Hilfe Schein) before participating in AERIS-10P build and test activities.

**Electrical fire:**
1. Disconnect the 24 V supply immediately.
2. If the fire is small (confined to a single PCB or component) and has not spread: use a Class C fire extinguisher (CO2 or dry powder — suitable for electrical fires). Never use water on an electrical fire.
3. If the fire has spread beyond the electronics enclosure: evacuate the area and call emergency services (112).
4. Do not re-enter the area until the fire service declares it safe.

### 9.4 Incident Reporting

All incidents involving RF exposure above the MPE, electrical shock, fire, or significant equipment damage must be:

1. Documented in the station log with full details (date, time, location, persons involved, sequence of events, immediate actions taken)
2. Reported to the project safety officer within 24 hours
3. Reviewed in a team debriefing before resuming operation
4. If involving members of the public: reported to the appropriate German authority (BNetzA for RF incidents, local health authority for injury)

---

## 10. Chemical Hazards and MSDS References

### 10.1 Solder and Flux

The AERIS-10P PCBs use **lead-free solder** (typically Sn96.5/Ag3.0/Cu0.5, SAC305 alloy, melting point 217–220°C) and associated **no-clean flux** or **water-soluble flux**.

**Solder fumes:** Solder flux fumes are respiratory irritants and potential sensitizers. Colophony (rosin) flux fumes can cause occupational asthma with repeated exposure.

- Use local exhaust ventilation (solder fume extractor) during all soldering
- Work in a ventilated room; do not work in an enclosed space without ventilation
- MSDS Reference: Supplier-specific — refer to flux manufacturer's Safety Data Sheet (e.g., Alpha Flux MSDS, Kester 245 No-Clean Flux MSDS)

### 10.2 Isopropyl Alcohol (IPA)

IPA (isopropyl alcohol, 2-propanol) is commonly used for PCB cleaning after soldering to remove flux residue.

**Hazards:** Flammable (flash point 11.7°C). Irritant to skin and eyes at high concentrations. Vapors are mildly narcotic at very high concentrations.

- Use in small quantities in a well-ventilated area
- Keep away from open flames and hot surfaces (including active soldering irons)
- Store in a sealed container away from heat sources
- MSDS Reference: Merck IPA MSDS, or local supplier's Safety Data Sheet
- UN number: UN1219 (flammable liquid)
- GHS hazard classes: H225 (highly flammable), H319 (eye irritant), H336 (may cause drowsiness)

### 10.3 PCB Chemicals and Etching

If the AERIS-10P antenna board (Rogers RO4003C substrate) is fabricated in-house using wet etching:

**Ferric chloride (FeCl3) etching solution:**
- Strong staining agent — avoid contact with skin and clothing
- Mildly corrosive to skin and eyes
- MSDS Reference: Ferric chloride solution MSDS (e.g., Sigma-Aldrich product SDS)
- Dispose of used etching solution as hazardous waste; do not pour down drain without neutralization

**Ammonium persulfate ((NH4)2S2O8) etching solution:**
- Oxidizer — keep away from flammable materials
- Irritant to skin, eyes, and respiratory system
- MSDS Reference: Ammonium persulfate MSDS

For the AERIS-10P, it is strongly recommended to use a professional PCB fabrication house (e.g., JLCPCB, PCBWay, or a German specialist such as Bungard for Rogers substrates) to avoid in-house chemical processing hazards. Rogers RO4003C is a specialized microwave laminate that requires precision etching for accurate 10 GHz patch dimensions (13.8 mm × 13.8 mm, tolerance ±0.05 mm) — professional fabrication also ensures better dimensional accuracy.

### 10.4 Thermal Paste and Adhesives

The PA (HMC451LS6GE) and other power-dissipating components may require thermal interface materials (thermal paste or phase-change pads) for heatsinking.

**Thermal paste (e.g., Arctic Silver 5, Dowsil TC-5026):**
- Minimal hazard in small quantities
- Avoid eye and skin contact; wash with soap and water after handling
- MSDS Reference: Arctic Silver 5 SDS, Dowsil TC-5026 SDS

**Cyanoacrylate adhesive (if used for component fixturing):**
- Fast-acting skin and eye irritant
- Vapors may cause eye and respiratory irritation
- Use in ventilated area; keep from contact with skin
- MSDS Reference: Loctite 401 SDS or equivalent

### 10.5 General Chemical Safety Practices

1. Maintain a current MSDS/SDS binder for all chemicals used in the AERIS-10P build and test process.
2. Label all chemical containers clearly with content, concentration, date, and hazard information.
3. Store chemicals according to their hazard class (flammables in a flammable cabinet, corrosives separately).
4. Dispose of chemical waste in accordance with German waste disposal regulations (Kreislaufwirtschaftsgesetz, KrWG) and local Landkreis/Gemeinde requirements.
5. First aid for chemical exposure: flush with large amounts of water; consult the relevant SDS for specific first aid measures; seek medical attention if symptoms persist.

---

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-07-14 | HASE-Radar Project Team | Initial release |

**Next review due:** 2027-01-14 or upon any significant design change that affects transmit power, antenna gain, or operating frequency.

---

*End of Document — AERIS-10P Safety Documentation Rev 1.0 — 2026-07-14*
*This document is a safety-critical document. Maintain a printed copy at the operating location at all times.*
