# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Run CrackMNIST pollution experiments across seeds, intensities, and splits.

Trains a UNet model under controlled input pollution and evaluates average
Dice loss on train/val/test splits across multiple random seeds. Results are
written incrementally to a CSV file named after the experiment configuration.
"""

import argparse
import ast
import random
import time

from crackmnist import CrackMNIST
from crackmnist.loss import DiceLoss
from crackmnist.nets import UNet
from crackmnist.transforms import InputNormalization, NumpyToTensor
import numpy as np
import pandas as pd
import torch
from torch import optim
from torch.utils import data
from torchvision import transforms

from src.crackmnist_eccv.utility import apply_per_image_pollution, enlarge_crack_tip


##############################################################################
# FIXED HYPERPARAMETERS
##############################################################################
NUM_EPOCHS = 10
BATCH_SIZE = 32
LR = 1e-4

##############################################################################
# PARAM RANGES
##############################################################################
TEST_PERC_RANGE = [0.0, 1.0]
NUM_SEEDS = 10
SIZE = "S"


##############################################################################
# COMMAND-LINE ARGUMENTS
##############################################################################
def parse_python_literal(text: str, expected_type: type) -> list:
    """Convert a string like '[0.1,0.2]' or '[(0.1,0.2)]' to a Python object.

    Args:
        text: String representation of a Python literal.
        expected_type: The expected Python type (e.g. list).

    Returns:
        Parsed Python object of the expected type.

    Raises:
        ArgumentTypeError: If parsing fails or type does not match.
        TypeError: If the parsed value is not an instance of expected_type.
    """
    try:
        value = ast.literal_eval(text)
        if not isinstance(value, expected_type):
            raise TypeError
        return value
    except Exception as err:
        raise argparse.ArgumentTypeError(
            f"Value '{text}' is not a valid {expected_type.__name__}"
        ) from err


parser = argparse.ArgumentParser(
    description="Run CrackMNIST experiments with flexible settings."
)

parser.add_argument(
    "pollution_type",
    nargs="?",
    default="blob",
    help="gaussian | salt_pepper | gaussian_blur | blob",
)
parser.add_argument(
    "intensity_range",
    nargs="?",
    default="[(0.1,0.2),(0.3,0.4),(0.5,0.6)]",
    help='Python literal, e.g. "[0.1,0.3,0.5]" or "[(0.1,0.2)]"',
)
parser.add_argument(
    "--pixels",
    type=int,
    default=64,
    help="Image size fed into CrackMNIST (default: 64)",
)
parser.add_argument(
    "--train_range",
    type=lambda s: parse_python_literal(s, list),
    default=[0.05, 0.1, 0.15, 0.2],
    help='Training-pollution percentages, e.g. "[0.0,0.25,0.5]"',
)
parser.add_argument(
    "--radius",
    type=int,
    default=8,
    help=("Blob-pollution radius (only used when pollution_type == 'blob'; default: 8)"),
)
args = parser.parse_args()

##############################################################################
# SET VARIABLES FROM ARGS
##############################################################################
SELECTED_POLLUTION_TYPE = args.pollution_type
INTENSITY_RANGE = parse_python_literal(args.intensity_range, list)
PIXELS = args.pixels
TRAIN_PERC_RANGE = args.train_range
RADIUS = args.radius

NAMING_CONSTANT = f"{PIXELS}_F9_{SELECTED_POLLUTION_TYPE}_radius{RADIUS}"


##############################################################################
# UTILITY: FIX RANDOM SEEDS
##############################################################################
def fix_random_seeds(seed: int) -> None:
    """Fix all relevant random seeds for reproducibility.

    Args:
        seed: Integer seed value.
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)


##############################################################################
# DEVICE
##############################################################################
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

##############################################################################
# LOAD DATASETS
##############################################################################
data_transform = transforms.Compose([
    NumpyToTensor(),
    InputNormalization(),
])
target_transform = transforms.Compose([
    NumpyToTensor(),
])

