#  ____      ___        __  ____   _______ _____ ____
# |  _ \\    / \\ \\      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \\ \\ /\\ / /  |  _ \\    | |    | | \\___ \\
# |  _ <  / ___ \\ V  V /   | |_) |   | |    | |  ___) |
# |_| \\_\\/_/   \\_\\_/\\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Manufacturer-sourced starter equipment references reviewed 2026-11-07.
Reference entries are NOT automatically approved for any panel or motor.
Review full OEM datasheet, short circuit coordination, current and site duty.
"""
SOURCE_REVIEW_DATE = '2026-11-07T00:00:00+00:00'
PRODUCTS = (
    ('Schneider Electric', "ATV320U22N4C", "Variable frequency drive (VFD)", "Altivar Machine ATV320, 2.2 kW heavy-duty drive, 380–500 V three-phase.",
     "https://www.se.com/za/en/product/ATV320U22N4C/variable-speed-drive-altivar-machine-atv320-2-2-kw-380-500-v-3-phases-compact/", {"rated_motor_power_kw":2.2,"supply_min_v":380,"supply_max_v":500,"phases":3,"continuous_output_a":5.5}),
    ('Schneider Electric', "ATV320D22N4C", "Variable frequency drive (VFD)", "Altivar Machine ATV320, 22 kW 400 V three-phase drive.",
     "https://www.se.com/za/en/product/ATV320D22N4C/variable-speed-drive-altivar-machine-atv320-22kw-400v-3-phases-compact/", {"rated_motor_power_kw":22,"supply_nominal_v":400,"phases":3}),
    ('Schneider Electric', "ATS22D17Q", "Soft starter", "Altistart 22, 7.5 kW at 400 V, 17 A starter rating. Manufacturer US page indicates discontinuation scheduled March 2027.",
     "https://www.se.com/us/en/product/ATS22D17Q/soft-starter-for-asynchronous-motor-altistart-22-control-230v-230-to-440v-4-to-7-5kw/", {"rated_motor_power_kw_at_400v":7.5,"starter_rating_a":17,"commercial_status":"US: scheduled end of commercialization 2027-03-31"}),
    ('Schneider Electric', "GV2ME14", "Motor protection circuit breaker (MPCB)", "TeSys GV2 three-pole thermal-magnetic motor breaker, adjustable 6–10 A.",
     "https://www.se.com/za/en/product/GV2ME14/motor-circuit-breaker-tesys-gv2-3p-610-a-thermal-magnetic-screw-clamp-terminals/", {"poles":3,"adjustment_min_a":6,"adjustment_max_a":10}),
)


def seed_pump_manufacturer_models(catalog):
    for manufacturer,model,category,description,url,specs in PRODUCTS:
        catalog.add(manufacturer,model,category,description,url,specifications=specs,
                    source_type='manufacturer product page (reviewed)',
                    verified_utc=SOURCE_REVIEW_DATE)
    return len(PRODUCTS)
