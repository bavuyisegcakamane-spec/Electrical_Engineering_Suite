#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Tests for ideal resistor networks."""
import math
import unittest
from calculations.circuits import series_resistance, parallel_resistance


class TestCircuits(unittest.TestCase):
    def test_series(self):
        self.assertEqual(series_resistance([100, 220, 330]), 650)

    def test_parallel(self):
        self.assertAlmostEqual(parallel_resistance([100, 100]), 50)

    def test_single_resistor(self):
        self.assertEqual(parallel_resistance([470]), 470)

    def test_short_circuit(self):
        self.assertEqual(parallel_resistance([0, 100]), 0)

    def test_empty(self):
        for function in (series_resistance, parallel_resistance):
            with self.assertRaises(ValueError):
                function([])

    def test_invalid(self):
        for function in (series_resistance, parallel_resistance):
            for values in ([-1, 100], [math.nan], [math.inf], [True, 1]):
                with self.subTest(function=function.__name__, values=values):
                    with self.assertRaises(ValueError):
                        function(values)

    def test_large_parallel(self):
        self.assertAlmostEqual(parallel_resistance([1e308, 1e308]), 5e307)


if __name__ == "__main__":
    unittest.main()
