"""Workspace editing, deletion and grouped report regression tests."""
import tempfile
import unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from projects.workspace import Workspace
from app.workspace_dialog import WorkspaceDialog
from reports.pdf_report import create_project_pdf_report


class TestWorkspaceEditing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_edit_delete_and_reopen(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Workspace(folder)
            store.add_calculation("Project", "Cable voltage drop", {"Current (A)": 10}, {"Drop (V)": 1}, ["Copper"])
            store.add_calculation("Project", "Fault current", {"Voltage (V)": 230}, {"Current (A)": 2300}, ["Simple"])
            store.update_calculation("Project", 0, "Cable voltage drop", {"Current (A)": 20}, {"Drop (V)": 2}, ["Copper"])
            self.assertEqual(store.load("Project")["calculations"][0]["inputs"]["Current (A)"], 20)
            store.delete_calculation("Project", 1)
            self.assertEqual(len(store.load("Project")["calculations"]), 1)
            for method in (lambda: store.delete_calculation("Project", 5),
                           lambda: store.update_calculation("Project", -1, "X", {}, {}, [])):
                with self.assertRaises(IndexError):
                    method()

    def test_dialog_summary_and_edit_form(self):
        with tempfile.TemporaryDirectory() as folder:
            dialog = WorkspaceDialog(directory=folder)
            dialog.projects.setEditText("Demo")
            dialog.open_project()
            dialog.store.add_calculation("Demo", "Power factor correction",
                                         {"Real power (kW)": 100, "Voltage L-L (V)": 400,
                                          "Initial PF": 0.8, "Target PF": 0.95},
                                         {"required compensation kvar": "42"}, ["Ideal"])
            dialog.current = dialog.store.load("Demo")
            dialog.refresh_entries()
            self.assertIn("Calculations: 1", dialog.summary.text())
            editor = dialog.calculation_editor(dialog.current['calculations'][0])
            self.assertEqual(editor.fields[2].text(), "0.8")
            editor.fields[2].setText("0.85")
            self.assertTrue(editor.build_data()[2])
            editor.close()
            dialog.close()

    def test_project_pdf(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Workspace(folder)
            for i in range(3):
                store.add_calculation("Demo", "Motor", {"Power (kW)": i + 1}, {"Current (A)": i + 2}, ["Balanced"])
            pdf = Path(folder) / "project.pdf"
            create_project_pdf_report(pdf, store.load("Demo"))
            self.assertTrue(pdf.read_bytes().startswith(b"%PDF-"))
            self.assertGreater(pdf.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
