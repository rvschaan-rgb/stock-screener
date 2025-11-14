# My Stock Screener

import pandas as pd
import yfinance as yf
import os
from datetime import datetime
from tqdm import tqdm

# ======================================================================
# Environment Validation (auto-check)
# ======================================================================
import importlib.util
from pathlib import Path

def verify_environment():
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir.parent / "data"
    output_dir = base_dir.parent / "outputs"

    required_files = [
        data_dir / "sp500_companies.csv",
        data_dir / "iShares-Russell-2000-ETF_fund.csv",
        data_dir / "nyse-listed.csv",
        data_dir / "SectorPE.xlsx",
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
# Dynamically get the folder where THIS script is located
# ======================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ======================================================================
# Load Ticker Symbols
# ======================================================================
def load_tickers():
    try:
        sp500 = pd.read_csv(os.path.join(BASE_DIR, "sp500_companies.csv"))["Symbol"]
        # Uncomment additional lists as needed:
        # other = pd.read_csv(os.path.join(BASE_DIR, "other-listed.csv"))["Symbol"]
        # nyse = pd.read_csv(os.path.join(BASE_DIR, "nyse-listed.csv"))["Symbol"]
        # russell = pd.read_csv(os.path.join(BASE_DIR, "iShares-Russell-2000-ETF_fund.csv"))["Symbol"]

        tickers = pd.concat([sp500]).drop_duplicates().tolist()
        return tickers

    except FileNotFoundError as e:
        print("\n❌ ERROR: Could not find one of the ticker CSV files.\n")
        print("Missing file:", e.filename)
        raise

# ======================================================================
# Load Sector PE file
# ======================================================================
def load_sector_pe():
    sector_file = os.path.join(BASE_DIR, "SectorPE.xlsx")
    try:
        df = pd.read_excel(sector_file)
        lookup = dict(zip(df["sectorKey"].str.lower().str.replace(" ", ""), df["sectorPE"]))
        print(f"✅ Loaded Sector PE table: {sector_file}")
        return lookup

    except PermissionError:
        print("\n⚠️ ERROR: Excel file is currently open. Close `SectorPE.xlsx` and run again.")
        raise

    except FileNotFoundError:
        print("\n❌ ERROR: Could not find SectorPE.xlsx at this location:")
        print(sector_file)
        raise

# ======================================================================
# EPS Growth Filter
# ======================================================================
def eps_growth_3yr(symbol):
    """
    Returns True if Diluted EPS has grown 3 years in a row.
    """
    try:
        ticker = yf.Ticker(symbol)
        income = ticker.income_stmt

        if "Diluted EPS" not in income.index:
            return False

        eps_vals = income.loc["Diluted EPS"].iloc[:3].tolist()
        eps_vals = [v for v in eps_vals if v is not None and not pd.isna(v)]

        if len(eps_vals) < 3:
            return False

        # Check 3-year EPS growth (oldest < middle < most recent)
        return eps_vals[2] < eps_vals[1] < eps_vals[0]

    except Exception:
        return False

# ======================================================================
# Screening Function
# ======================================================================
def screen_stocks(tickers, sector_pe_lookup):
    results = []

    for symbol in tqdm(tickers, desc="Screening PE vs Sector"):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.get_info()

            stock_pe = info.get("trailingPE")
            stock_sector = info.get("sector")

            if stock_pe is None or stock_sector is None:
                continue

            sector_key = stock_sector.lower().replace(" ", "")
            sectorPE = sector_pe_lookup.get(sector_key)
            if sectorPE is None:
                continue

            # Skip if stock PE is higher than sector PE
            if stock_pe >= sectorPE:
                continue

            # EPS growth filter
            if not eps_growth_3yr(symbol):
                continue

            results.append({
                "Symbol": symbol,
                "Sector": stock_sector,
                "Stock PE": stock_pe,
                "Sector Avg PE": sectorPE,
                "3-Year EPS Growth": "Yes"
            })

        except Exception:
            continue

    return results

# ======================
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
    filename = os.path.join(BASE_DIR, f"Screen_Results_{timestamp}.xlsx")
    df.to_excel(filename, index=False)

    print(f"✨ Done! Stocks worth looking at: {len(df)}")
    print(f"📁 Exported results to: {filename}")