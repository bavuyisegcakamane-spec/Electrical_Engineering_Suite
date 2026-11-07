#  ____      ___        __  ____   _______ _____ ____
# |  _ \\    / \\ \\      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \\ \\ /\\ / /  |  _ \\    | |    | | \\___ \\
# |  _ <  / ___ \\ V  V /   | |_) |   | |    | |  ___) |
# |_| \\_\\/_/   \\_\\_/\\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Preliminary water-pump control panel study UI."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QDoubleSpinBox, QSpinBox, QPushButton, QPlainTextEdit, QLabel, QHBoxLayout)
from calculations.pump_panel import Pump, PUMP_KW, STARTERS, study_panel
from database.pump_panel_components import conceptual_bom
from database.pump_panel_database import PumpPanelDatabase
from app.branding import BRAND_SIGNATURE


class PumpPanelDialog(QDialog):
    def __init__(self, parent=None, database=None):
        super().__init__(parent)
        self.panel_repository = PumpPanelDatabase(database) if database is not None else None
        self.setWindowTitle('raw.bytes | Water Pump Panel Study (Preliminary)')
        self.resize(850, 720)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(BRAND_SIGNATURE))
        layout.addWidget(QLabel('1-4 three-phase motors | 2.2-45 kW | DOL / Star-delta / Soft starter / VFD'))
        form = QFormLayout()
        self.count = QSpinBox(); self.count.setRange(1, 4); self.count.setValue(2)
        self.simultaneous = QSpinBox(); self.simultaneous.setRange(1, 4); self.simultaneous.setValue(2)
        self.count.valueChanged.connect(self._update_count)
        self.voltage = QDoubleSpinBox(); self.voltage.setRange(200, 690); self.voltage.setValue(400); self.voltage.setSuffix(' V')
        self.pf = QDoubleSpinBox(); self.pf.setRange(0.01, 1); self.pf.setDecimals(2); self.pf.setValue(0.85)
        self.efficiency = QDoubleSpinBox(); self.efficiency.setRange(0.01, 1); self.efficiency.setDecimals(2); self.efficiency.setValue(0.90)
        self.breaker = QDoubleSpinBox(); self.breaker.setRange(1, 2000); self.breaker.setValue(150); self.breaker.setSuffix(' A')
        for label, control in (('Installed pumps', self.count), ('Simultaneously running', self.simultaneous),
                               ('Line voltage', self.voltage), ('Motor power factor (assumed)', self.pf),
                               ('Motor efficiency (assumed)', self.efficiency), ('Main breaker rating', self.breaker)):
            form.addRow(label, control)
        layout.addLayout(form)
        self.motor_rows = []
        for index in range(4):
            line = QHBoxLayout()
            kw = QComboBox(); kw.addItems(str(x) for x in PUMP_KW); kw.setCurrentText('7.5')
            starter = QComboBox(); starter.addItems(STARTERS)
            label = QLabel(f'Pump {index + 1}')
            line.addWidget(label); line.addWidget(kw); line.addWidget(starter)
            layout.addLayout(line)
            self.motor_rows.append((label, kw, starter))
        self._update_count()
        calculate = QPushButton('Calculate preliminary panel running load')
        calculate.clicked.connect(self.calculate)
        layout.addWidget(calculate)
        if self.panel_repository is not None:
            save_button = QPushButton('Save draft panel and complete component checklist to database')
            save_button.clicked.connect(self.save_draft)
            layout.addWidget(save_button)
        self.output = QPlainTextEdit(); self.output.setReadOnly(True)
        layout.addWidget(self.output)
        self.calculate()

    def _update_count(self, *_):
        n = self.count.value()
        self.simultaneous.setMaximum(n)
        for index, row in enumerate(self.motor_rows):
            for widget in row:
                widget.setVisible(index < n)

    def save_draft(self):
        pumps = [Pump(float(kw.currentText()), starter.currentText(), f'Pump {i+1}')
                 for i, (_, kw, starter) in enumerate(self.motor_rows[:self.count.value()])]
        panel_id = self.panel_repository.create_panel('Pump panel draft', pumps,
                         self.voltage.value(), self.breaker.value())
        self.output.appendPlainText(f'\nSaved draft panel #{panel_id} with {len(self.panel_repository.get_bom(panel_id))} checklist rows. All selections remain unverified.')

    def calculate(self):
        pumps = [Pump(float(kw.currentText()), starter.currentText(), f'Pump {i+1}')
                 for i, (_, kw, starter) in enumerate(self.motor_rows[:self.count.value()])]
        result = study_panel(pumps, self.voltage.value(), self.pf.value(),
                             self.efficiency.value(), self.breaker.value(),
                             self.simultaneous.value())
        lines = [f'{p["name"]}: {p["power_kw"]} kW | {p["starter"]} | estimated FLC {p["estimated_running_a"]:.2f} A'
                 for p in result['pumps']]
        lines += ['', f'Installed motor running load: {result["installed_running_a"]:.2f} A',
                  f'Worst-case {result["simultaneous"]} simultaneous running: {result["simultaneous_running_a"]:.2f} A',
                  f'Main breaker: {result["main_breaker_a"]:.0f} A | running utilization {result["estimated_utilization_percent"]:.1f}%',
                  'RUNNING LOAD EXCEEDS MAIN RATING' if result['exceeds_main_rating'] else 'Running-load estimate below main rating (not a design approval)',
                  '', 'DESIGN WARNINGS:'] + [f'- {w}' for w in result['warnings']]
        bom = conceptual_bom([p.starter for p in pumps])
        lines += ['', 'CONCEPTUAL PANEL COMPONENT CHECKLIST (not sized):']
        lines += [f'- {item}' for item in bom['common']]
        for branch in bom['per_pump']:
            lines += [f'Pump {branch["pump"]} ({branch["starter"]}):']
            lines += [f'  - {item}' for item in branch['components']]
        self.output.setPlainText('\n'.join(lines))
