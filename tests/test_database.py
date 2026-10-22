import tempfile
import unittest
from pathlib import Path

from database.database import Database
from database.models import ProjectModel


class TestProjectModel(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.tmp.name) / "test.db")
        self.database.initialize()
        self.projects = ProjectModel(self.database)

    def tearDown(self):
        self.database.close()
        self.tmp.cleanup()

    def test_create_and_fetch(self):
        project_id = self.projects.create("Test", "Description")
        project = self.projects.get_by_id(project_id)
        self.assertEqual(project[1], "Test")

    def test_delete(self):
        project_id = self.projects.create("Test", "Description")
        self.projects.delete(project_id)
        self.assertIsNone(self.projects.get_by_id(project_id))

    def test_is_connected(self):
        self.assertTrue(self.database.is_connected())
        self.database.close()
        self.assertFalse(self.database.is_connected())

    
if __name__ == "__main__":
    unittest.main()