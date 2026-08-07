# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Post-processing utility for blob experiment CSV files.

When blob pollution intensities are stored as tuple-like strings
(e.g. "(0.1, 0.2)"), this script extracts the first float value from
the 'intensity' column so that the CSV can be used directly by
plot_seaborn_automated.py.

Usage
-----
    # Write to a new file (safe default):
    python for_blob_formatting.py --input 128_F9_blob_radius8.csv

    # Specify a custom output path:
    python for_blob_formatting.py --input 128_F9_blob_radius8.csv --output cleaned.csv

    # Overwrite the input file in-place (use with caution):
    python for_blob_formatting.py --input 128_F9_blob_radius8.csv --inplace
"""

import argparse
import sys

import pandas as pd


def extract_first_float(value: str | float) -> float | None:
    """Extract a float from a value that may be a tuple-like string.

    Args:
        value: If a string starting with '(', the first comma-separated element
            is parsed. Otherwise the value is cast directly to float.

    Returns:
    -------
    float or None
        Parsed float, or None if parsing fails.
    """
    try:
        if isinstance(value, str) and value.startswith("("):
            return float(value.split(",")[0].strip("() "))
        return float(value)
    except (ValueError, AttributeError):
        return None


def main() -> None:
    """Parse arguments, load CSV, extract float intensities, and save."""
    parser = argparse.ArgumentParser(
        description=(
            "Extract first float from tuple-like 'intensity' values in a blob CSV file."
        )
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to the input CSV file (e.g. 128_F9_blob_radius8.csv).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help=("Path for the output CSV file. Defaults to '<input_stem>_formatted.csv'."),
    )
    parser.add_argument(
        "--inplace",
        action="store_true",
        help="Overwrite the input file. Cannot be combined with --output.",
    )
    args = parser.parse_args()

    if args.inplace and args.output:
        print(
            "Error: --inplace and --output cannot be used together.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.inplace:
        output_path = args.input
    elif args.output:
        output_path = args.output
    else:
        stem = args.input.removesuffix(".csv")
        output_path = f"{stem}_formatted.csv"

    df = pd.read_csv(args.input)

    if "intensity" not in df.columns:
        print(
            f"Error: no 'intensity' column found in '{args.input}'.",
            file=sys.stderr,
        )
        sys.exit(1)

    df["intensity"] = df["intensity"].apply(extract_first_float)

    n_failed = df["intensity"].isna().sum()
    if n_failed > 0:
        print(
            f"Warning: {n_failed} row(s) could not be parsed and were set to NaN.",
            file=sys.stderr,
        )

    df.to_csv(output_path, index=False)
    print(f"Done. Formatted CSV saved to: {output_path}")


if __name__ == "__main__":
    main()
