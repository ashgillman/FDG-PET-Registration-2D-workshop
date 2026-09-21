#!/usr/bin/env python3
"""Build the student and facilitator notebooks from readable source cells."""

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parent


def notebook(cells):
    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3"},
    }
    return nb


def md(text):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text):
    return nbf.v4.new_code_cell(text.strip())


student_cells = [
    md(
        """
# 🧠 Neuroimaging stress: line up the brain images

Stress is not controlled by one single "stress centre". It recruits interacting brain systems involved in detecting important events, remembering context, monitoring the body, directing attention, and regulating responses.

Neuroimaging gives us different views of those systems:

- **MRI** uses magnetic fields and radio waves to show detailed anatomy.
- **FDG-PET** maps the distribution of a radioactive glucose-like tracer. It is blurrier than MRI, but gives an integrated picture of glucose use during the tracer-uptake period.
- **fMRI** repeatedly measures a blood-oxygen-related signal. A computer looks for small changes that follow a task. A short synthetic fMRI example appears as **bonus content** later.

MRI and PET may be acquired on different days and different scanners. If the person's head is not in exactly the same position, the bright PET signal will sit over the wrong anatomy. **Registration** means moving the images into alignment before measuring or interpreting them.

Today you are the neuroimaging team: inspect the images, align PET with MRI, use an anatomical atlas to identify stress-related regions, and see how a simple fMRI activation map can be made.

> The anatomy comes from an averaged MRI template and anatomical atlas. The PET values and bonus fMRI signals are educational examples—not patient scans, diagnoses, or validated stress biomarkers.

<div style="padding:12px 16px;border-left:6px solid #31688e;background:#eef6fb"><b>The main mission</b><br>MRI + PET → registration → quality check → atlas regions → regional measurements → careful interpretation</div>
        """
    ),
    md(
        """
## 1. RUN THIS — open the imaging toolkit

Click the cell below, then press **Shift + Enter**. The code is complete; you do not need to type anything.
        """
    ),
    code(
        """
import matplotlib.pyplot as plt
from IPython.display import Markdown, display
from workshop_helpers import (
    animate_optimiser_search, calculate_correlation_map, compare_pet_patterns,
    how_well_matched, load_workshop_data, normalise_match_score, optimise,
    shift_image, show_alignment, show_fmri_inputs, show_fmri_result,
    show_region_atlas, show_region_measurements, show_score,
)

data = load_workshop_data()
mri = data["mri"]
brain_outline = data["brain_mask"]
baseline_pet = data["baseline_pet"]
stress_pattern_pet = data["stress_pattern_pet"]
challenge_pet = data["challenge_pet"]
region_specs = data["metadata"]["regions"]
region_masks = {
    "Hippocampus": data["hippocampus_mask"],
    "Amygdala": data["amygdala_mask"],
    "Insula": data["insula_mask"],
}
print("✓ Toolkit ready.")
        """
    ),
    md(
        """
## 2. Meet MRI and PET

### MRI: what tissue is where?

MRI uses a strong magnetic field and radiofrequency pulses to excite hydrogen nuclei in the body's tissues, then measures the signals they produce as they relax. Different tissues produce different signals, allowing MRI to make detailed pictures of anatomy—in simple terms, it shows us **what tissue is where**.

### PET: what is the body doing?

For PET, we inject a small amount of a **tracer** that behaves like a substance important to the body and carries a radioactive tag. The scanner detects signals from the tag, allowing us to map where the tracer goes.

In this workshop the tracer is **FDG**, which behaves similarly to glucose—a sugar that cells use as an energy source. Its distribution gives us information about glucose use in different tissues. PET is therefore called a **functional imaging modality**: it helps tell us about what the body is doing, although its images are blurrier than MRI.

The images below show the same axial level of the brain. The front of the head is at the top.

### PREDICT

Which image will show anatomical boundaries most clearly? Which one shows glucose-tracer distribution?
        """
    ),
    code(
        """
fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), constrained_layout=True)
axes[0].imshow(mri, cmap="gray", vmin=0, vmax=1)
axes[0].set_title("MRI: detailed anatomy", fontsize=14)
pet_artist = axes[1].imshow(stress_pattern_pet, cmap="magma", vmin=0, vmax=1.0)
axes[1].set_title("PET: glucose-tracer pattern", fontsize=14)
for ax in axes:
    ax.set_xticks([])
    ax.set_yticks([])
fig.colorbar(pet_artist, ax=axes[1], shrink=0.82, label="Relative FDG signal")
fig.suptitle("Two images, two kinds of information", fontsize=16, fontweight="bold");
        """
    ),
    md(
        """
<details><summary><b>CHECK YOUR ANSWER</b></summary><br>The MRI shows anatomy most clearly. PET is lower-resolution, but its colour represents the spatial distribution of the glucose-like tracer.</details>
        """
    ),
    md(
        """
## 3. Four regions in the stress story

An **atlas** is a labelled map placed into the same coordinate system as the MRI. It lets us ask questions about named anatomical regions rather than "some bright pixels".

These four regions often appear in stress-neuroimaging discussions. They work in networks and each has many functions beyond this short description:

- **Hippocampus:** supplies memory and context—*Have I encountered this before? Where and when?*
- **Amygdala:** helps identify emotionally important events, including possible threat.
- **Insula:** represents aspects of the body's internal state and helps identify salient events.
- **Anterior cingulate:** contributes to appraisal, attention, conflict monitoring, and regulation.

There is no universal rule that every region simply "lights up" during stress. The direction and size of a finding depend on the task, timing, population, and imaging method.
        """
    ),
    code(
        """
show_region_atlas(data["region_mri"], data["region_masks"], region_specs);
        """
    ),
    md(
        """
## 4. Acquiring and processing the data

Imagine that we have recruited a volunteer for our brain stress study. They visit the imaging centre and we acquire two scans:

| MRI scanner | PET/CT scanner |
|---|---|
| <img src="images/mri_scanner.jpg" alt="A modern MRI scanner" style="width:100%;height:300px;object-fit:cover"> | <img src="images/pet_scanner.jpg" alt="A modern PET/CT scanner" style="width:100%;height:300px;object-fit:cover"> |
| The MRI scanner gives us a detailed picture of the volunteer's brain anatomy. | Modern PET systems are often combined with CT. The PET part detects the tracer distribution that gives us information about glucose use. |

The scans are acquired separately, on different scanners. The volunteer gets off one bed and later lies down on another. Even with careful positioning, we cannot put their head in **exactly** the same place and angle each time.

That means the raw MRI and PET images do not automatically line up. Before we measure PET signal in a named brain region, we need to **process the data** by aligning the PET with the MRI. This alignment step is called **registration**.

### Your registration task

The PET below has the sort of positional mismatch we could get from separate acquisitions. Change the two correction values and run the cell again. The cyan line is the MRI brain boundary; it is not a named region.

**Sign convention:** positive `x` moves PET right; positive `y` moves it down. The units are **millimetres (mm)**. Try values from **−10 mm to +10 mm**; decimals are allowed.

### CHANGE ONLY THE TWO NUMBERS BELOW

Start at zero. Use the outer edge first, then compare internal features in the fused image.
        """
    ),
    code(
        """
x_correction_mm = 0.0
y_correction_mm = 0.0

student_pet = shift_image(challenge_pet, x_correction_mm, y_correction_mm)
show_alignment(mri, student_pet, brain_outline, title="Your manual registration");
        """
    ),
    md(
        """
## 5. Quantify your match

Eyes are useful, but a computer needs a number. We use **Pearson correlation**, which asks whether the brightness patterns in our MRI and PET tend to vary together. For this deliberately related pair of images, better alignment produces a larger correlation. Clinical multimodal registration may use more sophisticated metrics.

For this activity the useful raw range is rescaled so the displayed **match score** runs from 0 to 1. Larger is better; it is not percentage accuracy.

Run the cell, return to the two-number cell, and try to improve the score two or three times.
        """
    ),
    code(
        """
student_score = how_well_matched(mri, student_pet)
show_score(student_score, label="Your match score");
        """
    ),
    md(
        """
<details><summary><b>NEED A HINT?</b></summary><br>Decide left/right before up/down and change one number at a time. First try whole millimetres, then add one decimal place near your best result.</details>

<details><summary><b>SHOW THE MANUAL SOLUTION</b></summary><br>The best-scoring correction is <code>x_correction_mm = -7.2</code> and <code>y_correction_mm = 5.3</code>.</details>
        """
    ),
    md(
        """
## 6. Let the computer search

First watch the optimiser explore different guesses, then make smaller adjustments as it settles. One graph tracks the x and y corrections; the other tracks the match score.

### PREDICT

Will it beat your current score?
        """
    ),
    code(
        """
search_animation = animate_optimiser_search(mri, challenge_pet, brain_outline)
display(search_animation)
        """
    ),
    md(
        """
The animation shows the search moving from broad exploration to smaller adjustments. For the reliable answer below, the computer first searches whole millimetres from −10 to +10, then checks tenths of a millimetre near its best guess. The student interface remains the same two correction values.
        """
    ),
    code(
        """
automatic_pet, best_x, best_y, automatic_score = optimise(mri, challenge_pet, search_range=10)
print(f"Your correction:      x={x_correction_mm:+.1f} mm, y={y_correction_mm:+.1f} mm | score {normalise_match_score(student_score):.3f} / 1")
print(f"Computer correction:  x={best_x:+.1f} mm, y={best_y:+.1f} mm | score {normalise_match_score(automatic_score):.3f} / 1")
print("The optimiser used a coarse search followed by a 0.1 mm refinement.")
show_alignment(mri, automatic_pet, brain_outline, title="Automatic registration result");
        """
    ),
    md(
        """
### Registration is one part of preprocessing

We have now turned two separately acquired scans into images that share the same coordinate system. This is an example of **preprocessing**: the collection of steps used to prepare raw scanner data before scientific measurement and interpretation.

A real study may also check image quality, correct for movement, reduce noise, account for scanner-specific effects, and transform images into a common reference space. The exact steps depend on the imaging method and the research question. Registration is the preprocessing step we have explored today.
        """
    ),
    md(
        """
### WHAT DID YOU NOTICE?

- Did the optimiser beat or equal your result?
- What extra possibilities would it need to test if PET could also rotate or change size?

<details><summary><b>CHECK YOUR ANSWER</b></summary><br>The computer should find x = −7.2 mm and y = +5.3 mm. Rotation or scaling would create many more candidate transformations, so the search would take longer.</details>
        """
    ),
    md(
        """
## 7. Ask anatomical questions

Registration puts the atlas regions and PET signal into the same coordinate system. We can now calculate the mean relative FDG signal inside each region.

The regions are anatomically defined, but the values are unitless workshop numbers—not clinical standardized uptake values.
        """
    ),
    code(
        """
measurement_figure, registered_values = show_region_measurements(
    automatic_pet, region_masks,
    title="Regional measurements after registration",
)
display(Markdown(
    "| Region | Mean relative FDG signal |\\n"
    "|---|---:|\\n" +
    "\\n".join(f"| {name} | {value:.3f} |" for name, value in registered_values.items())
))
        """
    ),
    code(
        """
_, wrong_values = show_region_measurements(
    challenge_pet, region_masks,
    title="What happens if we measure before registration?",
)
print("Amygdala measurement")
print(f"  Before registration: {wrong_values['Amygdala']:.3f}")
print(f"  After registration:  {registered_values['Amygdala']:.3f}")
        """
    ),
    md(
        """
<details><summary><b>WHY DOES REGISTRATION MATTER?</b></summary><br>The atlas mask stays attached to MRI anatomy. If PET is displaced, the mask samples some wrong PET pixels and misses some intended pixels. A plausible-looking scan can therefore produce a biased regional number.</details>
        """
    ),
    md(
        """
## 8. Compare two PET patterns

The same anatomy, noise, blur, and colour scale are used below. In the second image, extra signal was deliberately inserted around selected atlas regions so that we have something visible to find and measure.

This is a **teaching model**, not a claim that every stressed brain has this pattern. Real stress findings vary with the experiment, timing, person, and analysis.

### PREDICT

Which regions will show the largest differences between the two patterns?
        """
    ),
    code(
        """
comparison_figure, baseline_values, stress_values = compare_pet_patterns(
    baseline_pet, stress_pattern_pet, region_masks
)
        """
    ),
    md(
        """
### INTERPRET CAREFULLY

1. Why did the atlas make this comparison more meaningful than simply choosing the brightest pixel?
2. Does the second image prove that somebody is stressed?
3. Why does FDG-PET give a different kind of information from an MRI?

<details><summary><b>CHECK YOUR ANSWER</b></summary><br><ol><li>The atlas selects the same named anatomy in both images.</li><li>No. These are educational images with deliberately inserted differences, and no single FDG pattern diagnoses stress.</li><li>MRI shows structure; FDG-PET shows an integrated glucose-tracer distribution over its uptake period.</li></ol></details>
        """
    ),
    md(
        """
# ⭐ BONUS CONTENT — make a synthetic fMRI activation map

The main workshop used PET because a single positive tracer image makes the registration idea easy to see. Real acute-stress experiments more often use task fMRI.

fMRI does **not** directly photograph neurons firing. It repeatedly measures a blood-oxygen-level-dependent (**BOLD**) signal. The effect is small, so researchers collect a time series while alternating conditions—for example, rest and a stressful task—and test which pixels follow the expected timing.

Our synthetic experiment has 64 scans arranged into alternating blocks. The images are deliberately noisy. Can you tell the rest frames from the stress-task frames just by looking?
        """
    ),
    code(
        """
show_fmri_inputs(data["fmri_timeseries"], data["fmri_task_blocks"]);
        """
    ),
    md(
        """
## Bonus exercise: let repetition reveal the pattern

The computer correlates each pixel's 64-value time series with the expected task response:

- correlation near **+1**: the pixel tends to rise and fall with the task;
- correlation near **0**: no consistent relationship;
- correlation near **−1**: the pixel tends to change in the opposite direction.

Change the threshold if you are curious. A lower threshold shows more pixels but also admits more noise.
        """
    ),
    code(
        """
correlation_threshold = 0.35

calculated_activation = calculate_correlation_map(
    data["fmri_timeseries"], data["fmri_task_design"]
)
show_fmri_result(
    data["fmri_mean"], data["fmri_task_blocks"], data["fmri_task_design"],
    data["fmri_roi_signal"], calculated_activation,
    threshold=correlation_threshold,
);
        """
    ),
    md(
        """
<details><summary><b>WHAT JUST HAPPENED?</b></summary><br>A tiny simulated task-related signal was added to amygdala and insula regions. It was difficult to see in individual frames. Repetition and correlation recovered a spatial activation map. Real fMRI uses more careful modelling, motion correction, statistical testing, and quality control.</details>

| FDG-PET | Task fMRI |
|---|---|
| One tracer-distribution image | A time series containing many images |
| Integrates glucose use over the uptake period | Tracks task-related BOLD changes over time |
| Positive tracer signal | Statistical activation or deactivation map |
| Registration locates uptake anatomically | Registration locates statistical findings anatomically |
        """
    ),
    md(
        """
## 9. Recap

<div style="text-align:center;font-size:1.18em;padding:16px;background:#f3f1fa;border-radius:8px"><b>anatomy + functional image → registration → atlas region → measurement → cautious interpretation</b></div>

Try explaining the workflow in one sentence. Where could an error at the start change the final conclusion?

<details><summary><b>ONE POSSIBLE SUMMARY</b></summary><br>We align a functional image to MRI anatomy, check the alignment, use an atlas to select named regions, measure the signal, and interpret the result according to what that imaging method can actually measure.</details>

### Sources and further reading

- [TemplateFlow: reusable imaging templates and atlases](https://www.templateflow.org/)
- [CerebrA atlas description](https://pmc.ncbi.nlm.nih.gov/articles/PMC7363886/)
- [Review of stress-induction methods in the MRI scanner](https://pubmed.ncbi.nlm.nih.gov/30631946/)
- [Meta-analysis of BOLD changes during acute stress](https://pubmed.ncbi.nlm.nih.gov/33497786/)

**Data note:** MRI anatomy and region labels come from the MNI152 nonlinear symmetric 2009c template and CerebrA atlas retrieved through TemplateFlow. The PET values are generated for this lesson; the bonus fMRI section is explicitly synthetic. See `DATA_SOURCES.md` for provenance, licences, transformations, and scientific cautions.
        """
    ),
]


