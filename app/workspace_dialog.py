"""Project workspace: save calculation snapshots and export a combined PDF."""
from pathlib import Path
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QComboBox, QPushButton, QLabel, QListWidget,
                               QFileDialog, QMessageBox)
from app.report_dialog import ReportDialog
from projects.workspace import Workspace
from reports.pdf_report import create_pdf_report


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
            for index, entry in enumerate(self.current["calculations"], 1):
                self.entries.addItem(f"{index}. {entry['type']}")

    def add_calculation(self):
        if not self.current:
            QMessageBox.warning(self, "No project", "Open or create a project first.")
            return
        dialog = ReportDialog(self)
        # Reuse its calculation fields but save into the project, not a standalone PDF.
        dialog.findChildren(QPushButton)[0].setText("Add to project")
        dialog.findChildren(QPushButton)[0].clicked.disconnect()
        dialog.findChildren(QPushButton)[0].clicked.connect(dialog.accept)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            name, inputs, outputs, assumptions = dialog.build_data()
            self.current = self.store.add_calculation(self.current["name"], name, inputs, outputs, assumptions)
            self.refresh_entries()
        except (ValueError, OSError) as exc:
            QMessageBox.warning(self, "Calculation error", str(exc))

    def export_pdf(self):
        if not self.current or not self.current["calculations"]:
            QMessageBox.warning(self, "No calculations", "Add at least one calculation first.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save project report", "project_report.pdf", "PDF Files (*.pdf)")
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        inputs, outputs, assumptions = {}, {}, []
        for index, entry in enumerate(self.current["calculations"], 1):
            prefix = f"{index}. {entry['type']}"
            inputs.update({f"{prefix} - {key}": value for key, value in entry['inputs'].items()})
            outputs.update({f"{prefix} - {key}": value for key, value in entry['outputs'].items()})
            assumptions.extend(f"{prefix}: {value}" for value in entry['assumptions'])
        try:
            create_pdf_report(path, self.current['name'], "Combined engineering calculations", inputs, outputs, assumptions)
        except (ValueError, OSError) as exc:
            QMessageBox.warning(self, "PDF error", str(exc))
            return
        QMessageBox.information(self, "Saved", f"Combined PDF saved to:\n{path}")
