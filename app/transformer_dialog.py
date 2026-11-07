"""Ideal transformer calculator dialog."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QLabel, QPushButton, QMessageBox)
from calculations.transformers import analyze_transformer


class TransformerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ideal Transformer Calculator")
        self.resize(550, 420)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Single-phase ideal transformer: rated steady-state relationships"))
        form = QFormLayout()
        self.fields = []
        for label, default in (("Primary voltage (V)", "230"),
                               ("Primary turns", "1000"),
                               ("Secondary turns", "500"),
                               ("Rated apparent power (VA)", "1000")):
            field = QLineEdit(default)
            form.addRow(label, field)
            self.fields.append(field)
        layout.addLayout(form)
        button = QPushButton("Calculate transformer")
        button.clicked.connect(self.calculate)
        layout.addWidget(button)
        self.result = QLabel("Enter transformer parameters and calculate.")
        layout.addWidget(self.result)
        layout.addWidget(QLabel("WARNING: Ideal estimates exclude losses, voltage regulation,"))
        layout.addWidget(QLabel("inrush, saturation, thermal limits and protection requirements."))

    def calculate(self):
        try:
            values = [float(field.text().strip()) for field in self.fields]
            result = analyze_transformer(*values)
        except (ValueError, OverflowError, ZeroDivisionError) as exc:
            self.result.setText("Invalid transformer inputs")
            QMessageBox.warning(self, "Transformer calculation error", str(exc))
            return
        self.result.setText("\n".join((
            f"Turns ratio Np/Ns: {result['turns_ratio_primary_to_secondary']:.6g}",
            f"Secondary voltage: {result['secondary_voltage_v']:.6g} V",
            f"Rated primary current: {result['primary_rated_current_a']:.6g} A",
            f"Rated secondary current: {result['secondary_rated_current_a']:.6g} A",
            f"Ideal apparent power (both sides): {result['rated_apparent_power_va']:.6g} VA",
        )))
