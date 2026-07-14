"""
AERIS-10P Radar Control Application
=====================================
PC-side control software for the AERIS-10P phased array radar.
Communicates with STM32H743 firmware via USB CDC-ACM (virtual serial port).

Usage:
    python aeris_control.py --help
    python aeris_control.py connect --port /dev/ttyACM0
    python aeris_control.py beam --az 30 --el 0
    python aeris_control.py pa-enable 1
    python aeris_control.py capture --n-chirps 100
    python aeris_control.py scan --az-min -45 --az-max 45 --step 5

Requirements:
    pip install pyserial PyYAML loguru
"""

import struct
import time
import threading
import queue
import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False
    print("Warning: pyserial not installed. Run: pip install pyserial")

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# ── Protocol constants ───────────────────────────────────────────────────────

SYNC1, SYNC2 = 0xAA, 0x55
CMD_PING          = 0x01
CMD_PONG          = 0x02
CMD_SET_BEAM      = 0x10
CMD_SET_CHIRP     = 0x11
CMD_START_CAPTURE = 0x20
CMD_DATA_PACKET   = 0x21
CMD_GET_STATUS    = 0x30
CMD_STATUS        = 0x31
CMD_SET_PA_ENABLE = 0x40
CMD_REBOOT        = 0x50

# ── Logging setup ────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger('aeris')

# ── Config loader ────────────────────────────────────────────────────────────

def load_config(path: str = 'config.yaml') -> dict:
    """Load YAML configuration file."""
    defaults = {
        'radar': {'serial_port': '/dev/ttyACM0', 'baud_rate': 115200},
        'rf': {'freq_start_hz': 10_000_000_000, 'freq_stop_hz': 10_100_000_000, 'sweep_time_us': 1000},
        'beam': {'default_az_deg': 0.0, 'default_el_deg': 0.0},
        'processing': {'adc_sample_rate_hz': 8000, 'n_chirps_per_cpi': 100},
        'regulatory': {'callsign': 'NOCALL', 'id_interval_s': 600},
    }
    if not HAS_YAML or not Path(path).exists():
        return defaults
    with open(path) as f:
        loaded = yaml.safe_load(f)
    # Merge with defaults
    for section, values in defaults.items():
        if section not in loaded:
            loaded[section] = values
        else:
            for k, v in values.items():
                if k not in loaded[section]:
                    loaded[section][k] = v
    return loaded

# ── Packet codec ─────────────────────────────────────────────────────────────

def checksum(data: bytes) -> int:
    result = 0
    for b in data:
        result ^= b
    return result

def build_packet(cmd: int, payload: bytes = b'') -> bytes:
    length = len(payload)
    header = bytes([SYNC1, SYNC2, (length >> 8) & 0xFF, length & 0xFF, cmd])
    body = header + payload
    return body + bytes([checksum(body)])

def parse_packet(data: bytes) -> Optional[tuple]:
    """Parse a received packet. Returns (cmd, payload) or None if invalid."""
    if len(data) < 6:
        return None
    if data[0] != SYNC1 or data[1] != SYNC2:
        return None
    length = (data[2] << 8) | data[3]
    cmd = data[4]
    if len(data) < 5 + length + 1:
        return None
    payload = data[5:5 + length]
    rx_cksum = data[5 + length]
    calc_cksum = checksum(data[:5 + length])
    if rx_cksum != calc_cksum:
        log.warning(f"Checksum mismatch: got {rx_cksum:#04x}, expected {calc_cksum:#04x}")
        return None
    return cmd, payload

# ── AERISController class ─────────────────────────────────────────────────────

