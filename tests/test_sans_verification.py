#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

import unittest
from calculations.sans_verification import REQUIREMENTS, review_evidence

class TestSANSEvidence(unittest.TestCase):
    def test_empty_is_unresolved(self):
        result = review_evidence({})
        self.assertEqual(result['outstanding'], len(REQUIREMENTS))
        self.assertEqual(result['compliance_status'].split(' - ')[0], 'NOT DETERMINED')

    def test_verified_requires_evidence(self):
        with self.assertRaises(ValueError):
            review_evidence({'earthing': {'status':'verified','note':''}})
        result=review_evidence({'earthing':{'status':'verified','note':'Test record #123'}})
        self.assertEqual(result['counts']['verified'],1)

    def test_issue_and_na(self):
        result=review_evidence({'dc_sources':{'status':'not applicable','note':'AC-only circuit'},
                                'device_curve':{'status':'issue','note':'Missing manufacturer data'}})
        self.assertEqual(result['counts']['issue'],1)
        self.assertEqual(result['counts']['not applicable'],1)
        self.assertEqual(result['outstanding'],len(REQUIREMENTS)-1)

    def test_bad_status_and_unknown_key(self):
        for records in ({'earthing':{'status':'compliant','note':'yes'}},
                        {'invented':{'status':'verified','note':'yes'}}):
            with self.assertRaises(ValueError):
                review_evidence(records)
