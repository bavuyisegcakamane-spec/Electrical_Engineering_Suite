#  ____      ___        __  ____   _______ _____ ____
# |  _ \\    / \\ \\      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \\ \\ /\\ / /  |  _ \\    | |    | | \\___ \\
# |  _ <  / ___ \\ V  V /   | |_) |   | |    | |  ___) |
# |_| \\_\\/_/   \\_\\_/\\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

import tempfile
from pathlib import Path
from database.database import Database
from database.equipment_catalog import EquipmentCatalog
from database.manufacturer_products import PRODUCTS, seed_manufacturer_products
from database.component_taxonomy import ALL_COMPONENT_TYPES


def test_manufacturer_seed_is_source_referenced_and_idempotent():
    assert len(PRODUCTS) == 5
    assert all(row[2] in ALL_COMPONENT_TYPES for row in PRODUCTS)
    with tempfile.TemporaryDirectory() as directory:
        db = Database(Path(directory) / 'models.db')
        db.initialize()
        try:
            catalog = EquipmentCatalog(db)
            assert seed_manufacturer_products(catalog) == 5
            assert seed_manufacturer_products(catalog) == 5
            rows = [r for r in catalog.search() if r['model'] in {p[1] for p in PRODUCTS}]
            assert len(rows) == 5
            assert all(r['verified_utc'] and r['source_url'].startswith('https://www.se.com/') for r in rows)
            assert next(r for r in rows if r['model'] == 'LRD08')['specifications']['adjustment_max_a'] == 4
            assert 'discontinued' in next(r for r in rows if r['model'] == 'A9F74116')['specifications']['commercial_status']
        finally:
            db.close()
