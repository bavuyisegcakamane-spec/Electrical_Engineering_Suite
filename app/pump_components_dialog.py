#  ____      ___        __  ____   _______ _____ ____
# |  _ \\    / \\ \\      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \\ \\ /\\ / /  |  _ \\    | |    | | \\___ \\
# |  _ <  / ___ \\ V  V /   | |_) |   | |    | |  ___) |
# |_| \\_\\/_/   \\_\\_/\\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Pump panel component requirements and saved panel BOM browser."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QTabWidget, QWidget)
from database.pump_panel_database import PumpPanelDatabase
from app.branding import BRAND_SIGNATURE


class PumpComponentsDialog(QDialog):
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.setWindowTitle('raw.bytes | Pump Panel Component Database')
        self.resize(1100, 740)
        self.repo = PumpPanelDatabase(database)
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
        tabs.addTab(panels_page, 'Saved panel BOMs')
        self.refresh_types(); self.refresh_panels()

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
        self.bom_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            values = (('Common' if row['motor_position'] is None else f'Pump {row["motor_position"]}'),
                      row['component'],row['quantity'],row['requirement'],
                      row['selected_catalog_id'] or 'Not selected',row['verification_status'])
            for j, value in enumerate(values):
                self.bom_table.setItem(i,j,QTableWidgetItem(str(value)))
