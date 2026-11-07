#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

import tempfile
import unittest
from pathlib import Path
from database.database import Database
from database.equipment_catalog import EquipmentCatalog, SEED

class TestEquipmentCatalog(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.tmp.name) / 'equipment.db')
        self.db.initialize()
        self.catalog = EquipmentCatalog(self.db)

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_seed_is_idempotent(self):
        self.catalog.seed_official_sources()
        self.catalog.seed_official_sources()
        self.assertEqual(len(self.catalog.search()),len(SEED))
        self.assertTrue(all(not r['specifications'] for r in self.catalog.search()))

    def test_search_and_persistence(self):
        self.catalog.seed_official_sources()
        self.assertEqual(len(self.catalog.search('Siemens')),1)
        self.assertEqual(len(self.catalog.search('breaker')),2)
        self.assertEqual(len(self.catalog.search('%')),0)
        self.assertEqual(len(EquipmentCatalog(self.db).search()),len(SEED))

    def test_source_validation(self):
        for url in ('http://example.com','file:///tmp/a','https://user:password@example.com'):
            with self.subTest(url=url),self.assertRaises(ValueError):
                self.catalog.add('Maker','Model','Breaker','Description',url)

    def test_specs_and_no_overwrite(self):
        self.catalog.add('Example','X1','Relay','Fictional example','https://example.org/x1',{'rated_current_a':10})
        self.catalog.add('Example','X1','Relay','Changed','https://example.org/x1',{'rated_current_a':99})
        self.assertEqual(self.catalog.search('X1')[0]['specifications']['rated_current_a'],10)
