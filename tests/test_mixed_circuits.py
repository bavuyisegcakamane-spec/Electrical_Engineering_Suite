"""Tests for a series resistor feeding two parallel branches."""
import math
import unittest
from calculations.mixed_circuits import analyze_mixed


class TestMixedCircuits(unittest.TestCase):
    def test_normal(self):
        result = analyze_mixed(12, 100, 200, 200)
        self.assertAlmostEqual(result["equivalent_resistance"], 200)
        self.assertAlmostEqual(result["source_current"], 0.06)
        self.assertAlmostEqual(result["r1_voltage"], 6)
        self.assertAlmostEqual(result["parallel_voltage"], 6)
        self.assertAlmostEqual(result["r2_current"], 0.03)
        self.assertAlmostEqual(result["r3_current"], 0.03)

    def test_short_branch(self):
        result = analyze_mixed(12, 100, 0, 200)
        self.assertEqual(result["parallel_voltage"], 0)
        self.assertAlmostEqual(result["r2_current"], 0.12)
        self.assertEqual(result["r3_current"], 0)

    def test_zero_supply(self):
        self.assertEqual(analyze_mixed(0, 100, 200, 300)["source_current"], 0)

    def test_invalid(self):
        for inputs in ((12, 0, 0, 100), (12, 100, 0, 0), (-12, 100, 200, 300),
                       (12, -1, 200, 300), (math.inf, 1, 2, 3), (12, 1, math.nan, 3)):
            with self.subTest(inputs=inputs):
                with self.assertRaises(ValueError):
                    analyze_mixed(*inputs)


if __name__ == "__main__":
    unittest.main()
