"""Educational transformer and motor performance estimates (not design approvals)."""
import math


def _check(**values):
    for key, value in values.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError(f"{key} must be a finite nonnegative number")


def transformer_performance(rated_kva, load_fraction, power_factor, core_loss_w,
                            full_load_copper_loss_w, no_load_secondary_v, full_load_secondary_v):
    """Constant core loss, copper loss proportional to load squared; approximate regulation."""
    _check(rated_kva=rated_kva, load_fraction=load_fraction, power_factor=power_factor,
           core_loss_w=core_loss_w, full_load_copper_loss_w=full_load_copper_loss_w,
           no_load_secondary_v=no_load_secondary_v, full_load_secondary_v=full_load_secondary_v)
    if rated_kva == 0 or not 0 < power_factor <= 1 or full_load_secondary_v == 0 or no_load_secondary_v == 0:
        raise ValueError("Rated kVA, power factor and both secondary voltages must be positive; PF at most 1")
    output_w = rated_kva * 1000 * load_fraction * power_factor
    copper_w = full_load_copper_loss_w * load_fraction ** 2
    losses_w = core_loss_w + copper_w
    efficiency = output_w / (output_w + losses_w) if output_w + losses_w else 0
    regulation = (no_load_secondary_v - full_load_secondary_v) / full_load_secondary_v * 100
    result = {"output_power_w": output_w, "copper_loss_w": copper_w,
              "total_losses_w": losses_w, "efficiency_percent": efficiency * 100,
              "full_load_voltage_regulation_percent": regulation}
    if not all(math.isfinite(v) for v in result.values()):
        raise ValueError("Calculated result exceeds numeric range")
    return result


def motor_starting_estimate(rated_current_a, starting_multiplier, starting_duration_s,
                            rated_speed_rpm, synchronous_speed_rpm):
    """User-specified starting-current multiplier; nominal slip from speeds."""
    _check(rated_current_a=rated_current_a, starting_multiplier=starting_multiplier,
           starting_duration_s=starting_duration_s, rated_speed_rpm=rated_speed_rpm,
           synchronous_speed_rpm=synchronous_speed_rpm)
    if min(rated_current_a, starting_multiplier, starting_duration_s, rated_speed_rpm, synchronous_speed_rpm) <= 0:
        raise ValueError("All values must be positive")
    if rated_speed_rpm >= synchronous_speed_rpm:
        raise ValueError("Rated speed must be below synchronous speed for induction-motor slip")
    starting_current = rated_current_a * starting_multiplier
    result = {"estimated_starting_current_a": starting_current,
              "starting_i_squared_t_a2s": starting_current ** 2 * starting_duration_s,
              "rated_slip_percent": (synchronous_speed_rpm - rated_speed_rpm) / synchronous_speed_rpm * 100}
    if not all(math.isfinite(v) for v in result.values()):
        raise ValueError("Calculated result exceeds numeric range")
    return result
