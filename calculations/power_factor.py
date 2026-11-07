"""Idealized balanced three-phase power factor correction estimates."""
import math


def estimate_correction(real_power_kw, voltage_ll_v, initial_pf, target_pf):
    """Calculate ideal reactive compensation and line current before/after.

    Assumes a constant real power, lagging initial PF, balanced sinusoidal
    three-phase supply and ideal compensation. Not a capacitor-bank design.
    """
    values = (real_power_kw, voltage_ll_v, initial_pf, target_pf)
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in values):
        raise ValueError("Inputs must be finite numbers.")
    if real_power_kw <= 0 or voltage_ll_v <= 0:
        raise ValueError("Real power and line-to-line voltage must be positive.")
    if not 0 < initial_pf <= 1 or not 0 < target_pf <= 1:
        raise ValueError("Power factors must be greater than zero and at most one.")
    if target_pf < initial_pf:
        raise ValueError("Target power factor must be at least the initial power factor.")
    initial_q = real_power_kw * math.sqrt(max(0.0, 1 - initial_pf ** 2)) / initial_pf
    target_q = real_power_kw * math.sqrt(max(0.0, 1 - target_pf ** 2)) / target_pf
    compensation_kvar = max(0.0, initial_q - target_q)
    initial_kva = real_power_kw / initial_pf
    target_kva = real_power_kw / target_pf
    initial_current = initial_kva * 1000 / (math.sqrt(3) * voltage_ll_v)
    target_current = target_kva * 1000 / (math.sqrt(3) * voltage_ll_v)
    results = (compensation_kvar, initial_kva, target_kva, initial_current, target_current)
    if not all(math.isfinite(x) for x in results):
        raise ValueError("Calculated result exceeds numeric range.")
    return {"required_compensation_kvar": compensation_kvar,
            "initial_apparent_kva": initial_kva, "target_apparent_kva": target_kva,
            "initial_line_current_amps": initial_current,
            "target_line_current_amps": target_current,
            "line_current_reduction_amps": initial_current - target_current}
