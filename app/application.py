"""Main application window."""

import sys

from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
)

from app.settings import (
    APP_NAME,
    APP_VERSION,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)


class MainWindow(PySide6.QtWidgets.QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.setup_ui()

    def setup_ui(self):
        """Create the main user interface."""

        central_widget = PySide6.QtWidgets.QWidget()
        layout = PySide6.QtWidgets.QVBoxLayout()

        title = PySide6.QtWidgets.QLabel(APP_NAME)
        title.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        version = PySide6.QtWidgets.QLabel(f"Version {APP_VERSION}")

        calculations_button = PySide6.QtWidgets.QPushButton(
            "Engineering Calculations"
        )

        database_button = PySide6.QtWidgets.QPushButton(
            "Database"
        )

        settings_button = PySide6.QtWidgets.QPushButton(
            "Settings"
        )

        exit_button = PySide6.QtWidgets.QPushButton(
            "Exit"
        )

        exit_button.clicked.connect(self.close)

        layout.addWidget(title)
        layout.addWidget(version)
        layout.addSpacing(20)

        layout.addWidget(calculations_button)
        layout.addWidget(database_button)
        layout.addWidget(settings_button)

        layout.addStretch()

        layout.addWidget(exit_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


def create_application():
    """Create and return the Qt application."""

    return PySide6.QtWidgets.QApplication(sys.argv)