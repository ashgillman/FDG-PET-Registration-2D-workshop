"""Small, student-facing helpers for the NeuroPET registration workshop."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


PET_VMIN = 0.0
PET_VMAX = 1.2
PET_CMAP = "magma"  # perceptually uniform and colour-vision-deficiency friendly
NMI_EXERCISE_MAX = 0.46


def load_workshop_data(path: str | Path = "data/workshop_brainweb.npz") -> dict[str, np.ndarray]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} is missing. Binder creates it during image build. "
            "For local use, run: python prepare_brainweb_data.py"
        )
    with np.load(path, allow_pickle=False) as archive:
        data = {name: archive[name] for name in archive.files}
    data["metadata"] = json.loads(str(data["metadata"]))
    return data


def shift_image(image: np.ndarray, x_offset: int = 0, y_offset: int = 0) -> np.ndarray:
    """Shift a 2-D image without wrapping.

    Positive ``x_offset`` moves image content right; positive ``y_offset``
    moves it down. Borders are filled with zero and the dimensions stay fixed.
    """
    if image.ndim != 2:
        raise ValueError("shift_image expects a 2-D image")
    if int(x_offset) != x_offset or int(y_offset) != y_offset:
        raise ValueError("Offsets must be whole numbers of pixels")
    x_offset, y_offset = int(x_offset), int(y_offset)
    height, width = image.shape
    shifted = np.zeros_like(image)
    if abs(x_offset) >= width or abs(y_offset) >= height:
        return shifted
    src_x0, src_x1 = max(0, -x_offset), min(width, width - x_offset)
    src_y0, src_y1 = max(0, -y_offset), min(height, height - y_offset)
    dst_x0, dst_x1 = max(0, x_offset), min(width, width + x_offset)
    dst_y0, dst_y1 = max(0, y_offset), min(height, height + y_offset)
    shifted[dst_y0:dst_y1, dst_x0:dst_x1] = image[src_y0:src_y1, src_x0:src_x1]
    return shifted


def how_well_matched(mri: np.ndarray, pet: np.ndarray) -> float:
    """Return normalized mutual information (0 to 1); larger is better.

    Mutual information is suitable for multimodal images because corresponding
    anatomy can have different brightness in MRI and PET. Intensities are
    grouped into 32 bins before the information entropies are calculated.
    """
    if mri.shape != pet.shape:
        raise ValueError("MRI and PET must have the same dimensions")
    joint_counts, _, _ = np.histogram2d(
        np.asarray(mri, dtype=float).ravel(),
        np.asarray(pet, dtype=float).ravel(),
        bins=32,
        range=((0.0, 1.0), (PET_VMIN, PET_VMAX)),
    )
    joint_probability = joint_counts / joint_counts.sum()
    mri_probability = joint_probability.sum(axis=1)
    pet_probability = joint_probability.sum(axis=0)

    def entropy(probability: np.ndarray) -> float:
        nonzero = probability[probability > 0]
        return float(-np.sum(nonzero * np.log2(nonzero)))

    mri_entropy = entropy(mri_probability)
    pet_entropy = entropy(pet_probability)
    denominator = mri_entropy + pet_entropy
    if denominator == 0:
        return 0.0
    joint_entropy = entropy(joint_probability)
    mutual_information = mri_entropy + pet_entropy - joint_entropy
    return float(np.clip(2.0 * mutual_information / denominator, 0.0, 1.0))


def optimise(
    mri: np.ndarray,
    pet: np.ndarray,
    search_range: int = 10,
) -> tuple[np.ndarray, int, int, float]:
    """Exhaustively test integer translations and return the best result."""
    if search_range < 0:
        raise ValueError("search_range must be non-negative")
    best_score = -np.inf
    best_x = best_y = 0
    best_pet = pet
    for y_offset in range(-search_range, search_range + 1):
        for x_offset in range(-search_range, search_range + 1):
            candidate = shift_image(pet, x_offset, y_offset)
            score = how_well_matched(mri, candidate)
            if score > best_score:
                best_pet, best_x, best_y, best_score = candidate, x_offset, y_offset, score
    return best_pet, best_x, best_y, float(best_score)


def measure_gm_uptake(pet: np.ndarray, gm_mask: np.ndarray) -> float:
    """Mean simulated PET value in the supplied grey-matter mask."""
    if pet.shape != gm_mask.shape:
        raise ValueError("PET and grey-matter mask must have the same dimensions")
    mask = np.asarray(gm_mask, dtype=bool)
    if not mask.any():
        raise ValueError("Grey-matter mask is empty")
    return float(np.mean(pet[mask]))


def _finish_axes(axes) -> None:
    for ax in np.atleast_1d(axes).flat:
        ax.set_xticks([])
        ax.set_yticks([])


def show_alignment(
    mri: np.ndarray,
    pet: np.ndarray,
    gm_contour: np.ndarray | None = None,
    *,
    title: str = "Registration check",
):
    """Show MRI, PET, and a fused overlay with common PET limits."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), constrained_layout=True)
    axes[0].imshow(mri, cmap="gray", vmin=0, vmax=1)
    axes[0].set_title("MRI")
    pet_artist = axes[1].imshow(pet, cmap=PET_CMAP, vmin=PET_VMIN, vmax=PET_VMAX)
    axes[1].set_title("PET")
    axes[2].imshow(mri, cmap="gray", vmin=0, vmax=1)
    axes[2].imshow(pet, cmap=PET_CMAP, vmin=PET_VMIN, vmax=PET_VMAX, alpha=0.58)
    axes[2].set_title("Fused image")
    if gm_contour is not None:
        for ax in axes:
            ax.contour(gm_contour, levels=[0.5], colors=["#35d0ff"], linewidths=1.0)
    _finish_axes(axes)
    fig.colorbar(pet_artist, ax=axes[1:], shrink=0.78, label="Relative tracer signal")
    fig.suptitle(title, fontsize=16, fontweight="bold")
    return fig


