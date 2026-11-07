#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

import unittest
from calculations.sans_screening import assess_cable_and_protection

ARGS = (230, 20, 32, .9, .85, 1, 7, 20, 6, 3)

class TestSANSScreening(unittest.TestCase):
    def test_partial_pass(self):
        result = assess_cable_and_protection(*ARGS)
        self.assertAlmostEqual(result['effective_ampacity_a'], 24.48)
        self.assertTrue(result['all_screening_checks_pass'])
        self.assertIn('NOT DETERMINED', result['compliance_status'])

    def test_voltage_drop_fail(self):
        args = list(ARGS)
        args[6] = 12
        result = assess_cable_and_protection(*args)
        self.assertFalse(result['checks']['voltage_drop_within_5_percent'])

    def test_device_breaking_fail(self):
        args = list(ARGS)
        args[8] = 2
        result = assess_cable_and_protection(*args)
        self.assertFalse(result['checks']['breaking_capacity_at_least_2_5_ka'])
        self.assertFalse(result['checks']['breaking_capacity_at_least_prospective_fault_ka'])

    def test_dc_limit(self):
        args = list(ARGS)
        args[0] = 1500
        self.assertTrue(assess_cable_and_protection(*args, supply_type='DC'))
        args[0] = 1501
        with self.assertRaises(ValueError):
            assess_cable_and_protection(*args, supply_type='DC')

    def test_invalid_factors(self):
        args = list(ARGS)
        args[3] = 1.1
        with self.assertRaises(ValueError):
            assess_cable_and_protection(*args)
