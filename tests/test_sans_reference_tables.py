import unittest
from calculations.sans_reference_tables import buried_cable_lookup


class TestReferenceTables(unittest.TestCase):
    def test_direct_two_core(self):
        r = buried_cable_lookup(2.5, 2, 'direct', 25, .5)
        self.assertEqual(r['tabulated_ampacity_a'], 37)
        self.assertEqual(r['partially_corrected_ampacity_a'], 37)
        self.assertEqual(r['compliance_status'], 'NOT DETERMINED')

    def test_pipe_three_core(self):
        r = buried_cable_lookup(16, 3, 'pipe', 30, 1.)
        self.assertEqual(r['tabulated_ampacity_a'], 75)
        self.assertAlmostEqual(r['partially_corrected_ampacity_a'], 75 * .94 * .96)

    def test_four_core(self):
        self.assertEqual(buried_cable_lookup(10, 4, 'direct', 25, .5)['tabulated_ampacity_a'], 70)

    def test_no_interpolation_or_unsupported(self):
        for args in ((2.5, 2, 'direct', 27, .5), (2.5, 2, 'direct', 25, .7),
                     (120, 2, 'direct', 25, .5), (2.5, 5, 'direct', 25, .5)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                buried_cable_lookup(*args)
