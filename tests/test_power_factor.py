"""Tests for ideal power factor correction estimates."""
import math
import unittest
from calculations.power_factor import estimate_correction


class TestPowerFactor(unittest.TestCase):
    def test_correction(self):
        result = estimate_correction(100, 400, 0.8, 0.95)
        expected = 100 * (0.75 - math.sqrt(1 - 0.95 ** 2) / 0.95)
        self.assertAlmostEqual(result["required_compensation_kvar"], expected)
        self.assertAlmostEqual(result["initial_apparent_kva"], 125)
        self.assertAlmostEqual(result["target_apparent_kva"], 100 / 0.95)
        self.assertGreater(result["line_current_reduction_amps"], 0)

    def test_no_correction_needed(self):
        result = estimate_correction(10, 400, 1, 1)
        self.assertEqual(result["required_compensation_kvar"], 0)
        self.assertEqual(result["line_current_reduction_amps"], 0)

    def test_invalid(self):
        for args in ((0, 400, 0.8, 0.95), (100, 0, 0.8, 0.95),
                     (100, 400, 0, 0.95), (100, 400, 0.8, 1.1),
                     (100, 400, 0.95, 0.8), (math.nan, 400, 0.8, 0.95),
                     (100, math.inf, 0.8, 0.95), (True, 400, 0.8, 0.95)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                estimate_correction(*args)


if __name__ == "__main__":
    unittest.main()
