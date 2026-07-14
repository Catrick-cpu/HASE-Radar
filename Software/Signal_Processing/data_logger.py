"""
AERIS-10P Radar Data Logger
============================
Records raw chirp data and detections to HDF5 files for post-processing.
"""

import h5py
import numpy as np
from datetime import datetime
from pathlib import Path
import logging

log = logging.getLogger(__name__)
SOFTWARE_VERSION = "1.0.0"


class RadarDataLogger:
    """Logs FMCW radar data to HDF5 files."""

    def __init__(self, output_dir: str = "./data", session_name: str = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_name = session_name or f"aeris_{ts}"
        self.filepath = self.output_dir / f"{self.session_name}.h5"
        self._hfile = None
        self._chirp_count = 0
        self._det_count = 0

    def open(self, params_dict: dict = None, operator: str = ""):
        """Open HDF5 file and write metadata."""
        self._hfile = h5py.File(self.filepath, 'w')
        meta = self._hfile.create_group("metadata")
        meta.attrs['session_name']     = self.session_name
        meta.attrs['software_version'] = SOFTWARE_VERSION
        meta.attrs['created']          = datetime.now().isoformat()
        meta.attrs['operator']         = operator
        if params_dict:
            for k, v in params_dict.items():
                try:
                    meta.attrs[k] = v
                except TypeError:
                    meta.attrs[k] = str(v)
        self._hfile.create_group("raw_data")
        self._hfile.create_group("detections")
        log.info(f"Session opened: {self.filepath}")

    def log_chirp_burst(self, data: np.ndarray,
                         beam_az: float = 0.0, beam_el: float = 0.0):
        """Save one CPI chirp matrix (num_chirps × num_samples)."""
        if self._hfile is None:
            raise RuntimeError("Call open() first")
        name = f"chirp_{self._chirp_count:06d}"
        ds = self._hfile["raw_data"].create_dataset(
            name, data=data.astype(np.complex64), compression="gzip"
        )
        ds.attrs['timestamp'] = datetime.now().isoformat()
        ds.attrs['beam_az']   = beam_az
        ds.attrs['beam_el']   = beam_el
        self._chirp_count += 1
        if self._chirp_count % 10 == 0:
            self._hfile.flush()

    def log_detections(self, detections: list, beam_az: float = 0.0, beam_el: float = 0.0):
        """Save detection list for one scan."""
        if not detections:
            return
        dt = np.dtype([
            ('range_m',      np.float32),
            ('velocity_mps', np.float32),
            ('amplitude_db', np.float32),
            ('snr_db',       np.float32),
            ('az_deg',       np.float32),
            ('el_deg',       np.float32),
        ])
        arr = np.zeros(len(detections), dtype=dt)
        for i, d in enumerate(detections):
            arr[i] = (getattr(d, 'range_m', 0), getattr(d, 'velocity_mps', 0),
                      getattr(d, 'amplitude_db', 0), getattr(d, 'snr_db', 0),
                      getattr(d, 'az_deg', beam_az), getattr(d, 'el_deg', beam_el))
        name = f"scan_{self._det_count:06d}"
        ds = self._hfile["detections"].create_dataset(name, data=arr)
        ds.attrs['timestamp'] = datetime.now().isoformat()
        ds.attrs['beam_az']   = beam_az
        ds.attrs['beam_el']   = beam_el
        self._det_count += 1

    def close(self):
        if self._hfile:
            self._hfile.flush()
            self._hfile.close()
            self._hfile = None
            log.info(f"Session closed: {self.filepath} ({self._chirp_count} CPIs)")

    def replay_session(self, filepath: str = None):
        """Generator yielding (data, beam_az, beam_el) for each stored CPI."""
        path = filepath or str(self.filepath)
        with h5py.File(path, 'r') as f:
            for key in sorted(f["raw_data"].keys()):
                ds = f["raw_data"][key]
                yield (np.array(ds), ds.attrs.get('beam_az', 0.0), ds.attrs.get('beam_el', 0.0))

    def export_detections_csv(self, output_csv: str = None, filepath: str = None):
        """Export all detections to CSV for analysis in Excel/pandas."""
        import csv
        path  = filepath or str(self.filepath)
        ofile = output_csv or str(self.filepath).replace('.h5', '_detections.csv')
        with h5py.File(path, 'r') as f, open(ofile, 'w', newline='') as cf:
            writer = csv.writer(cf)
            writer.writerow(['scan', 'timestamp', 'range_m', 'velocity_mps',
                             'amplitude_db', 'snr_db', 'az_deg', 'el_deg'])
            for key in sorted(f["detections"].keys()):
                ds  = f["detections"][key]
                ts  = ds.attrs.get('timestamp', '')
                for row in ds:
                    writer.writerow([key, ts] + list(row))
        log.info(f"Exported detections to: {ofile}")
        return ofile
