"""Three-phase motor operating-point calculator."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QPushButton, QMessageBox
from calculations.motors import analyze_motor


class MotorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Three-Phase Motor Analysis")
        self.resize(510, 420)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Balanced three-phase motor, rated steady-state estimate"))
        form = QFormLayout()
        self.inputs = []
        for label, default in (("Shaft output power (kW)", "7.5"),
                               ("Line-to-line voltage (V)", "400"),
                               ("Efficiency (0-1)", "0.9"),
                               ("Power factor (0-1)", "0.85"),
                               ("Shaft speed (RPM)", "1450")):
            field = QLineEdit(default)
            form.addRow(label, field)
            self.inputs.append(field)
        layout.addLayout(form)
        self.result = QLabel("Enter motor nameplate/estimated values and select Analyze.")
        layout.addWidget(self.result)
        button = QPushButton("Analyze motor")
        button.clicked.connect(self.calculate)
        layout.addWidget(button)
        layout.addWidget(QLabel("Not for motor starting current, cable sizing, or protection selection."))

    def calculate(self):
        try:
            values = [float(field.text().strip()) for field in self.inputs]
            result = analyze_motor(*values)
        except (ValueError, OverflowError, ZeroDivisionError) as exc:
            self.result.setText("Invalid motor input")
            QMessageBox.warning(self, "Motor calculation error", str(exc))
            return
        self.result.setText("\n".join((
            f"Input real power: {result['input_kw']:.6g} kW",
            f"Apparent power: {result['apparent_kva']:.6g} kVA",
            f"Rated line current: {result['line_current_amps']:.6g} A",
            f"Reactive power: {result['reactive_kvar']:.6g} kVAr",
            f"Shaft torque: {result['shaft_torque_nm']:.6g} N m",
            f"Estimated losses: {result['losses_kw']:.6g} kW",
        )))
