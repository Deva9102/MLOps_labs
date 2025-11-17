from __future__ import annotations

import argparse
import json
from pathlib import Path

from .log_setup import configure_logging
from .data_quality import run_quality_checks


def parse_args() -> argparse.Namespace:
    """
    Define and parse command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Dataset Quality Checker with structured logging"
    )

    parser.add_argument(
        "csv_path",
        help="Path to the input CSV file",
    )
    parser.add_argument(
        "--out",
        dest="out_path",
        help=(
            "Optional path for the JSON summary file "
            "(default: <csv_path>.quality_summary.json)"
        ),
    )

    return parser.parse_args()


def main() -> None:
    """
    Entry point for the CLI.
    """

    # Set up logging
    logger = configure_logging()

    # Read CLI arguments
    args = parse_args()
    csv_path = Path(args.csv_path)

    # Log the start of the run
    logger.info(
        "Starting dataset quality checker",
        extra={"event": "start", "path": str(csv_path)},
    )

    # Basic validation
    if not csv_path.exists():
        logger.error(
            "Input CSV file does not exist",
            extra={"event": "cli_error", "path": str(csv_path)},
        )
        print(f"ERROR: CSV file not found: {csv_path}")
        raise SystemExit(1)

    # Run all checks on the dataset
    summary = run_quality_checks(csv_path)
    print("\n=== Dataset Quality Summary ===")
    print(f"Path: {summary['path']}")
    print(f"Rows: {summary['n_rows']}, Columns: {summary['n_cols']}")

    # Missing values section
    print("\nMissing values per column:")
    for col, count in summary["missing_values"].items():
        print(f"  - {col}: {count}")

    # Numeric ranges section
    print("\nNumeric columns (min, max, negative_count):")
    for col, stats in summary["numeric_ranges"].items():
        print(
            f"  - {col}: min={stats['min']}, "
            f"max={stats['max']}, "
            f"negative_count={stats['negative_count']}"
        )

    # Constant columns section
    print("\nConstant columns (all non-null values the same):")
    if summary["constant_columns"]:
        for col in summary["constant_columns"]:
            print(f"  - {col}")
    else:
        print("  (none)")

    # High-cardinality categoricals section
    print("\nHigh-cardinality categorical columns:")
    if summary["high_cardinality_columns"]:
        for col, uniq in summary["high_cardinality_columns"].items():
            print(f"  - {col}: unique_values={uniq}")
    else:
        print("  (none)")

    # Out-of-range values section
    print("\nRange issues (columns checked against rules):")
    if summary["range_issues"]:
        for col, info in summary["range_issues"].items():
            print(
                f"  - {col}: "
                f"allowed=[{info['min_allowed']}, {info['max_allowed']}], "
                f"actual_min={info['actual_min']}, "
                f"actual_max={info['actual_max']}, "
                f"out_of_range_count={info['out_of_range_count']}"
            )
    else:
        print("  (none)")

    out_path = (
        Path(args.out_path)
        if args.out_path
        else csv_path.with_suffix(".quality_summary.json")
    )

    # Make sure the output directory exists
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the summary dictionary as pretty JSON
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info(
        "Dataset quality summary written",
        extra={
            "event": "summary_written",
            "output_path": str(out_path),
        },
    )

    print(f"\nSummary written to: {out_path}")


if __name__ == "__main__":
    main()
