"""Analysis of an ideal DC circuit: R1 in series with (R2 parallel R3)."""
import math
from calculations.circuits import series_resistance, parallel_resistance


def analyze_mixed(voltage, r1, r2, r3):
    """Return resistance, source current, and individual branch voltage/current.

    A zero-ohm parallel branch is supported, but a fully shorted supply is rejected.
    """
    values = (voltage, r1, r2, r3)
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError("All inputs must be finite numbers.")
    if voltage < 0:
        raise ValueError("Supply voltage cannot be negative.")
    if r2 == 0 and r3 == 0:
        raise ValueError("Two ideal shorted parallel branches have indeterminate current sharing.")
    parallel = parallel_resistance([r2, r3])
    total = series_resistance([r1, parallel])
    if total == 0:
        raise ValueError("Circuit has zero equivalent resistance (ideal short circuit).")
    source_current = voltage / total
    parallel_voltage = source_current * parallel
    branch2 = parallel_voltage / r2 if r2 else (source_current if r3 else 0.0)
    branch3 = parallel_voltage / r3 if r3 else (source_current if r2 else 0.0)
    if not all(math.isfinite(v) for v in (source_current, parallel_voltage, branch2, branch3)):
        raise ValueError("Result exceeds supported numeric range.")
    return {
        "equivalent_resistance": total,
        "source_current": source_current,
        "r1_voltage": source_current * r1,
        "parallel_voltage": parallel_voltage,
        "r2_current": branch2,
        "r3_current": branch3,
    }
