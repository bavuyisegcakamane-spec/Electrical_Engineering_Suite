"""Verified limited lookups from SANS 10142-1:2017 Edition 2.

Only explicitly transcribed rows. No interpolation, extrapolation, or compliance verdict.
"""
import math

SOIL_TEMPERATURE_70C = {10: 1.15, 15: 1.11, 20: 1.05, 25: 1.00, 30: .94, 35: .88, 40: .82}  # Table 6.11
BURIAL_DEPTH = {  # Table 6.16: (direct buried, in buried pipes)
    .5: (1., 1.), .6: (.98, .99), .8: (.96, .98),
    1.: (.94, .96), 1.25: (.92, .95), 1.5: (.90, .94),
}
# Table 6.8, multicore PVC copper armoured cables, soil 25 C, max conductor 70 C.
# Values: direct buried 2-core, direct buried 3/4-core, pipe 2-core, pipe 3/4-core.
BURIED_PVC_COPPER_AMPACITY = {
    1.5: (29, 24, 23, 20), 2.5: (37, 32, 31, 26),
    4.: (50, 42, 41, 34), 6.: (62, 53, 51, 43),
    10.: (83, 70, 68, 58), 16.: (107, 91, 88, 75),
    25.: (142, 119, 116, 96), 35.: (171, 143, 139, 116),
    50.: (203, 169, 165, 138), 70.: (249, 210, 203, 171),
}


def buried_cable_lookup(area_mm2, cores, installation, soil_temperature_c, burial_depth_m):
    """Only Table 6.8 copper PVC armoured, Table 6.11 and Table 6.16 subset.

    Grouping, soil resistivity, harmonics and all other factors are NOT included.
    """
    if not all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)
               for x in (area_mm2, soil_temperature_c, burial_depth_m)):
        raise ValueError('Inputs must be finite numeric values')
    if cores not in (2, 3, 4) or installation not in ('direct', 'pipe'):
        raise ValueError('Supported: 2, 3 or 4 cores; direct burial or buried pipe')
    if area_mm2 not in BURIED_PVC_COPPER_AMPACITY:
        raise ValueError('Conductor size not present in verified Table 6.8 subset')
    if soil_temperature_c not in SOIL_TEMPERATURE_70C or burial_depth_m not in BURIAL_DEPTH:
        raise ValueError('Select an exact listed soil temperature and burial depth; no interpolation')
    column = (0 if cores == 2 else 1) + (0 if installation == 'direct' else 2)
    base = BURIED_PVC_COPPER_AMPACITY[area_mm2][column]
    temperature_factor = SOIL_TEMPERATURE_70C[soil_temperature_c]
    depth_factor = BURIAL_DEPTH[burial_depth_m][0 if installation == 'direct' else 1]
    adjusted = base * temperature_factor * depth_factor
    return {'reference': 'SANS 10142-1:2017 Ed 2 Tables 6.8, 6.11, 6.16',
            'tabulated_ampacity_a': base, 'soil_temperature_factor': temperature_factor,
            'burial_depth_factor': depth_factor, 'partially_corrected_ampacity_a': adjusted,
            'compliance_status': 'NOT DETERMINED',
            'missing_factors': 'Soil resistivity (6.12), grouping (6.13), other applicable conditions, voltage drop, protection and earth fault studies'}
