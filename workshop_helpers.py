"""Small, student-facing helpers for the NeuroPET registration workshop."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import shift as ndimage_shift


PET_VMIN = 0.0
PET_VMAX = 1.0
PET_CMAP = "magma"
PIXEL_SIZE_MM = 1.0
CORRELATION_EXERCISE_MIN = 0.60
CORRELATION_EXERCISE_MAX = 0.755
REGION_COLOURS = {
    "Hippocampus": "#22b8cf",
    "Amygdala": "#ff4d6d",
    "Insula": "#ffb703",
    "Anterior cingulate": "#8338ec",
}


def load_workshop_data(
    path: str | Path = "data/workshop_templateflow.npz",
) -> dict[str, np.ndarray]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} is missing. Binder creates it during image build. "
            "For local use, run: python prepare_templateflow_data.py"
        )
    with np.load(path, allow_pickle=False) as archive:
        data = {name: archive[name] for name in archive.files}
    data["metadata"] = json.loads(str(data["metadata"]))
    return data


def shift_image(
    image: np.ndarray,
    x_offset_mm: float = 0,
    y_offset_mm: float = 0,
) -> np.ndarray:
    """Shift a 2-D image by millimetres without wrapping.

    Positive x moves image content right; positive y moves it down. The
    TemplateFlow workshop slice has 1 mm pixels. Borders are filled with zero.
    """
    if image.ndim != 2:
        raise ValueError("shift_image expects a 2-D image")
    x_offset_mm, y_offset_mm = float(x_offset_mm), float(y_offset_mm)
    if not np.isfinite([x_offset_mm, y_offset_mm]).all():
        raise ValueError("Offsets must be finite numbers")
    return ndimage_shift(
        image,
        shift=(y_offset_mm / PIXEL_SIZE_MM, x_offset_mm / PIXEL_SIZE_MM),
        order=1,
        mode="constant",
        cval=0.0,
        prefilter=False,
    )


def how_well_matched(mri: np.ndarray, pet: np.ndarray) -> float:
    """Return Pearson correlation between image patterns; larger is better."""
    if mri.shape != pet.shape:
        raise ValueError("MRI and PET must have the same dimensions")
    first = np.asarray(mri, dtype=float).ravel()
    second = np.asarray(pet, dtype=float).ravel()
    first -= first.mean()
    second -= second.mean()
    denominator = np.linalg.norm(first) * np.linalg.norm(second)
    if denominator == 0:
        return 0.0
    return float(np.clip(np.dot(first, second) / denominator, -1.0, 1.0))


def optimise(
    mri: np.ndarray,
    pet: np.ndarray,
    search_range: int = 10,
    fine_step: float = 0.1,
) -> tuple[np.ndarray, float, float, float]:
    """Search whole millimetres, then refine to a fraction of a millimetre."""
    if search_range < 0:
        raise ValueError("search_range must be non-negative")
    best_score = -np.inf
    best_x = best_y = 0.0
    best_pet = pet
    for y_offset in range(-search_range, search_range + 1):
        for x_offset in range(-search_range, search_range + 1):
            candidate = shift_image(pet, x_offset, y_offset)
            score = how_well_matched(mri, candidate)
            if score > best_score:
                best_pet, best_x, best_y, best_score = candidate, float(x_offset), float(y_offset), score

    if fine_step <= 0 or fine_step > 1:
        raise ValueError("fine_step must be greater than 0 and at most 1")
    fine_x = np.round(np.arange(best_x - 1.0, best_x + 1.0 + fine_step / 2, fine_step), 6)
    fine_y = np.round(np.arange(best_y - 1.0, best_y + 1.0 + fine_step / 2, fine_step), 6)
    for y_offset in fine_y:
        for x_offset in fine_x:
            candidate = shift_image(pet, x_offset, y_offset)
            score = how_well_matched(mri, candidate)
            if score > best_score:
                best_pet, best_x, best_y, best_score = candidate, float(x_offset), float(y_offset), score
    return best_pet, best_x, best_y, float(best_score)


def measure_region(pet: np.ndarray, region_mask: np.ndarray) -> float:
    """Return the mean simulated PET value in a supplied region mask."""
    if pet.shape != region_mask.shape:
        raise ValueError("PET and region mask must have the same dimensions")
    mask = np.asarray(region_mask, dtype=bool)
    if not mask.any():
        raise ValueError("Region mask is empty")
    return float(np.mean(pet[mask]))


def _finish_axes(axes) -> None:
    for ax in np.atleast_1d(axes).flat:
        ax.set_xticks([])
        ax.set_yticks([])


def show_alignment(
    mri: np.ndarray,
    pet: np.ndarray,
    outline: np.ndarray | None = None,
    *,
    title: str = "Registration check",
):
    """Show MRI, PET, and a fused overlay with common PET limits."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), constrained_layout=True)
    axes[0].imshow(mri, cmap="gray", vmin=0, vmax=1)
    axes[0].set_title("MRI: anatomy")
    pet_artist = axes[1].imshow(pet, cmap=PET_CMAP, vmin=PET_VMIN, vmax=PET_VMAX)
    axes[1].set_title("PET: glucose use")
    axes[2].imshow(mri, cmap="gray", vmin=0, vmax=1)
    axes[2].imshow(pet, cmap=PET_CMAP, vmin=PET_VMIN, vmax=PET_VMAX, alpha=0.58)
    axes[2].set_title("Fused image")
    if outline is not None:
        for ax in axes:
            ax.contour(outline, levels=[0.5], colors=["#35d0ff"], linewidths=1.0)
    _finish_axes(axes)
    fig.colorbar(pet_artist, ax=axes[1:], shrink=0.78, label="Relative FDG signal")
    fig.suptitle(title, fontsize=16, fontweight="bold")
    return fig


