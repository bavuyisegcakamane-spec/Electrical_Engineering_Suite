#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Advanced equipment calculation regression tests."""
import math
import unittest
from calculations.advanced_equipment import transformer_performance, motor_starting_estimate


class TestAdvancedEquipment(unittest.TestCase):
    def test_transformer(self):
        result = transformer_performance(100, 1, 0.8, 400, 600, 415, 400)
        self.assertAlmostEqual(result['output_power_w'], 80000)
        self.assertAlmostEqual(result['total_losses_w'], 1000)
        self.assertAlmostEqual(result['efficiency_percent'], 80000 / 81000 * 100)
        self.assertAlmostEqual(result['full_load_voltage_regulation_percent'], 3.75)

    def test_partial_load(self):
        result = transformer_performance(100, 0.5, 1, 400, 800, 415, 400)
        self.assertAlmostEqual(result['copper_loss_w'], 200)
        self.assertAlmostEqual(result['total_losses_w'], 600)

    def test_motor(self):
        result = motor_starting_estimate(20, 6, 5, 1450, 1500)
        self.assertAlmostEqual(result['estimated_starting_current_a'], 120)
        self.assertAlmostEqual(result['starting_i_squared_t_a2s'], 72000)
        self.assertAlmostEqual(result['rated_slip_percent'], 100 / 30)

    def test_invalid(self):
        for operation in (lambda: transformer_performance(100, 1, 1.2, 1, 1, 415, 400),
                          lambda: transformer_performance(100, 1, 1, math.nan, 1, 415, 400),
                          lambda: motor_starting_estimate(20, 6, 5, 1500, 1500),
                          lambda: motor_starting_estimate(20, -1, 5, 1450, 1500)):
            with self.assertRaises(ValueError):
                operation()


if __name__ == '__main__':
    unittest.main()
