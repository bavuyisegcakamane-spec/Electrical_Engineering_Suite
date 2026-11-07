#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Local SQLite measurements and troubleshooting history."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox, QLineEdit,
                               QTextEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem)
from database.field_records import FieldRecords


class FieldRecordsDialog(QDialog):
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Measurement and Fault History")
        self.resize(850, 560)
        self.records = FieldRecords(database)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.kind = QComboBox()
        self.kind.addItems(("measurement", "fault"))
        self.equipment = QLineEdit()
        self.description = QTextEdit()
        self.description.setMaximumHeight(65)
        self.value = QLineEdit()
        self.unit = QLineEdit()
        form.addRow("Record type", self.kind)
        form.addRow("Equipment", self.equipment)
        form.addRow("Observation / test description", self.description)
        form.addRow("Numeric value (measurements)", self.value)
        form.addRow("Unit", self.unit)
        layout.addLayout(form)
        save = QPushButton("Save record locally")
        save.clicked.connect(self.save_record)
        layout.addWidget(save)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(("ID", "UTC time", "Type", "Equipment", "Description", "Value", "Unit"))
        layout.addWidget(self.table)
        refresh = QPushButton("Refresh history")
        refresh.clicked.connect(self.refresh)
        layout.addWidget(refresh)
        self.refresh()

    def save_record(self):
        try:
            value = float(self.value.text()) if self.value.text().strip() else None
            self.records.add(self.kind.currentText(), self.equipment.text(),
                             self.description.toPlainText(), value, self.unit.text())
        except (ValueError, OverflowError) as exc:
            QMessageBox.warning(self, "Invalid record", str(exc))
            return
        self.refresh()

    def refresh(self):
        rows = self.records.recent()
        self.table.setRowCount(len(rows))
        for row_index, record in enumerate(rows):
            for col_index, value in enumerate(record):
                self.table.setItem(row_index, col_index, QTableWidgetItem("" if value is None else str(value)))