def normalise_match_score(score: float) -> float:
    """Map the useful correlation range for this exercise onto 0 to 1."""
    useful_range = CORRELATION_EXERCISE_MAX - CORRELATION_EXERCISE_MIN
    return float(np.clip((score - CORRELATION_EXERCISE_MIN) / useful_range, 0.0, 1.0))


def show_score(score: float, *, label: str = "Match score"):
    """Display correlation on an exercise-normalised 0-to-1 scale."""
    display_score = normalise_match_score(score)
    fig, ax = plt.subplots(figsize=(8, 1.4))
    ax.barh([0], [1], color="#e6e6e6", height=0.55)
    ax.barh([0], [display_score], color="#31688e", height=0.55)
    ax.axvline(display_score, color="#fde725", linewidth=3)
    ax.set_xlim(0, 1)
    ax.set_xticks(np.arange(0, 1.01, 0.2))
    ax.set_yticks([])
    ax.set_xlabel("Exercise-normalised score: larger means the patterns match better")
    ax.set_title(f"{label}: {display_score:.3f} / 1", fontweight="bold")
    fig.tight_layout()
    return fig


def animate_rough_optimiser(
    mri: np.ndarray,
    pet: np.ndarray,
    outline: np.ndarray | None = None,
    *,
    search_range: int = 10,
    seed: int = 2026,
):
    """Animate a deliberately rough search that eventually reaches the optimum."""
    from IPython.display import HTML
    from matplotlib.animation import FuncAnimation

    _, optimum_x, optimum_y, _ = optimise(mri, pet, search_range=search_range)
    rng = np.random.default_rng(seed)
    guesses = [(0, 0)]
    guesses.extend(
        (
            int(rng.integers(-search_range, search_range + 1)),
            int(rng.integers(-search_range, search_range + 1)),
        )
        for _ in range(7)
    )
    for radius in [7, 6, 5, 4, 3, 2, 2, 1, 1]:
        x = int(np.clip(optimum_x + rng.integers(-radius, radius + 1), -search_range, search_range))
        y = int(np.clip(optimum_y + rng.integers(-radius, radius + 1), -search_range, search_range))
        guesses.append((x, y))
    guesses.extend([(optimum_x, optimum_y), (optimum_x, optimum_y)])

    shifted_images = [shift_image(pet, x, y) for x, y in guesses]
    display_scores = [
        normalise_match_score(how_well_matched(mri, image)) for image in shifted_images
    ]
    fig = plt.figure(figsize=(10, 5.2), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, width_ratios=(1.35, 1), height_ratios=(1, 1))
    image_ax = fig.add_subplot(grid[:, 0])
    offset_ax = fig.add_subplot(grid[0, 1])
    score_ax = fig.add_subplot(grid[1, 1])
    heading = fig.suptitle("A rough optimiser starts searching…", fontsize=16, fontweight="bold")

    def draw(frame: int):
        x, y = guesses[frame]
        display_score = display_scores[frame]
        guess_numbers = np.arange(1, frame + 2)
        trail = np.asarray(guesses[: frame + 1])

        image_ax.clear()
        image_ax.imshow(mri, cmap="gray", vmin=0, vmax=1)
        image_ax.imshow(
            shifted_images[frame], cmap=PET_CMAP,
            vmin=PET_VMIN, vmax=PET_VMAX, alpha=0.58,
        )
        if outline is not None:
            image_ax.contour(outline, levels=[0.5], colors=["#35d0ff"], linewidths=1.0)
        image_ax.set_title(f"Trial {frame + 1}: x={x:+.1f}, y={y:+.1f}")
        image_ax.set_xticks([])
        image_ax.set_yticks([])

        offset_ax.clear()
        offset_ax.plot(guess_numbers, trail[:, 0], color="#31688e", marker="o", label="x correction")
        offset_ax.plot(guess_numbers, trail[:, 1], color="#e66101", marker="o", label="y correction")
        offset_ax.set_xlim(1, len(guesses))
        offset_ax.set_ylim(-search_range - 1, search_range + 1)
        offset_ax.set_xlabel("Guess number")
        offset_ax.set_ylabel("Correction (mm)")
        offset_ax.set_title("Where has it guessed?", fontweight="bold")
        offset_ax.grid(alpha=0.25)
        offset_ax.legend(loc="upper right", fontsize=8)

        score_ax.clear()
        score_ax.plot(guess_numbers, display_scores[: frame + 1], color="#31688e", marker="o")
        score_ax.scatter(guess_numbers[-1], display_score, color="#fde725", edgecolor="black", s=90, zorder=3)
        score_ax.set_xlim(1, len(guesses))
        score_ax.set_ylim(0, 1.02)
        score_ax.set_xlabel("Guess number")
        score_ax.set_ylabel("Match score")
        score_ax.set_title(f"Current score: {display_score:.3f} / 1", fontweight="bold")
        score_ax.grid(alpha=0.25)

        if frame == len(guesses) - 1:
            heading.set_text("Found it — the images are aligned")
        elif frame >= 8:
            heading.set_text("Smaller jumps as the optimiser settles")
        else:
            heading.set_text("A rough optimiser jumps around")

    animation = FuncAnimation(fig, draw, frames=len(guesses), interval=450, repeat=False)
    html = HTML(animation.to_jshtml(fps=2.2, default_mode="once"))
    plt.close(fig)
    return html


