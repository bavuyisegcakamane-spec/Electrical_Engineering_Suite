#  ____      ___        __  ____   _______ _____ ____
# |  _ \\    / \\ \\      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \\ \\ /\\ / /  |  _ \\    | |    | | \\___ \\
# |  _ <  / ___ \\ V  V /   | |_) |   | |    | |  ___) |
# |_| \\_\\/_/   \\_\\_/\\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Manufacturer-page sourced SKU samples reviewed 2026-11-07.
These are reference records, not design approvals or proof of current local availability.
Commercial status may differ by region and date. Recheck manufacturer documents.
"""
from datetime import datetime, timezone

SOURCE_REVIEW_DATE = '2026-11-07T00:00:00+00:00'
PRODUCTS = (
    ('Schneider Electric', "A9F74116", "Miniature circuit breaker (MCB)", "Acti9 iC60N; 1P C-curve 16 A. Manufacturer UAE page reports discontinued Nov 2020.",
     "https://www.se.com/ae/en/product/A9F74116/miniature-circuit-breaker-mcb-acti9-ic60n-1p-16a-c-curve-6000a-iec-en-608981-10ka-iec-en-609472/", {"rated_current_a":16,"poles":1,"trip_curve":"C","breaking_capacity_iec60898_ka":6,"breaking_capacity_iec60947_ka":10,"commercial_status":"discontinued (UAE, 2020-11-01)"}),
    ('Schneider Electric', "A9R11225", "Residual current device (RCD/RCCB)", "Acti9 iID; 2P 25 A type AC 30 mA. Manufacturer Indonesia page reports discontinued Sep 2025.",
     "https://www.se.com/id/en/product/A9R11225/residual-current-circuit-breaker-rccb-acti9-iid-2p-25a-ac-type-30ma/", {"rated_current_a":25,"poles":2,"residual_trip_ma":30,"rcd_type":"AC","commercial_status":"discontinued (Indonesia, 2025-09-23)"}),
    ('Schneider Electric', "LC1D09P7", "Contactor", "TeSys D contactor; 3P (3 NO), 9 A AC-3 at <=440 V, 230 V AC coil.",
     "https://www.se.com/za/en/product/LC1D09P7/tesys-d-contactor-3p3-no-ac3-440-v-9-a-230-vac-coil/", {"rated_current_ac3_a":9,"ac3_voltage_max_v":440,"coil_voltage_v":230,"coil_supply":"AC","poles":3,"main_contacts":"3 NO"}),
    ('Schneider Electric', "LRD08", "Overload relay", "TeSys LRD thermal overload relay; adjustable 2.5 to 4 A, trip class 10A.",
     "https://www.se.com/za/en/product/LRD08/tesys-lrd-thermal-overload-relays-2-5-4-a-class-10a/", {"adjustment_min_a":2.5,"adjustment_max_a":4,"trip_class":"10A"}),
    ('Schneider Electric', "RXM2AB2P7", "Control relay", "Harmony miniature plug-in relay; 2 changeover contacts, 12 A, 230 V AC coil, LED.",
     "https://www.se.com/za/en/product/RXM2AB2P7/harmony-miniature-plugin-relay-12-a-2-co-with-led-with-lockable-test-button-230-v-ac/", {"thermal_current_a":12,"coil_voltage_v":230,"coil_supply":"AC","contacts":"2 CO","led":True}),
)


def seed_manufacturer_products(catalog):
    """Idempotently insert reviewed model-specific manufacturer references."""
    for manufacturer, model, category, description, url, specs in PRODUCTS:
        catalog.add(manufacturer, model, category, description, url,
                    specifications=specs, source_type='manufacturer product page (reviewed)',
                    verified_utc=SOURCE_REVIEW_DATE)
    return len(PRODUCTS)
