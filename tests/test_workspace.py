"""Project persistence and combined report integration."""
import tempfile
import unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from projects.workspace import Workspace
from app.workspace_dialog import WorkspaceDialog
from reports.pdf_report import create_pdf_report


class TestWorkspace(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_create_reopen_and_append(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Workspace(folder)
            store.save(store.load("Demo Project"))
            store.add_calculation("Demo Project", "Motor", {"Voltage (V)": 400},
                                  {"Current (A)": "12"}, ["Balanced"])
            store.add_calculation("Demo Project", "Load", {"Power (W)": 1000},
                                  {"Energy (kWh)": "2"}, ["Constant load"])
            self.assertEqual(len(store.load("Demo Project")["calculations"]), 2)
            self.assertIn("Demo Project", store.list_projects())
            dialog = WorkspaceDialog(directory=folder)
            dialog.projects.setEditText("Demo Project")
            dialog.open_project()
            self.assertEqual(dialog.entries.count(), 2)
            dialog.close()

    def test_reject_path_traversal(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Workspace(folder)
            for name in ("../escape", "", "x/y", "bad:name"):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    store.load(name)

    def test_combined_pdf(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Workspace(folder)
            store.add_calculation("Demo", "Motor", {"Power (kW)": 7.5}, {"Current (A)": "14"}, ["Balanced"])
            store.add_calculation("Demo", "Load", {"Power (W)": 2000}, {"Energy (kWh)": "4"}, ["Steady"])
            project = store.load("Demo")
            inputs, outputs, assumptions = {}, {}, []
            for i, item in enumerate(project["calculations"], 1):
                inputs.update({f"{i}. {item['type']} - {k}": v for k, v in item['inputs'].items()})
                outputs.update({f"{i}. {item['type']} - {k}": v for k, v in item['outputs'].items()})
                assumptions.extend(item['assumptions'])
            path = Path(folder) / "combined.pdf"
            create_pdf_report(path, "Demo", "Combined engineering calculations", inputs, outputs, assumptions)
            self.assertTrue(path.read_bytes().startswith(b"%PDF-"))


if __name__ == "__main__":
    unittest.main()
