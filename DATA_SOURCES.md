# Data sources, processing, and licensing

## Summary

This repository contains code and notebooks, but intentionally excludes all
BrainWeb source and derived image arrays. During a Binder image build,
`postBuild` runs `prepare_brainweb_data.py`, which downloads one official source
file and creates `data/workshop_brainweb.npz`. Notebook execution then requires
no download.

The PET images are explicitly synthetic educational examples. They are not
patient scans and contain no identifiable health information.

## Software: Casper O. da Costa-Luis' Python BrainWeb

- Package: `brainweb==1.7.0`
- Author: Casper O. da Costa-Luis
- Repository: <https://github.com/casperdcl/brainweb>
- PyPI: <https://pypi.org/project/brainweb/>
- DOI: <https://doi.org/10.5281/zenodo.3269888>
- Software licence: Mozilla Public License 2.0 (MPL-2.0)

The preparation pipeline uses the package's official subject URL table, binary
loader, label definitions (`brainweb.Act`), and T1 tissue intensities
(`brainweb.T1`). The workshop implements its own deliberately simple 2-D
translation search so students can understand every candidate tested.

The MPL-2.0 licence applies to the Python package's source code. It must not be
assumed to license the separately downloaded McGill BrainWeb anatomical data.

## Anatomical source data

- Provider: McConnell Brain Imaging Centre, Montreal Neurological Institute,
  McGill University
- Dataset: BrainWeb 20 normal anatomical models
- Subject: 04, discrete/crisp anatomical model
- Official information page:
  <https://brainweb.bic.mni.mcgill.ca/brainweb/anatomic_normal_20.html>
- File selected by Python BrainWeb: `subject_04.bin.gz`
- Expected array: unsigned 16-bit, `(z, y, x) = (362, 434, 362)`, 0.5 mm grid
- SHA-256 of the file validated on 2026-09-18:
  `4f1b1d1e9c143d860e8b3c7dcd0713b759c8556e2c248495212f29bbbbac126b`

The 20-subject model defines background, CSF, grey matter, white matter, fat,
muscle, skin, skull, vessels, connective tissue, dura, and marrow. This workshop
uses only CSF, grey matter, and white matter.

## Licensing status and publishing decision

The official BrainWeb pages provide downloads and request/identify scholarly
citations, but the pages reviewed did not provide a formal data licence or an
explicit grant to redistribute the anatomical files or derived arrays. Public
downloadability alone is not treated here as redistribution permission.

Consequently:

- neither `subject_04.bin.gz` nor `data/workshop_brainweb.npz` should be
  committed to a public repository without permission or a documented licence;
- `data/workshop_brainweb.npz` is listed in `data/.gitignore`;
- local users obtain the source directly from the official site through the
  Python BrainWeb package;
- Binder obtains and processes the file during environment build, before the
  student session.

Project-owner decision still required: confirm with the BrainWeb rights holder
whether redistribution of the small prepared 2-D array—or public distribution
of a prebuilt container containing it—is permitted. Until then, publish the
code-only repository and allow each environment to retrieve the official source.

## Deterministic processing record

`prepare_brainweb_data.py` performs the following steps:

1. Downloads or accepts `subject_04.bin.gz` and verifies its SHA-256.
2. Loads the `(362, 434, 362)` `uint16` volume with `brainweb.load_file`.
3. Clears the low auxiliary bits and interprets tissue codes with
   `brainweb.Act.indices`.
4. Selects axial slice `z = 190`. Candidate slices from `z = 100` to `280` were
   visually inspected; 190 was chosen for its recognisable outline, cortical
   grey matter, ventricles, and useful internal registration features.
5. Crops rows `30:420` and the full `0:362` columns, adds 14 zero-valued pixels
   on each left/right side to make a square field of view, resamples to
   `192 × 192`, and flips the display vertically so anterior is at the top and
   the posterior/occipital side is at the bottom. The additional field-of-view
   margin prevents the blurred PET edge from being clipped. Left/right is not
   labelled because it has not been independently verified.
6. Builds an MRI-like image from Python BrainWeb's T1 tissue intensities, with a
   mild deterministic bias field, blur, and noise.
7. Builds low- and high-binding synthetic PET images from tissue masks. Both use
   the same intensity scale, 3.4-pixel Gaussian blur, and noise realisation.
8. Creates the challenge by shifting only the low-binding PET by `x = +7`,
   `y = -5` pixels. Positive x is right; positive y is down.
9. Stores arrays and machine-readable JSON metadata in a compressed NPZ file.

Random seed: `20260918`.

The grey-matter mask is a tissue segmentation only. It is not presented as a
specific anatomical region such as precuneus, posterior cingulate, or temporal
lobe.

## Synthetic PET model

Relative pre-blur tissue signals are:

| Tissue | Low-binding case | High-binding case |
|---|---:|---:|
| CSF | 0.08 | 0.08 |
| White matter | 0.52 | 0.52 |
| Grey matter | 0.76 | 1.12 |

These numbers are workshop design parameters, not clinical standardized uptake
values. The common scale allows a fair within-workshop comparison only.

## Requested citations and acknowledgements

Please retain the following when reusing the workshop:

1. da Costa-Luis, C. O. *BrainWeb-based multimodal models of 20 normal brains*.
   Zenodo. <https://doi.org/10.5281/zenodo.3269888>
2. Aubert-Broche, B., Griffin, M., Pike, G. B., Evans, A. C., & Collins, D. L.
   (2006). Twenty new digital brain phantoms for creation of validation image
   data bases. *IEEE Transactions on Medical Imaging, 25*(11), 1410–1416.
   <https://doi.org/10.1109/TMI.2006.883453>
3. Aubert-Broche, B., Evans, A. C., & Collins, D. L. (2006). A new improved
   version of the realistic digital brain phantom. *NeuroImage, 32*(1), 138–145.
   <https://doi.org/10.1016/j.neuroimage.2006.03.052>
4. BrainWeb, McConnell Brain Imaging Centre, Montreal Neurological Institute,
   McGill University: <https://brainweb.bic.mni.mcgill.ca/brainweb/>
