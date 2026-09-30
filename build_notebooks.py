#!/usr/bin/env python3
"""Build the full, click-and-run workshop notebook from readable source cells."""

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parent


def notebook(cells):
    for index, cell in enumerate(cells):
        cell.id = f"workshop-{index:03d}"
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
# 🧠 Brain imaging and stress: line up the images

Stress is not controlled by one single "stress centre". Different parts of the brain help us notice events, remember what happened before, sense changes in the body, and decide what to do next. In this workshop, you will use brain images to ask where some of those parts are and what an imaging scan can tell us about them.

Brain imaging gives us different views of those systems:

- **MRI** shows the brain's structure: **what tissue is where**.
- **PET** shows where a small amount of an injected, detectable substance has gone. This gives clues about **what the body is doing**. PET looks blurrier than MRI.

MRI and PET may be taken on different days and different scanners. If the person's head is in a slightly different position, the images will not line up. Later, you will move one image to match the other. Researchers call this **registration**.

Today you are the brain-imaging team. You will inspect MRI and PET images, line them up, use a labelled brain map to find four regions, and compare measurements from those regions. There is an optional bonus activity after the main workshop.

> These pictures are teaching materials. The MRI anatomy and region labels come from shared research resources; the PET values are made for this lesson. They are not scans of a patient and cannot diagnose stress.

<div style="padding:12px 16px;border-left:6px solid #31688e;background:#eef6fb"><b>The main mission</b><br>Look at the scans → line them up → check the match → find brain regions → measure and interpret</div>
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
import numpy as np
from IPython.display import Markdown, display
from workshop_helpers import (
    animate_optimiser_search, compare_pet_patterns,
    how_well_matched, load_workshop_data, normalise_match_score, optimise,
    search_trial_count, shift_image, show_alignment,
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

An MRI scanner uses a strong magnet and short pulses of radio waves. Different tissues respond in different ways, so the scanner can make a detailed picture of the brain's structure. MRI helps answer **what tissue is where?**

### PET: what is the body doing?

For PET, a person receives a small injection of a **tracer**. A tracer is a substance we can follow inside the body. It has a radioactive tag that gives off signals the PET scanner can detect. Think of the tag as making the substance visible to the scanner.

The tracer in this lesson is called **FDG**. It is similar to glucose, a sugar cells use for energy. By seeing where FDG collects, we get clues about glucose use. This is why PET can help answer **what is the body doing?** It does not show thoughts or measure stress directly. It also looks blurrier than MRI.

Both pictures below show a slice through the brain, as though we looked down from above. The front of the head is at the top. The third panel puts the two images together, so you can see why both kinds of information are useful. The PET colours are on a lesson scale: brighter means more detected FDG signal.

### PREDICT

Which image shows the edges of brain structures most clearly? Which image shows where more FDG has collected?
        """
    ),
    code(
        """
fig, axes = plt.subplots(1, 3, figsize=(14, 4.6), constrained_layout=True)
axes[0].imshow(mri, cmap="gray", vmin=0, vmax=1)
axes[0].set_title("MRI: detailed anatomy", fontsize=14)
pet_artist = axes[1].imshow(stress_pattern_pet, cmap="magma", vmin=0, vmax=1.0)
axes[1].set_title("PET: where FDG collected", fontsize=14)
axes[2].imshow(mri, cmap="gray", vmin=0, vmax=1)
axes[2].imshow(np.ma.masked_less(stress_pattern_pet, 0.15), cmap="magma", vmin=0, vmax=1, alpha=0.60)
axes[2].set_title("Together: anatomy + PET", fontsize=14)
for ax in axes:
    ax.set_xticks([])
    ax.set_yticks([])
fig.colorbar(pet_artist, ax=axes[1], shrink=0.82, label="FDG signal (lesson scale)")
fig.suptitle("Two images, two kinds of information", fontsize=16, fontweight="bold");
        """
    ),
    md(
        """
<details><summary><b>CHECK YOUR ANSWER</b></summary><br>The MRI shows the structure most clearly. In PET, brighter colours show where more FDG was detected. The combined view helps place the PET signal within the brain.</details>
        """
    ),
    md(
        """
### Look closer: why do we need both?

The next two pictures enlarge the same central area. Look for sharp lines in MRI and smoother patches in PET. A bright PET patch is easier to locate when you can see the MRI structure beneath it.
        """
    ),
    code(
        """
centre_y, centre_x = (size // 2 for size in mri.shape)
zoom = np.s_[centre_y - 45:centre_y + 45, centre_x - 50:centre_x + 50]
fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), constrained_layout=True)
axes[0].imshow(mri[zoom], cmap="gray", vmin=0, vmax=1, interpolation="nearest")
axes[0].set_title("MRI close-up: clearer edges")
axes[1].imshow(stress_pattern_pet[zoom], cmap="magma", vmin=0, vmax=1, interpolation="nearest")
axes[1].set_title("PET close-up: smoother signal")
for ax in axes:
    ax.set_xticks([])
    ax.set_yticks([])
        """
    ),
    md(
        """
