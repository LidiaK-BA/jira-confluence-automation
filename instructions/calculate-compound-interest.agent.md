---
description: "Use when calculating compound interest or invoking tools/compound_interest.py."
---

- Use `tools/compound_interest.py` to calculate compound interest; do not estimate the result.
- Run the command from the repository root with four positional arguments in this order: `python tools/compound_interest.py <principal> <annual_rate> <compounds_per_year> <total_years>`.
- Pass the annual rate as a decimal, such as `0.05` for 5%; pass compounds per year as a positive integer.
- Principal, annual rate, and total years must be non-negative numbers. Total years may be fractional.
- For example, `python tools/compound_interest.py 1000 0.05 12 2` prints a final amount of `$1,104.94` and interest earned of `$104.94`.
- Present both results using the script's labels, `Final amount` and `Interest earned`, and preserve the currency formatting to two decimal places.
- If the command reports invalid input, relay the error and request corrected values instead of presenting a calculated result.
