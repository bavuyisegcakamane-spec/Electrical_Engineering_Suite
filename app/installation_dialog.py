#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Installation screening tools with explicit user-supplied assumptions."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QFormLayout, QLineEdit, QLabel, QPushButton, QMessageBox
from calculations.installation_assessment import cable_screening, earth_fault_loop_screening, validate_installation_voltage

CONFIG = {
    "Cable ampacity / voltage-drop screening": (
        ("Design current (A)", "Reference ampacity (A)", "Combined derating factor", "One-way length (m)", "Conductor resistance (ohms/km)", "Nominal voltage (V)"),
        ("20", "32", "0.8", "30", "1.15", "230"), cable_screening),
    "Earth fault-loop screening": (
        ("Line-to-earth voltage (V)", "Measured loop impedance (ohms)", "User-supplied assumed disconnection current (A)"),
        ("230", "0.8", "100"), earth_fault_loop_screening),
}


class InstallationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cable / Earthing / Protection Screening")
        self.resize(680, 490)
        layout = QVBoxLayout(self)
        self.selector = QComboBox()
        self.selector.addItems(CONFIG)
        self.selector.currentTextChanged.connect(self.configure)
        layout.addWidget(self.selector)
        self.supply_type = QComboBox()
        self.supply_type.addItems(('AC', 'DC'))
        layout.addWidget(QLabel('Supply type (cable screening only; earth-fault loop is AC only)'))
        layout.addWidget(self.supply_type)
        layout.addWidget(QLabel('SANS 10142-1:2017 Ed 2 scope: up to 1000 V AC / 1500 V DC'))
        self.form = QFormLayout()
        layout.addLayout(self.form)
        self.fields = []
        button = QPushButton("Calculate screening estimate")
        button.clicked.connect(self.calculate)
        layout.addWidget(button)
        self.result = QLabel("Enter assumptions and calculate.")
        layout.addWidget(self.result)
        layout.addWidget(QLabel("WARNING: Not a cable selection, disconnection-time or compliance determination."))
        layout.addWidget(QLabel("Verify installation method, tables, harmonics, fault withstand and local standards."))
        self.configure(self.selector.currentText())

    def configure(self, name):
        while self.form.rowCount():
            self.form.removeRow(0)
        self.fields = []
        labels, defaults, _ = CONFIG[name]
        for label, default in zip(labels, defaults):
            field = QLineEdit(default)
            self.form.addRow(label, field)
            self.fields.append(field)

    def calculate(self):
        try:
            _, _, function = CONFIG[self.selector.currentText()]
            values = [float(field.text()) for field in self.fields]
            if function is cable_screening:
                result = function(*values, supply_type=self.supply_type.currentText())
            else:
                if self.supply_type.currentText() != 'AC':
                    raise ValueError('Earth-fault loop screening currently supports AC only')
                result = function(*values)
        except (ValueError, OverflowError, ZeroDivisionError) as exc:
            QMessageBox.warning(self, "Invalid inputs", str(exc))
            return
        self.result.setText("\n".join(f"{key.replace('_', ' ').title()}: {value:.6g}" if isinstance(value, float) else f"{key.replace('_', ' ').title()}: {value}" for key, value in result.items()))
