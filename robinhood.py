import robin_stocks.robinhood as r
from dotenv import load_dotenv
from prettytable import PrettyTable
import smtplib
from email.message import EmailMessage

import os
import json
import time

def email_alert(positive_change):
  msg = EmailMessage()
  msg['to']   = os.getenv("EMAIL")
  msg['from'] = os.getenv("EMAIL")

  if(positive_change):
    msg.set_content('WE\'RE UP BIG')
    msg['subject'] = 'GOOD'
  else:
    msg.set_content('WE\'RE DOWN BAD')
    msg['subject'] = 'BAD'

  server = smtplib.SMTP("smtp.gmail.com", 587)
  server.starttls()
  server.login(os.getenv("EMAIL"), os.getenv("GMAILPASS"))
  server.send_message(msg)
  server.quit()


def getLastPrice(quotes, stock):
  for item in quotes:
    if item['symbol'] == stock['symbol']:
      return float(item['last_trade_price'])

def show(table, equity, profit):
  print(table)
  print(f"\nPortfolio Value: ${round(equity, 2)}")
  print(f"Profit Value:    ${round(profit, 2)}")

def main():
  load_dotenv()
  username = os.getenv("USERNAME")
  password = os.getenv("PASSWORD")

  # Log in to your Robinhood account
  r.login(username, password)

  equity = 0

  while(1):
    # Get your portfolio information
    old_equity = equity
    portfolio = r.profiles.load_portfolio_profile()
    equity = float(portfolio['equity'])
    profit = equity

    if((old_equity < equity) and (old_equity != 0)):
      email_alert(positive_change=True)
    
    if((old_equity > equity) and (old_equity != 0)):
      email_alert(positive_change=False)

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

    table = PrettyTable()
    table.field_names = ["Stock", "Quantity", "Buy Price", "Total Buy Value", "Total Current Value", "Profit"]
    for stock in positions:
      name                = stock['symbol']
      last_price          = getLastPrice(quotes, stock)

      quantity            = round(float(stock['quantity']), 3)
      buy_price           = round(float(stock['average_buy_price']), 3)
      total_buy_value     = round(float(stock['quantity']) * float(stock['average_buy_price']), 3)
      total_current_value = round(float(stock['quantity']) * last_price, 3)
      profit_per_stock    = round(total_current_value - total_buy_value, 3)

      table.add_row([name, quantity, buy_price, total_buy_value, total_current_value, profit_per_stock])
      profit -= total_buy_value

    show(table, equity, profit)

    # Print every 10min
    time.sleep(60 * 10)

if __name__ == "__main__":
  main()