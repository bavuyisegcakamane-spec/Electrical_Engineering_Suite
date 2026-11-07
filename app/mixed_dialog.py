#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Mixed series-parallel circuit analysis with schematic and branch results."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QPushButton, QMessageBox
from calculations.mixed_circuits import analyze_mixed


class MixedCircuitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mixed Circuit Analyzer")
        self.resize(510, 410)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Circuit topology: R1 in series with R2 and R3 in parallel"))
        schematic = QLabel("+V --- [R1] ---+--- [R2] ---+--- 0V\n               |            |\n               +--- [R3] ---+")
        schematic.setStyleSheet("font-family: Consolas, monospace; white-space: pre;")
        layout.addWidget(schematic)
        form = QFormLayout()
        self.inputs = []
        for label, default in (("Supply voltage (V)", "12"), ("R1 (ohms)", "100"), ("R2 (ohms)", "200"), ("R3 (ohms)", "200")):
            field = QLineEdit(default)
            form.addRow(label, field)
            self.inputs.append(field)
        layout.addLayout(form)
        self.result = QLabel("Select Analyze to calculate voltage and current.")
        self.result.setTextInteractionFlags(self.result.textInteractionFlags())
        layout.addWidget(self.result)
        button = QPushButton("Analyze circuit")
        button.clicked.connect(self.calculate)
        layout.addWidget(button)

    def calculate(self):
        try:
            result = analyze_mixed(*(float(field.text().strip()) for field in self.inputs))
        except (ValueError, OverflowError, ZeroDivisionError) as exc:
            self.result.setText("Invalid circuit input")
            QMessageBox.warning(self, "Circuit analysis error", str(exc))
            return
        self.result.setText("\n".join((
            f"Equivalent resistance: {result['equivalent_resistance']:.8g} ohms",
            f"Source / R1 current: {result['source_current']:.8g} A",
            f"Voltage across R1: {result['r1_voltage']:.8g} V",
            f"Voltage across R2 and R3: {result['parallel_voltage']:.8g} V",
            f"Current through R2: {result['r2_current']:.8g} A",
            f"Current through R3: {result['r3_current']:.8g} A",
        )))
