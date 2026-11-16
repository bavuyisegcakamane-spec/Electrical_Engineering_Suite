import tempfile
from pathlib import Path
import pytest
from calculations.pump_panel import Pump
from database.database import Database
from database.pump_panel_database import PumpPanelDatabase
from database.lv_panel_materials import PANEL_MATERIALS

def test_categories_and_manual_bom_material():
    with tempfile.TemporaryDirectory() as folder:
        db = Database(Path(folder) / 'materials.db')
        db.initialize()
        try:
            repo = PumpPanelDatabase(db)
            assert len(PANEL_MATERIALS) == 6
            assert all(any(r['name'] == name for r in repo.list_component_types(name))
                       for names in PANEL_MATERIALS.values() for name in names)
            panel = repo.create_panel('450V panel', [Pump(2.2, 'DOL')], voltage_v=450)
            repo.add_material_to_panel(panel, 'Busbar end cap', quantity=3)
            item = next(r for r in repo.get_bom(panel) if r['component'] == 'Busbar end cap')
            assert item['quantity'] == 3
            assert item['requirement'] == 'review'
            assert item['verification_status'] == 'unverified'
            with pytest.raises(ValueError, match='already exists'):
                repo.add_material_to_panel(panel, 'Busbar end cap')
            with pytest.raises(ValueError, match='Pump position'):
                repo.add_material_to_panel(panel, 'Panel light', motor_position=2)
        finally:
            db.close()
