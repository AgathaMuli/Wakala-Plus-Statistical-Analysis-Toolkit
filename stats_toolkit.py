"""Statistical helper functions for the agent deposit toolkit.

This module keeps the calculations in plain Python and leaves NumPy for the
validation step only.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

DATA_PATH = Path("data") / "agent_deposits.csv"


def load_column(path: Path, column: str) -> tuple[list[float], list[tuple[int, str]]]:
    """Return valid numeric values and the rejected rows.

    Rows are counted starting at 2 because the CSV header sits on row 1.
    Missing values, placeholders and invalid text are rejected and reported
    with their source row number and original raw value.
    """
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV file is missing a header row: {path}")
        if column not in reader.fieldnames:
            raise KeyError(f"Column '{column}' was not found in {path}")

        valid_values: list[float] = []
        rejected: list[tuple[int, str]] = []

        for row_index, row in enumerate(reader, start=2):
            raw_value = row.get(column, "")
            clean_value = "" if raw_value is None else str(raw_value).strip()

            if clean_value == "" or clean_value.lower() in {"na", "n/a", "nan", "null", "none", "-", "--", "."}:
                rejected.append((row_index, raw_value or ""))
                continue

            try:
                number = float(clean_value)
            except ValueError:
                rejected.append((row_index, raw_value or ""))
                continue

            if math.isnan(number) or math.isinf(number):
                rejected.append((row_index, raw_value or ""))
                continue

            valid_values.append(number)

    return valid_values, rejected


def mean(values: list[float]) -> float:
    """Return the arithmetic mean of a non-empty list."""
    if not values:
        raise ValueError("Mean requires at least one value.")
    return sum(values) / len(values)


def median(values: list[float]) -> float:
    """Return the median, handling odd and even samples."""
    if not values:
        raise ValueError("Median requires at least one value.")

    ordered = sorted(values)
    midpoint = len(ordered) // 2
    if len(ordered) % 2 == 0:
        return (ordered[midpoint - 1] + ordered[midpoint]) / 2
    return ordered[midpoint]


def mode(values: list[float]) -> list[float]:
    """Return every value with the highest frequency.

    If there is a tie, the function returns all tied modes in ascending order.
    """
    if not values:
        raise ValueError("Mode requires at least one value.")

    counts: dict[float, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1

    highest_frequency = max(counts.values())
    modes = sorted(value for value, frequency in counts.items() if frequency == highest_frequency)
    return modes


def variance(values: list[float], sample: bool = True) -> float:
    """Return sample or population variance.

    The default sample setting uses n - 1. If there is only one item, the result
    is 0.0 to keep the calculation stable and to align with the standard
    deviation rule for a single observation.
    """
    if not values:
        raise ValueError("Variance requires at least one value.")
    if len(values) == 1:
        return 0.0

    average = mean(values)
    total = sum((value - average) ** 2 for value in values)
    denominator = len(values) - 1 if sample else len(values)
    return total / denominator


def std_dev(values: list[float], sample: bool = True) -> float:
    """Return the sample or population standard deviation."""
    if not values:
        raise ValueError("Standard deviation requires at least one value.")
    return math.sqrt(variance(values, sample=sample))


def quartiles(values: list[float]) -> tuple[float, float, float]:
    """Return Q1, Q2 and Q3 using the median-of-halves method.

    For odd-sized samples, the median is excluded from both halves before the
    lower and upper medians are calculated.
    """
    if not values:
        raise ValueError("Quartiles require at least one value.")

    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0], ordered[0], ordered[0]

    q2 = median(ordered)
    midpoint = len(ordered) // 2
    if len(ordered) % 2 == 0:
        lower_half = ordered[:midpoint]
        upper_half = ordered[midpoint:]
    else:
        lower_half = ordered[:midpoint]
        upper_half = ordered[midpoint + 1:]

    q1 = median(lower_half) if lower_half else q2
    q3 = median(upper_half) if upper_half else q2
    return q1, q2, q3


def iqr_outliers(values: list[float], k: float = 1.5) -> dict[str, Any]:
    """Find values outside the IQR fences."""
    if not values:
        raise ValueError("Outlier detection requires at least one value.")
    if k < 0:
        raise ValueError("k must be non-negative.")

    q1, _, q3 = quartiles(values)
    iqr = q3 - q1
    lower_fence = q1 - k * iqr
    upper_fence = q3 + k * iqr
    outliers = [value for value in values if value < lower_fence or value > upper_fence]

    return {
        "IQR": iqr,
        "lower_fence": lower_fence,
        "upper_fence": upper_fence,
        "Lower Fence": lower_fence,
        "Upper Fence": upper_fence,
        "Outliers": outliers,
    }


class StatisticsAnalyzer:
    """Wrap a numeric column and expose summary statistics as a single object."""

    def __init__(self, values: list[float], name: str = "values") -> None:
        self.values = list(values)
        self.name = name
        self.rejected: list[tuple[int, str]] = []
        self._sorted_values: list[float] | None = None
        self._summary_cache: dict[str, Any] | None = None

    @classmethod
    def from_csv(cls, path: Path, column: str) -> "StatisticsAnalyzer":
        """Create a new analyzer from a CSV column."""
        values, rejected = load_column(path, column)
        analyzer = cls(values, name=column)
        analyzer.rejected = rejected
        return analyzer

    def _cache_sorted_values(self) -> list[float]:
        if self._sorted_values is None:
            self._sorted_values = sorted(self.values)
        return self._sorted_values

    def _compute_quartiles(self) -> tuple[float, float, float]:
        ordered = self._cache_sorted_values()
        return quartiles(ordered)

    def summary(self) -> dict[str, Any]:
        if self._summary_cache is not None:
            return self._summary_cache

        if not self.values:
            raise ValueError("Cannot summarize an empty dataset.")

        q1, q2, q3 = self._compute_quartiles()
        iqr_result = iqr_outliers(self.values)
        iqr = iqr_result["IQR"]
        lower_fence = iqr_result["Lower Fence"]
        upper_fence = iqr_result["Upper Fence"]
        outliers = iqr_result["Outliers"]

        summary = {
            "name": self.name,
            "count": len(self.values),
            "mean": mean(self.values),
            "median": q2,
            "mode": mode(self.values),
            "variance": variance(self.values),
            "std_dev": std_dev(self.values),
            "Q1": q1,
            "Q2": q2,
            "Q3": q3,
            "IQR": iqr,
            "Lower Fence": lower_fence,
            "Upper Fence": upper_fence,
            "Outliers": outliers,
        }
        self._summary_cache = summary
        return summary

    def without_outliers(self) -> "StatisticsAnalyzer":
        """Return a new analyzer with the detected outliers removed."""
        summary = self.summary()
        remaining_values = self.values.copy()
        for outlier in summary["Outliers"]:
            if outlier in remaining_values:
                remaining_values.remove(outlier)

        return StatisticsAnalyzer(remaining_values, name=f"{self.name} (without outliers)")

    def report(self) -> str:
        """Return a readable summary for the dataset."""
        summary = self.summary()
        lines = [
            f"Statistics Report: {summary['name']}",
            f"Count: {summary['count']}",
            f"Mean: {summary['mean']}",
            f"Median: {summary['median']}",
            f"Mode: {summary['mode']}",
            f"Variance: {summary['variance']}",
            f"Standard deviation: {summary['std_dev']}",
            f"Q1: {summary['Q1']}",
            f"Q2: {summary['Q2']}",
            f"Q3: {summary['Q3']}",
            f"IQR: {summary['IQR']}",
            f"Lower fence: {summary['Lower Fence']}",
            f"Upper fence: {summary['Upper Fence']}",
            f"Outliers: {summary['Outliers']}",
        ]
        return "\n".join(lines)


def compare_with_numpy(analyzer: StatisticsAnalyzer) -> dict[str, bool]:
    """Compare the toolkit against NumPy using a tolerance check."""
    import numpy as np

    values = np.asarray(analyzer.values, dtype=float)
    summary = analyzer.summary()
    comparison: dict[str, bool] = {}

    if values.size == 0:
        return {"mean": False, "median": False, "mode": False, "variance": False, "std_dev": False, "Q1": False, "Q2": False, "Q3": False}

    unique, counts = np.unique(values, return_counts=True)
    numpy_modes = unique[counts == counts.max()]

    q1, q2, q3 = quartiles(analyzer.values)
    ordered = np.sort(values)
    if ordered.size == 1:
        np_q1, np_q2, np_q3 = ordered[0], ordered[0], ordered[0]
    else:
        midpoint = ordered.size // 2
        if ordered.size % 2 == 0:
            lower_half = ordered[:midpoint]
            upper_half = ordered[midpoint:]
        else:
            lower_half = ordered[:midpoint]
            upper_half = ordered[midpoint + 1:]
        np_q1 = float(np.median(lower_half))
        np_q2 = float(np.median(ordered))
        np_q3 = float(np.median(upper_half))

    np_q1_matches = math.isclose(q1, np_q1, rel_tol=1e-9, abs_tol=1e-9)
    np_q2_matches = math.isclose(q2, np_q2, rel_tol=1e-9, abs_tol=1e-9)
    np_q3_matches = math.isclose(q3, np_q3, rel_tol=1e-9, abs_tol=1e-9)

    comparison["mean"] = math.isclose(float(np.mean(values)), float(summary["mean"]), rel_tol=1e-9, abs_tol=1e-9)
    comparison["median"] = math.isclose(float(np.median(values)), float(summary["median"]), rel_tol=1e-9, abs_tol=1e-9)
    comparison["mode"] = np.allclose(np.sort(numpy_modes), np.sort(np.asarray(summary["mode"], dtype=float)), rtol=1e-9, atol=1e-9)
    comparison["variance"] = math.isclose(float(np.var(values, ddof=1)), float(summary["variance"]), rel_tol=1e-9, abs_tol=1e-9)
    comparison["std_dev"] = math.isclose(float(np.std(values, ddof=1)), float(summary["std_dev"]), rel_tol=1e-9, abs_tol=1e-9)
    comparison["Q1"] = np_q1_matches
    comparison["Q2"] = np_q2_matches
    comparison["Q3"] = np_q3_matches
    return comparison


__all__ = [
    "DATA_PATH",
    "StatisticsAnalyzer",
    "compare_with_numpy",
    "iqr_outliers",
    "load_column",
    "mean",
    "median",
    "mode",
    "quartiles",
    "std_dev",
    "variance",
]
