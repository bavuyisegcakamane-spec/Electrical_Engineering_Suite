"""Interactive calculator using the shared engineering calculation engine."""
import math
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QComboBox, QLineEdit, QLabel, QPushButton, QMessageBox
from calculations import calculate_voltage, calculate_current, calculate_resistance, calculate_power_vi, calculate_power_ir, calculate_power_vr, calculate_energy

OPERATIONS = {
    "Voltage (V = I × R)": (calculate_voltage, ("Current (A)", "Resistance (Ω)"), "V"),
    "Current (I = V / R)": (calculate_current, ("Voltage (V)", "Resistance (Ω)"), "A"),
    "Resistance (R = V / I)": (calculate_resistance, ("Voltage (V)", "Current (A)"), "Ω"),
    "Power (P = V × I)": (calculate_power_vi, ("Voltage (V)", "Current (A)"), "W"),
    "Power (P = I² × R)": (calculate_power_ir, ("Current (A)", "Resistance (Ω)"), "W"),
    "Power (P = V² / R)": (calculate_power_vr, ("Voltage (V)", "Resistance (Ω)"), "W"),
    "Energy (E = P × t)": (calculate_energy, ("Power (W)", "Time (hours)"), "Wh"),
}

class CalculatorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Engineering Calculations")
        self.resize(430, 260)
        layout = QVBoxLayout(self)
        self.operation = QComboBox()
        self.operation.addItems(OPERATIONS)
        layout.addWidget(self.operation)
        form = QFormLayout()
        self.first = QLineEdit()
        self.second = QLineEdit()
        self.first_label = QLabel()
        self.second_label = QLabel()
        form.addRow(self.first_label, self.first)
        form.addRow(self.second_label, self.second)
        layout.addLayout(form)
        self.result = QLabel("Enter two values and select Calculate.")
        layout.addWidget(self.result)
        button = QPushButton("Calculate")
        button.clicked.connect(self.calculate)
        layout.addWidget(button)
        self.operation.currentTextChanged.connect(self.update_labels)
        self.update_labels()

    def update_labels(self, *_):
        _, labels, _ = OPERATIONS[self.operation.currentText()]
        self.first_label.setText(labels[0])
        self.second_label.setText(labels[1])
        self.result.setText("Enter two values and select Calculate.")

    def calculate(self):
        function, _, unit = OPERATIONS[self.operation.currentText()]
        try:
            values = (float(self.first.text().strip()), float(self.second.text().strip()))
            if not all(math.isfinite(value) for value in values):
                raise ValueError("Inputs must be finite numbers.")
            answer = function(*values)
            if not math.isfinite(answer):
                raise ValueError("Result is outside the supported numeric range.")
        except (ValueError, OverflowError, ZeroDivisionError) as exc:
            self.result.setText("Invalid input")
            QMessageBox.warning(self, "Calculation error", str(exc))
            return
        self.result.setText(f"Result: {answer:.8g} {unit}")
