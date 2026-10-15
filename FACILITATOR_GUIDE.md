# Facilitator guide: brain stress imaging workshop

Use [PRESENTATION_RUN_SCRIPT.md](PRESENTATION_RUN_SCRIPT.md) for the spoken story, transitions, screen cues, and limits on technical detail.
Students are researchers investigating what happens in the brain during stress and testing candidate regions implicated by earlier research.
The notebook follows their study: scans, alignment, a brain map, regional measurements, and evidence across people.

The [full workshop notebook](NeuroPET_exercise.ipynb) is written so students can
run every cell and read it later without a presenter. In class, pause at the
predictions and let students experiment with the two registration numbers.
A shorter student edition can be made later if the
full version proves too long.

## Suggested timing

| Time | Activity | Ask students |
|---:|---|---|
| 0–3 min | Research question and candidate regions | How could you investigate which brain regions are implicated in stress? |
| 3–13 min | MRI and PET; short clip, molecules, and scan images | What information does each scanner add? |
| 13–26 min | Separate scanner visits and manual registration | What went wrong when we combined the scans? |
| 26–32 min | Match score | How could a computer judge your match? |
| 32–38 min | Computer search and preprocessing | Does the computer improve on your match? |
| 38–46 min | Atlas identification, then region functions | Where should we measure, and why those areas? |
| 46–51 min | Regional measurements and PET patterns | Which measurements differ between the examples? |
| 51–58 min | Group-size exercise | Does a larger group change the underlying effect, or our confidence in the pattern? |
| 58–60 min | Close the main study story | How did our team get from scans to evidence? |
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
  Before introducing their functions, students use the named explorer to identify the unnamed pictures.
  Answers: A = insula, B = hippocampus, C = anterior cingulate, D = amygdala.
- **PET-pattern comparison:** The second pattern contains deliberately added
  signal near selected regions. The increments are teaching choices, not
  measured stress effects. No single pattern diagnoses stress.
  The displayed PET slice supports measurements in three areas; the anterior cingulate is shown at another level in the atlas.
  The group-size exercise includes all four to illustrate what a whole-brain study might measure.
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
   after data preparation needs no network access for calculations.
   The linked MRI clip needs internet access; open it before class.
   The molecule diagram is bundled with the notebook.
2. Run the notebook once with **Restart Kernel and Run All**. The editable
   values start in a valid state.
3. If the animation does not play, continue to the next search cell; its
   calculated result and plot still demonstrate the idea.

The MRI anatomy and atlas labels are research template resources. PET and bonus
fMRI signals are made for the workshop, not patient data. See
[DATA_SOURCES.md](DATA_SOURCES.md) for the full provenance, licensing, and
scientific limitations.