train_dataset_full = CrackMNIST(
    split="train",
    pixels=PIXELS,
    size=SIZE,
    transform=data_transform,
    target_transform=target_transform,
)

val_dataset_full = CrackMNIST(
    split="val",
    pixels=PIXELS,
    size=SIZE,
    transform=data_transform,
    target_transform=target_transform,
)

test_dataset_full = CrackMNIST(
    split="test",
    pixels=PIXELS,
    size=SIZE,
    transform=data_transform,
    target_transform=target_transform,
)

##############################################################################
# ENLARGE THE ANNOTATED TIP REGION TO 3x3
##############################################################################
train_dataset_full.masks = np.array([
    enlarge_crack_tip(mask) for mask in train_dataset_full.masks
])
val_dataset_full.masks = np.array([
    enlarge_crack_tip(mask) for mask in val_dataset_full.masks
])
test_dataset_full.masks = np.array([
    enlarge_crack_tip(mask) for mask in test_dataset_full.masks
])

print("Dataset loaded")
train_loader_full = data.DataLoader(
    train_dataset_full, batch_size=BATCH_SIZE, shuffle=False, num_workers=4
)
val_loader_full = data.DataLoader(
    val_dataset_full, batch_size=BATCH_SIZE, shuffle=False, num_workers=4
)
test_loader_full = data.DataLoader(
    test_dataset_full, batch_size=BATCH_SIZE, shuffle=False, num_workers=4
)


##############################################################################
# HELPER: CONFIG & EVALUATION FUNCTION
##############################################################################
def get_pollution_config(
    pollution_type: str, intensity: float | tuple[float, float]
) -> dict:
    """Return keyword arguments for apply_per_image_pollution.

    Args:
        pollution_type: One of 'blob', 'gaussian', 'salt_pepper',
            'gaussian_blur'.
        intensity: Float or (min, max) tuple depending on pollution type.

    Returns:
        Dict with 'pollution_type' and 'pollution_kwargs' keys.

    Raises:
        ValueError: If the pollution type is unsupported or intensity format
            is wrong.
    """
    if pollution_type == "blob":
        if not isinstance(intensity, tuple) or len(intensity) != 2:
            raise ValueError("Blob pollution requires intensity as a (min, max) tuple")
        return {
            "pollution_type": pollution_type,
            "pollution_kwargs": {
                "radius": RADIUS,
                "target_min_oar": intensity[0],
                "target_max_oar": intensity[1],
            },
        }
    elif pollution_type in ["gaussian", "salt_pepper", "gaussian_blur"]:
        if not isinstance(intensity, (float, int)):
            raise ValueError(f"{pollution_type} requires intensity as a float or int")
        return {
            "pollution_type": pollution_type,
            "pollution_kwargs": {"intensity": intensity},
        }
    else:
        raise ValueError(f"Unsupported pollution type: {pollution_type}")


def evaluate(
    model: torch.nn.Module,
    loader: data.DataLoader,
    pollution_ratio: float,
    pollution_type: str,
    pollution_kwargs: dict,
) -> float:
    """Run model in eval mode and return average DiceLoss over the loader.

    Args:
        model: Trained PyTorch model.
        loader: DataLoader to evaluate on.
        pollution_ratio: Fraction of images to pollute.
        pollution_type: Type of pollution to apply.
        pollution_kwargs: Additional keyword arguments for the pollution
            function.

    Returns:
        Average DiceLoss as a float.
    """
    model.eval()
    criterion = DiceLoss()
    total_loss, total_count = 0.0, 0

    with torch.no_grad():
        for inputs, targets in loader:
            inputs = apply_per_image_pollution(
                inputs,
                pollution_ratio=pollution_ratio,
                pollution_type=pollution_type,
                **pollution_kwargs,
            )
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, targets.unsqueeze(1).float() / 255.0)
            batch_size = inputs.size(0)
            total_loss += loss.item() * batch_size
            total_count += batch_size

    return total_loss / total_count if total_count else 0.0


