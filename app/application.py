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
from app.calculator_dialog import CalculatorDialog
from app.circuit_dialog import CircuitDialog
from app.mixed_dialog import MixedCircuitDialog
from app.load_dialog import LoadDialog
from app.motor_dialog import MotorDialog


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

        circuit_button = QPushButton("Circuit Analyzer")
        mixed_button = QPushButton("Mixed Circuit Analyzer")
        load_button = QPushButton("Electrical Load Calculator")
        motor_button = QPushButton("Motor Analysis")

        database_button = QPushButton(
            "Database"
        )

        settings_button = QPushButton(
            "Settings"
        )

        exit_button = QPushButton(
            "Exit"
        )

        calculations_button.clicked.connect(self.open_calculations)
        circuit_button.clicked.connect(self.open_circuits)
        mixed_button.clicked.connect(self.open_mixed_circuits)
        load_button.clicked.connect(self.open_loads)
        motor_button.clicked.connect(self.open_motors)
        database_button.clicked.connect(self.open_database)
        settings_button.clicked.connect(self.open_settings)
        exit_button.clicked.connect(self.close)

        layout.addWidget(title)
        layout.addWidget(version)
        layout.addWidget(database_status)

        layout.addSpacing(20)

        layout.addWidget(
            calculations_button
        )
        layout.addWidget(circuit_button)
        layout.addWidget(mixed_button)
        layout.addWidget(load_button)
        layout.addWidget(motor_button)

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

        dialog = CalculatorDialog(self)
        dialog.exec()

    def open_circuits(self):
        """Open the resistor circuit analyzer."""
        dialog = CircuitDialog(self)
        dialog.exec()

    def open_mixed_circuits(self):
        """Open the mixed resistor circuit analyzer."""
        dialog = MixedCircuitDialog(self)
        dialog.exec()

    def open_loads(self):
        """Open the electrical load calculator."""
        dialog = LoadDialog(self)
        dialog.exec()

    def open_motors(self):
        """Open three-phase motor analysis."""
        dialog = MotorDialog(self)
        dialog.exec()

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