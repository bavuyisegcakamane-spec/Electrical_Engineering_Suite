"""Preliminary cable checks using externally verified input ratings.

No built-in ampacity table or regulatory compliance claim. Installation method,
insulation, grouping, ambient conditions and applicable standards must be checked
by a qualified designer. These functions are screening calculations only.
"""
import math


def _positive_finite(name, value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a positive finite number.")
    return float(value)


def derated_ampacity(reference_ampacity_a, temperature_factor=1.0,
                    grouping_factor=1.0, other_factor=1.0,
                    design_current_a=None, breaker_rating_a=None):
    """Apply independently sourced correction factors to a verified reference Iz.

    The reference ampacity and factors MUST come from a documented applicable
    standard/manufacturer table; default 1.0 does not imply suitable conditions.
    """
    reference = _positive_finite("Reference ampacity", reference_ampacity_a)
    factors = [temperature_factor, grouping_factor, other_factor]
    for factor in factors:
        if _positive_finite("Correction factor", factor) > 1:
            raise ValueError("Correction factors above 1 need a separate engineering assessment.")
    adjusted = reference * math.prod(factors)
    if not math.isfinite(adjusted) or adjusted <= 0:
        raise ValueError("Invalid adjusted ampacity.")
    result = {"reference_ampacity_a": reference, "derated_ampacity_a": adjusted,
              "correction_factors": tuple(factors)}
    if design_current_a is not None:
        ib = _positive_finite("Design current", design_current_a)
        result["design_current_within_ampacity"] = ib <= adjusted
    if breaker_rating_a is not None:
        protective = _positive_finite("Breaker rating", breaker_rating_a)
        result["breaker_nominal_within_ampacity"] = protective <= adjusted
    if design_current_a is not None and breaker_rating_a is not None:
        result["nominal_current_chain_passes"] = ib <= protective <= adjusted
    result["warning"] = ("Preliminary Ib <= In <= Iz check only; does not verify "
                         "trip curves, overload operation, short-circuit protection or compliance.")
    return result


def adiabatic_short_circuit_check(area_mm2, fault_current_a, clearing_time_s, k_a_sqrt_s_per_mm2):
    """Screen I²t <= (k*S)² using a separately verified material/insulation k.

    Only valid where the adiabatic approximation applies. Verify k, actual
    let-through energy, protective-device characteristics and applicable limits.
    """
    s = _positive_finite("Conductor area", area_mm2)
    current = _positive_finite("Fault current", fault_current_a)
    duration = _positive_finite("Clearing time", clearing_time_s)
    k = _positive_finite("Adiabatic k factor", k_a_sqrt_s_per_mm2)
    energy = (current ** 2) * duration
    withstand = (k * s) ** 2
    if not math.isfinite(energy) or not math.isfinite(withstand):
        raise ValueError("Calculated energy exceeds numeric range.")
    return {"fault_energy_a2s": energy, "conductor_limit_a2s": withstand,
            "thermal_screen_passes": energy <= withstand,
            "max_adiabatic_time_s": (k * s / current) ** 2,
            "warning": "Preliminary adiabatic screen only; not a verified protection design."}
