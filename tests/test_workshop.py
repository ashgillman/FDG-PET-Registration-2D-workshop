from pathlib import Path

import numpy as np

from workshop_helpers import (
    how_well_matched,
    measure_gm_uptake,
    optimise,
    shift_image,
)


DATA = Path("data/workshop_brainweb.npz")


def test_shift_sign_and_no_wrap():
    image = np.zeros((5, 6), dtype=int)
    image[1, 1] = 7
    shifted = shift_image(image, x_offset=2, y_offset=1)
    assert shifted[2, 3] == 7
    assert shifted.sum() == 7


def test_shift_inverse_away_from_cropped_edges():
    image = np.zeros((8, 8), dtype=int)
    image[2:5, 2:5] = 1
    restored = shift_image(shift_image(image, 2, -1), -2, 1)
    np.testing.assert_array_equal(restored, image)


def test_workshop_acceptance_checks():
    if not DATA.exists():
        raise AssertionError("Run python prepare_brainweb_data.py before the tests")
    with np.load(DATA, allow_pickle=False) as data:
        mri = data["mri"]
        gm_mask = data["gm_mask"]
        challenge = data["challenge_pet"]
        low = data["low_binding_pet"]
        high = data["high_binding_pet"]

    initial_score = how_well_matched(mri, challenge)
    aligned, best_x, best_y, best_score = optimise(mri, challenge, search_range=10)
    assert (best_x, best_y) == (-7, 5)
    assert best_score > initial_score
    assert measure_gm_uptake(aligned, gm_mask) > measure_gm_uptake(challenge, gm_mask)
    assert measure_gm_uptake(high, gm_mask) > measure_gm_uptake(low, gm_mask)
    # The blurred PET brain must have background margin on every edge.
    assert max(low[0].max(), low[-1].max(), low[:, 0].max(), low[:, -1].max()) < 0.01
