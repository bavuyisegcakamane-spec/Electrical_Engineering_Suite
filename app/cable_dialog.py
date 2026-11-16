#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Educational conductor voltage-drop estimator."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QPushButton, QComboBox, QMessageBox
from calculations.cables import estimate_voltage_drop
from calculations.cable_sizing import derated_ampacity
from database.cable_reference_database import CableReferenceRepository
from app.cable_reference_entry_dialog import CableReferenceEntryDialog


class CableDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cable Voltage Drop Estimator")
        self.resize(560, 490)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Resistive voltage-drop estimate only; not cable sizing or code compliance."))
        self.material = QComboBox()
        self.material.addItems(["Copper", "Aluminium"])
        self.phases = QComboBox()
        self.phases.addItems(["Single-phase", "Three-phase (balanced)"])
        form = QFormLayout()
        form.addRow("Conductor material", self.material)
        form.addRow("Supply", self.phases)
        self.fields = []
        for name, default in (("Load current (A)", "20"), ("One-way length (m)", "30"),
                              ("Conductor area (mm2)", "4"), ("Supply voltage (V)", "230"),
                              ("Conductor temperature (C)", "70"), ("Power factor", "1")):
            field = QLineEdit(default)
            form.addRow(name, field)
            self.fields.append(field)
        layout.addLayout(form)
        self.result = QLabel("Enter values and calculate.")
        layout.addWidget(self.result)
        button = QPushButton("Estimate voltage drop")
        button.clicked.connect(self.calculate)
        layout.addWidget(button)
        layout.addWidget(QLabel("WARNING: Ignores reactance, installation method, derating, fault duty and protection."))
        layout.addWidget(QLabel("Verify cable ampacity and voltage-drop limits against applicable standards."))
        self.reference_repo = None
        if parent is not None and getattr(parent, 'database', None) is not None:
            self.reference_repo = CableReferenceRepository(parent.database)
            self.reference = QComboBox()
            self.reference.addItem('Select a user-entered source reference', None)
            for row in self.reference_repo.list_ratings():
                self.reference.addItem(f'{row["area_mm2"]:g} mm2 | {row["reference_ampacity_a"]:g} A | {row["source_title"]} | UNVERIFIED', row['id'])
            layout.addWidget(QLabel('User-entered reference ratings (not verified by software):'))
            layout.addWidget(self.reference)
            self.temperature_factor = QLineEdit('1.0')
            self.grouping_factor = QLineEdit('1.0')
            self.breaker_rating = QLineEdit('20')
            source_form = QFormLayout()
            source_form.addRow('Temperature factor (sourced)', self.temperature_factor)
            source_form.addRow('Grouping factor (sourced)', self.grouping_factor)
            source_form.addRow('Breaker nominal current (A)', self.breaker_rating)
            layout.addLayout(source_form)
            add = QPushButton('Add sourced cable reference')
            add.clicked.connect(self.add_reference)
            layout.addWidget(add)
            check = QPushButton('Check stored cable reference (preliminary)')
            check.clicked.connect(self.check_reference)
            layout.addWidget(check)

    def add_reference(self):
        if self.reference_repo is None:
            return
        dialog = CableReferenceEntryDialog(self.reference_repo, self)
        if dialog.exec() == QDialog.Accepted:
            self.reference.clear()
            self.reference.addItem('Select a user-entered source reference', None)
            for row in self.reference_repo.list_ratings():
                self.reference.addItem(f'{row["area_mm2"]:g} mm2 | {row["reference_ampacity_a"]:g} A | {row["source_title"]} | UNVERIFIED', row['id'])
            self.reference.setCurrentIndex(self.reference.count() - 1)

    def check_reference(self):
        if self.reference_repo is None or self.reference.currentData() is None:
            QMessageBox.warning(self, 'Reference required', 'Add a fully cited cable rating to the reference database first.')
            return
        try:
            row = self.reference_repo.get(self.reference.currentData())
            result = derated_ampacity(row['reference_ampacity_a'],
                float(self.temperature_factor.text()), float(self.grouping_factor.text()),
                design_current_a=float(self.fields[0].text()),
                breaker_rating_a=float(self.breaker_rating.text()))
        except (ValueError, TypeError, OverflowError) as exc:
            QMessageBox.warning(self, 'Cable screening error', str(exc))
            return
        self.result.setText(f'Reference: {row["source_title"]}, {row["source_edition"]}, {row["table_reference"]}\n'
            f'UNVERIFIED source | derated ampacity: {result["derated_ampacity_a"]:.2f} A\n'
            f'Preliminary nominal-current chain: {"PASS" if result["nominal_current_chain_passes"] else "FAIL"}\n'
            'Not a cable selection or compliance approval.')

    def calculate(self):
        try:
            values = [float(field.text().strip()) for field in self.fields]
            result = estimate_voltage_drop(*values[:4], material=self.material.currentText(),
                                           phases=3 if self.phases.currentIndex() else 1,
                                           conductor_temp_c=values[4], power_factor=values[5])
        except (ValueError, OverflowError, ZeroDivisionError) as exc:
            self.result.setText("Invalid cable input")
            QMessageBox.warning(self, "Cable calculation error", str(exc))
            return
        self.result.setText("\n".join((
            f"Estimated voltage drop: {result['voltage_drop_v']:.6g} V",
            f"Voltage drop: {result['voltage_drop_percent']:.6g}%",
            f"Estimated receiving voltage: {result['estimated_load_voltage_v']:.6g} V",
        )))
