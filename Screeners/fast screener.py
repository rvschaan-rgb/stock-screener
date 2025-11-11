import pandas as pd
import asyncio
import aiohttp
import yfinance as yf
from datetime import datetime
from tqdm.asyncio import tqdm
import os

# ========================
# CONFIGURATION
# ========================
MAX_CONCURRENT = 50           # max concurrent async requests
BATCH_SIZE = 100              # batch size for fundamentals
YF_SLOWDOWN = 0.05            # optional delay between batches

# ========================
# LOAD TICKERS
# ========================
def load_tickers():
    sp500 = pd.read_csv("sp500_companies.csv")["Symbol"]
    russell = pd.read_csv("iShares-Russell-2000-ETF_fund.csv")["Symbol"]
    nyse = pd.read_csv("nyse-listed.csv")["Symbol"]
    other = pd.read_csv("other-listed.csv")["Symbol"]

    tickers = pd.concat([sp500, russell, nyse, other]).drop_duplicates().tolist()
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
    return series.iloc[-1]

# ========================
# ASYNC FETCH FUNDAMENTALS
# ========================
async def fetch_pe_batch(symbols):
    """Fetch P/E, sector P/E, and debt/equity asynchronously."""
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
# ASYNC SCREEN SINGLE STOCK
# ========================
async def screen(symbol, fundamentals, market_pe):
    pe, sector_pe, de_ratio = fundamentals

    if pe is None or de_ratio is None or de_ratio >= 1.0:
        return None

    try:
        ticker = yf.Ticker(symbol)

        # EPS growth
        income = ticker.income_stmt
        if "Diluted EPS" not in income.index: 
            return None
        eps_vals = income.loc["Diluted EPS"].iloc[:3].tolist()
        if len(eps_vals) != 3 or not (eps_vals[0] > eps_vals[1] > eps_vals[2]):
            return None

        # Technicals
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
# ASYNC EXECUTION WRAPPER
# ========================
async def main():
    # Fetch fundamentals in batches
    fundamentals = {}
    chunks = [tickers[i:i+BATCH_SIZE] for i in range(0, len(tickers), BATCH_SIZE)]
    for chunk in tqdm(chunks, desc="Batch fundamentals"):
        batch_res = await fetch_pe_batch(chunk)
        fundamentals.update(batch_res)
        await asyncio.sleep(YF_SLOWDOWN)

    # Market average P/E
    pe_values = [v[0] for v in fundamentals.values() if v[0] is not None]
    market_pe = sum(pe_values) / len(pe_values)
    print(f"📊 Market-wide Avg P/E: {market_pe:.2f}")

    # Screen all stocks concurrently
    results = []
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def sem_screen(symbol):
        async with semaphore:
            return await screen(symbol, fundamentals[symbol], market_pe)

    tasks = [sem_screen(sym) for sym in tickers]
    for res in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Screening stocks"):
        r = await res
        if r:
            results.append(r)

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

# ========================
# RUN ASYNC
# ========================
if __name__ == "__main__":
    asyncio.run(main())
