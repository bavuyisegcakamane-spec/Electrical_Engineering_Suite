#  ____      ___        __  ____   _______ _____ ____
# |  _ \\    / \\ \\      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \\ \\ /\\ / /  |  _ \\    | |    | | \\___ \\
# |  _ <  / ___ \\ V  V /   | |_) |   | |    | |  ___) |
# |_| \\_\\/_/   \\_\\_/\\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Pump panel component requirements and saved panel BOM browser."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QTabWidget, QWidget,
    QMessageBox, QPlainTextEdit)
from database.pump_panel_database import PumpPanelDatabase
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
        self.types_table = QTableWidget(0, 3)
        self.types_table.setHorizontalHeaderLabels(('Component', 'Scope', 'Description'))
        self.types_table.setColumnWidth(0, 450)
        self.types_table.setColumnWidth(1, 120)
        types_layout.addWidget(self.types_table)
        tabs.addTab(types_page, 'All panel components')
        panels_page = QWidget(); panels_layout = QVBoxLayout(panels_page)
        selector = QHBoxLayout()
        self.panel = QComboBox(); self.panel.currentIndexChanged.connect(self.refresh_bom)
        selector.addWidget(QLabel('Saved panel'))
        selector.addWidget(self.panel)
        refresh = QPushButton('Refresh saved panels'); refresh.clicked.connect(self.refresh_panels)
        selector.addWidget(refresh)
        panels_layout.addLayout(selector)
        self.bom_table = QTableWidget(0, 6)
        self.bom_table.setHorizontalHeaderLabels(('Pump', 'Component', 'Qty', 'Requirement', 'Selected catalogue ID', 'Verification'))
        self.bom_table.setColumnWidth(1, 440)
        panels_layout.addWidget(self.bom_table)
        model_row = QHBoxLayout()
        self.models = QComboBox()
        model_row.addWidget(QLabel('Manufacturer model'))
        model_row.addWidget(self.models)
        load_models = QPushButton('Load manufacturer starter references')
        load_models.clicked.connect(self.load_models)
        model_row.addWidget(load_models)
        panels_layout.addLayout(model_row)
        self.notes = QPlainTextEdit()
        self.notes.setPlaceholderText('Required sizing and coordination review notes (unverified)')
        self.notes.setMaximumHeight(75)
        panels_layout.addWidget(self.notes)
        assign = QPushButton('Assign selected model to highlighted BOM row (UNVERIFIED)')
        assign.clicked.connect(self.assign_model)
        panels_layout.addWidget(assign)
        tabs.addTab(panels_page, 'Saved panel BOMs')
        self.refresh_types(); self.refresh_panels(); self.refresh_models()

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
        self.types_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, key in enumerate(('name','scope','description')):
                self.types_table.setItem(i,j,QTableWidgetItem(str(row[key])))

    def refresh_panels(self, *_):
        self.panel.blockSignals(True)
        self.panel.clear()
        for row in self.repo.list_panels():
            self.panel.addItem(f'#{row["id"]} {row["title"]} | {row["pump_count"]} pumps | {row["main_breaker_a"]:g} A',row['id'])
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