def normalise_match_score(score: float) -> float:
    """Map the useful NMI range for this exercise onto 0 to 1."""
    return float(np.clip(score / NMI_EXERCISE_MAX, 0.0, 1.0))


def show_score(score: float, *, label: str = "Match score"):
    """Display raw NMI on an exercise-normalised 0-to-1 scale."""
    display_score = normalise_match_score(score)
    fig, ax = plt.subplots(figsize=(8, 1.4))
    ax.barh([0], [1], color="#e6e6e6", height=0.55)
    ax.barh([0], [display_score], color="#31688e", height=0.55)
    ax.axvline(display_score, color="#fde725", linewidth=3)
    ax.set_xlim(0, 1)
    ax.set_xticks(np.arange(0, 1.01, 0.2))
    ax.set_yticks([])
    ax.set_xlabel("Exercise-normalised score: larger means the image patterns match better")
    ax.set_title(f"{label}: {display_score:.3f} / 1", fontweight="bold")
    fig.tight_layout()
    return fig


def animate_rough_optimiser(
    mri: np.ndarray,
    pet: np.ndarray,
    gm_contour: np.ndarray | None = None,
    *,
    search_range: int = 10,
    seed: int = 2026,
):
    """Animate a deliberately rough search that eventually reaches the optimum."""
    from IPython.display import HTML
    from matplotlib.animation import FuncAnimation

    _, optimum_x, optimum_y, _ = optimise(mri, pet, search_range=search_range)
    rng = np.random.default_rng(seed)

    # Wild guesses first, then progressively smaller jumps around the best
    # location. The final two frames hold on the optimum.
    guesses = [(0, 0)]
    guesses.extend(
        (int(rng.integers(-search_range, search_range + 1)),
         int(rng.integers(-search_range, search_range + 1)))
        for _ in range(7)
    )
    for radius in [7, 6, 5, 4, 3, 2, 2, 1, 1]:
        x = int(np.clip(optimum_x + rng.integers(-radius, radius + 1), -search_range, search_range))
        y = int(np.clip(optimum_y + rng.integers(-radius, radius + 1), -search_range, search_range))
        guesses.append((x, y))
    guesses.extend([(optimum_x, optimum_y), (optimum_x, optimum_y)])

    shifted_images = [shift_image(pet, x, y) for x, y in guesses]
    nmi_scores = [how_well_matched(mri, image) for image in shifted_images]
    display_scores = [normalise_match_score(score) for score in nmi_scores]
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
        trail = np.asarray(guesses[:frame + 1])

        image_ax.clear()
        image_ax.imshow(mri, cmap="gray", vmin=0, vmax=1)
        image_ax.imshow(
            shifted_images[frame], cmap=PET_CMAP,
            vmin=PET_VMIN, vmax=PET_VMAX, alpha=0.58,
        )
        if gm_contour is not None:
            image_ax.contour(gm_contour, levels=[0.5], colors=["#35d0ff"], linewidths=1.0)
        image_ax.set_title(f"Trial {frame + 1}: x={x:+d}, y={y:+d}")
        image_ax.set_xticks([])
        image_ax.set_yticks([])

        offset_ax.clear()
        offset_ax.plot(guess_numbers, trail[:, 0], color="#31688e", marker="o", label="x correction")
        offset_ax.plot(guess_numbers, trail[:, 1], color="#e66101", marker="o", label="y correction")
        offset_ax.set_xlim(1, len(guesses))
        offset_ax.set_ylim(-search_range - 1, search_range + 1)
        offset_ax.set_xlabel("Guess number")
        offset_ax.set_ylabel("Correction (pixels)")
        offset_ax.set_title("Where has it guessed?", fontweight="bold")
        offset_ax.grid(alpha=0.25)
        offset_ax.legend(loc="upper right", fontsize=8)

        score_ax.clear()
        score_ax.plot(guess_numbers, display_scores[:frame + 1], color="#31688e", marker="o")
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


