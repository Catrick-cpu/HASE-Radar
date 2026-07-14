# AERIS-10P Control Software
## Version 1.0 — 2026-07-14

Control and monitoring software for the AERIS-10P 10 GHz FMCW Phased Array Radar.

---

## Installation

```bash
# Python 3.10+ required
python --version

# Install dependencies
pip install -r requirements.txt

# Verify installation
python aeris_control.py --help
```

### System Requirements
- Python 3.10 or newer
- Operating System: Linux (Raspberry Pi OS, Ubuntu) or Windows 10/11
- USB CDC-ACM driver: built-in on Linux/Mac; Windows uses native USB CDC driver

---

## Quick Start

### 1. Connect Hardware
```
AERIS-10P USB Micro-B → USB-A on Raspberry Pi 5 or Laptop
24V Power Supply → XT60 connector on AERIS-10P front panel
```

### 2. Identify Serial Port
```bash
# Linux:
ls /dev/ttyACM*     # should show /dev/ttyACM0

# Windows:
# Check Device Manager → Ports (COM & LPT) → "USB Serial Device (COMx)"

# Using aeris_control.py:
python aeris_control.py list-ports
```

### 3. Edit Configuration
```bash
# Copy and edit config:
cp config.yaml my_config.yaml
nano my_config.yaml   # set serial_port and callsign
```

### 4. Basic Operation
```bash
# Check connection and system status
python aeris_control.py status --port /dev/ttyACM0

# Set beam to broadside (0°)
python aeris_control.py beam --az 0 --el 0

# Enable PA (start transmitting)
python aeris_control.py pa-enable 1

# Capture ADC data
python aeris_control.py capture --n 8000 --save session.npy

# Beam scan -45° to +45°
python aeris_control.py scan --az-min -45 --az-max 45 --step 5
```

---

## Commands Reference

| Command | Arguments | Description |
|---|---|---|
| `list-ports` | (none) | List available serial ports |
| `status` | `--port PORT` | Get system status (PA state, beam angles, temperature) |
| `beam` | `--az DEG --el DEG` | Set beam steering angles (az: ±45°, el: ±30°) |
| `pa-enable` | `0` or `1` | Enable (1) or disable (0) the power amplifier |
| `capture` | `--n N --save FILE` | Capture N ADC samples, optionally save to .npy |
| `scan` | `--az-min --az-max --step --el` | Beam scan across azimuth range |
| `reboot` | (none) | Reboot STM32 firmware |

---

## Signal Processing Pipeline

After capturing data, process with the signal processing scripts:

```bash
# Test processing without hardware (synthetic data):
cd ../Signal_Processing
python demo_no_hardware.py --scenario highway

# Process captured data:
python fmcw_processing.py  # runs built-in demo

# Compute link budget:
cd ../../RF_System
python link_budget_calculator.py --range-km 3 --rcs 10 --sweep
```

---

## Configuration Reference (config.yaml)

```yaml
radar:
  serial_port: /dev/ttyACM0  # Linux; use COM3 on Windows
  baud_rate: 115200

rf:
  freq_start_hz: 10000000000  # 10.000 GHz
  freq_stop_hz: 10100000000   # 10.100 GHz
  sweep_time_us: 1000          # 1 ms

beam:
  default_az_deg: 0.0
  default_el_deg: 0.0

regulatory:
  callsign: "DL0EXAMPLE"   # Replace with your Klasse A callsign!
  id_interval_s: 600        # Station ID every 10 minutes (required by law)
```

---

## Regulatory Note

This software implements automatic station identification as required by German amateur radio regulations (AFuG 2017, §16). The callsign is transmitted in the log every `id_interval_s` seconds. Set your actual Klasse A callsign in `config.yaml` before operating.

**Do not operate without a valid Klasse A amateur radio license.**

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `No such file /dev/ttyACM0` | Check USB cable, try different USB port, verify firmware is running (LED blinks) |
| `No PONG response` | Firmware may be in bootloader mode. Press RESET on AERIS board. |
| `PA enable has no effect` | Check PA_EN GPIO wiring, verify +5V and +12V on RF board |
| `No data in capture` | Check ADC SPI wiring, verify ADS8661 is powered (+5V AVDD, +3.3V DVDD) |
| Chirp not locking | Check ADF4159 SPI communication, verify OCXO is powered and warm |

---

## Development

```bash
# Run with verbose logging:
python aeris_control.py --verbose status

# Extend the protocol (add new commands):
# 1. Add CMD_NEW_COMMAND = 0x60 in aeris_control.py
# 2. Add corresponding case in main.c Process_USB_Command()
# 3. Add method in AERISController class
# 4. Flash firmware: cd ../../Software/Embedded/firmware && make flash
```
