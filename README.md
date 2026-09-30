# Neuroimaging stress: 2-D PET–MRI registration workshop

[![Binder](https://gesis.mybinder.org/badge_logo.svg)](https://gesis.mybinder.org/v2/gh/ashgillman/FDG-PET-Registration-2D-workshop/HEAD?urlpath=%2Fdoc%2Ftree%2FNeuroPET_exercise.ipynb)

A click-and-run Jupyter workshop for high-school students. Students explore
MRI and PET, line up the images, compare a numerical match score, and measure
PET signal in named brain areas. New terms are explained as they appear. An
optional bonus section introduces fMRI through repeated images of a pretend
task.

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

- `NeuroPET_exercise.ipynb` — the full, self-explanatory activity, with many
  images, complete code cells, and optional fMRI bonus content.
- A finished copy of the student notebook is built automatically on GitHub
  Actions, with plots and results already calculated. Download the
  `NeuroPET-exercise-finished` artifact from the latest successful
  [Build finished notebook run](https://github.com/ashgillman/FDG-PET-Registration-2D-workshop/actions/workflows/finished-notebook.yml).
  The animation is omitted from this review copy; the calculated optimiser
  result remains directly below it. The finished copy is not tracked in Git.
- `FACILITATOR_GUIDE.md` — suggested timing, teaching points, expected
  answers, and preparation notes. A shorter student notebook may be derived
  later if the full activity is too long for a class session.

Students only need to run cells and optionally change two correction values in
millimetres. Every cell has a valid initial state, so **Restart Kernel and Run
All** works.

In the computer-search section, students can also change the coarse and fine
search steps, then compare elapsed time and match score. The optimiser evaluates
image matches as it runs; its coarse pass uses a smaller preview image and its
final passes use the full images.

The hippocampus, amygdala, insula, and anterior cingulate were selected as
accessible examples from distributed stress-related circuitry described in:
van der Werff et al. (2013), *Neuroimaging resilience to stress: a review*,
*Frontiers in Behavioral Neuroscience*, 7, 39.
<https://doi.org/10.3389/fnbeh.2013.00039>

These regions have many functions and do not form a complete or universal
"stress circuit." Their inclusion is a teaching choice, not a claim that every
stress experiment should produce a particular result in each region.

## Launch on Binder

Use this link after pushing the repository:

<https://mybinder.org/v2/gh/ashgillman/FDG-PET-Registration-2D-workshop/HEAD?labpath=NeuroPET_exercise.ipynb>

The first Binder build installs the Python environment, retrieves the selected
TemplateFlow resources, and prepares a compact local dataset. Notebook execution
then makes no network requests.

## Run locally

On Linux, with Nix (the same pinned environment used by GitHub Actions):

```bash
nix develop --command python prepare_templateflow_data.py
nix develop --command python scripts/build_finished_notebook.py
nix develop --command jupyter lab NeuroPET_exercise.ipynb
```

The finished copy is written to `dist/NeuroPET_exercise_finished.ipynb`.
On macOS or without Nix, use pip:

```bash
python -m pip install -r requirements.txt
python prepare_templateflow_data.py
jupyter lab NeuroPET_exercise.ipynb
```

The TemplateFlow cache defaults to `.templateflow-cache/` inside the project.
Set `TEMPLATEFLOW_HOME` before running the preparation script if a different
cache location is preferred.

## Verify

```bash
python -m pytest -q
jupyter nbconvert --to notebook --execute NeuroPET_exercise.ipynb \
  --output /tmp/NeuroPET_exercise.executed.ipynb \
  --ExecutePreprocessor.timeout=240
```

Expected core checks:

- best-scoring correction: `x = -7.2 mm`, `y = +5.3 mm`;
- automatic match score exceeds the starting score;
- misregistration changes the atlas-region measurement;
- the simulated stress-challenge pattern exceeds baseline in the selected
  hippocampus, amygdala, and insula masks;
- fMRI task correlation is stronger inside the injected activation regions;
- repeated preparation produces deterministic arrays.

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
