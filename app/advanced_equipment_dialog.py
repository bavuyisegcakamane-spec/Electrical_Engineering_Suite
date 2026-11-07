"""Advanced educational transformer and motor calculations."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QComboBox, QFormLayout, QLineEdit,
                               QLabel, QPushButton, QMessageBox, QScrollArea, QWidget)
from calculations.advanced_equipment import transformer_performance, motor_starting_estimate

CONFIG = {
    "Transformer performance": (
        ("Rated kVA", "Load fraction (1 = full)", "Power factor", "Core loss (W)",
         "Full-load copper loss (W)", "No-load secondary voltage (V)", "Full-load secondary voltage (V)"),
        ("100", "0.75", "0.9", "400", "900", "415", "400"), transformer_performance),
    "Induction motor starting estimate": (
        ("Rated current (A)", "Starting current multiplier", "Starting duration (s)",
         "Rated speed (rpm)", "Synchronous speed (rpm)"),
        ("20", "6", "5", "1450", "1500"), motor_starting_estimate),
}


class AdvancedEquipmentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Equipment Estimates")
        self.resize(610, 550)
        layout = QVBoxLayout(self)
        self.selector = QComboBox()
        self.selector.addItems(CONFIG)
        self.selector.currentTextChanged.connect(self.configure)
        layout.addWidget(self.selector)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        self.form = QFormLayout(body)
        scroll.setWidget(body)
        layout.addWidget(scroll)
        self.fields = []
        calculate = QPushButton("Calculate")
        calculate.clicked.connect(self.calculate)
        layout.addWidget(calculate)
        self.result = QLabel("Enter parameters and calculate.")
        layout.addWidget(self.result)
        layout.addWidget(QLabel("Estimates only: not validated for equipment selection or protection settings."))
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
            result = function(*(float(field.text()) for field in self.fields))
        except (ValueError, OverflowError, ZeroDivisionError) as exc:
            QMessageBox.warning(self, "Calculation error", str(exc))
            return
        self.result.setText("\n".join(f"{key.replace('_', ' ').title()}: {value:.6g}" for key, value in result.items()))
