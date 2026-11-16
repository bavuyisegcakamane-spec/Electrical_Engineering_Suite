import tempfile
from pathlib import Path
import pytest
from calculations.pump_panel import Pump
from database.database import Database
from database.equipment_catalog import EquipmentCatalog
from database.pump_panel_database import PumpPanelDatabase
from database.pump_manufacturer_models import seed_pump_manufacturer_models

def test_screening_rejects_wrong_model_and_undersized_drive():
    with tempfile.TemporaryDirectory() as folder:
        db = Database(Path(folder) / 'screen.db')
        db.initialize()
        try:
            catalog = EquipmentCatalog(db)
            seed_pump_manufacturer_models(catalog)
            repo = PumpPanelDatabase(db)
            panel = repo.create_panel('Test 22kW', [Pump(22, 'VFD')])
            item = next(x for x in repo.get_bom(panel) if 'Variable frequency drive' in x['component'])
            products = {x['model']: x['id'] for x in catalog.search()}
            with pytest.raises(ValueError, match='exceeds listed model rating'):
                repo.assign_catalog_model(item['bom_id'], products['ATV320U22N4C'])
            with pytest.raises(ValueError, match='does not match'):
                repo.assign_catalog_model(item['bom_id'], products['GV2ME14'])
            assert next(x for x in repo.get_bom(panel) if x['bom_id']==item['bom_id'])['selected_catalog_id'] is None
            repo.assign_catalog_model(item['bom_id'], products['ATV320D22N4C'])
            saved = next(x for x in repo.get_bom(panel) if x['bom_id']==item['bom_id'])
            assert saved['verification_status'] == 'unverified'
            assert 'Automatic review' in saved['sizing_notes']
        finally:
            db.close()