facilitator_cells = [
    md(
        """
# Neuroimaging stress workshop — facilitator notebook

This is the answer key, run sheet, science-language guide, and technical check for `NeuroPET_exercise.ipynb`. Run all cells before the session.

> MRI anatomy and atlas labels are open template resources. PET and fMRI signals are deterministic educational simulations, not patient data or validated stress biomarkers.
        """
    ),
    md("## RUN THIS — pre-flight check"),
    code(
        """
import platform
import matplotlib
import numpy as np
from workshop_helpers import (
    calculate_correlation_map, compare_pet_patterns, how_well_matched,
    load_workshop_data, measure_region, normalise_match_score, optimise,
    shift_image, show_alignment, show_fmri_result, show_region_atlas,
    show_region_measurements,
)

data = load_workshop_data()
mri = data["mri"]
brain_outline = data["brain_mask"]
baseline_pet = data["baseline_pet"]
stress_pet = data["stress_pattern_pet"]
challenge_pet = data["challenge_pet"]
region_masks = {
    "Hippocampus": data["hippocampus_mask"],
    "Amygdala": data["amygdala_mask"],
    "Insula": data["insula_mask"],
}
print(f"Python {platform.python_version()} | NumPy {np.__version__} | Matplotlib {matplotlib.__version__}")
print(f"Dataset: {mri.shape} | TemplateFlow {data['metadata']['templateflow_version']}")
print(f"Template: {data['metadata']['template']} | Atlas: {data['metadata']['atlas']}")
print("✓ Pre-flight imports and data load succeeded.")
        """
    ),
    md(
        """
## Suggested run sheet

| Time | Student section | Speaking prompt |
|---:|---|---|
| 0–7 | Welcome + modalities | Structure, glucose use, and BOLD answer different questions |
| 7–14 | Meet the regions | No single stress centre; networks and context matter |
| 14–27 | Acquire + manually register | A volunteer cannot be positioned identically in two scanners |
| 27–34 | Match score | A computer needs a numerical definition of better |
| 34–42 | Optimiser | Coarse-to-fine translation search; what changes if rotation is allowed? |
| 42–53 | Atlas measurement | Wrong alignment means wrong anatomical pixels |
| 53–60 | Compare patterns + recap | A simulation is not a diagnosis or universal effect |
| Optional 15 | fMRI bonus | Repetition converts a noisy time series into an activation map |

The core remains workable as a one-hour session. The bonus is suitable for extra time or independent follow-up.
        """
    ),
    md(
        """
## Science framing

- Call the PET images **simulated FDG patterns**, not patient scans.
- FDG-PET integrates tracer distribution over the uptake period; it is not an instantaneous stress meter.
- Stress does not have one universal regional pattern. Findings depend on task, timing, population, and analysis.
- The atlas regions are anatomically meaningful, but their brief functional descriptions are deliberately simplified.
- BOLD fMRI is an indirect haemodynamic signal. The bonus activation map is a correlation demonstration, not a full general linear model.
- Registration is one preprocessing step. Real pipelines may also include quality control, motion correction, noise reduction, scanner-specific corrections, and spatial normalisation.
        """
    ),
    md("## Atlas check"),
    code(
        """
show_region_atlas(data["region_mri"], data["region_masks"], data["metadata"]["regions"]);
        """
    ),
    md(
        """
## Answer key — registration

The best-scoring correction is **x = −7.2 mm, y = +5.3 mm**. Positive x moves image content right; positive y moves it down. The source grid is 1 mm, and interpolation allows sub-millimetre corrections.
        """
    ),
    code(
        """
initial_score = how_well_matched(mri, challenge_pet)
manual_answer = shift_image(challenge_pet, x_offset_mm=-7.2, y_offset_mm=5.3)
manual_score = how_well_matched(mri, manual_answer)
automatic_pet, best_x, best_y, automatic_score = optimise(mri, challenge_pet, search_range=10)
print(f"Initial correlation: {initial_score:.4f} → display {normalise_match_score(initial_score):.3f} / 1")
print(f"Manual correlation:  {manual_score:.4f} → display {normalise_match_score(manual_score):.3f} / 1")
print(f"Automatic result:    {automatic_score:.4f} at x={best_x:+.1f} mm, y={best_y:+.1f} mm")
np.testing.assert_allclose((best_x, best_y), (-7.2, 5.3), atol=0.05)
assert automatic_score > initial_score
show_alignment(mri, automatic_pet, brain_outline, title="Expected automatic result");
        """
    ),
    md(
        """
The displayed score maps the useful correlation range for this exercise (`0.60` to `0.755`) onto `0` to `1`. Call it a **match score**, never percentage accuracy. Pearson correlation is kept intentionally transparent here; clinical multimodal registration often uses metrics designed for differing image contrasts.
        """
    ),
    md("## Answer key — atlas measurements"),
    code(
        """
figure, registered_values = show_region_measurements(
    automatic_pet, region_masks, title="Expected registered measurements"
)
wrong_amygdala = measure_region(challenge_pet, region_masks["Amygdala"])
print(f"Amygdala before registration: {wrong_amygdala:.3f}")
print(f"Amygdala after registration:  {registered_values['Amygdala']:.3f}")
assert registered_values["Amygdala"] > wrong_amygdala
comparison, baseline_values, stress_values = compare_pet_patterns(
    baseline_pet, stress_pet, region_masks
)
for name in region_masks:
    assert stress_values[name] > baseline_values[name]
        """
    ),
    md(
        """
The inserted regional increments are workshop design choices: amygdala +0.36, insula +0.24, and hippocampus +0.12 before PET blurring. They are not literature-derived effect sizes. The purpose is to make registration and atlas-based measurement visible.
        """
    ),
    md("## Bonus answer key — synthetic fMRI"),
    code(
        """
calculated_activation = calculate_correlation_map(
    data["fmri_timeseries"], data["fmri_task_design"]
)
np.testing.assert_allclose(calculated_activation, data["fmri_activation_map"], atol=1e-5)
injected = data["fmri_activation_mask"] > 0.30
brain = data["fmri_mean"] > 0.10
print(f"Mean correlation inside injected region: {calculated_activation[injected].mean():.3f}")
print(f"Mean elsewhere in brain:                 {calculated_activation[brain & ~injected].mean():.3f}")
show_fmri_result(
    data["fmri_mean"], data["fmri_task_blocks"], data["fmri_task_design"],
    data["fmri_roi_signal"], calculated_activation, threshold=0.35,
);
        """
    ),
    md(
        """
## Troubleshooting

- **A student gets lost:** Kernel → Restart Kernel and Run All, then return to the two-number cell. Its initial zero values are valid.
- **Data file missing locally:** run `python prepare_templateflow_data.py` once. Binder runs this during image build.
- **Plots appear twice:** keep the semicolon at the end of plotting cells.
- **Animation is static:** allow JavaScript for the notebook output, or skip directly to the exhaustive optimiser cell.
- **Internet unavailable in class:** launch Binder instances beforehand or prepare the data locally. Notebook execution itself makes no network requests.
- **Discussion runs short:** ask why a strong image correlation does not prove clinical validity, or what motion would do to an fMRI time series.

See `DATA_SOURCES.md` for exact resources, licences, processing, and scientific references.
        """
    ),
]


nbf.write(notebook(student_cells), ROOT / "NeuroPET_exercise.ipynb")
nbf.write(notebook(facilitator_cells), ROOT / "NeuroPET_facilitator.ipynb")
print("Built NeuroPET_exercise.ipynb and NeuroPET_facilitator.ipynb")
