"""Clause-referenced limited SANS 10142-1:2017 Ed 2 engineering checks.

Exact tabulated values only; no automatic compliance certification.
"""
import math
from calculations.sans_reference_tables import buried_cable_lookup
from calculations.installation_assessment import validate_installation_voltage

AIR_PVC_70C = {10:1.22,15:1.17,20:1.12,25:1.06,30:1.,35:.94,40:.87,45:.79,50:.71,55:.61,60:.50,65:.35}  # 6.10
SOIL_RESISTIVITY = {  # 6.12: direct, pipe
    .7:(1.17,1.07),.8:(1.13,1.05),.9:(1.09,1.04),1.:(1.06,1.02),
    1.2:(1.,1.),1.5:(.93,.96),2.:(.83,.91),2.5:(.76,.87),
    3.:(.71,.83),3.5:(.65,.80),4.:(.61,.77),
}
# Table 6.13 horizontal grouping, exact transcribed subset: touching or 300 mm.
GROUPING = {
    'direct': {2:(.81,.91),3:(.70,.84),4:(.63,.81),5:(.59,.78),6:(.55,.76),
               7:(.52,.75),8:(.50,.74),9:(.48,.74),10:(.47,.73),11:(.45,.72),12:(.44,.72)},
    'pipe': {2:(.90,.93),3:(.82,.87),4:(.78,.85),5:(.75,.82),6:(.72,.81),
             7:(.70,.80),8:(.69,.79),9:(.68,.78),10:(.67,.78),11:(.66,.77),12:(.65,.77)},
}


def buried_cable_extended(area_mm2, cores, installation, soil_temp_c, depth_m,
                          soil_resistivity_km_w, grouped_cables, spacing_mm):
    base = buried_cable_lookup(area_mm2, cores, installation, soil_temp_c, depth_m)
    if soil_resistivity_km_w not in SOIL_RESISTIVITY:
        raise ValueError('Soil resistivity must be an exact Table 6.12 value')
    if isinstance(grouped_cables, bool) or not isinstance(grouped_cables, int) or grouped_cables not in range(1,13):
        raise ValueError('Supported number of grouped cables: 1 to 12')
    if spacing_mm not in (0,300):
        raise ValueError('Only touching (0 mm) or 300 mm grouping spacing supported')
    resistivity = SOIL_RESISTIVITY[soil_resistivity_km_w][0 if installation == 'direct' else 1]
    grouping = 1. if grouped_cables == 1 else GROUPING[installation][grouped_cables][0 if spacing_mm == 0 else 1]
    corrected = base['partially_corrected_ampacity_a'] * resistivity * grouping
    return {**base, 'soil_resistivity_factor':resistivity, 'grouping_factor':grouping,
            'extended_corrected_ampacity_a':corrected,
            'reference':'SANS 10142-1:2017 Ed 2 Tables 6.8, 6.11, 6.12, 6.13, 6.16',
            'missing_factors':'Other installation conditions, harmonics, neutral, manufacturer data, voltage drop and protection',
            'compliance_status':'NOT DETERMINED'}


def protective_earthing_review(supply_type, voltage_v, design_current_a, corrected_ampacity_a,
                                device_rating_a, breaking_capacity_ka, prospective_fault_ka,
                                earth_loop_ohms, trip_current_a, device_trip_time_s,
                                required_disconnection_time_s, rcd_trip_ma=None, multiple_dc_sources=False):
    """Compare user-supplied manufacturer/test inputs, not inferred curves or Zs limits.

    AC earth-loop estimate uses idealized U/Z. DC loop/trip analysis is NOT supported.
    """
    numbers = (voltage_v,design_current_a,corrected_ampacity_a,device_rating_a,
               breaking_capacity_ka,prospective_fault_ka)
    if any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or x<=0 for x in numbers):
        raise ValueError('Ratings must be finite positive numbers')
    validate_installation_voltage(voltage_v,supply_type)
    checks = {'load_within_ampacity':design_current_a<=corrected_ampacity_a,
              'device_rating_within_ampacity':device_rating_a<=corrected_ampacity_a,
              'breaking_capacity_at_least_2_5_ka':breaking_capacity_ka>=2.5,
              'breaking_capacity_at_least_prospective_fault':breaking_capacity_ka>=prospective_fault_ka}
    if rcd_trip_ma is not None:
        if not isinstance(rcd_trip_ma,(int,float)) or isinstance(rcd_trip_ma,bool) or not math.isfinite(rcd_trip_ma) or rcd_trip_ma<=0:
            raise ValueError('RCD rating must be positive and finite')
        checks['rcd_rating_at_most_30_ma_for_30_ma_applications'] = rcd_trip_ma<=30
    if supply_type=='AC':
        extra=(earth_loop_ohms,trip_current_a,device_trip_time_s,required_disconnection_time_s)
        if any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or x<=0 for x in extra):
            raise ValueError('AC fault-loop and disconnection inputs must be finite positive numbers')
        estimated=voltage_v/earth_loop_ohms
        checks['idealized_fault_current_at_least_device_trip_threshold']=estimated>=trip_current_a
        checks['user_supplied_trip_time_within_user_supplied_limit']=device_trip_time_s<=required_disconnection_time_s
    else:
        estimated=None
    return {'reference':'SANS 10142-1:2017 Ed 2 clauses 5.2.3, 6.7.1, 6.11-6.13',
            'checks':checks,'idealized_ac_fault_current_a':estimated,
            'multiple_dc_sources_require_individual_protection':bool(supply_type=='DC' and multiple_dc_sources),
            'compliance_status':'NOT DETERMINED',
            'required_verification':'Actual earthing system and continuity, RCD application, verified device curve/time, fault-loop measurement, fault withstand, DC-rated protection and all source locations, authorized inspection'}
