# NeuroSTEM: Computing of Neuroscience Data

[![Binder](https://gesis.mybinder.org/badge_logo.svg)](https://gesis.mybinder.org/v2/gh/ashgillman/FDG-PET-Registration-2D-workshop/HEAD?urlpath=%2Fdoc%2Ftree%2FNeuroSTEM_exercise.ipynb)

One of four NeuroSTEM workshops, **Computing of Neuroscience Data** is a click-and-run Jupyter workshop for high-school students. Students explore
MRI and PET, identify areas using a brain atlas, line up
the images, compare a numerical match score, and measure PET signal. A short
exercise uses a made-for-class group
of volunteers to show how sample size affects a correlation estimate.
New terms are explained as they appear. An optional bonus section introduces
fMRI through repeated images of a pretend task.

MRI anatomy and labels come from the MNI152 nonlinear symmetric 2009c template
and CerebrA atlas retrieved through TemplateFlow. PET and fMRI signals are
educational simulations. There are no clinical scans or patient data.

## Licence

Original educational content—workshop prose, lesson design, generated teaching
figures, and other non-code material—is licensed under
[CC BY 4.0](LICENSE-CC-BY-4.0). Please credit Ashley Gillman, link to the
licence, and indicate changes when reusing it.

The Python source code and code cells are licensed under the
[MIT License](LICENSE).

Third-party images, templates, and atlas resources retain their own licences;
they are not relicensed by this repository. See [NOTICE](NOTICE) and
`DATA_SOURCES.md` for their attribution and terms.

## Notebooks

- `NeuroSTEM_exercise.ipynb` — the student activity, including optional fMRI bonus content.
- [Finished notebook](https://github.com/ashgillman/FDG-PET-Registration-2D-workshop/actions/workflows/finished-notebook.yml) — download the `NeuroSTEM-exercise-finished` artifact from the latest successful run for calculated plots and results.
- `FACILITATOR_GUIDE.md` — timing, teaching points, expected answers, and preparation notes.
- `PRESENTATION_RUN_SCRIPT.md` — speaking notes for presenting the workshop.
- Companion quiz: [standard](output/pdf/NeuroSTEM_workshop_quiz.pdf) (one A4 page) or [large print](output/pdf/NeuroSTEM_workshop_quiz_large_print.pdf) (two A4 pages, 18-point main text).
  Print at actual size (100%).

The hippocampus, amygdala, insula, and anterior cingulate were selected as
accessible examples from distributed stress-related circuitry described in:
van der Werff et al. (2013), *Neuroimaging resilience to stress: a review*,
*Frontiers in Behavioral Neuroscience*, 7, 39.
<https://doi.org/10.3389/fnbeh.2013.00039>

## Launch on Binder

Use this link after pushing the repository:

<https://mybinder.org/v2/gh/ashgillman/FDG-PET-Registration-2D-workshop/HEAD?labpath=NeuroSTEM_exercise.ipynb>

The first Binder build installs the Python environment, retrieves the selected
TemplateFlow resources, and prepares a compact local dataset. Notebook execution
then makes no network requests.

## Run locally

On Linux, with Nix (the same pinned environment used by GitHub Actions):

```bash
nix develop --command python prepare_templateflow_data.py
nix develop --command python scripts/build_finished_notebook.py
nix develop --command jupyter lab NeuroSTEM_exercise.ipynb
```

The finished copy is written to `dist/NeuroSTEM_exercise_finished.ipynb`.
On macOS or without Nix, use pip:

```bash
python -m pip install -r requirements.txt
python prepare_templateflow_data.py
jupyter lab NeuroSTEM_exercise.ipynb
```

The TemplateFlow cache defaults to `.templateflow-cache/` inside the project.
Set `TEMPLATEFLOW_HOME` before running the preparation script if a different
cache location is preferred.

## Project files

- `prepare_templateflow_data.py` — reproducible TemplateFlow retrieval and
  deterministic PET/fMRI simulation.
- `workshop_helpers.py` — compact registration, plotting, regional-measurement,
  and fMRI-analysis API.
- `build_notebooks.py` — readable source for rebuilding the workshop notebook.
- `flake.nix` and `flake.lock` — pinned Nix environment for CI and local runs.
- `scripts/build_finished_notebook.py` — executes and validates a review copy
  under ignored `dist/`; GitHub Actions publishes it as a downloadable artifact.
- `.github/workflows/finished-notebook.yml` — builds the finished copy on each
  push to `main` and on manual dispatch.
- `tests/test_workshop.py` — numerical acceptance checks.
- `requirements.txt` and `postBuild` — Binder environment and data preparation.
- `DATA_SOURCES.md` — provenance, licences, transformations, citations, and
  interpretation limits.
