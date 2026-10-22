"""Main application window."""

import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.settings import (
    APP_NAME,
    APP_VERSION,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)

from database.database import Database


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, database):
        super().__init__()

        self.database = database

        self.setWindowTitle(
            f"{APP_NAME} v{APP_VERSION}"
        )

        self.resize(
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
        )

        self.setup_ui()

    def setup_ui(self):
        """Create the main user interface."""

        central_widget = QWidget()
        layout = QVBoxLayout()

        title = QLabel(APP_NAME)

        title.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        version = QLabel(
            f"Version {APP_VERSION}"
        )

        status_text = (
            "● Database: Connected"
            if self.database.is_connected()
            else "● Database: Disconnected"
        )

        database_status = QLabel(status_text)

        calculations_button = QPushButton(
            "Engineering Calculations"
        )

        database_button = QPushButton(
            "Database"
        )

        settings_button = QPushButton(
            "Settings"
        )

        exit_button = QPushButton(
            "Exit"
        )

        exit_button.clicked.connect(
            self.close
        )

        layout.addWidget(title)
        layout.addWidget(version)
        layout.addWidget(database_status)

        layout.addSpacing(20)

        layout.addWidget(
            calculations_button
        )

        layout.addWidget(
            database_button
        )

        layout.addWidget(
            settings_button
        )

        layout.addStretch()

        layout.addWidget(
            exit_button
        )

        central_widget.setLayout(layout)

        self.setCentralWidget(
            central_widget
        )

    def open_calculations(self):
        """Open the engineering calculations view."""

        self.show_placeholder("Engineering Calculations")

    def open_database(self):
        """Open the database view."""

        self.show_placeholder("Database")

    def open_settings(self):
        """Open the settings view."""

        self.show_placeholder("Settings")

    def show_placeholder(self, feature_name):
        """Tell the user a feature is not built yet."""

        QMessageBox.information(
            self,
            feature_name,
            f"{feature_name} is coming soon.",
        )


def create_application():
    """Create the Qt application."""

    return QApplication(sys.argv)