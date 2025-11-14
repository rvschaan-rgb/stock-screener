# My Stock Screener

import pandas as pd
import yfinance as yf
import importlib.util
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

# ======================================================================
# Environment Validation (auto-check)
# ======================================================================

def verify_environment():
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir.parent / "data"
    output_dir = base_dir.parent / "outputs"

    required_files = [
        data_dir / "sp500.csv",
        data_dir / "russell_2000_etf.csv",
        data_dir / "nyse.csv",
        data_dir / "sector_pe.xlsx",
    ]

    required_libs = ["pandas", "yfinance", "tqdm", "openpyxl"]

    print("=" * 60)
    print("🔧 ENVIRONMENT CHECK")
    print("=" * 60)

    # --- Check files and folders ---
    for f in required_files:
        if not f.exists():
            raise FileNotFoundError(f"❌ Missing required file: {f}")
        else:
            print(f"✅ Found: {f.name}")

    if not output_dir.exists():
        print(f"⚠️ Output folder missing, creating: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)

    # --- Check library dependencies ---
    for lib in required_libs:
        if importlib.util.find_spec(lib) is None:
            raise ImportError(f"❌ Missing Python library: {lib}")
        else:
            print(f"✅ Library OK: {lib}")

    print("=" * 60)
    print("🎯 Environment OK — proceeding.\n")

# Run environment verification
verify_environment()

# ======================================================================
# Define paths dynamically
# ======================================================================
BASE_DIR = Path(__file__).resolve().parent  # /scripts
DATA_DIR = BASE_DIR.parent / "data"
OUTPUT_DIR = BASE_DIR.parent / "outputs"

# Ensure output folder exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ======================================================================
# Load Ticker Symbols
# ======================================================================
def load_tickers():
    try:
        sp500 = pd.read_csv(DATA_DIR / "sp500.csv")["Symbol"]
        russell = pd.read_csv(DATA_DIR / "russell_2000_etf.csv")["Symbol"]
        nyse = pd.read_csv(DATA_DIR / "nyse.csv")["Symbol"]

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
    sector_file = DATA_DIR / "sector_pe.xlsx"
    try:
        df = pd.read_excel(sector_file)
        lookup = dict(zip(df["sectorKey"].str.lower().str.replace(" ", ""), df["sectorPE"]))
        print(f"✅ Loaded Sector PE table: {sector_file}")
        return lookup

    except PermissionError:
        print("\n⚠️ ERROR: Close sector_pe.xlsx first.")
        raise

    except FileNotFoundError:
        print("\n❌ ERROR: Could not find sector_pe.xlsx.")
        raise

# ======================================================================
# EPS Growth Filter
# ======================================================================
def eps_growth_2yr(symbol):
    """
    Returns True if Diluted EPS has grown 2 years in a row.
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
            if stock_pe <= (1.05 * int(sector_avg_pe)):
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

            if today_volume >= (0.90 * int(avg_10day_volume)):
                f4 += 1
            else:
                continue

            current_price = hist["Close"].iloc[-1]
            high_20 = hist["High"].tail(20).max()
            sma_50 = hist["Close"].rolling(window=50).mean().iloc[-1]

            if current_price >= (0.90 * int(high_20)) and current_price >= sma_50:
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
def main():
    tickers = load_tickers()
    print(f"✅ Total tickers loaded: {len(tickers)}")

    sector_pe_lookup = load_sector_pe()

    results = screen_stocks(tickers, sector_pe_lookup)

    # Export results
    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%m-%d-%y_%H-%M")
    filename = OUTPUT_DIR / f"watch_screen_results_{timestamp}.xlsx"
    df.to_excel(filename, index=False)

    print(f"✨ Done! Final screened stock count: {len(df)}")
    print(f"📁 Exported results to: {filename}")

if __name__ == "__main__":
    verify_environment()
    main()