import tempfile
from pathlib import Path
from PySide6.QtWidgets import QApplication, QDialog
from database.database import Database
from database.cable_reference_database import CableReferenceRepository
from app.cable_reference_entry_dialog import CableReferenceEntryDialog
from app.cable_dialog import CableDialog


def test_reference_entry_dialog_save_and_refresh(monkeypatch):
    app = QApplication.instance() or QApplication([])
    with tempfile.TemporaryDirectory() as folder:
        db = Database(Path(folder) / "ui.db")
        db.initialize()
        try:
            class Parent(QDialog):
                pass
            parent = Parent()
            parent.database = db
            dialog = CableDialog(parent)
            entry = CableReferenceEntryDialog(CableReferenceRepository(db), dialog)
            for key, value in {
                "source_title": "Example source",
                "source_edition": "Revision A",
                "table_reference": "Table 1",
                "installation_method": "Example installation",
                "conductor_description": "3-core PVC example",
                "area_mm2": "10",
                "reference_ampacity_a": "65",
            }.items():
                entry.entries[key].setText(value)
            entry.save()
            assert entry.result() == QDialog.Accepted
            assert len(CableReferenceRepository(db).list_ratings()) == 1
            monkeypatch.setattr(CableReferenceEntryDialog, "exec", lambda self: QDialog.Accepted)
            dialog.add_reference()
            assert dialog.reference.count() == 2
            assert dialog.reference.currentData() is not None
            dialog.check_reference()
            assert "UNVERIFIED" in dialog.result.text()
        finally:
            db.close()