##############################################################################
# TRAIN & FINAL-EVAL
##############################################################################
def train_and_evaluate(
    train_perc: float,
    test_perc: float,
    intensity: float | tuple[float, float],
    seed: int,
) -> tuple[float, float, float]:
    """Train a UNet and evaluate on val and test sets.

    Args:
        train_perc: Fraction of training images to pollute.
        test_perc: Fraction of test images to pollute during evaluation.
        intensity: Pollution intensity (float or tuple for blob).
        seed: Random seed for reproducibility.

    Returns:
        Tuple of (final_val_loss, final_test_loss, final_train_loss).
    """
    fix_random_seeds(seed)

    model = UNet(in_ch=2, out_ch=1, init_features=128, dropout_prob=0.2).to(device)
    criterion = DiceLoss()
    optimizer = optim.Adam(model.parameters(), lr=LR)

    config = get_pollution_config(SELECTED_POLLUTION_TYPE, intensity)
    pollution_type = config["pollution_type"]
    pollution_kwargs = config["pollution_kwargs"]

    model.train()
    for _epoch in range(NUM_EPOCHS):
        for inputs, targets in train_loader_full:
            inputs = apply_per_image_pollution(
                inputs,
                pollution_ratio=train_perc,
                pollution_type=pollution_type,
                **pollution_kwargs,
            )
            inputs, targets = inputs.to(device), targets.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets.unsqueeze(1).float() / 255.0)
            loss.backward()
            optimizer.step()

    final_val_loss = evaluate(
        model,
        val_loader_full,
        pollution_ratio=train_perc,
        pollution_type=pollution_type,
        pollution_kwargs=pollution_kwargs,
    )
    final_test_loss = evaluate(
        model,
        test_loader_full,
        pollution_ratio=test_perc,
        pollution_type=pollution_type,
        pollution_kwargs=pollution_kwargs,
    )
    final_train_loss = evaluate(
        model,
        train_loader_full,
        pollution_ratio=train_perc,
        pollution_type=pollution_type,
        pollution_kwargs=pollution_kwargs,
    )

    return final_val_loss, final_test_loss, final_train_loss


##############################################################################
# MAIN LOOP
##############################################################################
results = []

for train_perc in TRAIN_PERC_RANGE:
    for test_perc in TEST_PERC_RANGE:
        for intensity in INTENSITY_RANGE:
            val_losses_seeds = []
            test_losses_seeds = []
            train_losses_seeds = []
            print(f"Processing: {train_perc}, {test_perc}, {intensity}")

            for seed in range(NUM_SEEDS):
                print("\t seed:", seed)
                start = time.time()

                val_loss, test_loss, train_loss = train_and_evaluate(
                    train_perc, test_perc, intensity=intensity, seed=seed
                )
                val_losses_seeds.append(val_loss)
                test_losses_seeds.append(test_loss)
                train_losses_seeds.append(train_loss)
                print("\t elapsed time:", time.time() - start)

            avg_val_loss = np.mean(val_losses_seeds)
            std_val_loss = np.std(val_losses_seeds)
            avg_test_loss = np.mean(test_losses_seeds)
            std_test_loss = np.std(test_losses_seeds)
            avg_train_loss = np.mean(train_losses_seeds)
            std_train_loss = np.std(train_losses_seeds)

            results.append({
                "train_perc": train_perc,
                "test_perc": test_perc,
                "intensity": intensity,
                "avg_test_loss": avg_test_loss,
                "std_test_loss": std_test_loss,
                "avg_val_loss": avg_val_loss,
                "std_val_loss": std_val_loss,
                "avg_train_loss": avg_train_loss,
                "std_train_loss": std_train_loss,
                "test_losses_seeds": test_losses_seeds,
            })

            df = pd.DataFrame(results)
            df.to_csv(f"{NAMING_CONSTANT}.csv", index=False)

print("DONE!")
