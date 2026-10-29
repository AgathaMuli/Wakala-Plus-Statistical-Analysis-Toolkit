## Overview
Wakala Plus runs a network of M-Pesa agents around Nairobi, Thika, Machakos and Nakuru. Its risk team watches daily deposit totals per agent: unusually high or low days can mean fraud, a float shortage or a data-entry error.

They want a small, dependable statistics toolkit they understand line by line, not a black box. You must implement every calculation yourself in plain Python first; NumPy is permitted only afterwards, to verify that your numbers agree. The data comes from agents typing figures into a phone app, so expect gaps, placeholders and typos alongside a few days that really are extreme.


# Agent Transaction Analytics

This module provides helper utilities to compute variance and standard deviation using pure Python math operations.

## Formula Selection Rationale

### Which formula suits this dataset?
For this operational dataset, **Sample Variance and Sample Standard Deviation ($n - 1$)** are the correct configurations to use.

### Why?
* **Partial Temporal Window:** The dataset only tracks transaction records spanning from September 1, 2026, through October 10, 2026. It does not encompass the entire lifetime operations of these banking agents, nor does it capture a complete fiscal cycle.
* **Statistical Inference:** Because this data represents a fractional window of ongoing business activity, it must be classified as a *sample* rather than a complete population.
* **Bias Correction:** Calculating variance using the population divisor ($n$) on a sample introduces downward bias, consistently underestimating the true variability of the system. Applying Bessel's Correction ($n - 1$) mathematically neutralizes this bias, ensuring a reliable estimate of operational volatility across the entire agent network.