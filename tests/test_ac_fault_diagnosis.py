"""Regression tests for AC engineering and symptom guidance."""
import math
import unittest
from calculations.ac_engineering import ac_impedance, three_phase_power, insulation_resistance
from calculations.fault_diagnosis import FAULT_GUIDES, diagnose_symptom


class TestACElectrical(unittest.TestCase):
    def test_three_phase(self):
        result = three_phase_power(400, 10, 0.8)
        self.assertAlmostEqual(result['apparent_power_va'], math.sqrt(3) * 4000)
        self.assertAlmostEqual(result['real_power_w'], math.sqrt(3) * 3200)
        self.assertAlmostEqual(result['reactive_power_var_magnitude'], math.sqrt(3) * 2400)

    def test_rlc(self):
        result = ac_impedance(10, 0.1, 0.0001, 50)
        self.assertAlmostEqual(result['inductive_reactance_ohms'], 10 * math.pi)
        self.assertTrue(0 < result['power_factor'] <= 1)

    def test_insulation(self):
        self.assertAlmostEqual(insulation_resistance(500, 5)['insulation_resistance_megohms'], 100)

    def test_validation(self):
        for call in (lambda: three_phase_power(400, 10, 1.1),
                     lambda: three_phase_power(400, math.inf, 0.9),
                     lambda: ac_impedance(0, 1, 1, 50),
                     lambda: insulation_resistance(500, 0)):
            with self.assertRaises(ValueError):
                call()

    def test_fault_guides(self):
        for symptom in FAULT_GUIDES:
            with self.subTest(symptom=symptom):
                report = diagnose_symptom(symptom)
                self.assertGreater(len(report['possible_causes']), 1)
                self.assertIn('qualified', ' '.join(report['safe_next_steps']))
        with self.assertRaises(ValueError):
            diagnose_symptom('not supported')


if __name__ == '__main__':
    unittest.main()
