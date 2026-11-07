#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Illustrative resistive voltage-drop estimates, NOT regulatory cable sizing."""
import math

RESISTIVITY_OHM_MM2_PER_M = {"Copper": 0.01724, "Aluminium": 0.02826}


def estimate_voltage_drop(current_amps, one_way_length_m, area_mm2, voltage_v,
                          material="Copper", phases=1, conductor_temp_c=20.0,
                          power_factor=1.0):
    """Estimate resistive component of AC voltage drop, ignoring reactance.

    1-phase uses 2 conductors; balanced 3-phase uses sqrt(3). Values are
    illustrative at stated conductor temperature, not ampacity or compliance.
    """
    values = (current_amps, one_way_length_m, area_mm2, voltage_v, conductor_temp_c, power_factor)
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in values):
        raise ValueError("Inputs must be finite numbers.")
    if current_amps < 0 or one_way_length_m < 0 or area_mm2 <= 0 or voltage_v <= 0:
        raise ValueError("Current and length must be non-negative; area and voltage positive.")
    if not 0 < power_factor <= 1:
        raise ValueError("Power factor must be greater than zero and at most one.")
    if phases not in (1, 3) or isinstance(phases, bool):
        raise ValueError("Phases must be 1 or 3.")
    if material not in RESISTIVITY_OHM_MM2_PER_M:
        raise ValueError("Material must be Copper or Aluminium.")
    if conductor_temp_c < -50 or conductor_temp_c > 200:
        raise ValueError("Temperature must be between -50 and 200 degrees C.")
    coefficient = 0.00393 if material == "Copper" else 0.00403
    rho = RESISTIVITY_OHM_MM2_PER_M[material] * (1 + coefficient * (conductor_temp_c - 20))
    factor = 2 if phases == 1 else math.sqrt(3)
    drop = factor * current_amps * one_way_length_m * rho / area_mm2 * power_factor
    percent = 100 * drop / voltage_v
    if not all(math.isfinite(x) for x in (drop, percent)):
        raise ValueError("Calculated result exceeds numeric range.")
    return {"voltage_drop_v": drop, "voltage_drop_percent": percent,
            "estimated_load_voltage_v": voltage_v - drop,
            "conductor_resistance_ohm_per_m": rho / area_mm2}
