#  ____      ___        __  ____   _______ _____ ____
# |  _ \\    / \\ \\      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \\ \\ /\\ / /  |  _ \\    | |    | | \\___ \\
# |  _ <  / ___ \\ V  V /   | |_) |   |    | |  ___) |
# |_| \\_\\/_/   \\_\\_/\\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Conceptual pump-panel BOM categories. No component sizing or approvals."""
COMMON = ('Main incoming isolator', 'Main circuit breaker', 'Busbar / power distribution',
          'Surge protective device (SPD)', 'Control power supply / transformer',
          'Emergency stop / safety circuit', 'Control MCB / fuse', 'Earth bar and bonding',
          'Terminal blocks and cable glands', 'Enclosure / ventilation',
          'Pump dry-run / level / pressure protection', 'Run / fault indication',
          'Overload / short-circuit coordination review', 'Interlocking / control logic',
          'Motor cables and earthing', 'Panel short-circuit withstand review')
BY_STARTER = {
    'DOL': ('Motor branch protection', 'AC-3 motor contactor', 'Thermal / electronic overload relay'),
    'Star-delta': ('Motor branch protection', 'Line / star / delta contactors',
                   'Star-delta timer and electrical/mechanical interlocks',
                   'Motor overload protection', 'Six-lead motor wiring / terminal verification'),
    'Soft starter': ('Motor branch protection', 'Soft starter rated for duty',
                     'Bypass contactor if required by manufacturer',
                     'Motor thermal / electronic overload protection'),
    'VFD': ('Drive-compatible upstream protection', 'Variable frequency drive sized for pump duty',
            'Drive EMC / line reactor / output filter assessment',
            'Motor thermal protection / drive fault interface',
            'Motor cable screening and grounding review'),
}


def conceptual_bom(starters):
    starters = tuple(starters)
    if not 1 <= len(starters) <= 4 or any(x not in BY_STARTER for x in starters):
        raise ValueError('Select 1 to 4 supported starters')
    return {'common': COMMON, 'per_pump': tuple({'pump':i + 1, 'starter':s,
            'components':BY_STARTER[s]} for i,s in enumerate(starters))}
