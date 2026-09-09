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