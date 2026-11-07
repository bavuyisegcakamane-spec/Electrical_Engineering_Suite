#  ____      ___        __  ____   _______ _____ ____
# |  _ \\    / \\ \\      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \\ \\ /\\ / /  |  _ \\    | |    | | \\___ \\
# |  _ <  / ___ \\ V  V /   | |_) |   | |    | |  ___) |
# |_| \\_\\/_/   \\_\\_/\\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Component type taxonomy, not a catalogue of verified manufacturer SKUs."""

COMPONENT_GROUPS = {
  'Protection': (
    'Miniature circuit breaker (MCB)',
    'Moulded-case circuit breaker (MCCB)',
    'Air circuit breaker (ACB)',
    'Residual current device (RCD/RCCB)',
    'Residual current breaker with overcurrent (RCBO)',
    'Earth leakage relay',
    'Fuse',
    'Fuse holder',
    'Surge protective device (SPD)',
    'Motor protection circuit breaker (MPCB)',
    'Overload relay',
    'Under/overvoltage relay',
    'Arc fault detection device (AFDD)'
  ),
  'Switching and control': (
    'Contactor',
    'Auxiliary contact block',
    'Control relay',
    'Time delay relay',
    'Solid state relay',
    'Latching relay',
    'Interposing relay',
    'Safety relay',
    'Motor starter',
    'Soft starter',
    'Variable frequency drive (VFD)',
    'Isolator/disconnector',
    'Changeover switch',
    'Automatic transfer switch (ATS)',
    'Pushbutton',
    'Selector switch',
    'Limit switch',
    'Emergency stop switch'
  ),
  'Power distribution': (
    'Distribution board',
    'Panelboard',
    'Busbar',
    'Busbar trunking',
    'Terminal block',
    'Power connector',
    'Cable gland',
    'DIN rail',
    'Enclosure',
    'Junction box',
    'Circuit monitoring meter',
    'Current transformer (CT)',
    'Voltage transformer (VT/PT)'
  ),
  'Cables and wiring': (
    'Copper power cable',
    'Aluminium power cable',
    'Control cable',
    'Instrumentation cable',
    'Flexible cord',
    'Cable lug',
    'Cable ferrule',
    'Cable tray',
    'Cable ladder',
    'Conduit',
    'Cable trunking',
    'Cable cleat',
    'Heat shrink tubing'
  ),
  'Machines and energy': (
    'Single phase motor',
    'Three phase motor',
    'Transformer',
    'Generator',
    'UPS',
    'Inverter',
    'Battery',
    'Battery management system (BMS)',
    'Solar PV module',
    'Solar charge controller',
    'EV charger',
    'Capacitor bank',
    'Power factor controller'
  ),
  'Sensing and automation': (
    'PLC',
    'HMI',
    'Temperature sensor',
    'Pressure sensor',
    'Proximity sensor',
    'Photoelectric sensor',
    'Encoder',
    'Thermocouple',
    'RTD',
    'Transducer',
    'Signal isolator',
    'Industrial gateway',
    'Ethernet switch',
    'Power supply (AC/DC)'
  ),
  'Earthing and safety': (
    'Earth electrode',
    'Earth bar',
    'Protective bonding conductor',
    'Earth clamp',
    'Insulation monitoring device',
    'Earth fault indicator',
    'Insulation tester',
    'Earth loop tester',
    'Multimeter',
    'Clamp meter'
  )
}

ALL_COMPONENT_TYPES = tuple(name for names in COMPONENT_GROUPS.values() for name in names)

SPECIFICATION_FIELDS = {
    'Protection': ('rated_voltage_v', 'rated_current_a', 'breaking_capacity_ka', 'poles', 'trip_curve', 'ac_dc_rating', 'standard'),
    'Switching and control': ('rated_voltage_v', 'rated_current_a', 'coil_voltage_v', 'contact_configuration', 'utilization_category', 'standard'),
    'Power distribution': ('rated_voltage_v', 'rated_current_a', 'short_circuit_rating_ka', 'ip_rating', 'standard'),
    'Cables and wiring': ('conductor_material', 'cross_section_mm2', 'cores', 'insulation', 'voltage_grade_v', 'standard'),
    'Machines and energy': ('rated_power_kw', 'rated_voltage_v', 'rated_current_a', 'frequency_hz', 'efficiency_percent', 'standard'),
    'Sensing and automation': ('supply_voltage_v', 'signal_type', 'output_type', 'ip_rating', 'standard'),
    'Earthing and safety': ('rated_voltage_v', 'measurement_range', 'accuracy', 'standard'),
}

def group_for(component_type):
    for group, names in COMPONENT_GROUPS.items():
        if component_type in names:
            return group
    return None
