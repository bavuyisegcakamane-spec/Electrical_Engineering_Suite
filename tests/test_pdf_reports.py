#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""PDF report generation and calculator integration tests."""
import tempfile
import unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from app.report_dialog import ReportDialog, CONFIG
from reports.pdf_report import create_pdf_report


class TestPdfReports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_pdf_header_and_size(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.pdf"
            create_pdf_report(path, "Sample report", "Motor", {"Voltage (V)": 400},
                              {"Current (A)": 12}, ["Balanced three phase"])
            self.assertTrue(path.read_bytes().startswith(b"%PDF-"))
            self.assertGreater(path.stat().st_size, 1000)

    def test_all_calculator_reports(self):
        dialog = ReportDialog()
        for name in CONFIG:
            with self.subTest(calculation=name):
                dialog.selector.setCurrentText(name)
                title, inputs, outputs, assumptions = dialog.build_data()
                self.assertEqual(title, name)
                self.assertTrue(inputs and outputs and assumptions)
                with tempfile.TemporaryDirectory() as folder:
                    path = Path(folder) / "report.pdf"
                    create_pdf_report(path, "Calculation report", title, inputs, outputs, assumptions)
                    self.assertTrue(path.read_bytes().startswith(b"%PDF-"))
        dialog.close()

    def test_reject_invalid(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                create_pdf_report(Path(folder) / "bad.pdf", "", "Motor", {"a": 1}, {"b": 2}, [])


if __name__ == "__main__":
    unittest.main()
