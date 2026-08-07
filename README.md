<!--
SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
SPDX-License-Identifier: CC-BY-4.0
-->
# Assessing the Data-Centric Robustness of a Crack Tip Detection Model through Artificial Data Pollution

This repository provides the experimental framework used in the study _Assessing the Data-Centric Robustness of a Crack Tip Detection Model through Artificial Data Pollution_.
The objective of the work is to evaluate the robustness of crack-tip segmentation methods under controlled data degradation scenarios. To this end, the CrackMNIST dataset is subjected to parameterized perturbations (noise, blur, and occlusions), and the performance of a U-Net segmentation model is assessed under varying degrees of input quality.

---

## 1. Introduction

CrackMNIST is a benchmark dataset designed for evaluating crack-tip detection, a common task in fracture mechanics and digital image correlation (DIC) analysis. In this study, input data quality is systematically varied to analyze how model performance depends on the presence and severity of specific artifacts. The aim is to quantify robustness characteristics and develop a reproducible methodology for assessing data quality impacts in supervised segmentation tasks.

---

## 2. Dataset

The dataset used in this study is sourced from the **CrackMNIST** Python package, available on the Python Package Index (PyPI). The dataset is automatically downloaded and cached on first use — no manual download or additional data configuration is required.

Example usage:

```python
from crackmnist import CrackMNIST
dataset = CrackMNIST(split="train", pixels=64)
```

---

## 3. Installation

### Requirements

- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/) (recommended)

  ```bash
  # Linux and macOS
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Windows PowerShell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

### 3.1 Clone the repository

```bash
git clone https://github.com/DLR-KI/crack-tip-localization
cd crackmnist-eccv
```

### 3.2 Install dependencies

```bash
uv sync
```

> **Note (Windows):** PyTorch is not available on PyPI for Windows and must be installed from the
> official PyTorch index after `uv sync`:
>
> ```powershell
> uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
> ```
>
> Replace `cpu` with `cu124` (or your CUDA version) if GPU support is needed.

---

## 4. Running Experiments

All experiments are executed through `run_experiment.py` inside the package.

### Example: Gaussian noise robustness evaluation

```bash
uv run python -m crackmnist_eccv.run_experiment "gaussian" "[0.3]" \
    --pixels 64 \
    --train_range "[0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.5, 0.75, 1.0]" \
    > log_gaussian_0.3.out 2>&1 &
```

### Example: Blob occlusion robustness evaluation (special case due to interval)

```bash
uv run python -m crackmnist_eccv.run_experiment "blob" "[(0.1, 0.2)]" \
    --pixels 64 \
    --radius 4 \
    --train_range "[0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.5, 0.75, 1.0]" \
    > log_blob_0.1_0.2_r4.out 2>&1 &
```

The script performs evaluation across multiple random seeds and automatically writes results to `.csv` files.

---

## 5. Plotting and Result Analysis

### 5.1 Standard pollution types (Gaussian, Salt & Pepper, Gaussian Blur)

```bash
# Fully polluted test set
uv run python -m crackmnist_eccv.plot_seaborn_automated \
    --input 128_F9_salt_pepper_radius8.csv \
    --test_perc 1.0 \
    --intensities 0.05 0.1 0.2

# Clean test set
uv run python -m crackmnist_eccv.plot_seaborn_automated \
    --input 128_F9_gaussian_radius8.csv \
    --test_perc 0.0 \
    --intensities 0.1 0.3 0.5
```

Figures are saved in PNG format.

### 5.2 Blob occlusion (pre-processing step required)

Blob experiment CSVs store intensity values as tuple strings (e.g. `"(0.1, 0.2)"`). Before plotting, convert the `intensity` column to plain floats:

```bash
# Writes a new file: 128_F9_blob_radius8_formatted.csv
uv run python -m crackmnist_eccv.for_blob_formatting --input 128_F9_blob_radius8.csv

# Or overwrite in-place
uv run python -m crackmnist_eccv.for_blob_formatting --input 128_F9_blob_radius8.csv --inplace
```

Then plot as usual:

```bash
uv run python -m crackmnist_eccv.plot_seaborn_automated \
    --input 128_F9_blob_radius8_formatted.csv \
    --test_perc 1.0 \
    --intensities 0.1 0.3 0.5
```

---

## 6. Repository Structure

```text
.
├── src/
│   └── crackmnist_eccv/
│       ├── __init__.py
│       ├── run_experiment.py       # Main experiment script
│       ├── utility.py              # Pollution functions and helpers
│       ├── plot_seaborn_automated.py  # Plotting script
│       └── for_blob_formatting.py  # Blob CSV post-processing utility
│
├── tests/
│   └── crackmnist_eccv/
│       └── test_utility.py
│
├── results/                        # Generated CSV files and plots (user-generated)
├── pyproject.toml
├── CITATION.cff
├── LICENSE.md
├── LICENSES/
└── README.md
```

---

## 7. Citation

Please use the included `CITATION.cff` file or click **"Cite this repository"** on GitLab to export a citation in your preferred format.

---

## 8. License

This repository is released under the **GPL-3.0-or-later** license, permitting reuse, modification, and redistribution with attribution.
