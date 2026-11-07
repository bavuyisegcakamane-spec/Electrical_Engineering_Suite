"""Educational PDF calculation reports using PySide6 (no extra dependencies)."""
import math
from pathlib import Path
from PySide6.QtGui import QFont, QFontMetrics, QPainter, QPdfWriter, QPageSize

DISCLAIMER = ("EDUCATIONAL ESTIMATE ONLY. Not a certified engineering design. "
              "Verify assumptions, installation conditions, safety and applicable "
              "standards with a qualified professional before real-world use.")


def create_project_pdf_report(path, project):
    """Render each saved calculation as a separate clearly labeled report section."""
    if not project.get('calculations'):
        raise ValueError('Project has no calculations to report.')
    inputs = {}
    outputs = {}
    assumptions = []
    for number, entry in enumerate(project['calculations'], 1):
        prefix = f"SECTION {number}: {entry['type']}"
        inputs[prefix] = 'Inputs below'
        inputs.update({f"{prefix} / {key}": value for key, value in entry['inputs'].items()})
        outputs[prefix] = 'Results below'
        outputs.update({f"{prefix} / {key}": value for key, value in entry['outputs'].items()})
        assumptions.extend(f"{prefix}: {item}" for item in entry['assumptions'])
    return create_pdf_report(path, project['name'],
                             f"Project summary: {len(project['calculations'])} calculations",
                             inputs, outputs, assumptions)


def create_pdf_report(path, title, calculation, inputs, outputs, assumptions):
    if not title.strip() or not calculation.strip() or not inputs or not outputs:
        raise ValueError("Title, calculation, inputs and outputs are required.")
    if any(isinstance(v, (int, float)) and not math.isfinite(v)
           for v in list(inputs.values()) + list(outputs.values())):
        raise ValueError("Non-finite values cannot be reported.")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = QPdfWriter(str(path))
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setResolution(96)
    writer.setTitle(title)
    writer.setCreator("Electrical Engineering Suite")
    painter = QPainter()
    if not painter.begin(writer):
        raise OSError("Cannot write PDF.")
    y = 65
    try:
        def line(value, bold=False, size=11):
            nonlocal y
            font = QFont("Arial", size)
            font.setBold(bold)
            painter.setFont(font)
            metrics = QFontMetrics(font)
            text = ""
            for word in str(value).split():
                candidate = (text + " " + word).strip()
                if text and metrics.horizontalAdvance(candidate) > writer.width() - 120:
                    if y > writer.height() - 85:
                        writer.newPage()
                        y = 65
                    painter.drawText(60, y, text)
                    y += 22
                    text = word
                else:
                    text = candidate
            if y > writer.height() - 85:
                writer.newPage()
                y = 65
            painter.drawText(60, y, text)
            y += 23

        line(title, True, 18)
        line(calculation, True, 13)
        y += 10
        line("INPUTS", True)
        for key, value in inputs.items():
            line(f"{key}: {value}")
        y += 10
        line("RESULTS", True)
        for key, value in outputs.items():
            line(f"{key}: {value}")
        y += 10
        line("ASSUMPTIONS", True)
        for item in assumptions:
            line("- " + item)
        y += 10
        line("SAFETY DISCLAIMER", True)
        line(DISCLAIMER)
    finally:
        painter.end()
    return path
