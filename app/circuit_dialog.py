"""Series and parallel resistor circuit analyzer."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox
from calculations.circuits import series_resistance, parallel_resistance


class CircuitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Circuit Analyzer")
        self.resize(460, 240)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Ideal DC resistor network"))
        self.mode = QComboBox()
        self.mode.addItems(["Series", "Parallel"])
        layout.addWidget(self.mode)
        layout.addWidget(QLabel("Resistances in ohms (comma-separated):"))
        self.resistances = QLineEdit()
        self.resistances.setPlaceholderText("e.g. 100, 220, 330")
        layout.addWidget(self.resistances)
        self.result = QLabel("Enter resistance values to calculate.")
        layout.addWidget(self.result)
        button = QPushButton("Calculate equivalent resistance")
        button.clicked.connect(self.calculate)
        layout.addWidget(button)

    def calculate(self):
        try:
            parts = self.resistances.text().split(",")
            if any(not part.strip() for part in parts):
                raise ValueError("Enter one or more comma-separated resistance values.")
            values = [float(part.strip()) for part in parts]
            function = series_resistance if self.mode.currentText() == "Series" else parallel_resistance
            answer = function(values)
        except (ValueError, OverflowError) as exc:
            self.result.setText("Invalid input")
            QMessageBox.warning(self, "Circuit calculation error", str(exc))
            return
        self.result.setText(f"Equivalent resistance: {answer:.8g} ohms")
