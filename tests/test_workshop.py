import json
from pathlib import Path

import numpy as np

from workshop_helpers import (
    calculate_correlation_map,
    how_well_matched,
    measure_region,
    normalise_match_score,
    optimise,
    shift_image,
)


DATA = Path("data/workshop_templateflow.npz")


def test_notebook_story_assets_are_present():
    source = Path("build_notebooks.py").read_text()
    assert "## 4. Acquiring and processing the data" in source
    assert "Registration is one part of preprocessing" in source
    for image in (Path("images/mri_scanner.jpg"), Path("images/pet_scanner.jpg")):
        assert image.exists()
        assert image.stat().st_size > 10_000


def test_finished_notebook_has_successful_executed_outputs():
    finished = json.loads(Path("NeuroPET_exercise_finished.ipynb").read_text())
    code_cells = [cell for cell in finished["cells"] if cell["cell_type"] == "code"]
    assert code_cells
    assert all(cell["execution_count"] is not None for cell in code_cells)
    assert not any(
        output.get("output_type") == "error"
        for cell in code_cells
        for output in cell.get("outputs", [])
    )


def test_shift_sign_and_no_wrap():
    image = np.zeros((5, 6), dtype=int)
    image[1, 1] = 7
    shifted = shift_image(image, x_offset_mm=2, y_offset_mm=1)
    assert shifted[2, 3] == 7
    assert shifted.sum() == 7


def test_shift_inverse_away_from_cropped_edges():
    image = np.zeros((8, 8), dtype=int)
    image[2:5, 2:5] = 1
    restored = shift_image(shift_image(image, 2, -1), -2, 1)
    np.testing.assert_array_equal(restored, image)


def test_registration_and_region_measurement_acceptance_checks():
    if not DATA.exists():
        raise AssertionError("Run python prepare_templateflow_data.py before the tests")
    with np.load(DATA, allow_pickle=False) as data:
        mri = data["mri"]
        challenge = data["challenge_pet"]
        baseline = data["baseline_pet"]
        stress = data["stress_pattern_pet"]
        masks = {
            "hippocampus": data["hippocampus_mask"],
            "amygdala": data["amygdala_mask"],
            "insula": data["insula_mask"],
        }

    initial_score = how_well_matched(mri, challenge)
    aligned, best_x, best_y, best_score = optimise(mri, challenge, search_range=10)
    np.testing.assert_allclose((best_x, best_y), (-7.2, 5.3), atol=0.05)
    assert best_score > initial_score
    assert normalise_match_score(best_score) > 0.95
    for mask in masks.values():
        assert mask.any()
        assert measure_region(stress, mask) > measure_region(baseline, mask)
    assert measure_region(aligned, masks["amygdala"]) > measure_region(
        challenge, masks["amygdala"]
    )
    assert max(
        stress[0].max(), stress[-1].max(), stress[:, 0].max(), stress[:, -1].max()
    ) < 0.02


def test_search_step_tradeoff_still_scores_the_returned_image():
    with np.load(DATA, allow_pickle=False) as data:
        mri = data["mri"]
        challenge = data["challenge_pet"]

    fine_image, fine_x, fine_y, fine_score = optimise(
        mri, challenge, coarse_step=2, fine_step=0.1
    )
    fast_image, fast_x, fast_y, fast_score = optimise(
        mri, challenge, coarse_step=4, fine_step=0.5
    )
    np.testing.assert_allclose((fine_x, fine_y), (-7.2, 5.3), atol=0.05)
    np.testing.assert_allclose(fine_image, shift_image(challenge, fine_x, fine_y))
    np.testing.assert_allclose(fast_image, shift_image(challenge, fast_x, fast_y))
    assert np.isclose(fine_score, how_well_matched(mri, fine_image))
    assert np.isclose(fast_score, how_well_matched(mri, fast_image))
    assert fine_score >= fast_score


def test_synthetic_fmri_analysis_recovers_injected_signal():
    with np.load(DATA, allow_pickle=False) as data:
        calculated = calculate_correlation_map(
            data["fmri_timeseries"], data["fmri_task_design"]
        )
        stored = data["fmri_activation_map"]
        injected = data["fmri_activation_mask"] > 0.30
        brain = data["fmri_mean"] > 0.10
    np.testing.assert_allclose(calculated, stored, atol=1e-5)
    assert calculated[injected].mean() > calculated[brain & ~injected].mean() + 0.45
