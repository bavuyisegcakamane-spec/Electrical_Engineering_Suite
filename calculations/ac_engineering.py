"""Deterministic educational AC circuit calculations, SI units."""
import math


def _positive(**values):
    for name, value in values.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be a finite positive number")


def ac_impedance(resistance_ohms, inductance_h, capacitance_f, frequency_hz):
    """Series RLC circuit: impedance magnitude, phase and power factor."""
    _positive(resistance_ohms=resistance_ohms, inductance_h=inductance_h,
              capacitance_f=capacitance_f, frequency_hz=frequency_hz)
    xl = 2 * math.pi * frequency_hz * inductance_h
    xc = 1 / (2 * math.pi * frequency_hz * capacitance_f)
    reactance = xl - xc
    magnitude = math.hypot(resistance_ohms, reactance)
    results = {"inductive_reactance_ohms": xl, "capacitive_reactance_ohms": xc,
               "net_reactance_ohms": reactance, "impedance_ohms": magnitude,
               "phase_angle_degrees": math.degrees(math.atan2(reactance, resistance_ohms)),
               "power_factor": resistance_ohms / magnitude}
    if not all(math.isfinite(v) for v in results.values()):
        raise ValueError("Calculated result exceeds numeric range")
    return results


def three_phase_power(voltage_line_v, current_line_a, power_factor):
    """Balanced sinusoidal three-phase load: P, Q and S."""
    _positive(voltage_line_v=voltage_line_v, current_line_a=current_line_a,
              power_factor=power_factor)
    if power_factor > 1:
        raise ValueError("Power factor must be at most 1")
    apparent = math.sqrt(3) * voltage_line_v * current_line_a
    real = apparent * power_factor
    reactive = apparent * math.sqrt(max(0.0, 1 - power_factor ** 2))
    if not all(math.isfinite(v) for v in (apparent, real, reactive)):
        raise ValueError("Calculated result exceeds numeric range")
    return {"apparent_power_va": apparent, "real_power_w": real,
            "reactive_power_var_magnitude": reactive}


def insulation_resistance(measured_voltage_v, leakage_current_microamps):
    """Ohmic estimate from a measured DC test voltage and leakage current.

    Does not determine pass/fail; test procedures and thresholds vary by standard.
    """
    _positive(measured_voltage_v=measured_voltage_v,
              leakage_current_microamps=leakage_current_microamps)
    megohms = measured_voltage_v / leakage_current_microamps
    if not math.isfinite(megohms):
        raise ValueError("Calculated result exceeds numeric range")
    return {"insulation_resistance_megohms": megohms}
