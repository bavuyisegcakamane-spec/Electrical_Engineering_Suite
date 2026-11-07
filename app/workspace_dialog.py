#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Project workspace: save calculation snapshots and export a combined PDF."""
from pathlib import Path
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QComboBox, QPushButton, QLabel, QListWidget,
                               QFileDialog, QMessageBox)
from app.report_dialog import ReportDialog, CONFIG
from projects.workspace import Workspace
from reports.pdf_report import create_project_pdf_report


class WorkspaceDialog(QDialog):
    def __init__(self, parent=None, directory=None):
        super().__init__(parent)
        self.setWindowTitle("Engineering Project Workspace")
        self.resize(660, 520)
        self.store = Workspace(directory or Path.home() / "Electrical_Engineering_Suite_Projects")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Local project files; calculation results are saved as snapshots."))
        row = QHBoxLayout()
        self.projects = QComboBox()
        self.projects.setEditable(True)
        row.addWidget(self.projects)
        load = QPushButton("Open / Create")
        load.clicked.connect(self.open_project)
        row.addWidget(load)
        layout.addLayout(row)
        self.current = None
        self.entries = QListWidget()
        layout.addWidget(self.entries)
        self.summary = QLabel("No project selected")
        layout.addWidget(self.summary)
        actions = QHBoxLayout()
        edit = QPushButton("Edit selected")
        edit.clicked.connect(self.edit_calculation)
        actions.addWidget(edit)
        remove = QPushButton("Delete selected")
        remove.clicked.connect(self.delete_calculation)
        actions.addWidget(remove)
        layout.addLayout(actions)
        add = QPushButton("Add a calculation")
        add.clicked.connect(self.add_calculation)
        layout.addWidget(add)
        export = QPushButton("Export combined PDF")
        export.clicked.connect(self.export_pdf)
        layout.addWidget(export)
        layout.addWidget(QLabel("Educational estimates only. Not a certified engineering design."))
        self.refresh_projects()

    def refresh_projects(self):
        previous = self.projects.currentText()
        self.projects.clear()
        self.projects.addItems(self.store.list_projects())
        self.projects.setEditText(previous)

    def open_project(self):
        try:
            self.current = self.store.load(self.projects.currentText().strip())
            self.store.save(self.current)
        except (ValueError, OSError) as exc:
            QMessageBox.warning(self, "Project error", str(exc))
            return
        self.refresh_projects()
        self.projects.setEditText(self.current["name"])
        self.refresh_entries()

    def refresh_entries(self):
        self.entries.clear()
        if self.current:
            counts = {}
            for index, entry in enumerate(self.current["calculations"], 1):
                kind = entry['type']
                counts[kind] = counts.get(kind, 0) + 1
                self.entries.addItem(f"{index}. {kind}")
            breakdown = ', '.join(f"{kind}: {count}" for kind, count in counts.items())
            self.summary.setText(f"Project: {self.current['name']} | Calculations: {len(self.current['calculations'])}\n{breakdown}")

    def add_calculation(self):
        if not self.current:
            QMessageBox.warning(self, "No project", "Open or create a project first.")
            return
        dialog = self.calculation_editor()
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            name, inputs, outputs, assumptions = dialog.build_data()
            self.current = self.store.add_calculation(self.current["name"], name, inputs, outputs, assumptions)
            self.refresh_entries()
        except (ValueError, OSError) as exc:
            QMessageBox.warning(self, "Calculation error", str(exc))

    def calculation_editor(self, entry=None):
        dialog = ReportDialog(self)
        button = dialog.findChildren(QPushButton)[0]
        button.setText("Save calculation to project")
        button.clicked.disconnect()
        button.clicked.connect(lambda: self.validate_editor(dialog))
        if entry:
            dialog.selector.setCurrentText(entry['type'])
            labels = CONFIG[entry['type']][0]
            for i, label in enumerate(labels):
                dialog.fields[i].setText(str(entry['inputs'][label]))
        return dialog

    def validate_editor(self, dialog):
        try:
            dialog.build_data()
        except (ValueError, OverflowError, ZeroDivisionError) as exc:
            QMessageBox.warning(dialog, "Invalid calculation", str(exc))
            return
        dialog.accept()

    def edit_calculation(self):
        if not self.current or self.entries.currentRow() < 0:
            QMessageBox.warning(self, "No selection", "Select a calculation to edit.")
            return
        index = self.entries.currentRow()
        entry = self.current['calculations'][index]
        if entry['type'] not in CONFIG or any(k not in entry['inputs'] for k in CONFIG[entry['type']][0]):
            QMessageBox.warning(self, "Unsupported snapshot", "This snapshot cannot be edited with the current calculator.")
            return
        dialog = self.calculation_editor(entry)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            name, inputs, outputs, assumptions = dialog.build_data()
            self.current = self.store.update_calculation(self.current['name'], index, name, inputs, outputs, assumptions)
            self.refresh_entries()
            self.entries.setCurrentRow(index)
        except (ValueError, OSError, IndexError) as exc:
            QMessageBox.warning(self, "Edit failed", str(exc))

    def delete_calculation(self):
        if not self.current or self.entries.currentRow() < 0:
            QMessageBox.warning(self, "No selection", "Select a calculation to delete.")
            return
        index = self.entries.currentRow()
        name = self.current['calculations'][index]['type']
        reply = QMessageBox.question(self, "Confirm deletion", f"Delete calculation {index + 1}: {name}? This cannot be undone.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            self.current = self.store.delete_calculation(self.current['name'], index)
            self.refresh_entries()
        except (ValueError, OSError, IndexError) as exc:
            QMessageBox.warning(self, "Deletion failed", str(exc))

    def export_pdf(self):
        if not self.current or not self.current["calculations"]:
            QMessageBox.warning(self, "No calculations", "Add at least one calculation first.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save project report", "project_report.pdf", "PDF Files (*.pdf)")
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        try:
            create_project_pdf_report(path, self.current)
        except (ValueError, OSError) as exc:
            QMessageBox.warning(self, "PDF error", str(exc))
            return
        QMessageBox.information(self, "Saved", f"Combined PDF saved to:\n{path}")
