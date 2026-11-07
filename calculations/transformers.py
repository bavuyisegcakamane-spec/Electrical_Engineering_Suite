#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Ideal single-phase transformer steady-state relationships.

Educational calculations only; no losses, regulation or protection modeled.
"""
import math


def analyze_transformer(primary_voltage_v, primary_turns, secondary_turns,
                        rated_apparent_power_va):
    """Return ideal secondary voltage and full-load rated currents.

    Assumes a single-phase ideal transformer, sinusoidal AC and positive
    rated apparent power. Turn counts may be specified as positive ratios.
    """
    values = (primary_voltage_v, primary_turns, secondary_turns, rated_apparent_power_va)
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0
           for v in values):
        raise ValueError("Voltage, turns and apparent power must be finite positive numbers.")
    ratio = primary_turns / secondary_turns
    secondary_voltage = primary_voltage_v / ratio
    primary_current = rated_apparent_power_va / primary_voltage_v
    secondary_current = rated_apparent_power_va / secondary_voltage
    results = (ratio, secondary_voltage, primary_current, secondary_current)
    if not all(math.isfinite(v) and v > 0 for v in results):
        raise ValueError("Calculated values exceed numeric range.")
    return {"turns_ratio_primary_to_secondary": ratio,
            "primary_voltage_v": primary_voltage_v,
            "secondary_voltage_v": secondary_voltage,
            "rated_apparent_power_va": rated_apparent_power_va,
            "primary_rated_current_a": primary_current,
            "secondary_rated_current_a": secondary_current,
            "ideal_primary_power_va": rated_apparent_power_va,
            "ideal_secondary_power_va": rated_apparent_power_va}
