#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Dashboard navigation, search and project overview tests."""
import tempfile
import unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from app.dashboard import Dashboard, TOOLS
from projects.workspace import Workspace


class StubWindow:
    def __init__(self):
        self.calls = []
    def __getattr__(self, name):
        if name.startswith('open_') or name == 'close':
            return lambda: self.calls.append(name)
        raise AttributeError(name)


class TestDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_categories_search_and_navigation(self):
        from PySide6.QtWidgets import QWidget
        class Window(QWidget, StubWindow):
            def __init__(self):
                QWidget.__init__(self)
                StubWindow.__init__(self)
        with tempfile.TemporaryDirectory() as folder:
            window = Window()
            dashboard = Dashboard(window, folder)
            self.assertEqual(len(dashboard.buttons), sum(len(x) for x in TOOLS.values()))
            dashboard.search.setText('motor')
            self.assertTrue(dashboard.buttons['Motor Analysis'].isVisibleTo(dashboard))
            self.assertFalse(dashboard.buttons['Cable Voltage Drop'].isVisibleTo(dashboard))
            dashboard.search.clear()
            dashboard.buttons['Motor Analysis'].click()
            self.assertIn('open_motors', window.calls)
            dashboard.close()
            window.close()

    def test_project_overview_refresh(self):
        from PySide6.QtWidgets import QWidget
        class Window(QWidget, StubWindow):
            def __init__(self):
                QWidget.__init__(self)
                StubWindow.__init__(self)
        with tempfile.TemporaryDirectory() as folder:
            window = Window()
            dashboard = Dashboard(window, folder)
            store = Workspace(folder)
            store.add_calculation('Test Project', 'Motor', {'Power': 1}, {'Current': 2}, ['Ideal'])
            dashboard.refresh_projects()
            self.assertIn('Saved projects: 1', dashboard.project_summary.text())
            self.assertIn('Saved calculations: 1', dashboard.project_summary.text())
            dashboard.close()
            window.close()


if __name__ == '__main__':
    unittest.main()
