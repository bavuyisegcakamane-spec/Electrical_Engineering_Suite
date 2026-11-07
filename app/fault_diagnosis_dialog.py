#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Guided, non-prescriptive electrical fault-finding interface."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLabel, QTextEdit, QPushButton
from calculations.fault_diagnosis import FAULT_GUIDES, diagnose_symptom


class FaultDiagnosisDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Electrical Fault-Finding Assistant")
        self.resize(650, 530)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select an observed symptom (guidance only; not a confirmed diagnosis)."))
        self.symptoms = QComboBox()
        self.symptoms.addItems(FAULT_GUIDES)
        layout.addWidget(self.symptoms)
        button = QPushButton("Show possible causes and safe next steps")
        button.clicked.connect(self.analyze)
        layout.addWidget(button)
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        layout.addWidget(self.results)
        self.analyze()

    def analyze(self):
        report = diagnose_symptom(self.symptoms.currentText())
        sections = ["POSSIBLE CAUSES (not ranked)"]
        sections.extend(f"- {item}" for item in report['possible_causes'])
        sections.append("\nSAFE NEXT STEPS")
        sections.extend(f"{i}. {item}" for i, item in enumerate(report['safe_next_steps'], 1))
        sections.extend(("\nSAFETY WARNING", report['warning']))
        self.results.setPlainText("\n".join(sections))
