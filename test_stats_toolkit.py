"""Unit tests for the statistics toolkit."""

import tempfile
import unittest
from pathlib import Path

from stats_toolkit import (
    StatisticsAnalyzer,
    iqr_outliers,
    load_column,
    mean,
    median,
    mode,
    std_dev,
    variance,
)


class TestCentralTendency(unittest.TestCase):
    def test_mean_of_known_values(self):
        self.assertAlmostEqual(mean([1, 2, 3, 4]), 2.5)

    def test_median_even_and_odd_lengths(self):
        self.assertEqual(median([1, 3, 2]), 2)
        self.assertEqual(median([1, 2, 3, 4]), 2.5)

    def test_mode_with_ties(self):
        self.assertEqual(mode([4, 4, 3, 3, 2]), [3, 4])

    def test_empty_input_raises(self):
        with self.assertRaises(ValueError):
            mean([])
        with self.assertRaises(ValueError):
            median([])
        with self.assertRaises(ValueError):
            mode([])


class TestSpread(unittest.TestCase):
    def test_sample_vs_population_variance(self):
        values = [1, 2, 3, 4]
        self.assertAlmostEqual(variance(values, sample=True), 1.6666666666666667)
        self.assertAlmostEqual(variance(values, sample=False), 1.25)

    def test_std_dev_single_value(self):
        self.assertEqual(std_dev([7]), 0.0)


class TestOutliers(unittest.TestCase):
    def test_no_outliers_in_uniform_data(self):
        values = [10, 11, 10, 12, 11, 10, 11, 12]
        result = iqr_outliers(values)
        self.assertEqual(result["Outliers"], [])

    def test_detects_obvious_outlier(self):
        values = [5, 6, 7, 8, 9, 100]
        result = iqr_outliers(values)
        self.assertIn(100, result["Outliers"])


class TestLoading(unittest.TestCase):
    def test_invalid_and_missing_values_are_rejected(self):
        with tempfile.NamedTemporaryFile("w", newline="", encoding="utf-8", delete=False) as handle:
            handle.write("agent_id,daily_deposits_kes\n")
            handle.write("AG-1,1200\n")
            handle.write("AG-2,\n")
            handle.write("AG-3,n/a\n")
            handle.write("AG-4,50.5\n")
            handle.write("AG-5,abc\n")
            handle.write("AG-6,-\n")
            temp_path = Path(handle.name)

        valid_values, rejected = load_column(temp_path, "daily_deposits_kes")
        self.assertEqual(valid_values, [1200.0, 50.5])
        self.assertEqual(len(rejected), 4)
        self.assertEqual(rejected[0][0], 3)
        temp_path.unlink()


class TestAnalyzer(unittest.TestCase):
    def test_analyzer_from_csv_and_summary(self):
        with tempfile.NamedTemporaryFile("w", newline="", encoding="utf-8", delete=False) as handle:
            handle.write("day,amount\n")
            handle.write("1,10\n")
            handle.write("2,20\n")
            handle.write("3,30\n")
            handle.write("4,40\n")
            handle.write("5,50\n")
            temp_path = Path(handle.name)

        analyzer = StatisticsAnalyzer.from_csv(temp_path, "amount")
        self.assertEqual(analyzer.name, "amount")
        self.assertEqual(analyzer.summary()["count"], 5)
        self.assertAlmostEqual(analyzer.summary()["mean"], 30.0)
        temp_path.unlink()


if __name__ == "__main__":
    unittest.main()
