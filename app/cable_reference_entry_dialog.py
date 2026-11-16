"""Manual entry of sourced cable ampacity references; never auto-verified."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QComboBox, QPushButton, QLabel, QMessageBox)


class CableReferenceEntryDialog(QDialog):
    def __init__(self, repository, parent=None):
        super().__init__(parent)
        self.repo = repository
        self.setWindowTitle("Add cable reference (unverified)")
        self.resize(540, 450)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Transcribe a manufacturer or standards table with full source details.\n"
                                "Entries remain UNVERIFIED until independently checked."))
        form = QFormLayout()
        self.entries = {}
        for key, label in (
            ("source_title", "Source document"),
            ("source_edition", "Edition / revision"),
            ("table_reference", "Table / page reference"),
            ("installation_method", "Installation method"),
            ("conductor_description", "Insulation / cores / configuration"),
            ("area_mm2", "Conductor area (mm2)"),
            ("reference_ampacity_a", "Reference ampacity (A)"),
            ("notes", "Notes / conditions"),
        ):
            field = QLineEdit()
            self.entries[key] = field
            form.addRow(label, field)
        self.material = QComboBox()
        self.material.addItems(["Copper", "Aluminium"])
        form.addRow("Material", self.material)
        layout.addLayout(form)
        save = QPushButton("Save as UNVERIFIED reference")
        save.clicked.connect(self.save)
        layout.addWidget(save)

    def save(self):
        try:
            values = {key: field.text().strip() for key, field in self.entries.items()}
            values["material"] = self.material.currentText()
            values["area_mm2"] = float(values["area_mm2"])
            values["reference_ampacity_a"] = float(values["reference_ampacity_a"])
            self.repo.add(**values)
        except (ValueError, TypeError) as exc:
            QMessageBox.warning(self, "Invalid cable reference", str(exc))
            return
        self.accept()
