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
from app.cable_dialog import CableDialog
from app.protection_dialog import ProtectionDialog
from app.power_factor_dialog import PowerFactorDialog
from app.report_dialog import ReportDialog
from app.workspace_dialog import WorkspaceDialog
from app.dashboard import Dashboard
from app.transformer_dialog import TransformerDialog
from app.ac_engineering_dialog import ACEngineeringDialog
from app.fault_diagnosis_dialog import FaultDiagnosisDialog
from app.advanced_equipment_dialog import AdvancedEquipmentDialog
from app.installation_dialog import InstallationDialog
from app.sans_screening_dialog import SANSScreeningDialog
from app.sans_cable_tables_dialog import SANSCableTablesDialog
from app.sans_extended_dialog import SANSExtendedDialog
from app.field_records_dialog import FieldRecordsDialog


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
        """Create the searchable categorized main dashboard."""
        self.dashboard = Dashboard(self)
        self.setCentralWidget(self.dashboard)

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

    def open_transformers(self):
        """Open ideal single-phase transformer calculator."""
        dialog = TransformerDialog(self)
        dialog.exec()

    def open_ac_engineering(self):
        dialog = ACEngineeringDialog(self)
        dialog.exec()

    def open_fault_diagnosis(self):
        dialog = FaultDiagnosisDialog(self)
        dialog.exec()

    def open_advanced_equipment(self):
        dialog = AdvancedEquipmentDialog(self)
        dialog.exec()

    def open_sans_extended(self):
        dialog = SANSExtendedDialog(self)
        dialog.exec()

    def open_sans_cable_tables(self):
        dialog = SANSCableTablesDialog(self)
        dialog.exec()

    def open_sans_screening(self):
        dialog = SANSScreeningDialog(self)
        dialog.exec()

    def open_installation(self):
        dialog = InstallationDialog(self)
        dialog.exec()

    def open_field_records(self):
        dialog = FieldRecordsDialog(self.database, self)
        dialog.exec()

    def open_cables(self):
        """Open educational cable voltage-drop estimator."""
        dialog = CableDialog(self)
        dialog.exec()

    def open_protection(self):
        """Open educational fault-current estimator."""
        dialog = ProtectionDialog(self)
        dialog.exec()

    def open_power_factor(self):
        """Open educational power factor correction estimator."""
        dialog = PowerFactorDialog(self)
        dialog.exec()

    def open_reports(self):
        """Open calculation-based PDF report generator."""
        dialog = ReportDialog(self)
        dialog.exec()

    def open_workspace(self):
        """Open saved engineering project workspace."""
        dialog = WorkspaceDialog(self)
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