def show_region_atlas(
    region_mri: np.ndarray,
    region_masks: np.ndarray,
    region_specs: list[dict[str, object]],
):
    """Show four stress-related regions on their clearest axial slices."""
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 9.0), constrained_layout=True)
    for ax, image, mask, spec in zip(axes.flat, region_mri, region_masks, region_specs):
        name = str(spec["display_name"])
        colour = str(spec["colour"])
        function = textwrap.fill(str(spec["function"]), width=42)
        ax.imshow(image, cmap="gray", vmin=0, vmax=1)
        ax.contour(mask, levels=[0.5], colors=[colour], linewidths=2.0)
        ax.set_title(f"{name}\n{function}", fontsize=11, color="#202020")
    _finish_axes(axes)
    fig.suptitle("Four regions often discussed in stress neuroimaging", fontsize=16, fontweight="bold")
    return fig


def show_region_measurements(
    pet: np.ndarray,
    region_masks: dict[str, np.ndarray],
    *,
    title: str,
):
    """Show named ROI contours and a bar chart of their PET means."""
    names = list(region_masks)
    values = {name: measure_region(pet, region_masks[name]) for name in names}
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), constrained_layout=True)
    artist = axes[0].imshow(pet, cmap=PET_CMAP, vmin=PET_VMIN, vmax=PET_VMAX)
    for name, mask in region_masks.items():
        axes[0].contour(mask, levels=[0.5], colors=[REGION_COLOURS[name]], linewidths=1.6)
    axes[0].set_title("Registered PET + atlas regions")
    _finish_axes(axes[0])
    fig.colorbar(artist, ax=axes[0], shrink=0.78, label="Relative FDG signal")

    colours = [REGION_COLOURS[name] for name in names]
    axes[1].bar(names, [values[name] for name in names], color=colours)
    axes[1].set_ylim(0, PET_VMAX)
    axes[1].set_ylabel("Mean relative FDG signal")
    axes[1].set_title("Same image, different anatomical questions")
    axes[1].tick_params(axis="x", rotation=18)
    axes[1].grid(axis="y", alpha=0.2)
    for index, name in enumerate(names):
        axes[1].text(index, values[name] + 0.025, f"{values[name]:.3f}", ha="center", fontsize=10)
    fig.suptitle(title, fontsize=15, fontweight="bold")
    return fig, values


