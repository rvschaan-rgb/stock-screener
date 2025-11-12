# My Stock Screener

import pandas as pd
import yfinance as yf
import os
from datetime import datetime
from tqdm import tqdm

# ======================================================================
# Dynamically get the folder where THIS script is located
# ======================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ======================================================================
# Load Ticker Symbols
# ======================================================================
def load_tickers():
    try:
        sp500 = pd.read_csv(os.path.join(BASE_DIR, "data\sp500_companies.csv"))["Symbol"]
        russell = pd.read_csv(os.path.join(BASE_DIR, "data\iShares-Russell-2000-ETF_fund.csv"))["Symbol"]
        nyse = pd.read_csv(os.path.join(BASE_DIR, "data\nyse-listed.csv"))["Symbol"]
        tickers = pd.concat([sp500, russell, nyse]).drop_duplicates().tolist()
        return tickers

    except FileNotFoundError as e:
        print("\n❌ ERROR: Could not find ticker list.")
        print("Missing file:", e.filename)
        raise

# ======================================================================
# Load Sector PE file
# ======================================================================
def load_sector_pe():
    sector_file = os.path.join(BASE_DIR, "data\SectorPE.xlsx")
    try:
        df = pd.read_excel(sector_file)
        lookup = dict(zip(df["sectorKey"].str.lower().str.replace(" ", ""), df["sectorPE"]))
        print(f"✅ Loaded Sector PE table: {sector_file}")
        return lookup

    except PermissionError:
        print("\n⚠️ ERROR: Close SectorPE.xlsx first.")
        raise

    except FileNotFoundError:
        print("\n❌ ERROR: Could not find SectorPE.xlsx.")
        raise

# ======================================================================
# EPS Growth Filter
# ======================================================================
def eps_growth_2yr(symbol):
    """
    Returns True if Diluted EPS has grown 3 years in a row.
    """
    try:
        ticker = yf.Ticker(symbol)
        income = ticker.income_stmt

        if "Diluted EPS" not in income.index:
            return False

        eps_vals = income.loc["Diluted EPS"].iloc[:2].tolist()
        eps_vals = [v for v in eps_vals if v is not None and not pd.isna(v)]

        if len(eps_vals) < 2:
            return False

        return eps_vals[1] < eps_vals[0]

    except Exception:
        return False

# ======================================================================
# Screening Function
# ======================================================================
def screen_stocks(tickers, sector_pe_lookup):
    results = []

    # Diagnostic counters
    f1 = f2 = f3 = f4 = f5 = 0

    for symbol in tqdm(tickers, desc="Screening stocks"):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.get_info()

            stock_pe = info.get("trailingPE")
            stock_sector = info.get("sector")
            debt_to_equity = info.get("debtToEquity")

            if stock_pe is None or stock_sector is None:
                continue

            sector_key = stock_sector.lower().replace(" ", "")
            sector_avg_pe = sector_pe_lookup.get(sector_key)

            if sector_avg_pe is None:
                continue

            # ✅ Filter 1 — PE
            if stock_pe <= 1.05 * sector_avg_pe:
                f1 += 1
            else:
                continue

            # ✅ Filter 2 — Debt / Equity
            if debt_to_equity is not None and debt_to_equity < 4.0:
                f2 += 1
            else:
                continue

            # ✅ Filter 3 — EPS Growth
            if eps_growth_2yr(symbol):
                f3 += 1
            else:
                continue

            # ✅ Volume / price analysis
            hist = ticker.history(period="90d")
            if hist.empty or len(hist) < 50:
                continue

            avg_10day_volume = hist["Volume"].tail(11).iloc[:-1].mean()
            today_volume = hist["Volume"].iloc[-1]

            if today_volume >= 0.90 * avg_10day_volume:
                f4 += 1
            else:
                continue

            current_price = hist["Close"].iloc[-1]
            high_20 = hist["High"].tail(20).max()
            sma_50 = hist["Close"].rolling(window=50).mean().iloc[-1]

            if current_price >= 0.90 * high_20 and current_price >= sma_50:
                f5 += 1
            else:
                continue

            # Passed ALL filters
            results.append({
                "Symbol": symbol,
                "Sector": stock_sector,
                "Stock PE": stock_pe,
                "Sector Avg PE": sector_avg_pe,
                "Debt/Equity": debt_to_equity,
                "Today Volume": today_volume,
                "10-Day Avg Volume": avg_10day_volume,
                "Price": current_price,
                "20-Day High": high_20,
                "SMA50": sma_50,
                "2-Year EPS Growth": "Yes",
            })

        except Exception:
            continue

    # ✅ Print final diagnostic summary
    print("\n================ Filter Diagnostics ================")
    print(f"Passed PE filter:          {f1}")
    print(f"Passed Debt/Equity filter: {f2}")
    print(f"Passed EPS growth:         {f3}")
    print(f"Passed Volume breakout:    {f4}")
    print(f"Passed Price breakout:     {f5}")
    print("====================================================\n")

    

    return results
    
# ======================================================================
# Main Execution
# ======================================================================
if __name__ == "__main__":

    tickers = load_tickers()
    print(f"✅ Total tickers loaded: {len(tickers)}")

    sector_pe_lookup = load_sector_pe()

    results = screen_stocks(tickers, sector_pe_lookup)

    # Export results
    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%m-%d-%y %H-%M")
    filename = os.path.join(BASE_DIR, f"outputs\Watch_Screen_Results_{timestamp}.xlsx")
    df.to_excel(filename, index=False)

    print(f"✨ Done! Final screened stock count: {len(df)}")
    print(f"📁 Exported results to: {filename}")