## 3. Four regions in the stress story

An **atlas** is a labelled map of the brain. Researchers can place its labels over an MRI to find named areas, rather than saying only "that bright patch over there". The coloured pictures below show four such areas. Each is shown on a brain slice where it is easy to see.

Researchers often study these four areas when investigating stress. They work with other areas and have many jobs beyond this short description:

- **Hippocampus:** helps us remember what happened and where—*Have I been here before?*
- **Amygdala:** helps us notice emotionally important events, including possible danger.
- **Insula:** helps us notice signals from inside the body, such as a racing heart.
- **Anterior cingulate:** helps direct attention and manage competing responses.

These areas do many other jobs too. There is no simple rule that they all "light up" whenever someone feels stress. What a study finds depends on the person, the task, and how and when the brain is measured.
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
| The MRI scanner gives us a detailed picture of the volunteer's brain structure. | This PET scanner is combined with a CT scanner. The PET part detects signals from the injected FDG tracer. |

The scans are acquired separately, on different scanners. The volunteer gets off one bed and later lies down on another. Even with careful positioning, we cannot put their head in **exactly** the same place and angle each time.

That means the MRI and PET images do not automatically line up. Before we measure the PET signal in a named brain area, we need to move the PET image to match the MRI. This is **registration**.

### Your registration task

The PET below has been moved to mimic the sort of mismatch we could get from two separate scanner visits. Change the two numbers and run the cell again. The cyan line shows the edge of the brain in the MRI.

**How the numbers work:** positive `x` moves PET right; positive `y` moves it down. The units are **millimetres (mm)**. Try values from **−10 mm to +10 mm**; decimals are allowed.

### CHANGE ONLY THE TWO NUMBERS BELOW

Start at zero. Use the outer edge first, then compare details in the combined MRI/PET image.
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
## 5. Give your match a score

Your eyes can judge whether the scans line up. A computer needs a number. We use **correlation**: a way to score how closely two patterns change together. Here, it compares the light and dark patterns across the MRI and PET images. When the images line up better, the correlation usually rises.

The graph below turns that number into a **match score** from 0 to 1, using a range chosen for this exercise. A larger score is better. It is **not** a percentage and does not tell us that the scan is medically correct.

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

The computer can also try many positions for us. This search is called an **optimiser**. Watch it make guesses and gradually focus on the better matches. One graph tracks the left/right and up/down moves; the other tracks the match score.

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
The animation shows the search exploring possible matches. Once it gets close, it makes smaller moves.

Now try changing the **two step sizes** in the next cell:

