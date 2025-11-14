import yfinance as yf
import pandas as pd
import os

# ======================
# Settings
# ======================
symbol = "MO"  # change to any stock you want

# ======================
# Fetch the stock
# ======================
ticker = yf.Ticker(symbol)

# ======================
# Get the income statement
# ======================
income = ticker.income_stmt

# ======================
# Export to Excel
# ======================
filename = os.path.join(f"{symbol}_income_statement.xlsx")
income.to_excel(filename)

print(f"✅ Income statement for {symbol} saved to:\n{filename}")
