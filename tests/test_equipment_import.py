#  ____      ___        __  ____   _______ _____ ____
# |  _ \\    / \\ \\      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \\ \\ /\\ / /  |  _ \\    | |    | | \\___ \\
# |  _ <  / ___ \\ V  V /   | |_) |   | |    | |  ___) |
# |_| \\_\\/_/   \\_\\_/\\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

import csv
import io
import tempfile
from pathlib import Path
import pytest
from database.database import Database
from database.equipment_catalog import EquipmentCatalog
from database.equipment_import import COLUMNS, import_equipment_csv


def csv_data(*rows):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=COLUMNS)
    writer.writeheader()
    for row in rows:
        writer.writerow(dict(zip(COLUMNS,row)))
    return output.getvalue()


def test_import_and_reimport():
    with tempfile.TemporaryDirectory() as directory:
        db = Database(Path(directory)/'test.db')
        db.initialize()
        try:
            catalog = EquipmentCatalog(db)
            data = csv_data(('Test Manufacturer','MODEL-X','MCB','Fictional device','https://example.org/datasheet',
                             'manufacturer datasheet','2026-11-07T12:00:00+00:00','{"rated_current_a":16}'))
            assert import_equipment_csv(catalog,data) == 1
            assert import_equipment_csv(catalog,data) == 1
            rows = catalog.search('MODEL-X')
            assert len(rows) == 1
            assert rows[0]['specifications']['rated_current_a'] == 16
            assert rows[0]['verified_utc'] == '2026-11-07T12:00:00+00:00'
        finally:
            db.close()


def test_invalid_row_rejected_before_writes():
    with tempfile.TemporaryDirectory() as directory:
        db = Database(Path(directory)/'test.db')
        db.initialize()
        try:
            catalog = EquipmentCatalog(db)
            good = ('Example','M1','Fuse','Fictional','https://example.org/m1','datasheet','2026-11-07T12:00:00Z','{}')
            bad = ('Example','M2','Fuse','Fictional','http://example.org/m2','datasheet','2026-11-07T12:00:00Z','{}')
            with pytest.raises(ValueError):
                import_equipment_csv(catalog,csv_data(good,bad))
            assert catalog.search() == []
        finally:
            db.close()
