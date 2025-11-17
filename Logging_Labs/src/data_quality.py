from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple

import pandas as pd

logger = logging.getLogger("dq_logger")


def load_dataset(path: str | Path) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame and log the result.

    Logs:
      - load_start: before reading
      - load_failed: if file is missing or another error occurs
      - load_done: on success, with number of rows and columns
    """
    path = Path(path)

    logger.info(
        "Loading dataset",
        extra={"event": "load_start", "path": str(path)},
    )

    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        logger.exception(
            "Dataset file not found",
            extra={"event": "load_failed", "path": str(path)},
        )
        raise
    except Exception:
        logger.exception(
            "Unexpected error while loading dataset",
            extra={"event": "load_failed", "path": str(path)},
        )
        raise

    # Successful load
    logger.info(
        "Dataset loaded",
        extra={
            "event": "load_done",
            "path": str(path),
            "n_rows": int(df.shape[0]),
            "n_cols": int(df.shape[1]),
        },
    )
    return df


def analyze_missing_values(df: pd.DataFrame) -> Dict[str, int]:
    """
    Count missing values per column and log a warning for any column
    that has at least one missing value.
    """
    missing_counts: Dict[str, int] = df.isna().sum().to_dict()

    for col, count in missing_counts.items():
        if count > 0:
            logger.warning(
                "Missing values detected",
                extra={
                    "event": "missing_values",
                    "column": col,
                    "missing_count": int(count),
                },
            )

    return {col: int(count) for col, count in missing_counts.items()}


def analyze_numeric_ranges(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Look at numeric columns and compute:
      - min value
      - max value
      - how many values are negative

    Logs a warning for columns that contain negative values.
    """
    summary: Dict[str, Dict[str, Any]] = {}

    # Only keep numeric columns
    numeric_df = df.select_dtypes(include="number")

    for col in numeric_df.columns:
        series = numeric_df[col]
        if series.empty:
            summary[col] = {"min": None, "max": None, "negative_count": 0}
            continue

        negative_count = int((series < 0).sum())
        col_min = float(series.min())
        col_max = float(series.max())

        summary[col] = {
            "min": col_min,
            "max": col_max,
            "negative_count": negative_count,
        }

        if negative_count > 0:
            logger.warning(
                "Negative values found in numeric column",
                extra={
                    "event": "negative_values",
                    "column": col,
                    "negative_count": negative_count,
                },
            )

    return summary


def basic_schema_summary(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Provide a very simple schema-like summary for each column
    """
    result: Dict[str, Dict[str, Any]] = {}

    for col in df.columns:
        unique_count = int(df[col].nunique(dropna=True))
        result[col] = {
            "dtype": str(df[col].dtype),
            "unique_values": unique_count,
        }
        logger.info(
            "Column summary",
            extra={
                "event": "column_summary",
                "column": col,
                "dtype": str(df[col].dtype),
                "unique_values": unique_count,
            },
        )

    return result

def analyze_constant_columns(df: pd.DataFrame) -> List[str]:
    """
    Detect columns where all non-null values are the same.
    """
    constant_cols: List[str] = []

    for col in df.columns:
        unique_non_null = df[col].dropna().nunique()
        if unique_non_null <= 1:
            constant_cols.append(col)
            logger.warning(
                "Constant column detected",
                extra={
                    "event": "constant_column",
                    "column": col,
                },
            )

    return constant_cols


def analyze_high_cardinality_categoricals(
    df: pd.DataFrame,
    threshold: int = 1000,
) -> Dict[str, int]:
    """
    Detect high-cardinality categorical columns.
    """
    high_card_cols: Dict[str, int] = {}

    # All non-numeric columns are treated as categorical here
    cat_df = df.select_dtypes(exclude="number")

    for col in cat_df.columns:
        unique_count = int(cat_df[col].nunique(dropna=True))
        if unique_count > threshold:
            high_card_cols[col] = unique_count
            logger.warning(
                "High-cardinality categorical column detected",
                extra={
                    "event": "high_cardinality",
                    "column": col,
                    "unique_values": unique_count,
                    "threshold": threshold,
                },
            )

    return high_card_cols


def check_value_ranges(
    df: pd.DataFrame,
    rules: Dict[str, Tuple[float, float]],
) -> Dict[str, Dict[str, Any]]:
    """
    Check that numeric columns fall within given [min, max] ranges.
    """
    issues: Dict[str, Dict[str, Any]] = {}

    for col, (min_allowed, max_allowed) in rules.items():
        if col not in df.columns:
            continue

        series = pd.to_numeric(df[col], errors="coerce")
        if series.empty:
            continue

        actual_min = float(series.min())
        actual_max = float(series.max())

        out_of_range_mask = (series < min_allowed) | (series > max_allowed)
        out_of_range_count = int(out_of_range_mask.sum())

        issues[col] = {
            "min_allowed": float(min_allowed),
            "max_allowed": float(max_allowed),
            "actual_min": actual_min,
            "actual_max": actual_max,
            "out_of_range_count": out_of_range_count,
        }

        if out_of_range_count > 0:
            logger.warning(
                "Out-of-range values detected",
                extra={
                    "event": "out_of_range",
                    "column": col,
                    "min_allowed": float(min_allowed),
                    "max_allowed": float(max_allowed),
                    "actual_min": actual_min,
                    "actual_max": actual_max,
                    "out_of_range_count": out_of_range_count,
                },
            )

    return issues


def run_quality_checks(path: str | Path) -> Dict[str, Any]:
    """
    Main entry point for the dataset quality checker.

    The returned dict is easy to print or save as JSON.
    """
    df = load_dataset(path)

    # Core checks
    missing_summary = analyze_missing_values(df)
    numeric_summary = analyze_numeric_ranges(df)
    schema_summary = basic_schema_summary(df)
    constant_cols = analyze_constant_columns(df)
    high_card_cols = analyze_high_cardinality_categoricals(df, threshold=5)
    range_issues = check_value_ranges(df, rules={"age": (0, 120)})

    logger.info(
        "Quality checks completed",
        extra={
            "event": "quality_done",
            "path": str(path),
        },
    )

    return {
        "path": str(path),
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
        "missing_values": missing_summary,
        "numeric_ranges": numeric_summary,
        "schema": schema_summary,
        "constant_columns": constant_cols,
        "high_cardinality_columns": high_card_cols,
        "range_issues": range_issues,
    }
