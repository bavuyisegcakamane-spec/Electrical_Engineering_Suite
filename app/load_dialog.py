"""Basic single/three-phase electrical load calculator."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QPushButton, QComboBox, QMessageBox
from calculations.loads import calculate_load


class LoadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Electrical Load Calculator")
        self.resize(490, 420)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Balanced AC load estimate (real input watts per item)"))
        self.phases = QComboBox()
        self.phases.addItems(["Single-phase", "Three-phase (balanced)"])
        layout.addWidget(self.phases)
        form = QFormLayout()
        self.inputs = []
        for label, default in (("Power per item (W)", "1000"), ("Quantity", "1"),
                               ("Voltage (V)", "230"), ("Power factor", "0.9"),
                               ("Hours at demand load", "2"), ("Demand factor (0-1)", "1")):
            field = QLineEdit(default)
            form.addRow(label, field)
            self.inputs.append(field)
        layout.addLayout(form)
        layout.addWidget(QLabel("Voltage: L-N for single phase; L-L for three phase."))
        self.result = QLabel("Enter values and select Calculate.")
        layout.addWidget(self.result)
        button = QPushButton("Calculate load")
        button.clicked.connect(self.calculate)
        layout.addWidget(button)

    def calculate(self):
        try:
            power = float(self.inputs[0].text())
            quantity_text = self.inputs[1].text().strip()
            quantity = int(quantity_text)
            if str(quantity) != quantity_text:
                raise ValueError("Quantity must be a positive whole number.")
            voltage, pf, hours, demand = (float(field.text()) for field in self.inputs[2:])
            result = calculate_load(power, quantity, voltage, pf, hours,
                                    3 if self.phases.currentIndex() else 1, demand)
        except (ValueError, OverflowError, ZeroDivisionError) as exc:
            self.result.setText("Invalid load input")
            QMessageBox.warning(self, "Load calculation error", str(exc))
            return
        self.result.setText("\n".join((
            f"Connected load: {result['connected_watts'] / 1000:.6g} kW",
            f"Demand load: {result['demand_watts'] / 1000:.6g} kW",
            f"Estimated line current: {result['line_current_amps']:.6g} A",
            f"Estimated energy: {result['energy_kwh']:.6g} kWh",
        )))
