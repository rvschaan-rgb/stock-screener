import yfinance as yf

ticker = "AAPL"  # change to any ticker you want

def show_volume(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)

    # Pull last 15 days of trading history
    hist = stock.history(period="15d")

    if hist.empty:
        print(f"No price history for {ticker_symbol}")
        return

    today_volume = hist["Volume"].iloc[-1]
    avg10_volume = hist["Volume"].tail(10).mean()

    print("-" * 50)
    print(f"Ticker: {ticker_symbol}")
    print(f"Today's Volume: {today_volume:,.0f}")
    print(f"10-Day Average Volume: {avg10_volume:,.0f}")
    print("-" * 50)

show_volume(ticker)
