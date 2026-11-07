"""Educational prospective fault-current and breaker rating comparisons.

Not suitable for protective device selection, arc-flash, or compliance decisions.
"""
import math


def estimate_fault_current(voltage_v, loop_impedance_ohms, breaker_rating_amps,
                           breaking_capacity_ka, phases=1):
    """Estimate ideal symmetrical RMS fault current from assumed loop impedance.

    For 1-phase, voltage is line-neutral; for 3-phase, line-line and the
    impedance is assumed per-phase positive-sequence equivalent. This is a
    simplified model, not an IEC 60909 or maximum/minimum fault study.
    """
    values = (voltage_v, loop_impedance_ohms, breaker_rating_amps, breaking_capacity_ka)
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError("All inputs must be finite numbers.")
    if any(v <= 0 for v in values):
        raise ValueError("All inputs must be greater than zero.")
    if phases not in (1, 3) or isinstance(phases, bool):
        raise ValueError("Phases must be 1 or 3.")
    phase_voltage = voltage_v if phases == 1 else voltage_v / math.sqrt(3)
    fault_amps = phase_voltage / loop_impedance_ohms
    ratio = fault_amps / breaker_rating_amps
    capacity_amps = breaking_capacity_ka * 1000
    if not all(math.isfinite(v) for v in (fault_amps, ratio, capacity_amps)):
        raise ValueError("Calculated result exceeds numeric range.")
    return {"fault_current_amps": fault_amps, "fault_current_ka": fault_amps / 1000,
            "fault_to_rating_ratio": ratio, "breaking_capacity_amps": capacity_amps,
            "exceeds_stated_breaking_capacity": fault_amps > capacity_amps}