def show_measurement(pet: np.ndarray, gm_mask: np.ndarray, *, title: str):
    """Show the PET image and exactly which pixels contribute to the mean."""
    selected = np.ma.masked_where(~np.asarray(gm_mask, dtype=bool), pet)
    mean_value = measure_gm_uptake(pet, gm_mask)
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.2), constrained_layout=True)
    artist = axes[0].imshow(pet, cmap=PET_CMAP, vmin=PET_VMIN, vmax=PET_VMAX)
    axes[0].contour(gm_mask, levels=[0.5], colors=["#35d0ff"], linewidths=1.0)
    axes[0].set_title("PET + grey-matter contour")
    axes[1].imshow(selected, cmap=PET_CMAP, vmin=PET_VMIN, vmax=PET_VMAX)
    axes[1].set_title(f"Pixels used\nmean = {mean_value:.3f}")
    _finish_axes(axes)
    fig.colorbar(artist, ax=axes, shrink=0.78, label="Relative tracer signal")
    fig.suptitle(title, fontsize=15, fontweight="bold")
    return fig


def compare_cases(low_pet: np.ndarray, high_pet: np.ndarray, gm_mask: np.ndarray):
    """Plot low/high synthetic cases with identical display limits."""
    low = measure_gm_uptake(low_pet, gm_mask)
    high = measure_gm_uptake(high_pet, gm_mask)
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.2), constrained_layout=True)
    for ax, image, name, value in zip(
        axes,
        [low_pet, high_pet],
        ["Low-binding case", "High-binding case"],
        [low, high],
    ):
        artist = ax.imshow(image, cmap=PET_CMAP, vmin=PET_VMIN, vmax=PET_VMAX)
        ax.contour(gm_mask, levels=[0.5], colors=["#35d0ff"], linewidths=0.9)
        ax.set_title(f"{name}\nmean GM uptake = {value:.3f}")
    _finish_axes(axes)
    fig.colorbar(artist, ax=axes, shrink=0.78, label="Relative tracer signal")
    return fig, low, high
