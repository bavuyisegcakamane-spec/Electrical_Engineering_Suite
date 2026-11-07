#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Tests for three-phase motor analysis."""
import math
import unittest
from calculations.motors import analyze_motor


class TestMotors(unittest.TestCase):
    def test_rated_motor(self):
        result = analyze_motor(7.5, 400, 0.9, 0.85, 1450)
        self.assertAlmostEqual(result["input_kw"], 7.5 / 0.9)
        self.assertAlmostEqual(result["line_current_amps"], 7500 / (math.sqrt(3) * 400 * 0.9 * 0.85))
        self.assertAlmostEqual(result["shaft_torque_nm"], 7500 * 60 / (2 * math.pi * 1450))
        self.assertAlmostEqual(result["losses_kw"], 7.5 / 0.9 - 7.5)

    def test_unity_pf_efficiency(self):
        result = analyze_motor(3, 400, 1, 1, 1500)
        self.assertAlmostEqual(result["reactive_kvar"], 0)
        self.assertAlmostEqual(result["input_kw"], 3)

    def test_invalid(self):
        for args in ((0, 400, 0.9, 0.85, 1450), (7.5, 0, 0.9, 0.85, 1450),
                     (7.5, 400, 0, 0.85, 1450), (7.5, 400, 0.9, 1.1, 1450),
                     (7.5, 400, 0.9, 0.85, 0), (math.inf, 400, 0.9, 0.85, 1450),
                     (7.5, 400, math.nan, 0.85, 1450), (True, 400, 0.9, 0.85, 1450)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                analyze_motor(*args)


if __name__ == "__main__":
    unittest.main()
