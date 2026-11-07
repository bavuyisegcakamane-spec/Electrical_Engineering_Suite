"""Educational power factor correction calculator UI."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QPushButton, QMessageBox
from calculations.power_factor import estimate_correction


class PowerFactorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Power Factor Correction")
        self.resize(580, 450)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Balanced three-phase, lagging power factor, ideal compensation"))
        form = QFormLayout()
        self.fields = []
        for label, default in (("Real load power (kW)", "100"),
                               ("Line-to-line voltage (V)", "400"),
                               ("Initial power factor", "0.8"),
                               ("Target power factor", "0.95")):
            field = QLineEdit(default)
            form.addRow(label, field)
            self.fields.append(field)
        layout.addLayout(form)
        self.result = QLabel("Enter values and select Calculate.")
        layout.addWidget(self.result)
        button = QPushButton("Calculate correction")
        button.clicked.connect(self.calculate)
        layout.addWidget(button)
        layout.addWidget(QLabel("WARNING: Estimated kVAr is not a capacitor-bank specification."))
        layout.addWidget(QLabel("Check harmonics, resonance, switching, load profile and applicable standards."))

    def calculate(self):
        try:
            values = [float(field.text().strip()) for field in self.fields]
            result = estimate_correction(*values)
        except (ValueError, OverflowError, ZeroDivisionError) as exc:
            self.result.setText("Invalid power factor input")
            QMessageBox.warning(self, "Power factor calculation error", str(exc))
            return
        self.result.setText("\n".join((
            f"Ideal reactive compensation: {result['required_compensation_kvar']:.6g} kVAr",
            f"Apparent power: {result['initial_apparent_kva']:.6g} to {result['target_apparent_kva']:.6g} kVA",
            f"Line current: {result['initial_line_current_amps']:.6g} to {result['target_line_current_amps']:.6g} A",
            f"Estimated current reduction: {result['line_current_reduction_amps']:.6g} A",
        )))
