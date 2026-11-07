"""Educational fault-current estimator tests."""
import math
import unittest
from calculations.protection import estimate_fault_current


class TestProtection(unittest.TestCase):
    def test_single_phase(self):
        result = estimate_fault_current(230, 0.1, 32, 6)
        self.assertAlmostEqual(result["fault_current_amps"], 2300)
        self.assertAlmostEqual(result["fault_to_rating_ratio"], 2300 / 32)
        self.assertFalse(result["exceeds_stated_breaking_capacity"])

    def test_three_phase(self):
        result = estimate_fault_current(400, 0.1, 32, 6, 3)
        self.assertAlmostEqual(result["fault_current_amps"], 400 / (math.sqrt(3) * 0.1))

    def test_capacity_exceeded(self):
        result = estimate_fault_current(230, 0.01, 32, 6)
        self.assertTrue(result["exceeds_stated_breaking_capacity"])

    def test_invalid(self):
        for args in ((0, 0.1, 32, 6), (230, 0, 32, 6), (230, 0.1, 0, 6),
                     (230, 0.1, 32, 0), (math.nan, 0.1, 32, 6),
                     (230, math.inf, 32, 6), (True, 0.1, 32, 6)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                estimate_fault_current(*args)
        with self.assertRaises(ValueError):
            estimate_fault_current(230, 0.1, 32, 6, phases=2)


if __name__ == "__main__":
    unittest.main()
