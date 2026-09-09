"""Electrical power calculations."""


def calculate_power_vi(voltage: float, current: float) -> float:
    """Calculate power using P = V × I."""

    return voltage * current


def calculate_power_ir(current: float, resistance: float) -> float:
    """Calculate power using P = I² × R."""

    if resistance < 0:
        raise ValueError("Resistance cannot be negative.")

    return current ** 2 * resistance


def calculate_power_vr(voltage: float, resistance: float) -> float:
    """Calculate power using P = V² / R."""

    if resistance <= 0:
        raise ValueError("Resistance must be greater than zero.")

    return voltage ** 2 / resistance


def calculate_energy(power_watts: float, time_hours: float) -> float:
    """Calculate energy in watt-hours.

    Energy = Power × Time
    """

    if power_watts < 0:
        raise ValueError("Power cannot be negative.")

    if time_hours < 0:
        raise ValueError("Time cannot be negative.")

    return power_watts * time_hours