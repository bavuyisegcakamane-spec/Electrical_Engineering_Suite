#  ____      ___        __  ____   _______ _____ ____
# |  _ \\    / \\ \\      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \\ \\ /\\ / /  |  _ \\    | |    | | \\___ \\
# |  _ <  / ___ \\ V  V /   | |_) |   | |    | |  ___) |
# |_| \\_\\/_/   \\_\\_/\\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

import tempfile
from pathlib import Path
import pytest
from database.database import Database
from database.pump_panel_database import PumpPanelDatabase
from calculations.pump_panel import Pump


def test_pump_panel_bom_persists_all_four_starter_variants():
    with tempfile.TemporaryDirectory() as folder:
        db = Database(Path(folder)/'panel.db')
        db.initialize()
        try:
            repo = PumpPanelDatabase(db)
            pumps = [Pump(2.2,'DOL'),Pump(11,'Star-delta'),Pump(22,'Soft starter'),Pump(45,'VFD')]
            panel_id = repo.create_panel('Pump station A',pumps)
            rows = repo.get_bom(panel_id)
            assert len(rows)>50
            assert len([r for r in rows if r['motor_position'] is None])>=40
            assert any('interlock' in r['component'].lower() and r['motor_position']==2 for r in rows)
            assert any('EMC' in r['component'] and r['motor_position']==4 for r in rows)
            assert all(r['verification_status']=='unverified' for r in rows)
            assert db.connection.execute('SELECT count(*) FROM pump_panel_motors').fetchone()[0]==4
            assert db.connection.execute('PRAGMA foreign_key_check').fetchall()==[]
        finally:
            db.close()


def test_reject_invalid_panel_without_creating_records():
    with tempfile.TemporaryDirectory() as folder:
        db=Database(Path(folder)/'panel.db'); db.initialize()
        try:
            repo=PumpPanelDatabase(db)
            with pytest.raises(ValueError):
                repo.create_panel('Bad', [Pump(45)]*5)
            assert db.connection.execute('SELECT count(*) FROM pump_panel_designs').fetchone()[0]==0
        finally:
            db.close()
