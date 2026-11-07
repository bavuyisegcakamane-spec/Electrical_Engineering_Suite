#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Ohm's Law calculations.

Ohm's Law:
    V = I × R
    I = V / R
    R = V / I
"""


def calculate_voltage(current: float, resistance: float) -> float:
    """Calculate voltage from current and resistance."""

    if resistance < 0:
        raise ValueError("Resistance cannot be negative.")

    return current * resistance


def calculate_current(voltage: float, resistance: float) -> float:
    """Calculate current from voltage and resistance."""

    if resistance <= 0:
        raise ValueError("Resistance must be greater than zero.")

    return voltage / resistance


def calculate_resistance(voltage: float, current: float) -> float:
    """Calculate resistance from voltage and current."""

    if current == 0:
        raise ValueError("Current cannot be zero.")

    return voltage / current