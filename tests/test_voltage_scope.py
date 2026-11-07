#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

import unittest
from calculations.installation_assessment import (validate_installation_voltage, cable_screening, earth_fault_loop_screening)

class TestVoltageScope(unittest.TestCase):
    def test_ac_limit_inclusive(self):
        self.assertEqual(validate_installation_voltage(1000, 'AC'), 1000)
        with self.assertRaises(ValueError):
            validate_installation_voltage(1000.01, 'AC')

    def test_dc_limit_inclusive(self):
        self.assertEqual(validate_installation_voltage(1500, 'DC'), 1500)
        with self.assertRaises(ValueError):
            validate_installation_voltage(1500.01, 'DC')

    def test_cable_screening_dc(self):
        result = cable_screening(20, 30, .8, 10, 1.2, 1500, 'DC')
        self.assertGreater(result['estimated_drop_percent'], 0)
        with self.assertRaises(ValueError):
            cable_screening(20, 30, .8, 10, 1.2, 1501, 'DC')

    def test_fault_loop_ac_limit(self):
        earth_fault_loop_screening(1000, 2, 100)
        with self.assertRaises(ValueError):
            earth_fault_loop_screening(1001, 2, 100)

    def test_invalid_type(self):
        with self.assertRaises(ValueError):
            validate_installation_voltage(230, 'ac')
