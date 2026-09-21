#!/usr/bin/env python3
"""Prepare the deterministic 2-D MRI, PET, atlas, and fMRI workshop data.

The source anatomy is the MNI152 nonlinear symmetric 2009c template and the
CerebrA anatomical atlas, both retrieved through TemplateFlow. PET and fMRI
signals are explicitly synthetic educational examples; they are not patient
data and do not represent a validated stress biomarker.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

import nibabel as nib
import numpy as np
from scipy.ndimage import gaussian_filter, gaussian_filter1d, shift as ndimage_shift
from skimage.transform import resize


TEMPLATE_ID = "MNI152NLin2009cSym"
ATLAS_IMAGE_NAME = "CerebrA"
ATLAS_TABLE_NAME = "CerebA"  # spelling used by the TemplateFlow TSV resource
RESOLUTION = 1
MAIN_Z_MM = -16
CROP_Y = slice(18, 211)  # 193 mm field of view; keeps the entire axial brain
OUTPUT_SHAPE = (193, 193)
FMRI_SHAPE = (96, 96)
RANDOM_SEED = 20260921
PIXEL_SIZE_MM = 1.0
# These generation offsets are calibrated so that the cross-modal correlation
# score has a clear sub-millimetre optimum at (-7.2 mm, +5.3 mm).
CHALLENGE_SHIFT_X_MM = 7.05
CHALLENGE_SHIFT_Y_MM = -4.8
EXPECTED_CORRECTION_X_MM = -7.2
EXPECTED_CORRECTION_Y_MM = 5.3

REGION_SPECS = (
    {
        "key": "hippocampus",
        "atlas_name": "Hippocampus",
        "display_name": "Hippocampus",
        "z_mm": -20,
        "colour": "#22b8cf",
        "function": "Adds context and memory: where, when, and what happened.",
    },
    {
        "key": "amygdala",
        "atlas_name": "Amygdala",
        "display_name": "Amygdala",
        "z_mm": -20,
        "colour": "#ff4d6d",
        "function": "Helps detect emotionally important events, including possible threat.",
    },
    {
        "key": "insula",
        "atlas_name": "Insula",
        "display_name": "Insula",
        "z_mm": 2,
        "colour": "#ffb703",
        "function": "Combines body-state signals with attention and emotional salience.",
    },
    {
        "key": "anterior_cingulate",
        "atlas_name": "Rostral Anterior Cingulate",
        "display_name": "Anterior cingulate",
        "z_mm": -10,
        "colour": "#8338ec",
        "function": "Supports appraisal, attention, conflict monitoring, and regulation.",
    },
)


def shift_image(image: np.ndarray, x_offset_mm: float, y_offset_mm: float) -> np.ndarray:
    """Subpixel translation with fixed dimensions and zero-filled borders."""
    return ndimage_shift(
        image,
        shift=(float(y_offset_mm) / PIXEL_SIZE_MM, float(x_offset_mm) / PIXEL_SIZE_MM),
        order=1,
        mode="constant",
        cval=0.0,
        prefilter=False,
    )


def _one_path(result) -> Path:
    if isinstance(result, (list, tuple)):
        if len(result) != 1:
            raise ValueError(f"Expected one TemplateFlow resource, got {result}")
        result = result[0]
    return Path(result)


def fetch_sources(cache_dir: Path) -> dict[str, Path]:
    """Fetch only the five TemplateFlow images and one label table we use."""
    os.environ.setdefault("TEMPLATEFLOW_HOME", str(cache_dir.resolve()))
    from templateflow import api

    common = {"template": TEMPLATE_ID, "resolution": RESOLUTION}
    paths = {
        "t1": _one_path(api.get(**common, suffix="T1w")),
        "atlas": _one_path(
            api.get(**common, atlas=ATLAS_IMAGE_NAME, suffix="dseg")
        ),
        "gm": _one_path(api.get(**common, label="GM", suffix="probseg")),
        "wm": _one_path(api.get(**common, label="WM", suffix="probseg")),
        "csf": _one_path(api.get(**common, label="CSF", suffix="probseg")),
        "labels": _one_path(
            api.get(
                TEMPLATE_ID,
                atlas=ATLAS_TABLE_NAME,
                suffix="dseg",
                extension=".tsv",
            )
        ),
    }
    missing = [str(path) for path in paths.values() if not path.exists() or path.stat().st_size == 0]
    if missing:
        raise FileNotFoundError(f"TemplateFlow did not retrieve usable resources: {missing}")
    return paths


def load_canonical(path: Path) -> nib.Nifti1Image:
    return nib.as_closest_canonical(nib.load(path))


def z_index(image: nib.Nifti1Image, z_mm: int) -> int:
    scale = float(image.affine[2, 2])
    origin = float(image.affine[2, 3])
    return int(round((z_mm - origin) / scale))


def axial_slice(
    volume: np.ndarray,
    image: nib.Nifti1Image,
    z_mm: int,
    *,
    order: int,
) -> np.ndarray:
    """Return a square axial display with anterior at top and left at left."""
    plane = volume[:, CROP_Y, z_index(image, z_mm)]
    display = np.rot90(plane)
    return resize(
        display,
        OUTPUT_SHAPE,
        order=order,
        mode="constant",
        anti_aliasing=order > 0,
        preserve_range=True,
    ).astype(np.float32 if order > 0 else np.int16)


def normalise_mri(image: np.ndarray) -> np.ndarray:
    positive = image[image > 0]
    lower, upper = np.percentile(positive, [0.5, 99.7])
    return np.clip((image - lower) / (upper - lower), 0, 1).astype(np.float32)


def read_labels(path: Path) -> dict[str, list[int]]:
    labels: dict[str, list[int]] = {}
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            labels.setdefault(row["name"], []).append(int(row["label"]))
    return labels


def region_mask(atlas_slice: np.ndarray, labels: dict[str, list[int]], name: str) -> np.ndarray:
    if name not in labels:
        raise KeyError(f"Atlas label not found: {name}")
    mask = np.isin(atlas_slice, labels[name])
    if not mask.any():
        raise ValueError(f"{name} is absent from the selected slice")
    return mask


def make_pet_images(
    gm: np.ndarray,
    wm: np.ndarray,
    csf: np.ndarray,
    region_masks: dict[str, np.ndarray],
    brain_mask: np.ndarray,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Create baseline and stress-pattern FDG-PET teaching images."""
    baseline_activity = 0.08 * csf + 0.38 * wm + 0.68 * gm
    stress_activity = baseline_activity.copy()
    # Deliberately visible workshop signals, not literature-derived effect sizes.
    stress_activity += 0.36 * region_masks["amygdala"]
    stress_activity += 0.24 * region_masks["insula"]
    stress_activity += 0.12 * region_masks["hippocampus"]

    shared_noise = gaussian_filter(rng.normal(0, 1, OUTPUT_SHAPE), sigma=1.8)

    def finish(activity: np.ndarray) -> np.ndarray:
        image = gaussian_filter(activity, sigma=4.0)
        image += 0.035 * shared_noise * brain_mask
        return np.clip(image, 0, 1.25).astype(np.float32)

    return finish(baseline_activity), finish(stress_activity)


