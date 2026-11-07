"""Basic balanced AC load and energy estimates; not a cable/protection design tool."""
import math


def calculate_load(power_watts, quantity, voltage, power_factor=1.0, hours=1.0, phases=1, demand_factor=1.0):
    """Calculate connected/demand load, line current and energy for one load group.

    Power is real input power per item in watts. Voltage is line-to-neutral for
    single phase and line-to-line for balanced three phase. Demand factor scales
    the simultaneous real power; energy assumes the demand load is sustained.
    """
    inputs = (power_watts, voltage, power_factor, hours, demand_factor)
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in inputs):
        raise ValueError("Inputs must be finite numbers.")
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
        raise ValueError("Quantity must be a positive whole number.")
    if phases not in (1, 3) or isinstance(phases, bool):
        raise ValueError("Phases must be 1 or 3.")
    if power_watts < 0 or voltage <= 0 or hours < 0:
        raise ValueError("Power and hours must be non-negative; voltage must be positive.")
    if not 0 < power_factor <= 1 or not 0 <= demand_factor <= 1:
        raise ValueError("Power factor must be (0, 1]; demand factor must be [0, 1].")
    connected = power_watts * quantity
    demand = connected * demand_factor
    current = demand / (voltage * power_factor * (math.sqrt(3) if phases == 3 else 1))
    energy = demand * hours / 1000
    if not all(math.isfinite(v) for v in (connected, demand, current, energy)):
        raise ValueError("Result exceeds supported numeric range.")
    return {"connected_watts": connected, "demand_watts": demand,
            "line_current_amps": current, "energy_kwh": energy}
