#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Electrical engineering calculation package."""

from .ohms_law import (
    calculate_voltage,
    calculate_current,
    calculate_resistance,
)

from .power import (
    calculate_power_vi,
    calculate_power_ir,
    calculate_power_vr,
    calculate_energy,
)

from .units import (
    watts_to_kilowatts,
    kilowatts_to_watts,
    watt_hours_to_kilowatt_hours,
    kilowatt_hours_to_watt_hours,
    milliamps_to_amps,
    amps_to_milliamps,
    millivolts_to_volts,
    volts_to_millivolts,
)