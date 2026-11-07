import unittest
from calculations.device_coordination import parse_curve_csv, review_device_coordination

UP = 'current_a,min_trip_s,max_trip_s\n100,1,2\n1000,.5,1\n10000,.2,.4\n'
DOWN = 'current_a,min_trip_s,max_trip_s\n100,.1,.2\n1000,.05,.1\n10000,.02,.04\n'

class TestDeviceCoordination(unittest.TestCase):
    def test_parse_and_compare(self):
        self.assertEqual(len(parse_curve_csv(UP)),3)
        result=review_device_coordination(UP,DOWN,1000,.4,'Fictional devices - test only')
        self.assertTrue(result['envelopes_separated_at_sampled_current'])
        self.assertTrue(result['downstream_upper_time_within_user_limit'])
        self.assertEqual(result['compliance_status'],'NOT DETERMINED')

    def test_no_extrapolation(self):
        with self.assertRaises(ValueError):
            review_device_coordination(UP,DOWN,10001,.4,'test')

    def test_invalid_csv(self):
        bad=('current_a,min_trip_s,max_trip_s\n100,2,1\n1000,1,2\n',
             'current_a,min_trip_s,max_trip_s\n100,1,2\n100,1,2\n',
             'current_a,trip_s\n100,1\n1000,2\n')
        for data in bad:
            with self.subTest(data=data),self.assertRaises(ValueError):
                parse_curve_csv(data)

    def test_not_selective(self):
        result=review_device_coordination(DOWN,UP,1000,.4,'test')
        self.assertFalse(result['envelopes_separated_at_sampled_current'])
        self.assertFalse(result['downstream_upper_time_within_user_limit'])

    def test_missing_source(self):
        with self.assertRaises(ValueError):
            review_device_coordination(UP,DOWN,1000,.4,'')
