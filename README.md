# Neuroimaging stress: 2-D PET–MRI registration workshop

[![Binder](https://gesis.mybinder.org/badge_logo.svg)](https://gesis.mybinder.org/v2/gh/ashgillman/FDG-PET-Registration-2D-workshop/HEAD?urlpath=%2Fdoc%2Ftree%2FNeuroPET_exercise.ipynb)

A click-and-run Jupyter workshop for high-school students. Students explore
MRI and FDG-PET, identify atlas-defined stress-related brain regions, manually
align displaced PET to MRI, improve a correlation-based match score, watch a
coarse-to-fine optimiser, and compare regional tracer measurements. A clearly
marked bonus section turns a small synthetic fMRI time series into an activation
map.

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

- `NeuroPET_exercise.ipynb` — student-facing, self-explanatory core activity
  plus optional fMRI bonus content.
- `NeuroPET_exercise_finished.ipynb` — the same activity with every cell
  already run, for reviewing the plots and results without executing code. Its
  large embedded animation is omitted; the calculated optimiser result remains
  directly below it.
- `NeuroPET_facilitator.ipynb` — run sheet, answers, expected values, science
  language, and technical checks.

Students only need to run cells and optionally change two correction values in
millimetres. Every cell has a valid initial state, so **Restart Kernel and Run
All** works.

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
jupyter nbconvert --to notebook --execute NeuroPET_facilitator.ipynb \
  --output /tmp/NeuroPET_facilitator.executed.ipynb \
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
- `build_notebooks.py` — readable source for rebuilding both `.ipynb` files.
- `NeuroPET_exercise_finished.ipynb` — checked-in executed snapshot of the
  student notebook; regenerate it with `jupyter nbconvert --execute` after
  changing the activity.
- `tests/test_workshop.py` — numerical acceptance checks.
- `requirements.txt` and `postBuild` — Binder environment and data preparation.
- `DATA_SOURCES.md` — provenance, licences, transformations, citations, and
  interpretation limits.
