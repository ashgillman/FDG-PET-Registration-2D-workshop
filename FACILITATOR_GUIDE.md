# Facilitator guide: brain stress imaging workshop

The [full workshop notebook](NeuroPET_exercise.ipynb) is written so students can
run every cell and read it later without a presenter. In class, pause at the
predictions and let students experiment with the two registration numbers and
the optimiser's step sizes. A shorter student edition can be made later if the
full version proves too long.

## Suggested timing

| Time | Activity | Ask students |
|---:|---|---|
| 0–8 min | Meet MRI and PET; inspect the full images and close-ups | Which scan shows structure more clearly? What does the PET colour mean? |
| 8–14 min | Four brain regions | Why can't one region tell us whether someone is stressed? |
| 14–27 min | Two scanner visits and manual registration | What happens if you change only left/right, then only up/down? |
| 27–34 min | Match score | Can you improve the number without being told the answer? |
| 34–42 min | Computer search | How do larger steps change the number of guesses and final score? |
| 42–51 min | Regional measurements and PET patterns | Why can a small position error change a regional average? |
| 51–60 min | Group-size exercise and recap | Does a larger group change the underlying effect, or our confidence in the pattern? |
| Optional 15–20 min | fMRI bonus | Why are repeated images useful when one image is noisy? |

These are pacing suggestions. For a one-hour session, keep the PET-pattern
comparison brief and leave the fMRI bonus for afterwards. The notebook has no
section timings visible to students.

## Key answers and teaching points

- **MRI and PET:** MRI shows anatomical detail. FDG-PET shows where an injected,
  detectable glucose-like substance collected over its uptake period. It does
  not give an instant reading of stress or a direct picture of thoughts.
- **Registration:** The intended best-scoring correction is **x = −7.2 mm,
  y = +5.3 mm**. Positive x moves PET right; positive y moves it down. Decimal
  corrections are supported. Let students try whole numbers first.
- **Score:** The code uses correlation between the two image brightness
  patterns. The displayed 0–1 match score rescales the useful range for this
  exercise; it is not percentage accuracy or proof of a clinically valid match.
- **Computer search:** The default search tries 2 mm early jumps on a smaller
  preview, then 0.5 mm and 0.1 mm steps on the full images. A larger step can
  reduce the number of guesses and may reduce the final match score.
- **Brain areas:** The hippocampus, amygdala, insula, and anterior cingulate
  have many roles. Their descriptions in the notebook are starting points, not
  one-function labels or a complete “stress circuit”. The single-region atlas
  explorer also offers ten other labels, so students can see that the atlas is
  a broad anatomical map.
- **PET-pattern comparison:** The second pattern contains deliberately added
  signal near selected regions. The increments are teaching choices, not
  measured stress effects. No single pattern diagnoses stress.
- **Group-size exercise:** Students change `number_of_study_participants` and
  rerun one cell to draw a new group. The built-in links are strong for amygdala,
  moderate for insula, weak for hippocampus, and absent for anterior cingulate.
  Correlation `r` is a simple effect-size measure here. Small samples can show
  strong-looking patterns by chance, including in the area with no built-in
  link. More people make the estimated pattern steadier; they do not strengthen
  the underlying link or establish causation.
- **fMRI bonus:** The repeated images contain a small simulated task-related
  signal. The result map compares each pixel's changing signal with task timing.
  Real studies require motion checks, statistical analysis, and other care.

## Before class

1. Open Binder ahead of time, or prepare `data/workshop_templateflow.npz`
   locally with `python prepare_templateflow_data.py`. Running the notebook
   after data preparation needs no network access.
2. Run the notebook once with **Restart Kernel and Run All**. The editable
   values start in a valid state.
3. If the animation does not play, continue to the next search cell; its
   calculated result and plot still demonstrate the idea.

The MRI anatomy and atlas labels are research template resources. PET and bonus
fMRI signals are made for the workshop, not patient data. See
[DATA_SOURCES.md](DATA_SOURCES.md) for the full provenance, licensing, and
scientific limitations.
