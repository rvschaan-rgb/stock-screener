import pandas as pd
import yfinance as yf
from pandas import json_normalize  # helps flatten nested dicts

tickers = ["PBA"]  # start small

results = []

for t in tickers:
    try:
        info = yf.Ticker(t).info
        # Flatten nested dicts
        flat_info = json_normalize(info)
        results.append(flat_info)
    except Exception as e:
        print(f"Error fetching {t}: {e}")

# Combine all into one DataFrame
if results:
    df = pd.concat(results, ignore_index=True)
    # Export to Excel
    df.to_excel("pba.xlsx", index=False)
    print("✅ Exported to nee.xlsx")
else:
    print("⚠️ No data fetched.")