def make_fmri(
    mri: np.ndarray,
    brain_mask: np.ndarray,
    activation_mask: np.ndarray,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    """Create a small BOLD block-design time series and its correlation map."""
    mean_image = resize(
        gaussian_filter(mri, sigma=2.2), FMRI_SHAPE,
        anti_aliasing=True, preserve_range=True,
    ).astype(np.float32)
    small_brain = resize(
        brain_mask.astype(float), FMRI_SHAPE,
        order=0, anti_aliasing=False, preserve_range=True,
    ) > 0.5
    small_activation = resize(
        activation_mask.astype(float), FMRI_SHAPE,
        order=1, anti_aliasing=True, preserve_range=True,
    )
    small_activation = gaussian_filter(small_activation, sigma=1.1)
    if small_activation.max() > 0:
        small_activation /= small_activation.max()

    n_timepoints = 64
    task_blocks = np.tile(np.r_[np.zeros(8), np.ones(8)], 4).astype(np.float32)
    task_design = gaussian_filter1d(task_blocks, sigma=1.4)
    task_design -= task_design.min()
    task_design /= task_design.max()

    spatial_noise = rng.normal(0, 1, (n_timepoints, *FMRI_SHAPE)).astype(np.float32)
    spatial_noise = gaussian_filter(spatial_noise, sigma=(0.7, 1.0, 1.0))
    drift = 0.003 * np.sin(np.linspace(0, 3 * np.pi, n_timepoints, dtype=np.float32))
    timeseries = mean_image[None, :, :] * (
        1.0
        + 0.045 * task_design[:, None, None] * small_activation[None, :, :]
        + drift[:, None, None]
    )
    timeseries += 0.014 * spatial_noise * small_brain[None, :, :]
    timeseries *= small_brain[None, :, :]

    design_z = (task_design - task_design.mean()) / task_design.std()
    voxel_mean = timeseries.mean(axis=0)
    centred = timeseries - voxel_mean
    denominator = np.sqrt(np.sum(centred**2, axis=0)) * np.sqrt(np.sum(design_z**2))
    correlation = np.divide(
        np.sum(centred * design_z[:, None, None], axis=0),
        denominator,
        out=np.zeros(FMRI_SHAPE, dtype=np.float32),
        where=denominator > 0,
    )
    roi = small_activation > 0.30
    roi_signal = timeseries[:, roi].mean(axis=1)
    roi_signal = 100 * roi_signal / roi_signal.mean()

    return {
        "fmri_mean": mean_image,
        "fmri_timeseries": timeseries.astype(np.float32),
        "fmri_task_blocks": task_blocks,
        "fmri_task_design": task_design.astype(np.float32),
        "fmri_roi_signal": roi_signal.astype(np.float32),
        "fmri_activation_map": correlation.astype(np.float32),
        "fmri_activation_mask": small_activation.astype(np.float32),
    }


def prepare(cache_dir: Path, output: Path) -> dict[str, object]:
    paths = fetch_sources(cache_dir)
    images = {key: load_canonical(paths[key]) for key in ("t1", "atlas", "gm", "wm", "csf")}
    reference = images["t1"]
    for key, image in images.items():
        if image.shape != reference.shape or not np.allclose(image.affine, reference.affine):
            raise ValueError(f"TemplateFlow resource {key} is not aligned to the T1 template")

    volumes = {key: np.asarray(image.dataobj) for key, image in images.items()}
    label_ids = read_labels(paths["labels"])

    mri = normalise_mri(axial_slice(volumes["t1"], reference, MAIN_Z_MM, order=1))
    gm = axial_slice(volumes["gm"], reference, MAIN_Z_MM, order=1)
    wm = axial_slice(volumes["wm"], reference, MAIN_Z_MM, order=1)
    csf = axial_slice(volumes["csf"], reference, MAIN_Z_MM, order=1)
    atlas_main = axial_slice(volumes["atlas"], reference, MAIN_Z_MM, order=0)
    brain_mask = (gm + wm + csf) > 0.18

    main_regions = {
        spec["key"]: region_mask(atlas_main, label_ids, spec["atlas_name"])
        for spec in REGION_SPECS[:3]
    }
    rng = np.random.default_rng(RANDOM_SEED)
    baseline_pet, stress_pattern_pet = make_pet_images(
        gm, wm, csf, main_regions, brain_mask, rng
    )
    challenge_pet = shift_image(
        stress_pattern_pet, CHALLENGE_SHIFT_X_MM, CHALLENGE_SHIFT_Y_MM
    )

    region_mri = []
    region_masks = []
    for spec in REGION_SPECS:
        region_mri.append(
            normalise_mri(axial_slice(volumes["t1"], reference, spec["z_mm"], order=1))
        )
        atlas_slice = axial_slice(volumes["atlas"], reference, spec["z_mm"], order=0)
        region_masks.append(region_mask(atlas_slice, label_ids, spec["atlas_name"]))

    fmri_activation = main_regions["amygdala"] | main_regions["insula"]
    fmri = make_fmri(mri, brain_mask, fmri_activation, rng)

    metadata = {
        "templateflow_version": __import__("templateflow").__version__,
        "template": TEMPLATE_ID,
        "atlas": ATLAS_IMAGE_NAME,
        "resolution_mm": RESOLUTION,
        "main_slice_z_mm": MAIN_Z_MM,
        "output_shape": list(OUTPUT_SHAPE),
        "random_seed": RANDOM_SEED,
        "pixel_size_mm": PIXEL_SIZE_MM,
        "challenge_generation_shift_xy_mm": [
            CHALLENGE_SHIFT_X_MM,
            CHALLENGE_SHIFT_Y_MM,
        ],
        "expected_correction_xy_mm": [
            EXPECTED_CORRECTION_X_MM,
            EXPECTED_CORRECTION_Y_MM,
        ],
        "sign_convention": "positive x moves right; positive y moves down; offsets are millimetres",
        "display_orientation": "axial; anterior at top; anatomical left at left",
        "pet_status": "synthetic educational FDG-PET patterns; not patient scans or validated biomarkers",
        "fmri_status": "synthetic educational BOLD time series; not patient data or a validated stress signature",
        "pet_blur_sigma_mm": 4.0,
        "regions": list(REGION_SPECS),
        "source_files": {key: path.name for key, path in paths.items()},
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        mri=mri,
        gm_probability=gm.astype(np.float32),
        brain_mask=brain_mask,
        baseline_pet=baseline_pet,
        stress_pattern_pet=stress_pattern_pet,
        challenge_pet=challenge_pet,
        hippocampus_mask=main_regions["hippocampus"],
        amygdala_mask=main_regions["amygdala"],
        insula_mask=main_regions["insula"],
        region_mri=np.stack(region_mri).astype(np.float32),
        region_masks=np.stack(region_masks),
        metadata=np.array(json.dumps(metadata)),
        **fmri,
    )
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(".templateflow-cache"),
        help="TemplateFlow cache (default: .templateflow-cache)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/workshop_templateflow.npz"),
        help="Prepared dataset path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = prepare(args.cache_dir, args.output)
    print(f"Prepared {args.output} from TemplateFlow resources")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
