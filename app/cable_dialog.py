"""Educational conductor voltage-drop estimator."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QPushButton, QComboBox, QMessageBox
from calculations.cables import estimate_voltage_drop


class CableDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cable Voltage Drop Estimator")
        self.resize(560, 490)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Resistive voltage-drop estimate only; not cable sizing or code compliance."))
        self.material = QComboBox()
        self.material.addItems(["Copper", "Aluminium"])
        self.phases = QComboBox()
        self.phases.addItems(["Single-phase", "Three-phase (balanced)"])
        form = QFormLayout()
        form.addRow("Conductor material", self.material)
        form.addRow("Supply", self.phases)
        self.fields = []
        for name, default in (("Load current (A)", "20"), ("One-way length (m)", "30"),
                              ("Conductor area (mm2)", "4"), ("Supply voltage (V)", "230"),
                              ("Conductor temperature (C)", "70"), ("Power factor", "1")):
            field = QLineEdit(default)
            form.addRow(name, field)
            self.fields.append(field)
        layout.addLayout(form)
        self.result = QLabel("Enter values and calculate.")
        layout.addWidget(self.result)
        button = QPushButton("Estimate voltage drop")
        button.clicked.connect(self.calculate)
        layout.addWidget(button)
        layout.addWidget(QLabel("WARNING: Ignores reactance, installation method, derating, fault duty and protection."))
        layout.addWidget(QLabel("Verify cable ampacity and voltage-drop limits against applicable standards."))

    def calculate(self):
        try:
            values = [float(field.text().strip()) for field in self.fields]
            result = estimate_voltage_drop(*values[:4], material=self.material.currentText(),
                                           phases=3 if self.phases.currentIndex() else 1,
                                           conductor_temp_c=values[4], power_factor=values[5])
        except (ValueError, OverflowError, ZeroDivisionError) as exc:
            self.result.setText("Invalid cable input")
            QMessageBox.warning(self, "Cable calculation error", str(exc))
            return
        self.result.setText("\n".join((
            f"Estimated voltage drop: {result['voltage_drop_v']:.6g} V",
            f"Voltage drop: {result['voltage_drop_percent']:.6g}%",
            f"Estimated receiving voltage: {result['estimated_load_voltage_v']:.6g} V",
        )))
