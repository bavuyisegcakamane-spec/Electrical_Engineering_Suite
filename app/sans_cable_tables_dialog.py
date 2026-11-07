"""Narrow, explicitly verified SANS 10142-1:2017 cable table subset."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QComboBox, QLabel, QPushButton, QTextEdit, QMessageBox
from calculations.sans_reference_tables import (BURIED_PVC_COPPER_AMPACITY, SOIL_TEMPERATURE_70C,
                                                  BURIAL_DEPTH, buried_cable_lookup)


class SANSCableTablesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('SANS 10142-1:2017 Ed 2 - Buried Cable Table Subset')
        self.resize(700, 530)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Only multicore PVC-insulated copper armoured cable; Tables 6.8, 6.11 and 6.16.'))
        form = QFormLayout()
        self.area = QComboBox()
        self.area.addItems(str(x) for x in BURIED_PVC_COPPER_AMPACITY)
        self.cores = QComboBox()
        self.cores.addItems(('2', '3', '4'))
        self.installation = QComboBox()
        self.installation.addItems(('direct', 'pipe'))
        self.temperature = QComboBox()
        self.temperature.addItems(str(x) for x in SOIL_TEMPERATURE_70C)
        self.temperature.setCurrentText('25')
        self.depth = QComboBox()
        self.depth.addItems(str(x) for x in BURIAL_DEPTH)
        form.addRow('Copper cross-section (mm2)', self.area)
        form.addRow('Number of cores', self.cores)
        form.addRow('Direct buried or buried pipe', self.installation)
        form.addRow('Soil temperature (C)', self.temperature)
        form.addRow('Burial depth (m)', self.depth)
        layout.addLayout(form)
        button = QPushButton('Look up verified table subset')
        button.clicked.connect(self.calculate)
        layout.addWidget(button)
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        layout.addWidget(self.result)
        self.calculate()

    def calculate(self):
        try:
            result = buried_cable_lookup(float(self.area.currentText()), int(self.cores.currentText()),
                                         self.installation.currentText(), float(self.temperature.currentText()),
                                         float(self.depth.currentText()))
        except ValueError as exc:
            QMessageBox.warning(self, 'Invalid lookup', str(exc))
            return
        self.result.setPlainText('\n'.join(f'{key.replace("_", " ").title()}: {value}' for key, value in result.items()))
