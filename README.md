# NeuroPET 2-D image-registration workshop

A click-and-run Jupyter workshop for high-school students. Students visually
align displaced PET to MRI, receive a normalized-mutual-information match
score, run a transparent exhaustive optimiser, and measure grey-matter tracer
signal.

All imaging is educational simulation. There are no clinical scans or patient
data in this project.

## Notebooks

- `NeuroPET_exercise.ipynb` — projected/student-facing 45–50 minute activity.
- `NeuroPET_facilitator.ipynb` — timing, answers, expected values, and checks.

Students only need to run cells and optionally change two integer offsets. Every
cell has a valid initial state, so **Restart Kernel and Run All** works.

## Launch on Binder

1. Put this directory in a public GitHub repository.
2. Open
   `https://mybinder.org/v2/gh/YOUR-ACCOUNT/YOUR-REPOSITORY/HEAD?labpath=NeuroPET_exercise.ipynb`
   after replacing the account and repository names.
3. Wait for the first image build. The `postBuild` script downloads one official
   BrainWeb subject and prepares the small 2-D workshop dataset. Student notebook
   execution itself makes no network requests.

The repository deliberately does not contain BrainWeb source or derived image
arrays because the upstream site's redistribution terms are not explicit. See
`DATA_SOURCES.md` before publishing a pre-generated dataset or Binder image.

## Run locally

```bash
python -m pip install -r requirements.txt
python prepare_brainweb_data.py
jupyter lab NeuroPET_exercise.ipynb
```

If you already have the official source file:

```bash
python prepare_brainweb_data.py --source /path/to/subject_04.bin.gz
```

The prepared file is deterministic and is ignored by Git.

## Verify

```bash
python -m pytest -q
jupyter nbconvert --to notebook --execute NeuroPET_exercise.ipynb \
  --output /tmp/NeuroPET_exercise.executed.ipynb \
  --ExecutePreprocessor.timeout=180
jupyter nbconvert --to notebook --execute NeuroPET_facilitator.ipynb \
  --output /tmp/NeuroPET_facilitator.executed.ipynb \
  --ExecutePreprocessor.timeout=180
```

Expected core checks:

- hidden displacement: `(+7, -5)` pixels;
- recovered correction: `(-7, +5)` pixels;
- automatic score exceeds the starting score;
- misregistration changes the grey-matter measurement;
- high-binding mean exceeds low-binding mean;
- repeated preparation produces identical arrays.

## Project files

- `prepare_brainweb_data.py` — reproducible BrainWeb download/processing path.
- `workshop_helpers.py` — compact student-facing registration and plotting API.
- `tests/test_workshop.py` — numerical acceptance checks.
- `requirements.txt` and `postBuild` — Binder environment and data preparation.
- `DATA_SOURCES.md` — provenance, transformations, citations, and licensing.
