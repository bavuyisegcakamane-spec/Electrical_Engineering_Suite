"""Load calculator unit tests."""
import math
import unittest
from calculations.loads import calculate_load


class TestLoads(unittest.TestCase):
    def test_single_phase(self):
        result = calculate_load(1000, 2, 230, 1, 3, 1)
        self.assertEqual(result["connected_watts"], 2000)
        self.assertAlmostEqual(result["line_current_amps"], 2000 / 230)
        self.assertEqual(result["energy_kwh"], 6)

    def test_three_phase(self):
        result = calculate_load(5000, 1, 400, 0.8, 2, 3)
        self.assertAlmostEqual(result["line_current_amps"], 5000 / (math.sqrt(3) * 400 * 0.8))
        self.assertEqual(result["energy_kwh"], 10)

    def test_demand_factor(self):
        result = calculate_load(1000, 4, 230, 1, 2, 1, 0.5)
        self.assertEqual(result["connected_watts"], 4000)
        self.assertEqual(result["demand_watts"], 2000)
        self.assertEqual(result["energy_kwh"], 4)

    def test_invalid(self):
        cases = ((1000, 0, 230), (1000, 1, 0), (-1, 1, 230),
                 (math.nan, 1, 230), (1000, 1, math.inf), (1000, 1.5, 230))
        for args in cases:
            with self.subTest(args=args), self.assertRaises(ValueError):
                calculate_load(*args)
        for kwargs in ({"power_factor": 0}, {"power_factor": 1.1},
                       {"demand_factor": -0.1}, {"demand_factor": 1.1},
                       {"hours": -1}, {"phases": 2}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                calculate_load(1000, 1, 230, **kwargs)


if __name__ == "__main__":
    unittest.main()
