"""Cable/earthing screening and persisted field record tests."""
import math
import tempfile
import unittest
from pathlib import Path
from calculations.installation_assessment import cable_screening, earth_fault_loop_screening
from database.database import Database
from database.field_records import FieldRecords


class TestInstallation(unittest.TestCase):
    def test_cable(self):
        result = cable_screening(20, 32, 0.8, 30, 1.15, 230)
        self.assertAlmostEqual(result['adjusted_ampacity_a'], 25.6)
        self.assertAlmostEqual(result['estimated_resistive_drop_v'], 1.38)
        self.assertFalse(result['current_exceeds_adjusted_ampacity'])

    def test_earth_loop(self):
        result = earth_fault_loop_screening(230, 0.8, 100)
        self.assertAlmostEqual(result['idealized_earth_fault_current_a'], 287.5)
        self.assertFalse(result['below_assumed_threshold'])

    def test_bad_inputs(self):
        for fn in (lambda: cable_screening(20, 32, 1.1, 30, 1.15, 230),
                   lambda: cable_screening(20, 32, 0.8, math.inf, 1.15, 230),
                   lambda: earth_fault_loop_screening(230, 0, 100)):
            with self.assertRaises(ValueError):
                fn()

    def test_records_persist(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'field.db'
            db = Database(path)
            db.initialize()
            records = FieldRecords(db)
            records.add('measurement', 'Panel A', 'Supply voltage', 230, 'V')
            records.add('fault', 'Motor 1', 'Intermittent trip')
            self.assertEqual(len(records.recent()), 2)
            db.close()
            db = Database(path)
            db.initialize()
            self.assertEqual(len(FieldRecords(db).recent()), 2)
            db.close()

    def test_records_validate(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Database(Path(directory) / 'field.db')
            db.initialize()
            records = FieldRecords(db)
            with self.assertRaises(ValueError):
                records.add('measurement', 'Panel', 'Voltage')
            with self.assertRaises(ValueError):
                records.add('fault', '', 'No equipment')
            with self.assertRaises(ValueError):
                records.add('measurement', 'Panel', 'Voltage', math.nan)
            db.close()


if __name__ == '__main__':
    unittest.main()
