"""
AERIS-10P Phase Array Calibration Module
==========================================
Measures and stores calibration tables for phase shifters and LNA amplitude.
"""

import numpy as np
from pathlib import Path
import logging

log = logging.getLogger(__name__)

N_ELEMENTS = 16
N_CODES    = 64
LSB_DEG    = 5.625  # degrees per code step


class PhaseCalibration:
    """Calibrate HMC647A phase shifter arrays."""

    def __init__(self, n_elements: int = N_ELEMENTS, n_codes: int = N_CODES):
        self.n_elements = n_elements
        self.n_codes    = n_codes
        # cal_table[element][code] = phase_error_degrees
        self.cal_table  = np.zeros((n_elements, n_codes), dtype=np.float32)
        self.loaded     = False

    def measure_phase_response(self, controller, element_idx: int,
                                 codes: np.ndarray = None) -> np.ndarray:
        """
        Measure actual phase for each code on one element.
        Requires: VNA or phase measurement instrument connected.

        controller: AERISController object with hardware access
        Returns: (n_codes,) array of measured phases in degrees
        """
        if codes is None:
            codes = np.arange(self.n_codes)
        measured = np.zeros(self.n_codes, dtype=float)
        log.info(f"Calibrating element {element_idx} ({self.n_codes} codes)...")
        for code in codes:
            controller.set_element_code(element_idx, int(code))
            # Wait for phase to settle (10 ms for measurement instrument)
            import time
            time.sleep(0.01)
            # Measure phase via VNA S21 measurement (instrument-specific)
            # TODO: implement VNA interface (GPIB/USB) for automated measurement
            # Placeholder: return nominal phase
            measured[int(code)] = code * LSB_DEG
        return measured

    def compute_cal_table(self, measured_phases: np.ndarray,
                           ideal_phases: np.ndarray = None) -> np.ndarray:
        """
        Compute correction offsets: correction = ideal - measured.

        Args:
            measured_phases: (n_elements, n_codes) array
            ideal_phases: (n_codes,) ideal phases, defaults to k*LSB_DEG

        Returns:
            cal_table: (n_elements, n_codes) phase corrections in degrees
        """
        if ideal_phases is None:
            ideal_phases = np.arange(self.n_codes) * LSB_DEG
        corrections = np.zeros_like(measured_phases)
        for i in range(self.n_elements):
            corrections[i] = ideal_phases - measured_phases[i]
        self.cal_table = corrections.astype(np.float32)
        self.loaded = True
        return self.cal_table

    def save_calibration(self, filename: str):
        """Save calibration table to numpy .npy file."""
        np.save(filename, self.cal_table)
        log.info(f"Calibration saved: {filename} ({self.n_elements}×{self.n_codes})")

    def load_calibration(self, filename: str) -> np.ndarray:
        """Load calibration table from .npy file."""
        self.cal_table = np.load(filename).astype(np.float32)
        self.loaded = True
        log.info(f"Calibration loaded: {filename}")
        return self.cal_table

    def apply_calibration(self, desired_phase_deg: float,
                           element_idx: int) -> int:
        """
        Convert desired phase to corrected code for one element.

        Args:
            desired_phase_deg: desired phase in degrees [0, 360)
            element_idx: which element

        Returns:
            corrected 6-bit code [0..63]
        """
        if not self.loaded:
            # No calibration: use nominal
            code = int(round(desired_phase_deg / LSB_DEG)) % N_CODES
            return code

        # Find code with minimum phase error after correction
        nominal_phases = np.arange(self.n_codes) * LSB_DEG
        corrected_phases = nominal_phases + self.cal_table[element_idx]
        corrected_phases = corrected_phases % 360.0

        # Normalize target
        target = desired_phase_deg % 360.0

        # Minimize |corrected - target| (circular)
        diff = corrected_phases - target
        diff = (diff + 180.0) % 360.0 - 180.0
        best_code = int(np.argmin(np.abs(diff)))
        return best_code

    def rms_phase_error(self) -> np.ndarray:
        """Return per-element RMS phase error in degrees."""
        return np.sqrt(np.mean(self.cal_table**2, axis=1))

    def print_summary(self):
        if not self.loaded:
            print("No calibration loaded.")
            return
        print(f"Phase Calibration Summary ({self.n_elements} elements):")
        print(f"  {'Element':>8}  {'RMS Error [deg]':>16}  {'Max Error [deg]':>16}")
        for i in range(self.n_elements):
            rms = np.sqrt(np.mean(self.cal_table[i]**2))
            mx  = np.max(np.abs(self.cal_table[i]))
            print(f"  {i:>8}  {rms:>16.2f}  {mx:>16.2f}")


class AmplitudeCalibration:
    """Calibrate per-element amplitude response."""

    def __init__(self, n_elements: int = N_ELEMENTS):
        self.n_elements    = n_elements
        self.amp_response  = np.ones(n_elements, dtype=np.float32)  # linear scale
        self.weights       = np.ones(n_elements, dtype=np.float32)  # combining weights

    def measure_amplitude_response(self, controller) -> np.ndarray:
        """Measure amplitude at each element (requires power meter or VNA)."""
        measured = np.ones(self.n_elements)
        log.info("Amplitude calibration — inject CW signal, measure per element")
        # TODO: implement measurement via instrument interface
        self.amp_response = measured.astype(np.float32)
        return self.amp_response

    def compute_amplitude_weights(self) -> np.ndarray:
        """Compute unity-gain weights: w = 1 / amplitude."""
        self.weights = (1.0 / (self.amp_response + 1e-9)).astype(np.float32)
        self.weights /= np.max(self.weights)  # normalize to max = 1
        return self.weights

    def save(self, filename: str):
        np.save(filename, {'amp': self.amp_response, 'weights': self.weights})

    def load(self, filename: str):
        data = np.load(filename, allow_pickle=True).item()
        self.amp_response = data['amp']
        self.weights      = data['weights']
