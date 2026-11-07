#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Electrical engineering unit conversions."""


def watts_to_kilowatts(watts: float) -> float:
    """Convert watts to kilowatts."""

    return watts / 1000


def kilowatts_to_watts(kilowatts: float) -> float:
    """Convert kilowatts to watts."""

    return kilowatts * 1000


def watt_hours_to_kilowatt_hours(watt_hours: float) -> float:
    """Convert watt-hours to kilowatt-hours."""

    return watt_hours / 1000


def kilowatt_hours_to_watt_hours(
    kilowatt_hours: float,
) -> float:
    """Convert kilowatt-hours to watt-hours."""

    return kilowatt_hours * 1000


def milliamps_to_amps(milliamps: float) -> float:
    """Convert milliamps to amps."""

    return milliamps / 1000


def amps_to_milliamps(amps: float) -> float:
    """Convert amps to milliamps."""

    return amps * 1000


def millivolts_to_volts(millivolts: float) -> float:
    """Convert millivolts to volts."""

    return millivolts / 1000


def volts_to_millivolts(volts: float) -> float:
    """Convert volts to millivolts."""

    return volts * 1000