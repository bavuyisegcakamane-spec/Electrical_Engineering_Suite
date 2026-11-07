#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Partial checks grounded in SANS 10142-1:2017 Edition 2.

Not a conformity assessment. Cable ratings and correction factors are user
supplied and must be selected from the applicable source tables or manufacturer.
"""
import math
from calculations.installation_assessment import validate_installation_voltage

REFERENCE = 'SANS 10142-1:2017 Edition 2'


def _positive(**values):
    for name, value in values.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f'{name} must be a finite positive number')


def assess_cable_and_protection(supply_voltage_v, design_current_a, tabulated_ampacity_a,
                                ambient_factor, grouping_factor, other_factor,
                                total_voltage_drop_v, protective_device_rating_a,
                                device_breaking_capacity_ka, prospective_short_circuit_ka,
                                supply_type='AC'):
    """Check selected numerical criteria only; never return a compliance verdict.

    Reference: 6.2.5.1, 6.2.5.2, 6.2.7.1.1/1.2 and 6.7.1.1.
    For DC the 5% check is a screening criterion: manufacturer requirements
    may govern instead. The AC voltage drop is supplied for the WHOLE run.
    """
    _positive(supply_voltage_v=supply_voltage_v, design_current_a=design_current_a,
              tabulated_ampacity_a=tabulated_ampacity_a, ambient_factor=ambient_factor,
              grouping_factor=grouping_factor, other_factor=other_factor,
              total_voltage_drop_v=total_voltage_drop_v,
              protective_device_rating_a=protective_device_rating_a,
              device_breaking_capacity_ka=device_breaking_capacity_ka,
              prospective_short_circuit_ka=prospective_short_circuit_ka)
    validate_installation_voltage(supply_voltage_v, supply_type)
    if any(f > 1 for f in (ambient_factor, grouping_factor, other_factor)):
        raise ValueError('This screening accepts correction factors in (0, 1]; verify other factors separately')
    effective_ampacity = tabulated_ampacity_a * ambient_factor * grouping_factor * other_factor
    drop_percent = total_voltage_drop_v / supply_voltage_v * 100
    values = (effective_ampacity, drop_percent)
    if not all(math.isfinite(v) for v in values):
        raise ValueError('Calculated result exceeds numeric range')
    checks = {
        'design_current_within_corrected_ampacity': design_current_a <= effective_ampacity,
        'protective_rating_within_corrected_ampacity': protective_device_rating_a <= effective_ampacity,
        'voltage_drop_within_5_percent': drop_percent <= 5,
        'breaking_capacity_at_least_2_5_ka': device_breaking_capacity_ka >= 2.5,
        'breaking_capacity_at_least_prospective_fault_ka': device_breaking_capacity_ka >= prospective_short_circuit_ka,
    }
    return {
        'reference': REFERENCE,
        'effective_ampacity_a': effective_ampacity,
        'voltage_drop_percent': drop_percent,
        'checks': checks,
        'all_screening_checks_pass': all(checks.values()),
        'compliance_status': 'NOT DETERMINED - incomplete checks, table and installation verification required',
        'required_verification': [
            'Installation method and cable construction: Table 6.1 and Tables 6.2(a)-6.9(b)',
            'Applicable factors: Tables 6.10-6.19, including burial, neutral, harmonics and solar exposure',
            'Full AC or DC voltage-drop path and equipment manufacturer requirements',
            'Device time-current curves, fault withstand, earthing arrangement and disconnection time',
            'Edition applicability and inspection/testing by an authorized competent person',
        ],
    }
