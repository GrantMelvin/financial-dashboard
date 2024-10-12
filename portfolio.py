import robin_stocks.robinhood as r
from dotenv import load_dotenv
from prettytable import PrettyTable
import os
import json

load_dotenv()
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

# Log in to your Robinhood account
r.login(username, password)

# Get your portfolio information
portfolio = r.profiles.load_portfolio_profile()
# Print portfolio value
equity = portfolio['equity']
print(f"Portfolio Value: ${equity}")
# Need:
# quantity            how much of it I own
# average_buy_price   how much I bought it for
positions = r.get_open_stock_positions()
# print(json.dumps(positions, indent=4))

# Gets symbols
tickers = [r.get_symbol_by_url(item["instrument"]) for item in positions]

# Need:
# symbol             what stock it is
# ask_price          how much it is selling for rn
# prev_close(?)      how much it closed for yesterday
quotes = r.get_quotes(tickers)
#print(json.dumps(quotes, indent=4))
# Print each stock position
table = PrettyTable()
table.field_names = ["Stock", "Quantity", "Buy Price", "Total Value"]
profit = float(equity)
for stock in positions:
  name = stock['symbol']
  quantity    = round(float(stock['quantity']), 3)
  buy_price   = round(float(stock['average_buy_price']), 3)
  total_value = round(float(stock['quantity']) * float(stock['average_buy_price']), 3)

  table.add_row([name, quantity, buy_price, total_value])
  profit -= total_value
print(f'Profit: ${round(profit,3)}')
print(table)