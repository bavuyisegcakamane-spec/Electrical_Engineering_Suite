#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Ideal transformer equations, validation and report integration."""
import math
import unittest
from calculations.transformers import analyze_transformer
from app.report_dialog import CONFIG


class TestTransformers(unittest.TestCase):
    def test_step_down(self):
        result = analyze_transformer(230, 1000, 500, 1000)
        self.assertAlmostEqual(result['turns_ratio_primary_to_secondary'], 2)
        self.assertAlmostEqual(result['secondary_voltage_v'], 115)
        self.assertAlmostEqual(result['primary_rated_current_a'], 1000 / 230)
        self.assertAlmostEqual(result['secondary_rated_current_a'], 1000 / 115)

    def test_step_up(self):
        result = analyze_transformer(120, 100, 500, 600)
        self.assertAlmostEqual(result['secondary_voltage_v'], 600)
        self.assertAlmostEqual(result['secondary_rated_current_a'], 1)
        self.assertEqual(result['ideal_primary_power_va'], result['ideal_secondary_power_va'])

    def test_one_to_one(self):
        result = analyze_transformer(230, 100, 100, 2300)
        self.assertAlmostEqual(result['secondary_voltage_v'], 230)
        self.assertAlmostEqual(result['primary_rated_current_a'], 10)
        self.assertAlmostEqual(result['secondary_rated_current_a'], 10)

    def test_invalid_inputs(self):
        for args in ((0, 100, 100, 1000), (230, 0, 100, 1000),
                     (230, 100, -1, 1000), (230, 100, 100, 0),
                     (math.nan, 100, 100, 1000), (230, math.inf, 100, 1000),
                     (True, 100, 100, 1000)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                analyze_transformer(*args)

    def test_report_config(self):
        labels, defaults, calculator, assumptions = CONFIG['Ideal transformer']
        self.assertEqual(len(labels), 4)
        self.assertTrue(calculator(*map(float, defaults)))
        self.assertTrue(assumptions)


if __name__ == '__main__':
    unittest.main()
