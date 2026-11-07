#  ____      ___        __  ____   _______ _____ ____
# |  _ \\    / \\ \\      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \\ \\ /\\ / /  |  _ \\    | |    | | \\___ \\
# |  _ <  / ___ \\ V  V /   | |_) |   | |    | |  ___) |
# |_| \\_\\/_/   \\_\\_/\\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Preliminary three-phase pump panel load study; NOT protection or cable design."""
from dataclasses import dataclass
from math import sqrt, isfinite

STARTERS = ('DOL', 'Star-delta', 'Soft starter', 'VFD')
PUMP_KW = (2.2, 3, 4, 5.5, 7.5, 11, 15, 18.5, 22, 30, 37, 45)

@dataclass(frozen=True)
class Pump:
    power_kw: float
    starter: str = 'DOL'
    name: str = 'Pump'


def _positive(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value <= 0:
        raise ValueError(f'{label} must be a positive finite number')


def study_panel(pumps, voltage_v=400, power_factor=0.85, efficiency=0.90,
                main_breaker_a=150, simultaneous=None):
    """Calculate input FLC estimates and simultaneous running load.

    Uses a single user-supplied PF/efficiency for all motors. Starter selection
    does NOT change running motor current. No starting-current estimate is made.
    """
    pumps = tuple(pumps)
    if not 1 <= len(pumps) <= 4:
        raise ValueError('Provide 1 to 4 pumps')
    for label, value in (('voltage', voltage_v), ('power factor', power_factor),
                         ('efficiency', efficiency), ('main breaker', main_breaker_a)):
        _positive(value, label)
    if not 0 < power_factor <= 1 or not 0 < efficiency <= 1:
        raise ValueError('Power factor and efficiency must be <= 1')
    if simultaneous is None:
        simultaneous = len(pumps)
    if isinstance(simultaneous, bool) or not isinstance(simultaneous, int) or not 1 <= simultaneous <= len(pumps):
        raise ValueError('Simultaneous pump count must be between 1 and installed pump count')
    records = []
    for pump in pumps:
        if not isinstance(pump, Pump) or pump.starter not in STARTERS:
            raise ValueError('Invalid pump or starting method')
        _positive(pump.power_kw, 'motor power')
        if not 2.2 <= pump.power_kw <= 45:
            raise ValueError('Motor power must be between 2.2 and 45 kW')
        current = pump.power_kw * 1000 / (sqrt(3) * voltage_v * power_factor * efficiency)
        records.append({'name':pump.name, 'power_kw':pump.power_kw,
                        'starter':pump.starter, 'estimated_running_a':round(current, 2)})
    # Conservative worst-case simultaneous subset: largest running currents.
    selected = sorted(records, key=lambda row:row['estimated_running_a'], reverse=True)[:simultaneous]
    running_a = sum(pump['power_kw'] * 1000 / (sqrt(3) * voltage_v * power_factor * efficiency)
                    for pump in selected)
    installed_a = sum(pump['power_kw'] * 1000 / (sqrt(3) * voltage_v * power_factor * efficiency)
                      for pump in records)
    warnings = ['PRELIMINARY ONLY: use motor nameplate FLA, manufacturer starter data, site fault level and qualified electrical design before equipment selection.',
                'Starting/inrush current, breaker trip curves, protection coordination, cable derating, voltage drop and thermal limits are NOT assessed.',
                'Star-delta requires a suitable six-terminal motor and correct delta run voltage; VFD and soft-starter sizing require manufacturer data.']
    if running_a > main_breaker_a:
        warnings.append('Estimated simultaneous running current EXCEEDS the main breaker rating; this arrangement is not suitable as entered.')
    else:
        warnings.append('Estimated running current is below the main breaker rating; this does NOT establish breaker suitability or safe operation.')
    return {'pumps':records, 'voltage_v':voltage_v, 'power_factor':power_factor,
            'efficiency':efficiency, 'simultaneous':simultaneous,
            'installed_running_a':round(installed_a, 2),
            'simultaneous_running_a':round(running_a, 2),
            'main_breaker_a':main_breaker_a,
            'estimated_utilization_percent':round(100 * running_a / main_breaker_a, 1),
            'exceeds_main_rating':running_a > main_breaker_a, 'warnings':warnings}
