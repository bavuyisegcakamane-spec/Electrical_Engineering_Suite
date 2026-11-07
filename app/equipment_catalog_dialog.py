#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Local, source-traceable electrical equipment catalogue UI."""
import webbrowser
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,
                               QTableWidget,QTableWidgetItem,QMessageBox,QFormLayout,QComboBox)
from database.equipment_catalog import EquipmentCatalog
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
        layout.addWidget(QLabel('Official manufacturer product families; ratings are not inferred. Verify exact SKU datasheets before design.'))
        actions = QHBoxLayout()
        self.query = QLineEdit()
        self.query.setPlaceholderText('Search manufacturer, model or category')
        self.query.textChanged.connect(self.refresh)
        actions.addWidget(self.query)
        seed = QPushButton('Import official source families')
        seed.clicked.connect(self.seed)
        actions.addWidget(seed)
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
            edit = QLineEdit()
            self.fields[key] = edit
            form.addRow(label, edit)
        layout.addLayout(form)
        add_button = QPushButton('Add sourced equipment record')
        add_button.clicked.connect(self.add_record)
        layout.addWidget(add_button)
        self.refresh()

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
            self.catalog.add(**{key: edit.text() for key, edit in self.fields.items()})
        except ValueError as exc:
            QMessageBox.warning(self,'Invalid equipment record',str(exc))
            return
        self.refresh()
