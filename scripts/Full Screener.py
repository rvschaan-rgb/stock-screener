import pandas as pd
import yfinance as yf
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time
import os

# ========================
# CONFIGURATION
# ========================
MAX_THREADS = os.cpu_count() * 2  # auto scale
YF_SLOWDOWN = 0.10                # delay between batch requests

# ========================
# LOAD TICKERS
# ========================
def load_tickers():
    sp500 = pd.read_csv("sp500_companies.csv")["Symbol"]
    russell = pd.read_csv("iShares-Russell-2000-ETF_fund.csv")["Symbol"]
    nyse = pd.read_csv("nyse-listed.csv")["Symbol"]
    other = pd.read_csv("other-listed.csv")["Symbol"]

    tickers = pd.concat([sp500, russell, nyse, other]).drop_duplicates().tolist()
    # keep only strings with alphabetic symbols
    tickers = [t for t in tickers if isinstance(t, str) and t.isalpha()]
    return tickers

tickers = load_tickers()
print(f"✅ Total tickers loaded: {len(tickers)}")

# ========================
# HELPERS
# ========================
def to_float_safe(x):
    try:
        return float(x)
    except:
        return None

def last(series):
    """Get last value safely using iloc"""
    return series.iloc[-1]

# ========================
# FETCH FUNDAMENTALS (BATCH)
# ========================
def fetch_pe_batch(symbols):
    """Fetch P/E, sector P/E, and debt/equity for a batch of symbols."""
    results = {}
    tickers_obj = yf.Tickers(" ".join(symbols))

    for s in symbols:
        try:
            info = tickers_obj.tickers[s].get_info()
            pe = to_float_safe(info.get("trailingPE"))
            sector_pe = to_float_safe(info.get("sectorTrailingPE"))
            de_ratio = to_float_safe(info.get("debtToEquity"))
            results[s] = (pe, sector_pe, de_ratio)
        except:
            results[s] = (None, None, None)
    return results

# ========================
# SCREEN SINGLE STOCK
# ========================
def screen(symbol, fundamentals, market_pe):
    pe, sector_pe, de_ratio = fundamentals

    # Basic filters
    if pe is None or de_ratio is None or de_ratio >= 1.0:
        return None

    try:
        ticker = yf.Ticker(symbol)

        # EPS growth check --------------------------
        income = ticker.income_stmt
        if "Diluted EPS" not in income.index: 
            return None
        eps_vals = income.loc["Diluted EPS"].iloc[:3].tolist()
        if len(eps_vals) != 3 or not (eps_vals[0] > eps_vals[1] > eps_vals[2]):
            return None

        # Technical filters --------------------------
        hist = ticker.history(period="60d")
        if hist.empty or len(hist) < 20: 
            return None

        price = ticker.fast_info.get("lastPrice")
        high_20 = hist["Close"].iloc[-20:].max()
        sma_50 = hist["Close"].iloc[-50:].mean()
        vol_20 = hist["Volume"].iloc[-20:].mean()
        vol_now = last(hist["Volume"])

        # Entry filter
        if not (price >= high_20 and price > sma_50 and vol_now > vol_20):
            return None

        # Valuation logic
        if (sector_pe and pe < sector_pe and pe < market_pe) or (pe < market_pe):
            return {
                "Stock": symbol,
                "Price": price,
                "P/E": pe,
                "Sector Avg P/E": sector_pe if sector_pe else "N/A",
                "EPS Positive Growth 3Y": True,
                "Debt/Equity": de_ratio,
            }

    except:
        return None

    return None

# ========================
# MAIN EXECUTION
# ========================
print("\n⏳ Fetching fundamentals (batched)…")

# Split into chunks to avoid throttling
chunks = [tickers[i:i+100] for i in range(0, len(tickers), 100)]
fundamentals = {}

for chunk in tqdm(chunks, desc="Batch download"):
    fundamentals.update(fetch_pe_batch(chunk))
    time.sleep(YF_SLOWDOWN)

# Market average P/E
pe_values = [v[0] for v in fundamentals.values() if v[0] is not None]
market_pe = sum(pe_values) / len(pe_values)
print(f"📊 Market-wide Avg P/E: {market_pe:.2f}")

# Screen stocks using threads
results = []
print("\n🔎 Screening stocks…")
with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    futures = {executor.submit(screen, symbol, fundamentals[symbol], market_pe): symbol for symbol in tickers}

    for future in tqdm(as_completed(futures), total=len(futures)):
        res = future.result()
        if res:
            results.append(res)

# Export results
timestamp = datetime.now().strftime("%m-%d-%y %H-%M")
df = pd.DataFrame(results)

if df.empty:
    print("\n⚠️ No stocks met criteria.")
else:
    df.sort_values("P/E", inplace=True)
    filename = f"Screened Stocks {timestamp}.xlsx"
    df.to_excel(filename, index=False)
    print(f"\n✅ Exported to: {filename}")

print(f"✨ Done! Total confirmed opportunities: {len(df)}")
