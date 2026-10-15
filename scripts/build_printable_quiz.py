#!/usr/bin/env python3
"""Build standard and large-print A4 quizzes using the workshop's atlas figure.

Run with a Python environment containing ReportLab.
The atlas figure is generated separately with the workshop Python environment:
  MPLCONFIGDIR=/tmp/neurostem-matplotlib .venv/bin/python scripts/export_printable_atlas_quiz.py
  python scripts/build_printable_quiz.py
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/pdf/NeuroSTEM_workshop_quiz.pdf"
FIGURE = ROOT / "images/atlas_quiz.png"
LARGE_OUTPUT = ROOT / "output/pdf/NeuroSTEM_workshop_quiz_large_print.pdf"
WORKSHOP_URL = "https://ashgillman.github.io/neurostem-2026/"


def pattern_table(pdf, top, large=False):
    """Blank judgments of the simulated stress-PET pattern for each group."""
    left = 42
    widths = [73, 120, 110, 85, A4[0] - 84 - 388]
    size, header_height, row_height = (18, 48, 46) if large else (10, 28, 26)
    headings = (["Group", "size"], ["Hippocampus"], ["Amygdala"],
                ["Insula"], ["Anterior", "cingulate"]) if large else (
        ["Participants"], ["Hippocampus"], ["Amygdala"],
        ["Insula"], ["Anterior", "cingulate"])
    bottom = top - header_height - 4 * row_height
    pdf.setFillColor(colors.black)
    pdf.setStrokeColor(colors.HexColor("#555555"))
    pdf.setLineWidth(0.8)
    x = left
    for width, lines in zip(widths, headings):
        pdf.line(x, bottom, x, top)
        pdf.setFont("Helvetica", size)
        baseline = top - header_height / 2 + (len(lines) - 1) * size * 0.55 - size * 0.35
        for value in lines:
            assert pdf.stringWidth(value, "Helvetica", size) < width - 4, value
            pdf.drawCentredString(x + width / 2, baseline, value)
            baseline -= size * 1.1
        x += width
    pdf.line(x, bottom, x, top)
    for y in [top, *[top - header_height - i * row_height for i in range(5)]]:
        pdf.line(left, y, x, y)
    for i, count in enumerate([5, 10, 50, 500]):
        pdf.drawCentredString(left + widths[0] / 2,
                             top - header_height - (i + 0.5) * row_height - size * 0.35,
                             str(count))


def footer(pdf):
    """Keep source notes compact and the printed workshop URL readable."""
    left, right = 42, A4[0] - 42
    pdf.saveState()
    pdf.translate(0, 8)
    pdf.setFillColor(colors.black)
    pdf.setStrokeColor(colors.HexColor("#9a9a9a"))
    pdf.setLineWidth(0.45)
    pdf.line(left, 87, right, 87)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(left, 75, f"Workshop: {WORKSHOP_URL}")
    pdf.linkURL(WORKSHOP_URL, (left, 73, right, 84), relative=1)
    notes = [
        (64, 8, "Teaching examples: workshop PET signals and participant data are simulated."),
        (53, 7, "MRI: MNI152 (Fonov et al., 2011); atlas: CerebrA (Manera et al., 2020), via TemplateFlow."),
        (42, 7, "Worksheet: Ashley Gillman, CC BY 4.0. Image terms and notices: DATA_SOURCES.md / NOTICE."),
        (31, 7, "MRI template: Copyright (C) 1993-2004 Louis Collins, McConnell Brain Imaging Centre,"),
        (21, 7, "Montreal Neurological Institute, McGill University."),
    ]
    for y, size, value in notes:
        pdf.setFont("Helvetica", size)
        pdf.drawString(left, y, value)
    pdf.restoreState()


def build_quiz():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT), pagesize=A4)
    pdf.setTitle("NeuroSTEM - Computing of Neuroscience Data - companion quiz")
    pdf.setAuthor("Ashley Gillman")
    width, height = A4
    left, right = 42, width - 42

    def text(x, y, value, size=11, bold=False):
        pdf.setFillColor(colors.HexColor("#202020"))
        pdf.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        pdf.drawString(x, y, value)

    def line(y, x1=left, x2=right):
        pdf.setStrokeColor(colors.HexColor("#9a9a9a"))
        pdf.setLineWidth(0.45)
        pdf.line(x1, y, x2, y)

    text(left, 803, "NeuroSTEM", 12, True)
    text(left, 777, "Computing of Neuroscience Data", 22, True)
    text(left, 756, "Companion quiz", 13)
    pdf.saveState()
    pdf.translate(0, 40)

    text(left, 686, "1. What is one example of what MRI is useful for?", 11, True)
    line(662)

    text(left, 632, "2. What is one example of what PET is useful for?", 11, True)
    line(608)

    text(left, 578, "3. Name the brain area outlined in each picture.", 11, True)
    text(left, 544, "The pictures show different slice levels through the brain.", 9)
    image = ImageReader(str(FIGURE))
    image_width, image_height = image.getSize()
    figure_height = (right - left) * image_height / image_width
    pdf.drawImage(image, left, 392, width=right-left, height=figure_height)
    for label, x, y in [("A:", left, 371), ("B:", 307, 371),
                        ("C:", left, 342), ("D:", 307, 342)]:
        text(x, y, label, 11, True)
        line(y - 2, x + 22, x + 242)

    question = "4. Why do we line up (register) the MRI and PET images before measuring PET signal in a brain area?"
    rows = simpleSplit(question, "Helvetica-Bold", 11, right - left)
    for index, row in enumerate(rows):
        text(left + (14 if index else 0), 307 - 15 * index, row, 11, True)
    line(270)

    text(left, 238, "5. Is a relationship between stress and PET signal suggested by the data?", 11, True)
    text(left, 221, "For each group size, write yes, no, or unsure for each region.", 10)
    pattern_table(pdf, 211)

    pdf.restoreState()
    footer(pdf)
    pdf.showPage()
    pdf.save()
    print(OUTPUT)


def build_large_quiz():
    pdf = canvas.Canvas(str(LARGE_OUTPUT), pagesize=A4)
    pdf.setTitle("NeuroSTEM - Computing of Neuroscience Data - large-print companion quiz")
    pdf.setAuthor("Ashley Gillman")
    left, right = 42, A4[0] - 42

    def text(y, value, x=left, size=18, bold=False):
        pdf.setFillColor(colors.black)
        pdf.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        assert pdf.stringWidth(value, "Helvetica-Bold" if bold else "Helvetica", size) <= right - x, value
        pdf.drawString(x, y, value)

    def line(y, x1=left, x2=right):
        pdf.setStrokeColor(colors.HexColor("#555555"))
        pdf.setLineWidth(0.8)
        pdf.line(x1, y, x2, y)

    def paragraph(y, value):
        """Wrap against the actual font metrics instead of fixed line breaks."""
        for row in simpleSplit(value, "Helvetica", 18, right - left):
            text(y, row)
            y -= 24
        return y + 24

    text(797, "NeuroSTEM companion quiz", size=22, bold=True)
    text(766, "Computing of Neuroscience Data")
    text(735, "Page 1 of 2")
    pdf.saveState()
    pdf.translate(0, 30)

    paragraph(668, "1. What is one example of what MRI is useful for?")
    line(638)

    paragraph(602, "2. What is one example of what PET is useful for?")
    line(572)

    paragraph(536, "3. Name the brain areas (page 2).")

    paragraph(500, "4. Why line up MRI and PET before measuring a brain area's PET signal?")
    line(446)

    paragraph(410, "5. Is a stress-PET pattern suggested?")
    paragraph(383, "Write yes, no, or unsure in each cell.")
    pattern_table(pdf, 365, large=True)
    pdf.restoreState()
    footer(pdf)
    pdf.showPage()

    text(790, "Brain regions - page 2 of 2", size=22, bold=True)
    paragraph(755, "3. Name each outlined brain area.")

    # Each image is a crop of the same workshop quiz axes, in A-D order.
    for letter, x, image_y in [("A", left, 414), ("B", 316, 414),
                               ("C", left, 129), ("D", 316, 129)]:
        text(image_y + 225, f"Picture {letter}", x=x)
        pdf.drawImage(str(ROOT / f"images/atlas_quiz_{letter}.png"),
                      x, image_y, width=210, height=210)
        text(image_y - 28, f"{letter}:", x=x)
        line(image_y - 31, x + 32, x + 210)
    footer(pdf)
    pdf.showPage()
    pdf.save()
    print(LARGE_OUTPUT)


if __name__ == "__main__":
    build_quiz()
    build_large_quiz()
