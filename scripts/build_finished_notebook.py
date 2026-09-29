"""Execute the student notebook and save a review copy outside Git tracking."""

from pathlib import Path

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "NeuroPET_exercise.ipynb"
DESTINATION = ROOT / "dist" / "NeuroPET_exercise_finished.ipynb"


def main():
    notebook = nbformat.read(SOURCE, as_version=4)
    animation_cells = 0
    for cell in notebook.cells:
        if cell.cell_type == "code" and "animate_optimiser_search(" in cell.source:
            cell.source = (
                "print('Animation omitted from this review copy; run the "
                "student notebook to watch it.')"
            )
            animation_cells += 1
    if animation_cells != 1:
        raise RuntimeError(f"Expected one animation cell, found {animation_cells}")

    NotebookClient(notebook, timeout=240, kernel_name="python3", resources={
        "metadata": {"path": str(ROOT)}
    }).execute()

    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    if not code_cells or any(cell.execution_count is None for cell in code_cells):
        raise RuntimeError("Some cells did not execute")
    if any(output.output_type == "error" for cell in code_cells for output in cell.outputs):
        raise RuntimeError("The executed notebook contains an error output")

    DESTINATION.parent.mkdir(exist_ok=True)
    nbformat.write(notebook, DESTINATION)
    print(f"Wrote {DESTINATION}")


if __name__ == "__main__":
    main()
