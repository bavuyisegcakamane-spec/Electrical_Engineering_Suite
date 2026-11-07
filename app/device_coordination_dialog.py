"""Local manufacturer curve envelope review (CSV input)."""
from pathlib import Path
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
                               QTextEdit, QFileDialog, QMessageBox, QLabel)
from calculations.device_coordination import review_device_coordination


class DeviceCoordinationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Manufacturer Device Curves - Preliminary Coordination')
        self.resize(780, 620)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('CSV format: current_a,min_trip_s,max_trip_s. Use documented manufacturer envelopes.'))
        form = QFormLayout()
        self.source = QLineEdit()
        self.source.setPlaceholderText('Manufacturer, model, settings, datasheet revision')
        self.current = QLineEdit('1000')
        self.limit = QLineEdit('0.4')
        form.addRow('Curve source / model', self.source)
        form.addRow('Prospective fault current (A)', self.current)
        form.addRow('Externally verified required disconnection time (s)', self.limit)
        layout.addLayout(form)
        self.csv_paths = {}
        for key in ('upstream', 'downstream'):
            button = QPushButton(f'Choose {key} device curve CSV')
            button.clicked.connect(lambda _=False, which=key: self.choose(which))
            layout.addWidget(button)
        run = QPushButton('Compare documented trip envelopes')
        run.clicked.connect(self.calculate)
        layout.addWidget(run)
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.result.setPlainText('Select both CSV files and supply manufacturer identification.')
        layout.addWidget(self.result)

    def choose(self, which):
        filename, _ = QFileDialog.getOpenFileName(self, 'Select manufacturer curve', '', 'CSV files (*.csv)')
        if filename:
            self.csv_paths[which] = filename
            self.result.append(f'{which.title()} curve selected: {Path(filename).name}')

    def calculate(self):
        try:
            if set(self.csv_paths) != {'upstream', 'downstream'}:
                raise ValueError('Both manufacturer curve files are required')
            result = review_device_coordination(
                Path(self.csv_paths['upstream']).read_text(encoding='utf-8-sig'),
                Path(self.csv_paths['downstream']).read_text(encoding='utf-8-sig'),
                float(self.current.text()), float(self.limit.text()), self.source.text())
        except (ValueError, OSError) as exc:
            QMessageBox.warning(self, 'Review cannot proceed', str(exc))
            return
        self.result.setPlainText('\n'.join(f'{key}: {value}' for key, value in result.items()))
