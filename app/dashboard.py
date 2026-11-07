"""Searchable categorized dashboard with a local project overview."""
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QLineEdit, QScrollArea, QGroupBox, QGridLayout)
from projects.workspace import Workspace

TOOLS = {
    "Circuits and fundamentals": [
        ("Engineering Calculations", "open_calculations"),
        ("AC / Impedance / Insulation Calculations", "open_ac_engineering"),
        ("Circuit Analyzer", "open_circuits"),
        ("Mixed Circuit Analyzer", "open_mixed_circuits")],
    "Loads and machines": [
        ("Electrical Load Calculator", "open_loads"),
        ("Motor Analysis", "open_motors"),
        ("Transformer Calculator", "open_transformers"),
        ("Advanced Motor / Transformer Estimates", "open_advanced_equipment"),
        ("Power Factor Correction", "open_power_factor")],
    "Cables and protection": [
        ("Cable Voltage Drop", "open_cables"),
        ("Protection / Fault Current", "open_protection"),
        ("Electrical Fault-Finding Assistant", "open_fault_diagnosis")],
    "Projects and reporting": [
        ("Project Workspace", "open_workspace"),
        ("Engineering PDF Reports", "open_reports")],
}


class Dashboard(QWidget):
    def __init__(self, window, project_directory=None):
        super().__init__(window)
        self.window = window
        self.store = Workspace(project_directory or Path.home() / "Electrical_Engineering_Suite_Projects")
        layout = QVBoxLayout(self)
        heading = QLabel("Engineering Dashboard")
        heading.setStyleSheet("font-size: 24px; font-weight: 600;")
        layout.addWidget(heading)
        layout.addWidget(QLabel("Choose a tool, search by name, or reopen a saved project."))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search calculators and tools...")
        self.search.textChanged.connect(self.filter_tools)
        layout.addWidget(self.search)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self.groups = {}
        self.buttons = {}
        sections = QVBoxLayout(container)
        for category, tools in TOOLS.items():
            group = QGroupBox(category)
            grid = QGridLayout(group)
            for index, (label, method) in enumerate(tools):
                button = QPushButton(label)
                button.setMinimumHeight(42)
                button.clicked.connect(getattr(window, method))
                grid.addWidget(button, index // 2, index % 2)
                self.buttons[label] = button
            sections.addWidget(group)
            self.groups[category] = group
        sections.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll, 1)
        overview = QGroupBox("Project overview")
        project_layout = QVBoxLayout(overview)
        self.project_summary = QLabel()
        project_layout.addWidget(self.project_summary)
        row = QHBoxLayout()
        refresh = QPushButton("Refresh projects")
        refresh.clicked.connect(self.refresh_projects)
        row.addWidget(refresh)
        open_projects = QPushButton("Open Project Workspace")
        open_projects.clicked.connect(self.open_projects)
        row.addWidget(open_projects)
        project_layout.addLayout(row)
        layout.addWidget(overview)
        footer = QHBoxLayout()
        for label, method in (("Database", "open_database"), ("Settings", "open_settings")):
            button = QPushButton(label)
            button.clicked.connect(getattr(window, method))
            footer.addWidget(button)
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(window.close)
        footer.addWidget(exit_button)
        layout.addLayout(footer)
        self.refresh_projects()

    def filter_tools(self, query):
        query = query.strip().casefold()
        for category, tools in TOOLS.items():
            visible = 0
            for label, _ in tools:
                match = query in label.casefold() or query in category.casefold()
                self.buttons[label].setVisible(match)
                visible += match
            self.groups[category].setVisible(bool(visible))

    def refresh_projects(self):
        names = self.store.list_projects()
        count = 0
        for name in names:
            try:
                count += len(self.store.load(name)["calculations"])
            except (OSError, ValueError, KeyError):
                continue
        recent = ", ".join(names[:3]) if names else "No saved projects yet"
        self.project_summary.setText(f"Saved projects: {len(names)}  |  Saved calculations: {count}\nProjects: {recent}")

    def open_projects(self):
        self.window.open_workspace()
        self.refresh_projects()
