#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""AC power, series RLC and insulation-resistance educational calculators."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox,
                               QLineEdit, QLabel, QPushButton, QMessageBox)
from calculations.ac_engineering import ac_impedance, three_phase_power, insulation_resistance

CONFIG = {
    "Balanced three-phase power": (["Line voltage (V)", "Line current (A)", "Power factor"],
                                   ["400", "10", "0.85"], three_phase_power),
    "Series RLC impedance": (["Resistance (ohms)", "Inductance (H)", "Capacitance (F)", "Frequency (Hz)"],
                             ["10", "0.1", "0.0001", "50"], ac_impedance),
    "Insulation resistance estimate": (["DC test voltage (V)", "Leakage current (microamps)"],
                                       ["500", "5"], insulation_resistance),
}


class ACEngineeringDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Additional Electrical Calculations")
        self.resize(560, 470)
        layout = QVBoxLayout(self)
        self.selector = QComboBox()
        self.selector.addItems(CONFIG)
        self.selector.currentTextChanged.connect(self.configure)
        layout.addWidget(self.selector)
        self.form = QFormLayout()
        layout.addLayout(self.form)
        self.fields = []
        button = QPushButton("Calculate")
        button.clicked.connect(self.calculate)
        layout.addWidget(button)
        self.output = QLabel("Results appear here.")
        layout.addWidget(self.output)
        layout.addWidget(QLabel("Educational estimates only. Not a substitute for certified testing or design."))
        self.configure(self.selector.currentText())

    def configure(self, selection):
        while self.form.count():
            item = self.form.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.fields = []
        labels, defaults, _ = CONFIG[selection]
        for label, default in zip(labels, defaults):
            field = QLineEdit(default)
            self.form.addRow(label, field)
            self.fields.append(field)

    def calculate(self):
        try:
            labels, _, function = CONFIG[self.selector.currentText()]
            values = [float(field.text().strip()) for field in self.fields]
            result = function(*values)
        except (ValueError, OverflowError, ZeroDivisionError) as exc:
            QMessageBox.warning(self, "Invalid inputs", str(exc))
            return
        self.output.setText("\n".join(f"{key.replace('_', ' ').title()}: {value:.6g}" for key, value in result.items()))
