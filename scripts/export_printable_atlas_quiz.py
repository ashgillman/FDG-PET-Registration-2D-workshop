#!/usr/bin/env python3
"""Export the workshop quiz with contours readable in grayscale printing."""

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as effects

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from workshop_helpers import load_workshop_data, show_atlas_quiz


figure = show_atlas_quiz(load_workshop_data(ROOT / "data/workshop_templateflow.npz"))
for axis in figure.axes:
    for contour in axis.collections:
        contour.set_edgecolor("white")
        contour.set_linewidth(1.6)
        contour.set_path_effects([effects.Stroke(linewidth=3.2, foreground="black"),
                                  effects.Normal()])
figure.savefig(ROOT / "images/atlas_quiz.png", dpi=300)
figure.canvas.draw()
for letter, axis in zip("ABCD", figure.axes):
    bounds = axis.get_window_extent().transformed(figure.dpi_scale_trans.inverted())
    figure.savefig(ROOT / f"images/atlas_quiz_{letter}.png", dpi=300,
                   bbox_inches=bounds, pad_inches=0)