def compare_pet_patterns(
    baseline_pet: np.ndarray,
    stress_pattern_pet: np.ndarray,
    region_masks: dict[str, np.ndarray],
):
    """Compare two simulated FDG patterns using identical scales."""
    names = list(region_masks)
    baseline = [measure_region(baseline_pet, region_masks[name]) for name in names]
    stress = [measure_region(stress_pattern_pet, region_masks[name]) for name in names]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.4), constrained_layout=True)
    for ax, image, label in zip(
        axes[:2],
        [baseline_pet, stress_pattern_pet],
        ["Baseline pattern", "Simulated stress-challenge pattern"],
    ):
        artist = ax.imshow(image, cmap=PET_CMAP, vmin=PET_VMIN, vmax=PET_VMAX)
        ax.set_title(label)
    _finish_axes(axes[:2])
    fig.colorbar(artist, ax=axes[:2], shrink=0.78, label="Relative FDG signal")

    x = np.arange(len(names))
    axes[2].bar(x - 0.18, baseline, width=0.36, color="#6c757d", label="Baseline")
    axes[2].bar(x + 0.18, stress, width=0.36, color="#d1495b", label="Stress pattern")
    axes[2].set_xticks(x, names, rotation=18)
    axes[2].set_ylim(0, PET_VMAX)
    axes[2].set_ylabel("Mean relative FDG signal")
    axes[2].set_title("Atlas-based regional measurements")
    axes[2].legend()
    axes[2].grid(axis="y", alpha=0.2)
    return fig, dict(zip(names, baseline)), dict(zip(names, stress))


def calculate_correlation_map(timeseries: np.ndarray, task_design: np.ndarray) -> np.ndarray:
    """Correlate each pixel's fMRI time course with the simulated task."""
    if timeseries.ndim != 3 or timeseries.shape[0] != len(task_design):
        raise ValueError("Time series must have shape (time, y, x) matching the task")
    design = np.asarray(task_design, dtype=float)
    design = (design - design.mean()) / design.std()
    centred = timeseries - timeseries.mean(axis=0)
    denominator = np.sqrt(np.sum(centred**2, axis=0)) * np.sqrt(np.sum(design**2))
    return np.divide(
        np.sum(centred * design[:, None, None], axis=0),
        denominator,
        out=np.zeros(timeseries.shape[1:], dtype=float),
        where=denominator > 0,
    )


def show_fmri_inputs(timeseries: np.ndarray, task_blocks: np.ndarray):
    """Show task timing and individual noisy fMRI frames."""
    frame_numbers = [4, 12, 20, 28]
    fig = plt.figure(figsize=(12, 6.2), constrained_layout=True)
    grid = fig.add_gridspec(2, 4, height_ratios=(1, 2.2))
    task_ax = fig.add_subplot(grid[0, :])
    task_ax.step(np.arange(len(task_blocks)), task_blocks, where="mid", color="#d1495b", linewidth=2)
    task_ax.fill_between(np.arange(len(task_blocks)), task_blocks, step="mid", color="#d1495b", alpha=0.2)
    task_ax.set_yticks([0, 1], ["rest", "stress task"])
    task_ax.set_xlabel("Scan number")
    task_ax.set_title("A block design alternates rest and a stress task", fontweight="bold")
    task_ax.set_xlim(0, len(task_blocks) - 1)
    task_ax.grid(axis="x", alpha=0.2)

    image_axes = [fig.add_subplot(grid[1, index]) for index in range(4)]
    for ax, frame in zip(image_axes, frame_numbers):
        ax.imshow(timeseries[frame], cmap="gray")
        condition = "stress task" if task_blocks[frame] else "rest"
        ax.set_title(f"Frame {frame + 1}: {condition}")
    _finish_axes(image_axes)
    fig.suptitle("One fMRI scan is a time series, not one activity picture", fontsize=16, fontweight="bold")
    return fig


def show_fmri_result(
    mean_image: np.ndarray,
    task_blocks: np.ndarray,
    task_design: np.ndarray,
    roi_signal: np.ndarray,
    correlation_map: np.ndarray,
    *,
    threshold: float = 0.35,
):
    """Show the simulated BOLD time course and thresholded correlation map."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), constrained_layout=True)
    scan = np.arange(len(task_blocks))
    axes[0].fill_between(scan, 99.0, 103.0, where=task_blocks > 0, color="#d1495b", alpha=0.13, label="stress-task block")
    axes[0].plot(scan, roi_signal, color="#31688e", linewidth=2, label="mean ROI signal")
    axes[0].plot(scan, 99.2 + 2.6 * task_design, color="#d1495b", linestyle="--", label="expected response shape")
    axes[0].set_xlabel("Scan number")
    axes[0].set_ylabel("Relative BOLD signal (mean = 100)")
    axes[0].set_title("The signal is tiny, noisy, and repeated", fontweight="bold")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.2)

    axes[1].imshow(mean_image, cmap="gray", vmin=0, vmax=1)
    overlay = np.ma.masked_less(correlation_map, threshold)
    artist = axes[1].imshow(overlay, cmap="autumn", vmin=threshold, vmax=0.9, alpha=0.78)
    axes[1].set_title(f"Pixels correlated with the task\nthreshold = {threshold:.2f}", fontweight="bold")
    _finish_axes(axes[1])
    fig.colorbar(artist, ax=axes[1], shrink=0.78, label="Correlation with task")
    fig.suptitle("Synthetic fMRI activation analysis", fontsize=16, fontweight="bold")
    return fig
