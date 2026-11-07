"""Generate calculation reports directly from existing calculation engines."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QLabel, QPushButton, QComboBox, QFileDialog, QMessageBox)
from calculations.loads import calculate_load
from calculations.motors import analyze_motor
from calculations.power_factor import estimate_correction
from calculations.cables import estimate_voltage_drop
from calculations.protection import estimate_fault_current
from reports.pdf_report import create_pdf_report

# Field labels include their units. Input ordering matches each calculation engine.
CONFIG = {
    "Electrical load": (["Power per item (W)", "Quantity", "Voltage (V)", "Power factor", "Hours", "Phases (1 or 3)", "Demand factor"],
                        ["1000", "2", "230", "0.9", "2", "1", "1"], calculate_load,
                        ["Balanced load if three phase", "Voltage is L-N for single phase, L-L for three phase", "Energy assumes constant demand load"]),
    "Three-phase motor": (["Output (kW)", "Voltage L-L (V)", "Efficiency", "Power factor", "Speed (RPM)"],
                          ["7.5", "400", "0.9", "0.85", "1450"], analyze_motor,
                          ["Balanced three-phase rated steady-state", "No starting or protection calculations"]),
    "Power factor correction": (["Real power (kW)", "Voltage L-L (V)", "Initial PF", "Target PF"],
                                ["100", "400", "0.8", "0.95"], estimate_correction,
                                ["Balanced three-phase, lagging PF", "Ideal correction; no harmonic or resonance analysis"]),
    "Cable voltage drop": (["Current (A)", "One-way length (m)", "Area (mm2)", "Voltage (V)"],
                           ["20", "30", "4", "230"], estimate_voltage_drop,
                           ["Copper, single-phase, 20 C, unity PF", "Resistive drop only; not cable ampacity or compliance"]),
    "Fault current": (["Voltage (V)", "Assumed impedance (ohms)", "Breaker rating (A)", "Breaking capacity (kA)"],
                      ["230", "0.1", "32", "6"], estimate_fault_current,
                      ["Single-phase simplified symmetrical RMS estimate", "Not a device selection, coordination or compliance study"]),
}


class ReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Engineering PDF Report Generator")
        self.resize(590, 490)
        layout = QVBoxLayout(self)
        self.title_field = QLineEdit("Electrical Engineering Calculation Report")
        layout.addWidget(QLabel("Report title"))
        layout.addWidget(self.title_field)
        self.selector = QComboBox()
        self.selector.addItems(CONFIG)
        layout.addWidget(self.selector)
        self.form = QFormLayout()
        self.fields = []
        self.field_labels = []
        for _ in range(7):
            field = QLineEdit()
            self.fields.append(field)
            label = QLabel("")
            self.field_labels.append(label)
            self.form.addRow(label, field)
        layout.addLayout(self.form)
        self.selector.currentTextChanged.connect(self.update_fields)
        self.update_fields()
        layout.addWidget(QLabel("PDF includes entered inputs, computed results, assumptions and safety warning."))
        button = QPushButton("Calculate and save PDF")
        button.clicked.connect(self.save_report)
        layout.addWidget(button)

    def update_fields(self, *_):
        labels, defaults, _, _ = CONFIG[self.selector.currentText()]
        for i, field in enumerate(self.fields):
            active = i < len(labels)
            field.setVisible(active)
            self.field_labels[i].setVisible(active)
            if active:
                self.field_labels[i].setText(labels[i])
                field.setText(defaults[i])

    def build_data(self):
        name = self.selector.currentText()
        labels, _, calculator, assumptions = CONFIG[name]
        values = [float(self.fields[i].text().strip()) for i in range(len(labels))]
        if name == "Electrical load":
            if not values[1].is_integer() or values[1] < 1 or values[5] not in (1, 3):
                raise ValueError("Quantity must be a positive integer and phases must be 1 or 3.")
            values[1], values[5] = int(values[1]), int(values[5])
        results = calculator(*values)
        return name, dict(zip(labels, values)), {k.replace('_', ' '): f"{v:.6g}" if isinstance(v, float) else str(v) for k, v in results.items()}, assumptions

    def save_report(self):
        try:
            name, inputs, outputs, assumptions = self.build_data()
            if not self.title_field.text().strip():
                raise ValueError("Report title is required.")
        except (ValueError, OverflowError, ZeroDivisionError) as exc:
            QMessageBox.warning(self, "Invalid report inputs", str(exc))
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save engineering report", "engineering_report.pdf", "PDF Files (*.pdf)")
        if not path:
            return
        if not path.lower().endswith('.pdf'):
            path += '.pdf'
        try:
            create_pdf_report(path, self.title_field.text(), name, inputs, outputs, assumptions)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "PDF creation failed", str(exc))
            return
        QMessageBox.information(self, "Report saved", f"PDF saved to:\n{path}")
