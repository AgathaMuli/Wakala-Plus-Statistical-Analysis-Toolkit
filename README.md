# Agent Transaction Analytics

Wakala Plus runs a network of M-Pesa agents across Nairobi, Thika, Machakos and Nakuru. The risk team monitors daily deposits and transaction counts to spot fraud, float shortages and data-entry issues. This project implements the calculations in plain Python and compares the results with NumPy only for verification.

## Project structure

```text
day3assignment/
├── README.md
├── analysis.ipynb
├── pyproject.toml
├── test_stats_toolkit.py
├── stats_toolkit.py
├── data/
│   └── agent_deposits.csv
├── output/
│   └── stats_report.txt
└── src/
    └── day3assignment/
        └── __init__.py
```

## Project goals

The toolkit is designed to do the following:

- Load a CSV column and reject missing or invalid values.
- Calculate mean, median and mode without using the statistics module.
- Compute variance and standard deviation using sample or population divisors.
- Detect outliers with the IQR method and a configurable fence factor.
- Wrap a single column in a reusable StatisticsAnalyzer object.
- Generate a summary report and compare the results against NumPy.

## Formula selection

For this operational dataset, sample variance and sample standard deviation are the correct choices. The records cover a limited window of activity rather than a full operational lifetime, so the sample formula avoids the downward bias that appears when the population divisor is used on partial data.

## Dataset handling rules

The loader rejects values such as empty strings, NA, N A, null, none, dash placeholders and malformed numeric text. Valid values are kept and used in all later calculations.

## How to run

From the project root, run the test suite:

```bash
python -m unittest -v
```

To generate the report from the notebook, open analysis.ipynb and run all cells in order. The output will be written to:

```text
output/stats_report.txt
```

You can also run the toolkit script directly:

```bash
python starter\ \(2\).py
```

## Notes

The code in stats_toolkit.py keeps every calculation transparent and easy to audit. NumPy is imported only inside compare_with_numpy so the report can be validated against the same values using a tolerance check.