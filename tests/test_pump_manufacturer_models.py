#  ____      ___        __  ____   _______ _____ ____
# |  _ \\    / \\ \\      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \\ \\ /\\ / /  |  _ \\    | |    | | \\___ \\
# |  _ <  / ___ \\ V  V /   | |_) |   |    | |  ___) |
# |_| \\_\\/_/   \\_\\_/\\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

import tempfile
from pathlib import Path
from calculations.pump_panel import Pump
from database.database import Database
from database.equipment_catalog import EquipmentCatalog
from database.pump_panel_database import PumpPanelDatabase
from database.pump_manufacturer_models import PRODUCTS,seed_pump_manufacturer_models


def test_manufacturer_models_can_link_to_unverified_bom():
    with tempfile.TemporaryDirectory() as folder:
        db=Database(Path(folder)/'test.db'); db.initialize()
        try:
            catalog=EquipmentCatalog(db)
            assert seed_pump_manufacturer_models(catalog)==4
            assert seed_pump_manufacturer_models(catalog)==4
            assert len([x for x in catalog.search() if x['model'] in {r[1] for r in PRODUCTS}])==4
            repo=PumpPanelDatabase(db)
            panel=repo.create_panel('Test',[Pump(2.2,'VFD')])
            bom=repo.get_bom(panel)
            item=next(x for x in bom if 'Variable frequency drive' in x['component'])
            model=next(x for x in catalog.search() if x['model']=='ATV320U22N4C')
            repo.assign_catalog_model(item['bom_id'],model['id'],'Check OEM output current and motor nameplate')
            updated=next(x for x in repo.get_bom(panel) if x['bom_id']==item['bom_id'])
            assert updated['selected_catalog_id']==model['id']
            assert updated['verification_status']=='unverified'
        finally:
            db.close()
