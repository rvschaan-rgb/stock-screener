# Stock Market Screener Project

This project provides a stock screening tool to analyze EPS growth, PE ratios, debt/equity, and volume/price trends across multiple stock indexes.

---

## Folder Structure

stock_market/
├── data/ # Input files: CSVs and Excel sheets
├── scripts/ # Python scripts
├── outputs/ # Generated Excel outputs
└── README.md # This file

## Setup & Usage

1. Ensure Python 3.10+ is installed.
2. Install required libraries:
    pip install pandas yfinance tqdm openpyxl
3. Place your data files in data/.
4. Run the main script:
    python scripts/watch_list_screener.py
5. Outputs will be generated in outputs/.

## Notes & Philosophy

This project demonstrates the “life as a business” approach:

Systematic: Clear step-by-step screening filters.
Consistent: Standardized folder structure and naming conventions.
Growth-focused: Each iteration builds on previous improvements.
The focus is on maintainable, readable code that can scale with additional projects and datasets.

## License / Disclaimer

This tool is for educational purposes and personal use. Do your own research before using it for financial decisions.

