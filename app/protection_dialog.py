"""Educational fault-current analysis UI with explicit safety limitations."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QPushButton, QComboBox, QMessageBox
from calculations.protection import estimate_fault_current


class ProtectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Protection and Fault Current (Educational)")
        self.resize(610, 470)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Simplified prospective symmetrical RMS fault current"))
        self.phases = QComboBox()
        self.phases.addItems(["Single-phase L-N", "Three-phase L-L (balanced)"])
        form = QFormLayout()
        form.addRow("Supply type", self.phases)
        self.fields = []
        for label, default in (("Nominal voltage (V)", "230"),
                               ("Assumed fault-loop impedance (ohms)", "0.1"),
                               ("Breaker nominal current (A)", "32"),
                               ("Stated breaking capacity (kA)", "6")):
            field = QLineEdit(default)
            form.addRow(label, field)
            self.fields.append(field)
        layout.addLayout(form)
        self.result = QLabel("Enter assumed values and select Estimate.")
        layout.addWidget(self.result)
        button = QPushButton("Estimate fault current")
        button.clicked.connect(self.calculate)
        layout.addWidget(button)
        layout.addWidget(QLabel("WARNING: Not a protective device selection or compliance tool."))
        layout.addWidget(QLabel("No trip curves, disconnection times, selectivity, thermal withstand, or arc-flash analysis."))
        layout.addWidget(QLabel("Qualified engineers must verify fault levels, installation details and applicable standards."))

    def calculate(self):
        try:
            values = [float(field.text().strip()) for field in self.fields]
            result = estimate_fault_current(*values, phases=3 if self.phases.currentIndex() else 1)
        except (ValueError, OverflowError, ZeroDivisionError) as exc:
            self.result.setText("Invalid protection input")
            QMessageBox.warning(self, "Fault-current estimation error", str(exc))
            return
        capacity_message = ("ABOVE stated breaking capacity: investigate with qualified engineer"
                            if result["exceeds_stated_breaking_capacity"] else
                            "Below stated breaking capacity in this simplified model; NOT a safety approval")
        self.result.setText("\n".join((
            f"Estimated fault current: {result['fault_current_amps']:.6g} A ({result['fault_current_ka']:.6g} kA)",
            f"Fault current / breaker nominal current: {result['fault_to_rating_ratio']:.6g} x",
            capacity_message,
        )))
