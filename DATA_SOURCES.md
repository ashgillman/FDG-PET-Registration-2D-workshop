# Data sources, processing, licensing, and interpretation

## Summary

The repository contains code and notebooks but not the downloaded TemplateFlow
volumes or the generated workshop array. During a Binder build, `postBuild`
runs `prepare_templateflow_data.py`, which retrieves the selected resources and
creates `data/workshop_templateflow.npz`. Notebook execution then requires no
network connection.

MRI anatomy and atlas labels are population-template resources, not a scan of a
workshop participant. Every PET and fMRI signal is a deterministic educational
simulation. There are no patient data or identifiable health information.

## Scanner photographs

The student notebook includes two local photographs so the acquisition story
remains visible without making a network request during notebook execution:

- `images/mri_scanner.jpg`: *Siemens Magnetom Aera MRI scanner*, by Ptrump16,
  retrieved from
  [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Siemens_Magnetom_Aera_MRI_scanner.jpg),
  licensed under
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
- `images/pet_scanner.jpg`: *PET CT scan*, by liz west, retrieved from
  [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:PET_CT_scan.jpg),
  licensed under
  [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/).

Both images are used unchanged apart from Wikimedia's thumbnail resizing. The
authors do not endorse this workshop.

## TemplateFlow

- Python client: `templateflow==25.0.1`
- Project: <https://www.templateflow.org/>
- Archive documentation: <https://www.templateflow.org/usage/archive/>
- TemplateFlow paper: Ciric et al. (2022), *Nature Methods*.
  <https://doi.org/10.1038/s41592-022-01681-2>
- Python-client licence: Apache License 2.0

TemplateFlow is a versioned interface to independently licensed templates and
atlases. Its client licence does not replace the licence attached to each data
resource.

## MRI template

- TemplateFlow identifier: `MNI152NLin2009cSym`
- Name: ICBM 152 nonlinear symmetric template, version 2009c
- Resolution: 1 mm isotropic
- T1-weighted resource:
  `tpl-MNI152NLin2009cSym_res-1_T1w.nii.gz`
- Tissue-probability resources: `label-GM`, `label-WM`, and `label-CSF`
- Original reference: Fonov et al. (2011), *NeuroImage*.
  <https://doi.org/10.1016/j.neuroimage.2010.07.033>

The licence distributed with the TemplateFlow template grants permission to
use, copy, modify, and distribute the material without fee, provided the
copyright notice is retained. The licence and attribution should remain with
redistributed source or derived template data.

## CerebrA anatomical atlas

- Atlas image:
  `tpl-MNI152NLin2009cSym_res-1_atlas-CerebrA_dseg.nii.gz`
- Label table:
  `tpl-MNI152NLin2009cSym_atlas-CerebA_dseg.tsv`
- Regions used: bilateral hippocampus, amygdala, insula, and rostral anterior
  cingulate
- Dataset DOI: <https://doi.org/10.12751/g-node.be5e62>
- Licence: CC0 1.0 public-domain dedication
- Atlas paper: Manera et al. (2020), *Scientific Data*.
  <https://doi.org/10.1038/s41597-020-0557-9>

The slightly different `CerebrA` and `CerebA` spellings are the identifiers
used by the TemplateFlow image and table resources respectively.

## Deterministic processing record

`prepare_templateflow_data.py` performs these steps:

1. Retrieves the T1 template, three tissue-probability maps, CerebrA label
   image, and label table through the TemplateFlow Python client.
2. Converts each NIfTI image to the closest canonical orientation and verifies
   that shape and affine geometry match.
3. Selects the main axial slice at MNI `z = -16 mm`, crops a `193 × 193 mm`
   field of view, and displays anterior at the top and anatomical left at the
   left. The retained grid is exactly `1 mm × 1 mm` per pixel.
4. Produces four atlas panels at levels that clearly show hippocampus
   (`z = -20 mm`), amygdala (`z = -20 mm`), insula (`z = +2 mm`), and rostral
   anterior cingulate (`z = -10 mm`).
5. Creates a baseline FDG-PET simulation from CSF, white-matter, and
   grey-matter probabilities. It then creates a deliberately visible
   stress-challenge teaching pattern by adding regional signal before applying
   a `4 mm` Gaussian blur and deterministic noise.
6. Generates the registration challenge with a sub-millimetre bilinear
   translation. The generation transform is calibrated so that the transparent
   Pearson-correlation search has a clear optimum at `x = -7.2 mm`,
   `y = +5.3 mm`. Because resampling and cross-modal intensity differences can
   move a numerical optimum slightly, this is an exercise design target rather
   than a ground-truth validation experiment.
7. Generates 64 synthetic fMRI frames with alternating rest/stress-task blocks,
   a small task-correlated signal in the amygdala/insula teaching mask,
   spatially smoothed noise, and low-frequency drift. The saved activation map
   is the per-pixel Pearson correlation with the simulated response timing.
8. Stores only the prepared 2-D arrays and machine-readable metadata in a
   compressed NPZ file.

Random seed: `20260921`.

## Synthetic FDG-PET model

Relative pre-blur tissue signals are:

| Component | Relative activity |
|---|---:|
| CSF | 0.08 |
| White matter | 0.38 |
| Grey matter | 0.68 |
| Additional hippocampal teaching signal | +0.12 |
| Additional amygdala teaching signal | +0.36 |
| Additional insular teaching signal | +0.24 |

These are workshop design parameters, not clinical standardized uptake values
or literature-derived stress effect sizes. The shared scale and noise pattern
permit controlled within-workshop comparisons only.

## Synthetic fMRI model

The bonus time series is a conceptual block-design demonstration. It uses a
small positive BOLD-like signal, a smoothed task response, noise, and drift so
that individual frames are ambiguous but the repeated pattern is recoverable.
It is not a realistic acquisition sequence, statistical parametric analysis,
or estimate of a biological stress effect.

## Scientific interpretation safeguards

- Stress recruits distributed, interacting systems; there is no single
  universal "stress centre" or activation pattern.
- Region functions are simplified teaching descriptions, not one-function
  labels.
- FDG-PET integrates tracer distribution over its uptake period and is not an
  instantaneous or diagnostic stress measurement.
- BOLD fMRI is an indirect haemodynamic signal. Real analysis requires motion
  correction, modelling, statistical inference, and quality control.
- A successful registration score does not establish clinical validity.

Useful stress-imaging background:

1. Noack et al. (2019). *Imaging stress: an overview of stress induction
   methods in the MR scanner.*
   <https://pubmed.ncbi.nlm.nih.gov/30631946/>
2. Berretz et al. (2021). *The brain under stress: a systematic review and
   activation likelihood estimation meta-analysis of changes in BOLD signal
   associated with acute stress exposure.*
   <https://pubmed.ncbi.nlm.nih.gov/33497786/>
