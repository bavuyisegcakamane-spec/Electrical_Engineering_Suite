import tempfile
from pathlib import Path
import pytest
from database.database import Database
from database.cable_reference_database import CableReferenceRepository
from calculations.cable_sizing import derated_ampacity


def test_cited_reference_persists_and_derates():
    with tempfile.TemporaryDirectory() as folder:
        db = Database(Path(folder) / "test.db")
        db.initialize()
        try:
            repo = CableReferenceRepository(db)
            assert repo.list_ratings() == []
            key = repo.add(source_title="Example manufacturer datasheet",
                source_edition="2026 revision", table_reference="Table A",
                installation_method="Example method", conductor_description="Example 3-core",
                material="Copper", area_mm2=10, reference_ampacity_a=70)
            row = repo.get(key)
            assert row["source_verified"] == 0
            assert derated_ampacity(row["reference_ampacity_a"], .8)["derated_ampacity_a"] == pytest.approx(56)
            assert CableReferenceRepository(db).get(key)["source_title"] == "Example manufacturer datasheet"
        finally:
            db.close()


def test_rejects_unsourced_rating():
    with tempfile.TemporaryDirectory() as folder:
        db = Database(Path(folder) / "test.db")
        db.initialize()
        try:
            repo = CableReferenceRepository(db)
            with pytest.raises(ValueError):
                repo.add(source_title="", source_edition="2026", table_reference="A",
                         installation_method="A", conductor_description="A",
                         material="Copper", area_mm2=10, reference_ampacity_a=70)
        finally:
            db.close()