- The **coarse step** is the size of the early jumps. A larger jump checks fewer positions, so it is usually faster, but may skip over a good area. Try `1`, `2`, or `4` mm.
- The **fine step** is the size of the final small moves. A larger value makes fewer guesses, but may stop a little farther from the best match. Try `0.1`, `0.2`, or `0.5` mm.

Compare the number of guesses, final position, match score, and run time.
        """
    ),
    code(
        """
from time import perf_counter

coarse_step_mm = 2    # Try 1, 2, or 4
fine_step_mm = 0.1    # Try 0.1, 0.2, or 0.5

search_started = perf_counter()
automatic_pet, best_x, best_y, automatic_score = optimise(
    mri, challenge_pet, search_range=10,
    coarse_step=coarse_step_mm, fine_step=fine_step_mm,
)
search_seconds = perf_counter() - search_started
print(f"Your correction:      x={x_correction_mm:+.1f} mm, y={y_correction_mm:+.1f} mm | score {normalise_match_score(student_score):.3f} / 1")
print(f"Computer correction:  x={best_x:+.1f} mm, y={best_y:+.1f} mm | score {normalise_match_score(automatic_score):.3f} / 1")
print(f"Guesses tested: {search_trial_count(10, coarse_step_mm, fine_step_mm)}")
print(f"Search time: {search_seconds:.2f} s | coarse step: {coarse_step_mm} mm | fine step: {fine_step_mm} mm")
show_alignment(mri, automatic_pet, brain_outline, title="Automatic registration result");
        """
    ),
    md(
        """
### Registration is one part of preprocessing

The two scans now line up, so a point in the PET image refers to the same place in the MRI. Getting images ready before measuring them is called **preprocessing**. Registration is one of those preparation steps.

A real study may also check whether each image is usable, correct for movement, and reduce unwanted noise. The exact preparation depends on the scan and the question researchers want to answer.
        """
    ),
    md(
        """
### WHAT DID YOU NOTICE?

- Did the optimiser beat or equal your result?
- What changed when you made a step size larger or smaller?
- What extra possibilities would it need to test if PET could also rotate or change size?

<details><summary><b>CHECK YOUR ANSWER</b></summary><br>With the starting step sizes, the computer should find x = −7.2 mm and y = +5.3 mm. Larger steps usually need fewer guesses but can give a slightly lower score. If PET could also turn or change size, the computer would have many more possible matches to test.</details>
        """
    ),
    md(
        """
## 7. Measure named brain areas

Because the PET and MRI now line up, we can use the labelled brain map to select the same area in both. The computer can then calculate the **average PET signal** inside each area.

The numbers are on a lesson scale. They are useful for comparing these images, but they are not clinical measurements.
        """
    ),
    code(
        """
measurement_figure, registered_values = show_region_measurements(
    automatic_pet, region_masks,
    title="Average PET signal after alignment",
)
display(Markdown(
    "| Brain area | Average FDG signal |\\n"
    "|---|---:|\\n" +
    "\\n".join(f"| {name} | {value:.3f} |" for name, value in registered_values.items())
))
        """
    ),
    code(
        """
_, wrong_values = show_region_measurements(
    challenge_pet, region_masks,
    title="What happens if we measure before alignment?",
)
print("Amygdala measurement")
print(f"  Before registration: {wrong_values['Amygdala']:.3f}")
print(f"  After registration:  {registered_values['Amygdala']:.3f}")
        """
    ),
    md(
        """
<details><summary><b>WHY DOES REGISTRATION MATTER?</b></summary><br>The labelled brain map stays in the MRI position. If PET is shifted, the chosen area covers some of the wrong PET pixels and misses some of the intended ones. That can change the average, even if the images look close at first glance.</details>
        """
    ),
    md(
        """
## 8. Compare two PET patterns

The two PET pictures below use the same brain shape, blur, and colour scale. In the second picture we deliberately added extra signal near some of the four labelled regions, so there is a difference to find and measure.

This is a **teaching example**. It does not show what every person's brain does under stress. Real results vary with the experiment and the person.

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

