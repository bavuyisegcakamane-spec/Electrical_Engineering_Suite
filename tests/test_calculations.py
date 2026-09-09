"""Tests for electrical engineering calculations."""

import unittest

from calculations import (
    calculate_voltage,
    calculate_current,
    calculate_resistance,
    calculate_power_vi,
    calculate_power_ir,
    calculate_power_vr,
    calculate_energy,
    watts_to_kilowatts,
    kilowatts_to_watts,
)


class TestOhmsLaw(unittest.TestCase):

    def test_voltage(self):
        result = calculate_voltage(2, 10)

        self.assertEqual(result, 20)

    def test_current(self):
        result = calculate_current(12, 100)

        self.assertEqual(result, 0.12)

    def test_resistance(self):
        result = calculate_resistance(12, 2)

        self.assertEqual(result, 6)


class TestPower(unittest.TestCase):

    def test_power_voltage_current(self):
        result = calculate_power_vi(12, 2)

        self.assertEqual(result, 24)

    def test_power_current_resistance(self):
        result = calculate_power_ir(2, 10)

        self.assertEqual(result, 40)

    def test_power_voltage_resistance(self):
        result = calculate_power_vr(20, 10)

        self.assertEqual(result, 40)

    def test_energy(self):
        result = calculate_energy(1000, 2)

        self.assertEqual(result, 2000)


class TestUnits(unittest.TestCase):

    def test_watts_to_kilowatts(self):
        result = watts_to_kilowatts(2000)

        self.assertEqual(result, 2)

    def test_kilowatts_to_watts(self):
        result = kilowatts_to_watts(2)

        self.assertEqual(result, 2000)


if __name__ == "__main__":
    unittest.main()