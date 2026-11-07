#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Input validation utilities."""


def require_number(value, field_name="Value") -> float:
    """Convert a value to a number."""

    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"{field_name} must be a valid number."
        )

    return number


def require_positive(value, field_name="Value") -> float:
    """Require a number greater than zero."""

    number = require_number(value, field_name)

    if number <= 0:
        raise ValueError(
            f"{field_name} must be greater than zero."
        )

    return number


def require_non_negative(
    value,
    field_name="Value",
) -> float:
    """Require a number greater than or equal to zero."""

    number = require_number(value, field_name)

    if number < 0:
        raise ValueError(
            f"{field_name} cannot be negative."
        )

    return number