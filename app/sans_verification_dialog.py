"""SANS evidence checklist, with local JSON import/export (not a certificate)."""
import json
from pathlib import Path
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
                               QTableWidgetItem, QComboBox, QLineEdit, QPushButton,
                               QFileDialog, QMessageBox)
from calculations.sans_verification import REQUIREMENTS, VALID_STATUSES, review_evidence


class SANSVerificationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('SANS 10142-1 - Evidence Register (NOT a compliance certificate)')
        self.resize(1080, 720)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Record evidence and unresolved issues. This tool cannot certify compliance.'))
        self.table = QTableWidget(len(REQUIREMENTS), 4)
        self.table.setHorizontalHeaderLabels(('Requirement', 'Reference', 'Status', 'Evidence / justification'))
        self.table.setColumnWidth(0, 390)
        self.table.setColumnWidth(1, 140)
        self.table.setColumnWidth(2, 145)
        self.table.setColumnWidth(3, 360)
        self.statuses = {}
        self.notes = {}
        for row, (key, description, clause) in enumerate(REQUIREMENTS):
            self.table.setItem(row, 0, QTableWidgetItem(description))
            self.table.setItem(row, 1, QTableWidgetItem(clause))
            status = QComboBox()
            status.addItems(VALID_STATUSES)
            self.table.setCellWidget(row, 2, status)
            note = QLineEdit()
            note.setPlaceholderText('Test record, drawing, document, or reason')
            self.table.setCellWidget(row, 3, note)
            self.statuses[key] = status
            self.notes[key] = note
        layout.addWidget(self.table)
        actions = QHBoxLayout()
        for label, callback in (('Review evidence', self.review),
                                ('Save JSON', self.save), ('Load JSON', self.load)):
            button = QPushButton(label)
            button.clicked.connect(callback)
            actions.addWidget(button)
        layout.addLayout(actions)
        self.summary = QLabel('Not reviewed. Compliance NOT DETERMINED.')
        layout.addWidget(self.summary)

    def gather(self):
        return {key: {'status': self.statuses[key].currentText(),
                      'note': self.notes[key].text()} for key, _, _ in REQUIREMENTS}

    def review(self):
        try:
            result = review_evidence(self.gather())
        except ValueError as exc:
            QMessageBox.warning(self, 'Evidence requires attention', str(exc))
            return None
        self.summary.setText(f"Unresolved: {result['outstanding']} of {len(REQUIREMENTS)}. "
                             + result['compliance_status'])
        return result

    def save(self):
        result = self.review()
        if result is None:
            return
        filename, _ = QFileDialog.getSaveFileName(self, 'Save evidence register',
                                                   'sans_evidence.json', 'JSON files (*.json)')
        if not filename:
            return
        try:
            Path(filename).write_text(json.dumps(result, indent=2), encoding='utf-8')
        except OSError as exc:
            QMessageBox.warning(self, 'Save failed', str(exc))

    def load(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Load evidence register', '', 'JSON files (*.json)')
        if not filename:
            return
        try:
            data = json.loads(Path(filename).read_text(encoding='utf-8'))
            rows = data['items']
            if not isinstance(rows, list) or len(rows) != len(REQUIREMENTS):
                raise ValueError('Incomplete evidence register')
            records = {item['key']: {'status': item['status'], 'note': item['note']} for item in rows}
            if len(records) != len(REQUIREMENTS):
                raise ValueError('Duplicate or missing requirements')
            review_evidence(records)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            QMessageBox.warning(self, 'Load failed', str(exc))
            return
        for key, _, _ in REQUIREMENTS:
            self.statuses[key].setCurrentText(records[key]['status'])
            self.notes[key].setText(records[key]['note'])
        self.review()
