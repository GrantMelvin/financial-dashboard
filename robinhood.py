import robin_stocks.robinhood as r
from dotenv import load_dotenv
from prettytable import PrettyTable
import os
import json

def getLastPrice(quotes, stock):
  for item in quotes:
    if item['symbol'] == stock['symbol']:
      return float(item['last_trade_price'])

def main():
  load_dotenv()
  username = os.getenv("USERNAME")
  password = os.getenv("PASSWORD")

  # Log in to your Robinhood account
  r.login(username, password)

  # Get your portfolio information
  portfolio = r.profiles.load_portfolio_profile()
  # Print portfolio value
  equity = float(portfolio['equity'])
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
  # print(json.dumps(quotes, indent=4))
  # Print each stock position
  table = PrettyTable()
  table.field_names = ["Stock", "Quantity", "Buy Price", "Total Buy Value", "Total Current Value", "Profit"]
  profit = float(equity)
  for stock in positions:
    last_price = getLastPrice(quotes, stock)
    name = stock['symbol']
    quantity            = round(float(stock['quantity']), 3)
    buy_price           = round(float(stock['average_buy_price']), 3)
    total_buy_value     = round(float(stock['quantity']) * float(stock['average_buy_price']), 3)
    total_current_value = round(float(stock['quantity']) * last_price, 3)
    profit_per_stock    = round(total_current_value - total_buy_value, 3)

    table.add_row([name, quantity, buy_price, total_buy_value, total_current_value, profit_per_stock])
    profit -= total_buy_value
  print(table)
  print(f"\nPortfolio Value: ${round(equity, 2)}")
  print(f"Profit Value:    ${round(profit, 2)}")

if __name__ == "__main__":
  main()