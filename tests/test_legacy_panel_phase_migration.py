import tempfile
from pathlib import Path
from database.database import Database
from database.pump_panel_database import PumpPanelDatabase


def test_real_legacy_schema_migrates_without_losing_panel():
    with tempfile.TemporaryDirectory() as folder:
        db = Database(Path(folder) / 'legacy.db')
        db.initialize()
        try:
            # Reconstruct a pre-phase-column schema, with a persisted legacy row.
            db.connection.execute("""CREATE TABLE pump_panel_designs (
                id INTEGER PRIMARY KEY, title TEXT NOT NULL,
                voltage_v REAL NOT NULL, main_breaker_a REAL NOT NULL,
                created_utc TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'draft')""")
            db.connection.execute("""INSERT INTO pump_panel_designs
                (id,title,voltage_v,main_breaker_a,created_utc)
                VALUES (7,'Legacy three-phase panel',400,150,'2026-01-01T00:00:00Z')""")
            repo = PumpPanelDatabase(db)
            panels = {row['id']: row for row in repo.list_panels()}
            assert panels[7]['phases'] == 3
            assert panels[7]['title'] == 'Legacy three-phase panel'
            assert repo.db.execute('SELECT phases FROM pump_panel_designs WHERE id=7').fetchone()[0] == 3
            # Migration can safely be rerun.
            assert PumpPanelDatabase(db).list_panels()[0]['phases'] == 3
        finally:
            db.close()
