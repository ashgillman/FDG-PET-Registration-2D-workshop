#!/usr/bin/env python3
"""Prepare the small, deterministic 2-D dataset used by the workshop.

This script intentionally keeps BrainWeb source data out of the repository.  It
uses Casper O. da Costa-Luis' ``brainweb`` package to download/load one of the
20 normal anatomical models, then creates an MRI-like image and two explicitly
synthetic PET examples from one visually selected axial slice.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import brainweb
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage.transform import resize


SUBJECT_FILENAME = "subject_04.bin.gz"
SUBJECT_SHA256 = "4f1b1d1e9c143d860e8b3c7dcd0713b759c8556e2c248495212f29bbbbac126b"
SLICE_INDEX = 190  # visually checked: clear cortex, ventricles, and brain outline
CROP = (slice(30, 420), slice(0, 362))  # includes margin beyond the whole brain
SQUARE_PADDING = ((0, 0), (14, 14))  # preserve isotropic geometry before resizing
OUTPUT_SHAPE = (192, 192)
RANDOM_SEED = 20260918
KNOWN_SHIFT_X = 7   # positive moves image content right
KNOWN_SHIFT_Y = -5  # negative moves image content up


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tissue_mask(label_codes: np.ndarray, name: str) -> np.ndarray:
    """Use brainweb's label definitions on a discrete anatomical slice."""
    return brainweb.Act.indices(label_codes, name).astype(np.float32)


def resample(image: np.ndarray, *, order: int = 1) -> np.ndarray:
    cropped = np.pad(image[CROP], SQUARE_PADDING, mode="constant")
    resized = resize(
        cropped,
        OUTPUT_SHAPE,
        order=order,
        mode="constant",
        anti_aliasing=order > 0,
        preserve_range=True,
    ).astype(np.float32)
    # Display convention for this workshop: anterior at the top and the
    # posterior/occipital side at the bottom. Left/right is intentionally not
    # labelled because it has not been independently verified.
    return np.flipud(resized).copy()


def shift_image(image: np.ndarray, x_offset: int, y_offset: int) -> np.ndarray:
    """Integer translation with fixed dimensions and zero-filled borders."""
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


def prepare(source: Path, output: Path) -> dict[str, object]:
    raw = brainweb.load_file(str(source))
    if raw.shape != (362, 434, 362) or raw.dtype != np.uint16:
        raise ValueError(f"Unexpected BrainWeb volume: shape={raw.shape}, dtype={raw.dtype}")

    # The low four bits can contain auxiliary flags.  brainweb's tissue codes
    # occupy the upper bits in multiples of 16.
    label_codes = raw[SLICE_INDEX] & np.uint16(0xFFF0)
    gm = resample(tissue_mask(label_codes, "greyMatter"))
    wm = resample(tissue_mask(label_codes, "whiteMatter"))
    csf = resample(tissue_mask(label_codes, "csf"))
    gm_mask = gm >= 0.35
    brain_mask = (gm + wm + csf) >= 0.25

    # MRI-like anatomy. Intensities come from brainweb.T1; the gentle bias and
    # noise are deterministic and included only to avoid a flat cartoon image.
    t1 = (
        brainweb.T1.greyMatter * gm
        + brainweb.T1.whiteMatter * wm
        + brainweb.T1.csf * csf
    )
    yy, xx = np.indices(OUTPUT_SHAPE, dtype=np.float32)
    bias = 0.94 + 0.10 * (xx / (OUTPUT_SHAPE[1] - 1)) + 0.03 * np.sin(yy / 24)
    rng = np.random.default_rng(RANDOM_SEED)
    mri = gaussian_filter(t1 * bias, sigma=0.65)
    mri += rng.normal(0, 1.2, OUTPUT_SHAPE) * brain_mask
    mri = np.clip(mri, 0, None)
    mri /= np.percentile(mri[brain_mask], 99.5)
    mri = np.clip(mri, 0, 1).astype(np.float32)

    # PET is entirely synthetic.  The same scale and noise realisation are
    # used for both cases so their grey-matter means can be compared directly.
    pet_noise = gaussian_filter(rng.normal(0, 1, OUTPUT_SHAPE), sigma=1.5)

    def make_pet(gm_activity: float) -> np.ndarray:
        activity = 0.08 * csf + 0.52 * wm + gm_activity * gm
        activity = gaussian_filter(activity, sigma=3.4)
        activity += 0.035 * pet_noise * brain_mask
        return np.clip(activity, 0, 1.30).astype(np.float32)

    low_binding_pet = make_pet(0.76)
    high_binding_pet = make_pet(1.12)
    challenge_pet = shift_image(low_binding_pet, KNOWN_SHIFT_X, KNOWN_SHIFT_Y)

    metadata = {
        "source": "McGill BrainWeb 20 normal anatomical models, subject 04 discrete model",
        "source_url": brainweb.LINKS[SUBJECT_FILENAME].replace("http://", "https://"),
        "source_filename": SUBJECT_FILENAME,
        "source_sha256": sha256(source),
        "brainweb_python_version": brainweb.__version__,
        "brainweb_python_author": brainweb.__author__,
        "slice_axis": "z",
        "slice_index": SLICE_INDEX,
        "original_shape_zyx": list(raw.shape),
        "crop_yx": [[CROP[0].start, CROP[0].stop], [CROP[1].start, CROP[1].stop]],
        "square_padding_yx": [list(SQUARE_PADDING[0]), list(SQUARE_PADDING[1])],
        "output_shape": list(OUTPUT_SHAPE),
        "random_seed": RANDOM_SEED,
        "known_shift_xy": [KNOWN_SHIFT_X, KNOWN_SHIFT_Y],
        "sign_convention": "positive x moves right; positive y moves down",
        "display_orientation": "axial; anterior at top and posterior/occipital at bottom; left/right unlabelled",
        "pet_status": "synthetic educational examples; not patient scans",
        "pet_blur_sigma_pixels": 3.4,
        "low_gm_activity": 0.76,
        "high_gm_activity": 1.12,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        mri=mri,
        gm_probability=gm,
        gm_mask=gm_mask,
        brain_mask=brain_mask,
        low_binding_pet=low_binding_pet,
        high_binding_pet=high_binding_pet,
        challenge_pet=challenge_pet,
        metadata=np.array(json.dumps(metadata)),
    )
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        help="Existing subject_04.bin.gz. If omitted, download via python-brainweb.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(".brainweb-cache"),
        help="Download cache (default: .brainweb-cache)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/workshop_brainweb.npz"),
        help="Prepared dataset path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.source is None:
        url = brainweb.LINKS[SUBJECT_FILENAME].replace("http://", "https://")
        source = Path(
            brainweb.get_file(
                SUBJECT_FILENAME,
                url,
                cache_dir=str(args.cache_dir),
                chunk_size=1024 * 1024,
            )
        )
    else:
        source = args.source

    observed_hash = sha256(source)
    if observed_hash != SUBJECT_SHA256:
        raise ValueError(
            "Source checksum differs from the file validated for this workshop: "
            f"expected {SUBJECT_SHA256}, got {observed_hash}"
        )
    metadata = prepare(source, args.output)
    print(f"Prepared {args.output} from {source}")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
