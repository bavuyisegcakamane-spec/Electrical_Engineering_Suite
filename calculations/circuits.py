#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Equivalent resistance for ideal DC resistor networks."""
import math


def _validate_resistances(resistances):
    values = tuple(resistances)
    if not values:
        raise ValueError("Enter at least one resistance.")
    for resistance in values:
        if isinstance(resistance, bool) or not isinstance(resistance, (int, float)):
            raise ValueError("Resistances must be numeric.")
        if not math.isfinite(resistance) or resistance < 0:
            raise ValueError("Resistances must be finite and non-negative.")
    return values


def series_resistance(resistances):
    """Return sum of resistances in ohms."""
    values = _validate_resistances(resistances)
    result = math.fsum(values)
    if not math.isfinite(result):
        raise ValueError("Equivalent resistance exceeds numeric range.")
    return result


def parallel_resistance(resistances):
    """Return equivalent resistance; a zero-ohm branch shorts the network."""
    values = _validate_resistances(resistances)
    if 0 in values:
        return 0.0
    # Normalize by the smallest resistance to avoid overflow in reciprocal sums.
    smallest = min(values)
    return smallest / math.fsum(smallest / value for value in values)
