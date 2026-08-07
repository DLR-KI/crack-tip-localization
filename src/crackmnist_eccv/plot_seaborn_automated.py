# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Generate test-loss performance curves from a pollution experiment CSV file.

Plots average test loss vs. proportion of polluted training inputs, grouped
by noise intensity, with ±1 standard deviation shading.

Usage
-----
    # Fully polluted test set, default intensities:
    python plot_seaborn_automated.py \
        --input 128_F9_salt_pepper_radius8.csv \
        --test_perc 1.0 --intensities 0.05 0.1 0.2

    # Clean test set, custom intensities:
    python plot_seaborn_automated.py \
        --input 128_F9_gaussian_radius8.csv \
        --test_perc 0.0 --intensities 0.1 0.3 0.5

    # Custom output path:
    python plot_seaborn_automated.py \
        --input 128_F9_blob_radius8.csv \
        --test_perc 1.0 --intensities 0.05 0.1 0.2 --output my_plot.png
"""

import argparse
import os
import sys

from matplotlib.patches import Patch
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the plotting script.

    Returns:
        Parsed argument namespace with input, test_perc, intensities, and output fields.
    """
    parser = argparse.ArgumentParser(
        description="Plot avg test loss curves from a pollution experiment CSV."
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help=("Path to the input CSV file (e.g. 128_F9_salt_pepper_radius8.csv)."),
    )
    parser.add_argument(
        "--test_perc",
        type=float,
        required=True,
        help=("Test pollution level to plot: 0.0 (clean) or 1.0 (fully polluted)."),
    )
    parser.add_argument(
        "--intensities",
        type=float,
        nargs="+",
        required=True,
        help=("One or more noise intensity values to include (e.g. 0.05 0.1 0.2)."),
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help=(
            "Path for the saved PNG file. "
            "Defaults to "
            "'final_<pollution>_plot_on_<test_label>_<suffix>.png'."
        ),
    )
    return parser.parse_args()


def main() -> None:
    """Load CSV, filter by test pollution level, and plot loss curves."""
    args = parse_args()

    df = pd.read_csv(args.input)

    required_cols = {
        "test_perc",
        "train_perc",
        "intensity",
        "avg_test_loss",
        "std_test_loss",
    }
    missing = required_cols - set(df.columns)
    if missing:
        print(
            f"Error: CSV is missing required columns: {missing}",
            file=sys.stderr,
        )
        sys.exit(1)

    df_filtered = df[df["test_perc"] == args.test_perc].copy()
    if df_filtered.empty:
        print(
            f"Error: no rows found with test_perc == {args.test_perc}. "
            f"Available values: {sorted(df['test_perc'].unique())}",
            file=sys.stderr,
        )
        sys.exit(1)

    df_filtered["train_perc"] = df_filtered["train_perc"] * 100

    pollution_type = args.input.split("_")[1]
    test_label = "fully clean" if args.test_perc == 0.0 else "fully polluted"

    sns.set(style="whitegrid", context="talk")
    palette = sns.color_palette("viridis", n_colors=len(args.intensities))

    plt.figure(figsize=(11, 6))

    for i, intensity in enumerate(args.intensities):
        data_subset = df_filtered[df_filtered["intensity"] == intensity].sort_values(
            "train_perc"
        )

        if data_subset.empty:
            print(
                f"Warning: no data for intensity={intensity} — skipping.",
                file=sys.stderr,
            )
            continue

        x = data_subset["train_perc"].to_numpy()
        y = data_subset["avg_test_loss"].to_numpy()
        std = data_subset["std_test_loss"].to_numpy()

        plt.plot(x, y, label=f"{intensity}", color=palette[i], marker="o")
        plt.fill_between(x, y - std, y + std, color=palette[i], alpha=0.3)

    first_legend = plt.legend(
        title="Noise intensity", loc="upper right", fontsize=14, title_fontsize=14
    )
    plt.gca().add_artist(first_legend)

    shaded_patch = Patch(facecolor="gray", alpha=0.3, label="±1 standard deviation")
    plt.legend(
        handles=[shaded_patch],
        title="Shaded area",
        loc="upper center",
        bbox_to_anchor=(0.6, 0.99),
        frameon=True,
        fontsize=14,
        title_fontsize=14,
        borderaxespad=0.5,
    )

    plt.title(
        f"Effect of training noise on {test_label} test performance",
        fontsize=14,
    )
    plt.xlabel("Proportion of polluted training inputs (%)", fontsize=14)
    plt.ylabel("Average test loss", fontsize=14)
    plt.tight_layout()

    if args.output:
        save_name = args.output
    else:
        suffix = os.path.splitext(args.input)[0].split("_")[-1]
        save_name = (
            f"final_{pollution_type}_plot_on_{test_label.replace(' ', '_')}_{suffix}.png"
        )

    plt.savefig(save_name, dpi=300)
    plt.show()
    print(f"Plot saved as: {save_name}")


if __name__ == "__main__":
    main()
