#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Rated operating estimates for balanced three-phase AC motors."""
import math


def analyze_motor(output_kw, voltage, efficiency, power_factor, speed_rpm):
    """Estimate rated input power, line current, apparent/reactive power and torque.

    Efficiency and power factor are decimal fractions, not percentages.
    Uses nominal steady-state conditions; not starting current or protection sizing.
    """
    values = (output_kw, voltage, efficiency, power_factor, speed_rpm)
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError("All inputs must be finite numbers.")
    if output_kw <= 0 or voltage <= 0 or speed_rpm <= 0:
        raise ValueError("Motor output power, line voltage and speed must be positive.")
    if not 0 < efficiency <= 1 or not 0 < power_factor <= 1:
        raise ValueError("Efficiency and power factor must be greater than 0 and at most 1.")
    input_kw = output_kw / efficiency
    apparent_kva = input_kw / power_factor
    line_current = apparent_kva * 1000 / (math.sqrt(3) * voltage)
    reactive_kvar = apparent_kva * math.sqrt(max(0.0, 1 - power_factor ** 2))
    torque_nm = output_kw * 1000 * 60 / (2 * math.pi * speed_rpm)
    if not all(math.isfinite(v) for v in (input_kw, apparent_kva, line_current, reactive_kvar, torque_nm)):
        raise ValueError("Calculated result exceeds numeric range.")
    return {"input_kw": input_kw, "apparent_kva": apparent_kva,
            "line_current_amps": line_current, "reactive_kvar": reactive_kvar,
            "shaft_torque_nm": torque_nm, "losses_kw": input_kw - output_kw}
