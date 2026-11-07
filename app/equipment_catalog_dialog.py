#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Local, source-traceable electrical equipment catalogue UI."""
import webbrowser
from pathlib import Path
from database.equipment_import import import_equipment_csv
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,
                               QTableWidget,QTableWidgetItem,QMessageBox,QFormLayout,QComboBox,QFileDialog)
from database.equipment_catalog import EquipmentCatalog
from database.manufacturer_products import seed_manufacturer_products
from app.pump_panel_dialog import PumpPanelDialog
from app.pump_components_dialog import PumpComponentsDialog
from database.component_taxonomy import COMPONENT_GROUPS, ALL_COMPONENT_TYPES
from app.branding import BRAND_SIGNATURE


class EquipmentCatalogDialog(QDialog):
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Electrical Equipment Catalogue - Source Referenced')
        self.resize(1050, 650)
        self.catalog = EquipmentCatalog(database)
        layout = QVBoxLayout(self)
        signature = QLabel(BRAND_SIGNATURE)
        signature.setObjectName('rawBytesSignature')
        signature.setStyleSheet('font-size: 18px; font-weight: 700; letter-spacing: 1px;')
        layout.addWidget(signature)
        panel_button = QPushButton('Water pump panel study (1-4 pumps, DOL / Star-delta / Soft starter / VFD)')
        panel_button.clicked.connect(self.open_pump_panel)
        layout.addWidget(panel_button)
        components_button = QPushButton('Browse water pump panel component database and saved BOMs')
        components_button.clicked.connect(self.open_pump_components)
        layout.addWidget(components_button)
        layout.addWidget(QLabel('Component types are a reference taxonomy, not verified products. Check exact manufacturer datasheets for ratings.'))
        browser = QHBoxLayout()
        self.component_group = QComboBox()
        self.component_group.addItems(COMPONENT_GROUPS)
        self.component_group.currentTextChanged.connect(self.update_component_types)
        self.component_type = QComboBox()
        self.component_type.setMinimumWidth(320)
        browser.addWidget(QLabel('Browse component group'))
        browser.addWidget(self.component_group)
        browser.addWidget(self.component_type)
        layout.addLayout(browser)
        self.update_component_types()
        actions = QHBoxLayout()
        self.query = QLineEdit()
        self.query.setPlaceholderText('Search manufacturer, model or category')
        self.query.textChanged.connect(self.refresh)
        actions.addWidget(self.query)
        seed = QPushButton('Import official source families')
        seed.clicked.connect(self.seed)
        actions.addWidget(seed)
        products_button = QPushButton('Import reviewed manufacturer models')
        products_button.clicked.connect(self.seed_products)
        actions.addWidget(products_button)
        import_button = QPushButton('Import reviewed manufacturer CSV')
        import_button.clicked.connect(self.import_csv)
        actions.addWidget(import_button)
        layout.addLayout(actions)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(('Manufacturer','Family / Model','Category','Description','Source URL'))
        self.table.setColumnWidth(0,140)
        self.table.setColumnWidth(1,240)
        self.table.setColumnWidth(2,175)
        self.table.setColumnWidth(3,310)
        self.table.setColumnWidth(4,350)
        layout.addWidget(self.table)
        open_button = QPushButton('Open selected manufacturer source in browser')
        open_button.clicked.connect(self.open_source)
        layout.addWidget(open_button)
        form = QFormLayout()
        self.fields = {}
        for key, label in (('manufacturer','Manufacturer'),('model','Exact model / family'),
                           ('category','Category'),('description','Description'),('source_url','Official HTTPS source URL')):
            edit = QComboBox() if key == 'category' else QLineEdit()
            if key == 'category':
                edit.setEditable(True)
                edit.addItems(ALL_COMPONENT_TYPES)
            self.fields[key] = edit
            form.addRow(label, edit)
        layout.addLayout(form)
        self.component_type.currentTextChanged.connect(self.fields['category'].setCurrentText)
        self.fields['category'].setCurrentText(self.component_type.currentText())
        add_button = QPushButton('Add sourced equipment record')
        add_button.clicked.connect(self.add_record)
        layout.addWidget(add_button)
        self.refresh()

    def open_pump_components(self):
        dialog = PumpComponentsDialog(self.catalog.db, self)
        dialog.exec()

    def open_pump_panel(self):
        dialog = PumpPanelDialog(self, self.catalog.db)
        dialog.exec()

    def update_component_types(self, *_):
        self.component_type.clear()
        self.component_type.addItems(COMPONENT_GROUPS[self.component_group.currentText()])

    def import_csv(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Choose reviewed equipment CSV', '', 'CSV files (*.csv)')
        if not filename:
            return
        try:
            count = import_equipment_csv(self.catalog, Path(filename).read_text(encoding='utf-8-sig'))
        except (ValueError, OSError) as exc:
            QMessageBox.warning(self, 'Import rejected', str(exc))
            return
        self.refresh()
        QMessageBox.information(self, 'Import finished', f'Processed {count} source-referenced rows. Manufacturer ratings are not independently verified.')

    def seed_products(self):
        count = seed_manufacturer_products(self.catalog)
        self.refresh()
        QMessageBox.information(self, 'Manufacturer references',
                                f'Processed {count} model references. Recheck datasheets and regional product status before design.')

    def seed(self):
        self.catalog.seed_official_sources()
        self.refresh()

    def refresh(self,*_):
        self.rows = self.catalog.search(self.query.text())
        self.table.setRowCount(len(self.rows))
        for i, record in enumerate(self.rows):
            for j, key in enumerate(('manufacturer','model','category','description','source_url')):
                self.table.setItem(i,j,QTableWidgetItem(str(record[key])))

    def open_source(self):
        index = self.table.currentRow()
        if 0 <= index < len(self.rows):
            webbrowser.open(self.rows[index]['source_url'])

    def add_record(self):
        try:
            self.catalog.add(**{key: (edit.currentText() if isinstance(edit, QComboBox) else edit.text())
                                for key, edit in self.fields.items()})
        except ValueError as exc:
            QMessageBox.warning(self,'Invalid equipment record',str(exc))
            return
        self.refresh()
