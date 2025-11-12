# 🧠 Stock Screener (Python)

A data-driven stock screening tool built in Python for identifying high-potential buying opportunities from the S&P 500 and creating a stock watch list.
This project combines practical programming skills with a disciplined approach to learning and decision-making — part of my personal philosophy of running **life as a business**.

---

## 🚀 Features

- **Automated Data Fetching:**  
  Retrieves up-to-date stock data using the [Yahoo Finance API (`yfinance`)](https://pypi.org/project/yfinance/).

- **Multithreading Support:**  
  Uses Python’s `concurrent.futures` to speed up stock data collection, allowing parallel downloads and improved performance.

- **Custom Filters:**  
  Applies logic to identify only top-tier stocks based on user-defined metrics like price action, moving averages, or volume.

- **Progress Tracking:**  
  Integrated with [`tqdm`](https://tqdm.github.io/) for real-time visual progress bars while fetching stock data.

- **Error Handling & Retry Logic:**  
  Prevents incomplete data pulls from breaking the analysis pipeline.

---

## 🧰 Technologies Used or Will be Used

| Tool / Library | Purpose |
|----------------|----------|
| `pandas` | Data manipulation and filtering |
| `yfinance` | Stock data retrieval |
| `datetime` | Time-based filtering |
| `concurrent.futures` | Multithreading for faster performance |
| `tqdm` | Progress bars for tracking completion |

---

## ⚙️ How It Works

1. **Load the S&P 500 ticker list**  
   - The script reads `sp500_companies.csv` containing company symbols.

2. **Pull data with `yfinance`**  
   - Downloads live market data for each ticker.

3. **Apply filters**  
   - Only the strongest candidates pass. Metrics and thresholds are adjustable, reflecting the principle of disciplined decision-making: measure, analyze, act.

4. **Output**  
   - Results are displayed in the console or saved for further review.

---
## 📋 How to Use

1. **Clone the repository:**

```bash
git clone https://github.com/rvschaan-rgb/stock-screener.git
cd stock-screener

2. Install dependencies (Python 3.10+ recommended):

pip install pandas yfinance tqdm

3. Make sure you have the S&P 500 ticker file:

    sp500_companies.csv should be in the same folder as the script.

    You can create or update it from public S&P 500 sources.

4. Run the stock screener:

python Buy\ Screener.py

5. Check the console for results

    Stocks that meet the criteria will be displayed.

    Modify filtering logic in the script to refine which stocks are selected.


## 📈 Example Output

Processing: 480/500 tickers...
❌ TSLA skipped (failed volume filter)
Analysis complete. 23 tickers passed all filters.

## 🧩 Future Plans

- Add visualization using `matplotlib` or `plotly`
- Integrate alerts (email, SMS, or Telegram)
- Convert script into a web-based dashboard (Flask / React)
- Automate daily screening via cron or Windows Task Scheduler

---

## 💡 Personal Philosophy

This project is more than a stock screener — it’s a reflection of how I approach **learning, skill-building, and life itself**.  

- **Life as a business:** Every action is treated as an investment in knowledge, skill, or opportunity.  
- **Systematic decision-making:** Whether coding or analyzing markets, I aim to remove emotion and rely on logic, discipline, and structured processes.  
- **Continuous improvement:** Every iteration of this script — every commit on GitHub — represents forward progress toward mastery.

This philosophy guides not only the design of this project but also my growth as a programmer and problem-solver.

---

## 📜 License

This project is open-source under the [MIT License](LICENSE) — feel free to fork, modify, and build on it.