<details><summary><b>CHECK YOUR ANSWER</b></summary><br><ol><li>The labelled map lets us compare the same named brain areas.</li><li>No. We deliberately added the differences, and one PET pattern cannot diagnose stress.</li><li>MRI shows structure; PET gives clues about where FDG collected over a period of time.</li></ol></details>
        """
    ),
    md(
        """
# ⭐ BONUS CONTENT — find task-related changes with fMRI

You have reached the optional bonus. We have used PET to follow an injected substance and compare brain areas. Another type of scan, **functional MRI (fMRI)**, can look for changes while a person does a task. It uses the MRI scanner rather than a PET tracer.

The scanner takes many images in a row. Small changes in blood flow and oxygen can affect the signal. This is called the **BOLD signal**; it is an indirect clue about brain activity, not a photograph of neurons firing. Researchers can compare times when someone is resting with times when they are doing a task.

Our made-for-class experiment has 64 images. It alternates between rest and a pretend stress task. Individual images contain plenty of random variation, or **noise**. Can you tell the rest images from the task images just by looking?
        """
    ),
    code(
        """
from workshop_helpers import calculate_correlation_map, show_fmri_inputs, show_fmri_result

show_fmri_inputs(data["fmri_timeseries"], data["fmri_task_blocks"]);
        """
    ),
    md(
        """
## Bonus exercise: let repetition reveal the pattern

The computer follows each small image square, called a **pixel**, across all 64 images. It then uses correlation to ask whether that pixel's signal follows the rest/task pattern:

- correlation near **+1**: the pixel tends to rise and fall with the task;
- correlation near **0**: no consistent relationship;
- correlation near **−1**: the pixel tends to change in the opposite direction.

Try changing the **threshold**, the cut-off for which pixels to show. A lower threshold shows more pixels, including more random noise.
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
<details><summary><b>WHAT JUST HAPPENED?</b></summary><br>We added a small task-related signal to two regions in these teaching images. It was hard to spot in one picture. Comparing the repeated images with the task timing made the pattern visible. Real fMRI studies need more steps to check movement, noise, and whether a finding is reliable.</details>

| FDG-PET | Task fMRI |
|---|---|
| One image showing where FDG collected | Many images taken one after another |
| Gives clues about glucose use over a period of time | Looks for signal changes that follow a task |
| Brighter PET colour means more measured FDG signal | A result map shows which pixels followed the task pattern |
        """
    ),
    md(
        """
## 9. Recap

<div style="text-align:center;font-size:1.18em;padding:16px;background:#f3f1fa;border-radius:8px"><b>See the structure → line up the images → choose a brain area → measure → think carefully about what the number means</b></div>

Try explaining the workflow in one sentence. Where could an error at the start change the final conclusion?

<details><summary><b>ONE POSSIBLE SUMMARY</b></summary><br>We line up PET with MRI, check the match, use a labelled brain map to choose areas, measure PET signal, and remember what PET can and cannot tell us.</details>

### Sources and further reading

- [TemplateFlow: reusable imaging templates and atlases](https://www.templateflow.org/)
- [CerebrA atlas description](https://pmc.ncbi.nlm.nih.gov/articles/PMC7363886/)
- [Review of stress-induction methods in the MRI scanner](https://pubmed.ncbi.nlm.nih.gov/30631946/)
- [Meta-analysis of BOLD changes during acute stress](https://pubmed.ncbi.nlm.nih.gov/33497786/)

**About these images:** The MRI anatomy and region labels come from shared research resources. PET and bonus fMRI signals were made for this lesson. None are patient scans. See `DATA_SOURCES.md` for the exact data sources, licences, and limits of these examples.
        """
    ),
]


nbf.write(notebook(student_cells), ROOT / "NeuroPET_exercise.ipynb")
print("Built NeuroPET_exercise.ipynb")