class AERISController:
    """Controls AERIS-10P radar via USB CDC-ACM protocol."""

    def __init__(self, port: str, baud: int = 115200, config: dict = None):
        self.port   = port
        self.baud   = baud
        self.config = config or {}
        self._serial: Optional['serial.Serial'] = None
        self._rx_queue = queue.Queue()
        self._rx_thread: Optional[threading.Thread] = None
        self._running = False
        self._data_buffer = bytearray()
        self._last_id_time = 0.0
        self._callsign = self.config.get('regulatory', {}).get('callsign', 'NOCALL')
        self._id_interval = self.config.get('regulatory', {}).get('id_interval_s', 600)

    def connect(self, timeout: float = 5.0) -> bool:
        """Open serial port and verify connectivity with PING."""
        if not HAS_SERIAL:
            log.error("pyserial not installed")
            return False
        try:
            self._serial = serial.Serial(self.port, self.baud, timeout=0.1)
            self._running = True
            self._rx_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self._rx_thread.start()
            log.info(f"Connected to {self.port} @ {self.baud} baud")
        except Exception as e:
            log.error(f"Failed to open {self.port}: {e}")
            return False

        # Send PING
        self._send(build_packet(CMD_PING))
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                cmd, payload = self._rx_queue.get(timeout=0.5)
                if cmd == CMD_PONG:
                    log.info("AERIS-10P connected — PONG received")
                    return True
            except queue.Empty:
                continue
        log.error(f"No PONG response within {timeout}s")
        return False

    def disconnect(self):
        self._running = False
        if self._serial and self._serial.is_open:
            self._serial.close()
        log.info("Disconnected")

    def _send(self, packet: bytes):
        if self._serial and self._serial.is_open:
            self._serial.write(packet)
            self._serial.flush()

    def _receive_loop(self):
        """Background thread: read bytes and parse packets."""
        while self._running:
            if not self._serial or not self._serial.is_open:
                break
            try:
                data = self._serial.read(256)
                if data:
                    self._data_buffer.extend(data)
                    self._process_buffer()
            except Exception:
                break

    def _process_buffer(self):
        """Extract complete packets from buffer."""
        while len(self._data_buffer) >= 6:
            # Find sync bytes
            idx = -1
            for i in range(len(self._data_buffer) - 1):
                if self._data_buffer[i] == SYNC1 and self._data_buffer[i+1] == SYNC2:
                    idx = i
                    break
            if idx < 0:
                self._data_buffer.clear()
                return
            if idx > 0:
                self._data_buffer = self._data_buffer[idx:]

            if len(self._data_buffer) < 6:
                return
            length = (self._data_buffer[2] << 8) | self._data_buffer[3]
            total_len = 5 + length + 1
            if len(self._data_buffer) < total_len:
                return
            packet_bytes = bytes(self._data_buffer[:total_len])
            self._data_buffer = self._data_buffer[total_len:]
            result = parse_packet(packet_bytes)
            if result:
                self._rx_queue.put(result)

    def _wait_for_response(self, expected_cmd: int, timeout: float = 2.0):
        """Wait for a specific command response."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                cmd, payload = self._rx_queue.get(timeout=0.2)
                if cmd == expected_cmd:
                    return payload
            except queue.Empty:
                continue
        return None

    # ── Public API ────────────────────────────────────────────────────

    def set_beam(self, az_deg: float, el_deg: float) -> bool:
        """Set beam steering angles."""
        az_deg = max(-45.0, min(45.0, az_deg))
        el_deg = max(-30.0, min(30.0, el_deg))
        payload = struct.pack('<ff', az_deg, el_deg)
        self._send(build_packet(CMD_SET_BEAM, payload))
        log.info(f"Beam → az={az_deg:.1f}° el={el_deg:.1f}°")
        self._check_station_id()
        return True

    def set_chirp(self, f_start_hz: int, f_stop_hz: int, sweep_time_us: int) -> bool:
        """Configure FMCW chirp parameters."""
        payload = struct.pack('<QQI', f_start_hz, f_stop_hz, sweep_time_us)
        self._send(build_packet(CMD_SET_CHIRP, payload))
        log.info(f"Chirp: {f_start_hz/1e9:.3f}–{f_stop_hz/1e9:.3f} GHz, {sweep_time_us} µs")
        return True

    def set_pa_enable(self, enable: bool) -> bool:
        """Enable or disable the power amplifier."""
        payload = bytes([1 if enable else 0])
        self._send(build_packet(CMD_SET_PA_ENABLE, payload))
        log.info(f"PA {'ENABLED' if enable else 'disabled'}")
        return True

    def capture(self, n_samples: int = 8000) -> Optional[list]:
        """Request and receive ADC data capture."""
        payload = struct.pack('<I', n_samples)
        self._send(build_packet(CMD_START_CAPTURE, payload))
        log.info(f"Capture started: {n_samples} samples")
        # Collect DATA_PACKET responses
        samples = []
        deadline = time.monotonic() + 10.0
        while time.monotonic() < deadline:
            try:
                cmd, payload = self._rx_queue.get(timeout=0.5)
                if cmd == CMD_DATA_PACKET and len(payload) >= 4:
                    seq = struct.unpack('<I', payload[:4])[0]
                    raw = payload[4:]
                    if HAS_NUMPY:
                        data = np.frombuffer(raw, dtype=np.uint16).astype(float)
                    else:
                        data = list(struct.unpack(f'<{len(raw)//2}H', raw))
                    samples.extend(data)
                    log.debug(f"  Received packet seq={seq}, {len(data)} samples")
                    if len(samples) >= n_samples:
                        break
            except queue.Empty:
                continue
        log.info(f"Capture complete: {len(samples)} samples received")
        return samples

    def get_status(self) -> dict:
        """Get system status."""
        self._send(build_packet(CMD_GET_STATUS))
        payload = self._wait_for_response(CMD_STATUS, timeout=2.0)
        if payload and len(payload) >= 13:
            flags = payload[0]
            az, el, temp = struct.unpack('<fff', payload[1:13])
            return {
                'pa_enabled':   bool(flags & 0x01),
                'pll_locked':   bool(flags & 0x02),
                'beam_az_deg':  az,
                'beam_el_deg':  el,
                'pa_temp_c':    temp,
            }
        return {}

    def reboot(self):
        """Reboot the STM32 firmware."""
        self._send(build_packet(CMD_REBOOT))
        log.info("Reboot command sent")

    def scan(self, az_min: float = -45, az_max: float = 45,
             az_step: float = 5, el_deg: float = 0,
             capture_per_beam: int = 100):
        """Scan beam across azimuth range, capturing data at each position."""
        az_positions = []
        az = az_min
        while az <= az_max + 0.01:
            az_positions.append(round(az, 1))
            az += az_step

        log.info(f"Starting beam scan: {az_positions[0]}° to {az_positions[-1]}° "
                 f"in {az_step}° steps ({len(az_positions)} positions)")

        results = {}
        for az in az_positions:
            self.set_beam(az, el_deg)
            time.sleep(0.05)  # settle time
            data = self.capture(capture_per_beam)
            results[az] = data
            log.info(f"  az={az:+6.1f}°: {len(data)} samples")

        return results

    def _check_station_id(self):
        """Check if station identification is due (every id_interval seconds)."""
        now = time.monotonic()
        if now - self._last_id_time >= self._id_interval:
            self._last_id_time = now
            log.info(f"[REGULATORY] Station identification: {self._callsign} "
                     f"(required every {self._id_interval}s per AFuG §16)")

    @staticmethod
    def list_ports() -> list:
        """List available serial ports."""
        if not HAS_SERIAL:
            return []
        return [p.device for p in serial.tools.list_ports.comports()]

# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='AERIS-10P Radar Control (v1.0)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python aeris_control.py list-ports
  python aeris_control.py status --port /dev/ttyACM0
  python aeris_control.py beam --az 30 --el 0
  python aeris_control.py capture --n 100 --save capture.npy
  python aeris_control.py scan --az-min -45 --az-max 45 --step 10
        """
    )
    parser.add_argument('--port', default=None, help='Serial port (default: from config.yaml)')
    parser.add_argument('--baud', type=int, default=115200)
    parser.add_argument('--config', default='config.yaml')
    parser.add_argument('--verbose', '-v', action='store_true')

    sub = parser.add_subparsers(dest='cmd')

    # list-ports
    sub.add_parser('list-ports', help='List available serial ports')

    # status
    sub.add_parser('status', help='Get system status')

    # beam
    p_beam = sub.add_parser('beam', help='Set beam steering')
    p_beam.add_argument('--az', type=float, default=0.0)
    p_beam.add_argument('--el', type=float, default=0.0)

    # pa-enable
    p_pa = sub.add_parser('pa-enable', help='Enable/disable PA')
    p_pa.add_argument('state', type=int, choices=[0, 1], help='0=off, 1=on')

    # capture
    p_cap = sub.add_parser('capture', help='Capture ADC samples')
    p_cap.add_argument('--n', type=int, default=8000, help='Number of samples')
    p_cap.add_argument('--save', type=str, help='Save to numpy .npy file')

    # scan
    p_scan = sub.add_parser('scan', help='Beam scan across azimuth')
    p_scan.add_argument('--az-min', type=float, default=-45)
    p_scan.add_argument('--az-max', type=float, default=45)
    p_scan.add_argument('--step', type=float, default=5)
    p_scan.add_argument('--el', type=float, default=0.0)

    # reboot
    sub.add_parser('reboot', help='Reboot firmware')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.cmd == 'list-ports':
        ports = AERISController.list_ports()
        if ports:
            print("Available serial ports:")
            for p in ports:
                print(f"  {p}")
        else:
            print("No serial ports found")
        return

    config = load_config(args.config)
    port = args.port or config.get('radar', {}).get('serial_port', '/dev/ttyACM0')

    if args.cmd is None:
        parser.print_help()
        return

    ctrl = AERISController(port, args.baud, config)
    if not ctrl.connect():
        sys.exit(1)

    try:
        if args.cmd == 'status':
            status = ctrl.get_status()
            print(f"PA enabled:  {status.get('pa_enabled', 'unknown')}")
            print(f"PLL locked:  {status.get('pll_locked', 'unknown')}")
            print(f"Beam:        az={status.get('beam_az_deg', 0):.1f}°  el={status.get('beam_el_deg', 0):.1f}°")
            print(f"PA temp:     {status.get('pa_temp_c', 0):.1f}°C")

        elif args.cmd == 'beam':
            ctrl.set_beam(args.az, args.el)

        elif args.cmd == 'pa-enable':
            ctrl.set_pa_enable(bool(args.state))

        elif args.cmd == 'capture':
            data = ctrl.capture(args.n)
            if data and args.save and HAS_NUMPY:
                np.save(args.save, np.array(data))
                print(f"Saved {len(data)} samples to {args.save}")
            else:
                print(f"Captured {len(data)} samples")

        elif args.cmd == 'scan':
            results = ctrl.scan(args.az_min, args.az_max, args.step, args.el)
            print(f"Scan complete: {len(results)} beam positions")
            for az, data in results.items():
                print(f"  az={az:+6.1f}°: {len(data)} samples")

        elif args.cmd == 'reboot':
            ctrl.reboot()

    finally:
        ctrl.disconnect()


if __name__ == '__main__':
    main()
