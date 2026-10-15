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
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/pdf/NeuroSTEM_workshop_quiz.pdf"
FIGURE = ROOT / "images/atlas_quiz.png"
LARGE_OUTPUT = ROOT / "output/pdf/NeuroSTEM_workshop_quiz_large_print.pdf"
WORKSHOP_URL = "https://ashgillman.github.io/neurostem-2026/"


def footer(pdf):
    """Keep source notes compact and the printed workshop URL readable."""
    left, right = 42, A4[0] - 42
    pdf.setFillColor(colors.black)
    pdf.setStrokeColor(colors.HexColor("#9a9a9a"))
    pdf.setLineWidth(0.45)
    pdf.line(left, 87, right, 87)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(left, 75, f"Workshop: {WORKSHOP_URL}")
    pdf.linkURL(WORKSHOP_URL, (left, 73, right, 84), relative=0)
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

    text(left, 813, "NeuroSTEM", 12, True)
    text(left, 787, "Computing of Neuroscience Data", 22, True)
    text(left, 766, "Companion quiz", 13)
    text(left, 740, "Name:", 10)
    line(738, left + 35, 360)
    text(385, 740, "Date:", 10)
    line(738, 415, right)
    text(left, 719, "Write short answers. Use the workshop atlas to help with question 3.", 10)

    text(left, 686, "1. What is one example of what MRI is useful for?", 11, True)
    line(662)
    line(639)

    text(left, 608, "2. What is one example of what PET is useful for?", 11, True)
    line(584)
    line(561)

    text(left, 530, "3. Name the brain area outlined in each picture.", 11, True)
    text(left, 512, "Use each name once: Amygdala, Anterior cingulate, Hippocampus, Insula.", 10)
    text(left, 496, "The pictures show different slice levels through the brain.", 9)
    image = ImageReader(str(FIGURE))
    image_width, image_height = image.getSize()
    figure_height = (right - left) * image_height / image_width
    pdf.drawImage(image, left, 344, width=right-left, height=figure_height)
    for label, x, y in [("A:", left, 323), ("B:", 307, 323),
                        ("C:", left, 294), ("D:", 307, 294)]:
        text(x, y, label, 11, True)
        line(y - 2, x + 22, x + 242)

    text(left, 254, "4. Why do we line up (register) the MRI and PET images", 11, True)
    text(left + 14, 239, "before measuring PET signal in a brain area?", 11, True)
    line(215)
    line(192)

    text(left, 157, "5. If stress ratings and PET signal are related in a group,", 11, True)
    text(left + 14, 142, "does that prove that stress caused the PET change? Why?", 11, True)
    line(118)
    line(95)

    footer(pdf)
    pdf.showPage()
    pdf.save()
    print(OUTPUT)


def build_large_quiz():
    pdf = canvas.Canvas(str(LARGE_OUTPUT), pagesize=A4)
    pdf.setTitle("NeuroSTEM - Computing of Neuroscience Data - large-print companion quiz")
    pdf.setAuthor("Ashley Gillman")
    left, right = 42, A4[0] - 42

    def text(y, value, x=left, size=24, bold=False):
        pdf.setFillColor(colors.black)
        pdf.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        assert pdf.stringWidth(value, "Helvetica-Bold" if bold else "Helvetica", size) <= right - x, value
        pdf.drawString(x, y, value)

    def line(y, x1=left, x2=right):
        pdf.setStrokeColor(colors.HexColor("#555555"))
        pdf.setLineWidth(0.8)
        pdf.line(x1, y, x2, y)

    text(817, "NeuroSTEM", size=16, bold=True)
    text(790, "Computing of Neuroscience Data", size=24, bold=True)
    text(767, "Companion quiz - page 1 of 2")
    text(727, "Name:")
    line(724, left + 79, right)

    text(682, "1. What is one example of what")
    text(653, "MRI is useful for?")
    line(622)
    line(595)

    text(556, "2. What is one example of what")
    text(527, "PET is useful for?")
    line(496)
    line(469)

    text(430, "3. Name the brain areas (page 2).")

    text(391, "4. Why line up MRI and PET before")
    text(362, "measuring a brain area's PET signal?")
    line(331)
    line(304)

    text(265, "5. Does a link between stress ratings")
    text(236, "and PET signal prove that stress")
    text(207, "caused the change? Why?")
    line(176)
    line(149)
    line(122)
    footer(pdf)
    pdf.showPage()

    text(800, "Brain regions - page 2 of 2", size=28, bold=True)
    text(765, "3. Name each outlined brain area.")
    text(732, "Use each name once:")
    text(700, "Amygdala, Anterior cingulate,")
    text(670, "Hippocampus, Insula.")

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
