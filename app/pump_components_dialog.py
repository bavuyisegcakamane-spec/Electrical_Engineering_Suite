#  ____      ___        __  ____   _______ _____ ____
# |  _ \\    / \\ \\      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \\ \\ /\\ / /  |  _ \\    | |    | | \\___ \\
# |  _ <  / ___ \\ V  V /   | |_) |   | |    | |  ___) |
# |_| \\_\\/_/   \\_\\_/\\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Pump panel component requirements and saved panel BOM browser."""
import csv
from urllib.parse import quote_plus
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QTabWidget, QWidget,
    QMessageBox, QPlainTextEdit, QSpinBox, QAbstractItemView, QDoubleSpinBox, QFormLayout)
from calculations.pump_panel import Pump, PUMP_KW, STARTERS
from database.pump_panel_database import PumpPanelDatabase
from database.lv_panel_materials import PANEL_MATERIALS
from database.equipment_catalog import EquipmentCatalog
from database.pump_manufacturer_models import seed_pump_manufacturer_models
from app.branding import BRAND_SIGNATURE


class PumpComponentsDialog(QDialog):
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.setWindowTitle('raw.bytes | Pump Panel Component Database')
        self.resize(1100, 740)
        self.repo = PumpPanelDatabase(database)
        self.catalog = EquipmentCatalog(database)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(BRAND_SIGNATURE))
        layout.addWidget(QLabel('Component requirements are generic. Manufacturer models and electrical ratings must be verified before selection.'))
        tabs = QTabWidget(); layout.addWidget(tabs)
        types_page = QWidget(); types_layout = QVBoxLayout(types_page)
        self.search = QLineEdit(); self.search.setPlaceholderText('Search panel components')
        self.search.textChanged.connect(self.refresh_types)
        types_layout.addWidget(self.search)
        self.category = QComboBox()
        self.category.addItems(['All categories'] + list(PANEL_MATERIALS))
        self.category.currentIndexChanged.connect(self.refresh_types)
        types_layout.addWidget(self.category)
        self.types_table = QTableWidget(0, 3)
        self.types_table.setHorizontalHeaderLabels(('Component', 'Scope', 'Description'))
        self.types_table.setColumnWidth(0, 450)
        self.types_table.setColumnWidth(1, 120)
        self.types_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.types_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.types_table.cellDoubleClicked.connect(self.add_selected_component)
        types_layout.addWidget(self.types_table)
        self.add_selected_button = QPushButton('Add highlighted component to saved panel BOM')
        self.add_selected_button.clicked.connect(self.add_selected_component)
        types_layout.addWidget(self.add_selected_button)
        types_layout.addWidget(QLabel('Select a saved panel on the Saved panel BOMs tab first. Double-click a component here to add it.'))
        tabs.addTab(types_page, 'All panel components')
        panels_page = QWidget(); panels_layout = QVBoxLayout(panels_page)
        selector = QHBoxLayout()
        self.panel = QComboBox(); self.panel.currentIndexChanged.connect(self.refresh_bom)
        selector.addWidget(QLabel('Saved panel'))
        selector.addWidget(self.panel)
        refresh = QPushButton('Refresh saved panels'); refresh.clicked.connect(self.refresh_panels)
        selector.addWidget(refresh)
        create = QPushButton('Create new panel')
        create.clicked.connect(self.create_panel_dialog)
        selector.addWidget(create)
        panels_layout.addLayout(selector)
        self.bom_table = QTableWidget(0, 6)
        self.bom_table.setHorizontalHeaderLabels(('Pump', 'Component', 'Qty', 'Requirement', 'Selected catalogue ID', 'Verification'))
        self.bom_table.setColumnWidth(1, 440)
        self.bom_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        panels_layout.addWidget(self.bom_table)
        model_row = QHBoxLayout()
        self.models = QComboBox()
        model_row.addWidget(QLabel('Manufacturer model'))
        model_row.addWidget(self.models)
        load_models = QPushButton('Load manufacturer starter references')
        load_models.clicked.connect(self.load_models)
        model_row.addWidget(load_models)
        panels_layout.addLayout(model_row)
        material_row = QHBoxLayout()
        self.material_category = QComboBox()
        self.material_category.addItems(list(PANEL_MATERIALS))
        self.material_category.currentIndexChanged.connect(self.refresh_material_choices)
        material_row.addWidget(self.material_category)
        self.material_choice = QComboBox()
        material_row.addWidget(self.material_choice)
        self.material_quantity = QSpinBox()
        self.material_quantity.setRange(1, 9999)
        material_row.addWidget(self.material_quantity)
        add_material = QPushButton('Add material to panel BOM (review required)')
        add_material.clicked.connect(self.add_material)
        material_row.addWidget(add_material)
        panels_layout.addLayout(material_row)
        self.notes = QPlainTextEdit()
        self.notes.setPlaceholderText('Required sizing and coordination review notes (unverified)')
        self.notes.setMaximumHeight(75)
        panels_layout.addWidget(self.notes)
        assign = QPushButton('Assign selected model to highlighted BOM row (UNVERIFIED)')
        assign.clicked.connect(self.assign_model)
        panels_layout.addWidget(assign)
        export = QPushButton('Export automatic BOM to CSV')
        export.clicked.connect(self.export_bom)
        panels_layout.addWidget(export)
        tabs.addTab(panels_page, 'Saved panel BOMs')
        search_page = QWidget(); search_layout = QVBoxLayout(search_page)
        search_layout.addWidget(QLabel('Search exact manufacturer part numbers, ratings and datasheets online. Results open in your browser; verify OEM sources before use.'))
        self.web_query = QLineEdit()
        self.web_query.setPlaceholderText('e.g. Schneider ATV320D22N4C 400V datasheet')
        search_layout.addWidget(self.web_query)
        search_btn = QPushButton('Search equipment on the internet')
        search_btn.clicked.connect(self.search_equipment_online)
        search_layout.addWidget(search_btn)
        from_bom = QPushButton('Use highlighted BOM component as search term')
        from_bom.clicked.connect(self.search_from_bom)
        search_layout.addWidget(from_bom)
        tabs.addTab(search_page, 'Find equipment online')
        self.refresh_types(); self.refresh_panels(); self.refresh_models(); self.refresh_material_choices()

    def create_panel_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Create saved pump panel')
        form = QFormLayout(dialog)
        title = QLineEdit()
        title.setPlaceholderText('e.g. Borehole pump control panel')
        form.addRow('Panel name', title)
        voltage = QDoubleSpinBox()
        voltage.setRange(1, 450)
        voltage.setValue(400)
        voltage.setSuffix(' V')
        form.addRow('Supply voltage', voltage)
        phases = QComboBox()
        phases.addItem('Three-phase', 3)
        phases.addItem('Single-phase', 1)
        form.addRow('Supply phases', phases)
        breaker = QDoubleSpinBox()
        breaker.setRange(1, 10000)
        breaker.setValue(150)
        breaker.setSuffix(' A')
        form.addRow('Main breaker (provisional)', breaker)
        count = QSpinBox()
        count.setRange(1, 4)
        form.addRow('Number of pumps', count)
        pump_rows = []
        for index in range(4):
            power = QComboBox()
            for kw in PUMP_KW:
                power.addItem(f'{kw:g} kW', kw)
            starter = QComboBox()
            starter.addItems(STARTERS)
            form.addRow(f'Pump {index + 1} power', power)
            form.addRow(f'Pump {index + 1} starter', starter)
            pump_rows.append((power, starter))
        def update_count(*_):
            for i, (power, starter) in enumerate(pump_rows):
                power.setEnabled(i < count.value())
                starter.setEnabled(i < count.value())
        count.valueChanged.connect(update_count)
        def update_phases(*_):
            single = phases.currentData() == 1
            for _, starter in pump_rows:
                if single:
                    starter.setCurrentText('DOL')
                for i in range(starter.count()):
                    starter.model().item(i).setEnabled(not single or starter.itemText(i) == 'DOL')
        phases.currentIndexChanged.connect(update_phases)
        update_count()
        update_phases()
        form.addRow(QLabel('Draft only: confirm nameplate currents, protection and coordination before construction.'))
        buttons = QHBoxLayout()
        save = QPushButton('Create saved panel')
        cancel = QPushButton('Cancel')
        buttons.addWidget(save)
        buttons.addWidget(cancel)
        form.addRow(buttons)
        cancel.clicked.connect(dialog.reject)
        def save_panel():
            pumps = [Pump(power.currentData(), starter.currentText())
                     for power, starter in pump_rows[:count.value()]]
            try:
                panel_id = self.repo.create_panel(title.text(), pumps,
                    voltage_v=voltage.value(), main_breaker_a=breaker.value(), phases=phases.currentData())
            except (ValueError, TypeError) as exc:
                QMessageBox.warning(dialog, 'Cannot create panel', str(exc))
                return
            dialog.accept()
            self.refresh_panels()
            index = self.panel.findData(panel_id)
            if index >= 0:
                self.panel.setCurrentIndex(index)
            QMessageBox.information(self, 'Saved panel created',
                'Draft panel created. You can now add materials and export its BOM.')
        save.clicked.connect(save_panel)
        dialog.exec()

    def add_selected_component(self, *_):
        index = self.types_table.currentRow()
        if index < 0:
            QMessageBox.warning(self, 'Select component', 'Highlight a component first.')
            return
        panel_id = self.panel.currentData()
        if panel_id is None:
            QMessageBox.warning(self, 'No saved panel', 'Create or select a saved panel under Saved panel BOMs first.')
            return
        component = self.types_table.item(index, 0).text()
        try:
            self.repo.add_material_to_panel(panel_id, component, quantity=1)
        except ValueError as exc:
            QMessageBox.warning(self, 'Cannot add component', str(exc))
            return
        self.refresh_bom()
        QMessageBox.information(self, 'Component added',
            f'{component} added to the saved panel BOM (quantity 1, review required).')

    def refresh_material_choices(self, *_):
        self.material_choice.clear()
        for name in PANEL_MATERIALS[self.material_category.currentText()]:
            self.material_choice.addItem(name)

    def add_material(self):
        panel_id = self.panel.currentData()
        if panel_id is None:
            QMessageBox.warning(self, 'No saved panel', 'Create or select a saved panel first.')
            return
        try:
            self.repo.add_material_to_panel(panel_id, self.material_choice.currentText(),
                                            quantity=self.material_quantity.value())
        except ValueError as exc:
            QMessageBox.warning(self, 'Cannot add material', str(exc))
            return
        self.refresh_bom()
        QMessageBox.information(self, 'Material added', 'Material added to the common panel BOM as review-required.')

    def export_bom(self):
        panel_id = self.panel.currentData()
        if panel_id is None:
            QMessageBox.warning(self, 'No panel', 'Select a saved pump panel first.')
            return
        path, _ = QFileDialog.getSaveFileName(self, 'Export pump panel bill of materials',
            f'pump_panel_{panel_id}_bom.csv', 'CSV files (*.csv)')
        if not path:
            return
        rows = self.repo.get_bom(panel_id)
        catalog = {r['id']: r for r in self.catalog.search(limit=500)}
        headers = ('Pump', 'Component', 'Quantity', 'Requirement', 'Manufacturer',
                   'Model', 'Verification', 'Sizing notes', 'OEM source URL')
        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as stream:
                writer = csv.writer(stream)
                writer.writerow(['DRAFT / UNVERIFIED - engineering review required'])
                writer.writerow(headers)
                for row in rows:
                    model = catalog.get(row['selected_catalog_id'], {})
                    writer.writerow([row['motor_position'] or 'Common', row['component'],
                        row['quantity'], row['requirement'], model.get('manufacturer', ''),
                        model.get('model', ''), row['verification_status'],
                        row['sizing_notes'], model.get('source_url', '')])
        except OSError as exc:
            QMessageBox.warning(self, 'Export failed', str(exc))
            return
        QMessageBox.information(self, 'BOM exported', f'Saved {len(rows)} BOM lines to {path}')

    def search_from_bom(self):
        index = self.bom_table.currentRow()
        if index < 0:
            QMessageBox.warning(self, 'Choose component', 'Highlight a BOM row first.')
            return
        self.web_query.setText(self.bom_rows[index]['component'] + ' manufacturer datasheet')
        self.search_equipment_online()

    def search_equipment_online(self):
        query = self.web_query.text().strip()
        if not query or len(query) > 250:
            QMessageBox.warning(self, 'Search term', 'Enter an equipment model or component (maximum 250 characters).')
            return
        url = QUrl('https://www.google.com/search?q=' + quote_plus(query))
        if not QDesktopServices.openUrl(url):
            QMessageBox.warning(self, 'Browser unavailable', 'Could not open your default web browser.')

    def load_models(self):
        seed_pump_manufacturer_models(self.catalog)
        self.refresh_models()
        QMessageBox.information(self, 'Manufacturer references',
            'Four sourced starter/protection models imported. Check suitability and availability before selection.')

    def refresh_models(self):
        self.models.clear()
        for row in self.catalog.search(limit=500):
            self.models.addItem(f'{row["manufacturer"]} | {row["model"]} | {row["category"]}',row['id'])

    def assign_model(self):
        index = self.bom_table.currentRow()
        if index < 0 or self.models.currentData() is None:
            QMessageBox.warning(self, 'Select a row and model', 'Select a saved panel BOM row and a manufacturer model first.')
            return
        bom_id = self.bom_rows[index]['bom_id']
        try:
            self.repo.assign_catalog_model(bom_id, self.models.currentData(), self.notes.toPlainText())
        except (ValueError, TypeError) as exc:
            QMessageBox.warning(self, 'Cannot assign model', str(exc))
            return
        self.refresh_bom()
        QMessageBox.information(self, 'Model linked', 'Model assigned as UNVERIFIED. Check component function, ratings and coordination before use.')

    def refresh_types(self, *_):
        rows = self.repo.list_component_types(self.search.text())
        selected = self.category.currentText()
        if selected != 'All categories':
            allowed = set(PANEL_MATERIALS[selected])
            rows = [row for row in rows if row['name'] in allowed]
        self.types_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, key in enumerate(('name','scope','description')):
                self.types_table.setItem(i,j,QTableWidgetItem(str(row[key])))

    def refresh_panels(self, *_):
        self.panel.blockSignals(True)
        self.panel.clear()
        for row in self.repo.list_panels():
            self.panel.addItem(f'#{row["id"]} {row["title"]} | {row["phases"]}-phase | {row["pump_count"]} pumps | {row["main_breaker_a"]:g} A',row['id'])
        self.panel.blockSignals(False)
        self.refresh_bom()

    def refresh_bom(self, *_):
        panel_id = self.panel.currentData()
        rows = self.repo.get_bom(panel_id) if panel_id is not None else []
        self.bom_rows = rows
        self.bom_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            values = (('Common' if row['motor_position'] is None else f'Pump {row["motor_position"]}'),
                      row['component'],row['quantity'],row['requirement'],
                      row['selected_catalog_id'] or 'Not selected',row['verification_status'])
            for j, value in enumerate(values):
                self.bom_table.setItem(i,j,QTableWidgetItem(str(value)))
