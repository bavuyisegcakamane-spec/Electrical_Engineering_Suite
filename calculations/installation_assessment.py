"""Preliminary cable, earthing and protection arithmetic; NOT code-compliant design."""
import math


def _positive(**kwargs):
    for name, value in kwargs.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be a finite positive number")


def cable_screening(design_current_a, reference_ampacity_a, correction_factor,
                    circuit_length_m, conductor_resistance_ohms_per_km, voltage_v):
    """Apply user-supplied derating and resistive single-phase loop drop (two conductors)."""
    _positive(design_current_a=design_current_a, reference_ampacity_a=reference_ampacity_a,
              correction_factor=correction_factor, circuit_length_m=circuit_length_m,
              conductor_resistance_ohms_per_km=conductor_resistance_ohms_per_km, voltage_v=voltage_v)
    if correction_factor > 1:
        raise ValueError("Correction factor must not exceed 1")
    adjusted_ampacity = reference_ampacity_a * correction_factor
    drop_v = 2 * design_current_a * circuit_length_m / 1000 * conductor_resistance_ohms_per_km
    results = {"adjusted_ampacity_a": adjusted_ampacity,
               "current_exceeds_adjusted_ampacity": design_current_a > adjusted_ampacity,
               "estimated_resistive_drop_v": drop_v,
               "estimated_drop_percent": 100 * drop_v / voltage_v}
    if not all(math.isfinite(v) for v in results.values() if isinstance(v, float)):
        raise ValueError("Calculated result exceeds numeric range")
    return results


def earth_fault_loop_screening(line_to_earth_voltage_v, measured_loop_impedance_ohms,
                               assumed_disconnection_current_a):
    """Compare idealized fault current with a USER-SUPPLIED disconnection threshold.

    No protective-device time curve, Zs limit, touch voltage, or standard is inferred.
    """
    _positive(line_to_earth_voltage_v=line_to_earth_voltage_v,
              measured_loop_impedance_ohms=measured_loop_impedance_ohms,
              assumed_disconnection_current_a=assumed_disconnection_current_a)
    prospective_a = line_to_earth_voltage_v / measured_loop_impedance_ohms
    ratio = prospective_a / assumed_disconnection_current_a
    if not math.isfinite(ratio) or not math.isfinite(prospective_a):
        raise ValueError("Calculated result exceeds numeric range")
    return {"idealized_earth_fault_current_a": prospective_a,
            "current_to_assumed_threshold_ratio": ratio,
            "below_assumed_threshold": prospective_a < assumed_disconnection_current_a}
