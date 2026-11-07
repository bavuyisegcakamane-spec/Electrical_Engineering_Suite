"""SANS 10142-1:2017 Ed 2 partial numeric screening interface."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
                               QPushButton, QMessageBox, QTextEdit, QScrollArea, QWidget, QLabel)
from calculations.sans_screening import assess_cable_and_protection

FIELDS = (
    ('Supply voltage (V)', '230'), ('Design current (A)', '20'),
    ('Tabulated ampacity (A) - verified source', '32'),
    ('Ambient correction factor', '0.9'), ('Grouping correction factor', '0.85'),
    ('Other applicable correction factor (combined)', '1'),
    ('TOTAL installation voltage drop (V)', '7'),
    ('Protective device rated current (A)', '20'),
    ('Device breaking capacity (kA)', '6'),
    ('Prospective short-circuit current (kA)', '3'),
)


class SANSScreeningDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('SANS 10142-1:2017 Ed 2 - Partial Installation Screening')
        self.resize(760, 680)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Partial checks only. Enter values verified from tables, device data and site measurements.'))
        self.supply_type = QComboBox()
        self.supply_type.addItems(('AC', 'DC'))
        layout.addWidget(self.supply_type)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        form = QFormLayout(body)
        self.fields = []
        for label, default in FIELDS:
            field = QLineEdit(default)
            form.addRow(label, field)
            self.fields.append(field)
        scroll.setWidget(body)
        layout.addWidget(scroll)
        button = QPushButton('Run partial checks')
        button.clicked.connect(self.calculate)
        layout.addWidget(button)
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        layout.addWidget(self.result)
        self.calculate()

    def calculate(self):
        try:
            values = [float(field.text().strip()) for field in self.fields]
            result = assess_cable_and_protection(*values, supply_type=self.supply_type.currentText())
        except (ValueError, OverflowError, ZeroDivisionError) as exc:
            QMessageBox.warning(self, 'Invalid inputs', str(exc))
            return
        lines = [result['reference'], f"Corrected ampacity: {result['effective_ampacity_a']:.5g} A",
                 f"Total voltage drop: {result['voltage_drop_percent']:.5g}%", '',
                 'PARTIAL NUMERIC CHECKS (NOT A COMPLIANCE CERTIFICATE)']
        lines.extend(f"{'PASS' if passed else 'REVIEW'}: {key.replace('_', ' ')}" for key, passed in result['checks'].items())
        lines.extend(('', result['compliance_status'], '', 'STILL REQUIRES VERIFICATION:'))
        lines.extend('- ' + item for item in result['required_verification'])
        self.result.setPlainText('\n'.join(lines))
