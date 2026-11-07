import unittest
from calculations.sans_extended_checks import buried_cable_extended,protective_earthing_review,AIR_PVC_70C

class TestSANSExtended(unittest.TestCase):
    def test_soil_grouping(self):
        result=buried_cable_extended(2.5,3,'direct',25,.5,1.2,2,0)
        self.assertAlmostEqual(result['extended_corrected_ampacity_a'],32*.81)
        self.assertEqual(result['compliance_status'],'NOT DETERMINED')

    def test_pipe_resistivity(self):
        result=buried_cable_extended(16,3,'pipe',30,1.,2.,3,300)
        self.assertAlmostEqual(result['extended_corrected_ampacity_a'],75*.94*.96*.91*.87)

    def test_reject_unlisted(self):
        with self.assertRaises(ValueError):
            buried_cable_extended(2.5,3,'direct',25,.5,1.3,2,0)
        with self.assertRaises(ValueError):
            buried_cable_extended(2.5,3,'direct',25,.5,1.2,2,150)

    def test_pvc_ambient_reference(self):
        self.assertEqual(AIR_PVC_70C[60],.5)

    def test_ac_protection_review(self):
        r=protective_earthing_review('AC',230,20,25,20,6,3,.8,100,.2,.4,30)
        self.assertTrue(all(r['checks'].values()))
        self.assertEqual(r['compliance_status'],'NOT DETERMINED')
        self.assertAlmostEqual(r['idealized_ac_fault_current_a'],287.5)

    def test_failed_trip(self):
        r=protective_earthing_review('AC',230,20,25,20,6,3,5,100,1,.4,100)
        self.assertFalse(r['checks']['idealized_fault_current_at_least_device_trip_threshold'])
        self.assertFalse(r['checks']['user_supplied_trip_time_within_user_supplied_limit'])
        self.assertFalse(r['checks']['rcd_rating_at_most_30_ma_for_30_ma_applications'])

    def test_dc_multiple_sources(self):
        r=protective_earthing_review('DC',1500,20,25,20,6,3,0,0,0,0,None,True)
        self.assertTrue(r['multiple_dc_sources_require_individual_protection'])
        self.assertIsNone(r['idealized_ac_fault_current_a'])
        with self.assertRaises(ValueError):
            protective_earthing_review('DC',1501,20,25,20,6,3,0,0,0,0)
