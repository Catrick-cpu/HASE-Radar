# AERIS-10P Validation Methods
## Rev 1.0 — 2026-07-14

---

## 1. Validation Philosophy

Each subsystem is validated independently before integration. Simulation predictions are compared against measurements. Pass/fail criteria are defined for each requirement.

**Validation levels:**
1. **L1 — Analysis:** verified by calculation (design-time, no hardware)
2. **L2 — Simulation:** verified by software simulation (demo_no_hardware.py, OpenEMS)
3. **L3 — Bench test:** verified by bench measurement (single board, lab instruments)
4. **L4 — Integration test:** verified in complete integrated system
5. **L5 — Field test:** verified in operational field conditions

---

## 2. Requirements Validation Matrix

| Req ID | Description | Target | Method | Level | Status |
|---|---|---|---|---|---|
| REQ-RF-001 | Chirp start frequency | 10.000 ±1 MHz | Spectrum analyzer | L3 | Pending |
| REQ-RF-002 | Chirp stop frequency | 10.100 ±1 MHz | Spectrum analyzer | L3 | Pending |
| REQ-RF-003 | Chirp bandwidth | 100 ±2 MHz | Spectrum analyzer | L3 | Pending |
| REQ-RF-004 | Chirp linearity | ≤1% deviation | Oscilloscope + FFT | L3 | Pending |
| REQ-RF-005 | TX output power | +25 to +30 dBm | Power meter | L3 | Pending |
| REQ-RF-006 | Phase shifter range | 0–354° all elements | VNA S21 phase | L3 | Pending |
| REQ-RF-007 | Phase shifter error | ≤3° RMS | VNA measurement | L3 | Pending |
| REQ-RF-008 | System noise figure | ≤3 dB | Y-factor | L3 | Pending |
| REQ-SYS-001 | Range resolution | ≤2 m | Corner reflector | L4 | Pending |
| REQ-SYS-002 | Max detection range (car) | ≥2 km | Field test | L5 | Pending |
| REQ-SYS-003 | Beam steering range | ±45° | Calibration antenna | L4 | Pending |
| REQ-SYS-004 | Beam width | ≤25° | Array pattern meas. | L4 | Pending |
| REQ-REG-001 | TX frequency in band | 10.000–10.500 GHz | Spectrum analyzer | L3 | Analysis done |
| REQ-REG-002 | TX power ≤75 W PEP | ≤75 W | Power meter | L3 | Pending |
| REQ-REG-003 | Station identification | Every 10 min | Software review | L2 | Analysis done |

---

## 3. Simulation-Hardware Correlation

For each test:
1. Run `demo_no_hardware.py` with same parameters (range, RCS, SNR)
2. Simulate and record: detected range, SNR, false alarm rate
3. Compare to hardware measurement result
4. Acceptance: within ±3 dB SNR, ±1 range bin

```python
# Run simulation for comparison:
python Software/Signal_Processing/demo_no_hardware.py \
  --scenario single \
  --no-display \
  --print-link-budget
```

---

## 4. Software Validation (Unit Tests)

```python
# Test signal processing pipeline:
python Software/Signal_Processing/fmcw_processing.py  # runs demo()

# Test link budget calculator:
python RF_System/link_budget_calculator.py --print-link-budget

# Test antenna simulation:
python RF_System/openems_antenna_simulation.py --mode analytical
```

**Test cases for fmcw_processing.py:**
- Single target at 500 m: verify detected range = 500 ±1.5 m
- Two targets at 500 m, 1200 m: verify both detected, resolved
- CFAR false alarm rate: 1000 noise-only trials, verify <1% false detections
- Phase monopulse: inject 30° angle, verify estimate within ±3°

---

## 5. Validation Report Template

After each test phase, complete this template:

```
AERIS-10P Validation Report
Test phase: [Phase name]
Date: [YYYY-MM-DD]
Operator: [Name + callsign]
Location: [Lab / field location]
Weather: [Temperature, humidity, conditions]

Equipment:
  VNA: [Model, serial, cal date]
  SA:  [Model, serial, cal date]
  Power meter: [Model, sensor, cal date]

Results:
  [Req ID]: Measured=[value], Spec=[value], PASS/FAIL

Issues:
  [Issue description, workaround applied]

Signature: _____________ Date: _________
```

---

## 6. Error Budget

| Error source | Magnitude | Impact |
|---|---|---|
| Phase shifter LSB (5.625°) | ±2.8° per element | ±1.4° beam pointing |
| Phase calibration residual | ±3° RMS | ~0.1 dB gain loss |
| Cable phase mismatch | ±3° | Same as calibration |
| Thermal drift (per 10°C) | ~0.5°/shifter | Correct with periodic recal |
| Total combined | ~±5° system | ~0.5 dB gain degradation |

**Conclusion:** Combined errors result in <0.5 dB gain loss and <2° beam pointing error. Acceptable for research-grade system.
