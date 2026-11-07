#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Tests for illustrative resistive voltage-drop estimates."""
import math
import unittest
from calculations.cables import estimate_voltage_drop


class TestCableVoltageDrop(unittest.TestCase):
    def test_single_phase_copper(self):
        result = estimate_voltage_drop(20, 30, 4, 230)
        self.assertAlmostEqual(result["voltage_drop_v"], 2 * 20 * 30 * 0.01724 / 4)
        self.assertAlmostEqual(result["voltage_drop_percent"], result["voltage_drop_v"] / 230 * 100)

    def test_three_phase_aluminium(self):
        result = estimate_voltage_drop(20, 30, 4, 400, "Aluminium", 3)
        self.assertAlmostEqual(result["voltage_drop_v"], math.sqrt(3) * 20 * 30 * 0.02826 / 4)

    def test_temperature_and_power_factor(self):
        cold = estimate_voltage_drop(20, 30, 4, 230)
        hot = estimate_voltage_drop(20, 30, 4, 230, conductor_temp_c=70)
        self.assertGreater(hot["voltage_drop_v"], cold["voltage_drop_v"])
        half_pf = estimate_voltage_drop(20, 30, 4, 230, power_factor=0.5)
        self.assertAlmostEqual(half_pf["voltage_drop_v"], cold["voltage_drop_v"] / 2)

    def test_invalid(self):
        cases = ((-1, 30, 4, 230), (20, -1, 4, 230), (20, 30, 0, 230),
                 (20, 30, 4, 0), (math.nan, 30, 4, 230), (20, 30, math.inf, 230))
        for args in cases:
            with self.subTest(args=args), self.assertRaises(ValueError):
                estimate_voltage_drop(*args)
        for kwargs in ({"material": "Steel"}, {"phases": 2}, {"power_factor": 0},
                       {"conductor_temp_c": 300}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                estimate_voltage_drop(20, 30, 4, 230, **kwargs)


if __name__ == "__main__":
    unittest.main()
