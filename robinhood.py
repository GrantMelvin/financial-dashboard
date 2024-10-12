import robin_stocks.robinhood as r
from dotenv import load_dotenv
from prettytable import PrettyTable
import smtplib
from email.message import EmailMessage

import os
import json
import time

# Sends me whatever message is passed
def processMessage(msg):
  server = smtplib.SMTP("smtp.gmail.com", 587)
  server.starttls()
  server.login(os.getenv("EMAIL"), os.getenv("GMAILPASS"))
  server.send_message(msg)
  server.quit()

# Emails me an alert
def email_alert(positive_change):
  msg = EmailMessage()
  msg['to']   = os.getenv("EMAIL")
  msg['from'] = os.getenv("EMAIL")

  if(positive_change):
    msg['subject'] = 'GOOD'
    msg.set_content('STONKS ARE UP')
  else:
    msg['subject'] = 'BAD'
    msg.set_content('STONKS ARE DOWN')

  # Sends the email from the smtp server
  processMessage(msg)

# Gets the last_sold_price from quotes given a stock
def getLastPrice(quotes, stock):
  for item in quotes:
    if item['symbol'] == stock['symbol']:
      return float(item['last_trade_price'])

# Prints the good stuff
def show(table, equity, profit):
  print(table)
  print(f"\nPortfolio Value: ${round(equity, 2)}")
  print(f"Profit Value:    ${round(profit, 2)}")

# Checks to see if there is an increase in portfolio value 
# and sends the appropriate message accordingly
def handleEquity(old, new):
  if((old < new) and (old != 0)):
    email_alert(positive_change=True)

  if((old > new) and (old != 0)):
    email_alert(positive_change=False)

# Checks to see if it is 6am, 12pm, 6pm, or 12am
def validTime():
  if((time.localtime().tm_hour == 6 and time.localtime().tm_min == 0) or
       (time.localtime().tm_hour == 12 and time.localtime().tm_min == 0) or
       (time.localtime().tm_hour == 18 and time.localtime().tm_min == 0) or 
       (time.localtime().tm_hour == 24 and time.localtime().tm_min == 0)):
    return True
  
  return False

def main():
  load_dotenv()
  username = os.getenv("USERNAME")
  password = os.getenv("PASSWORD")

  # Log in to your Robinhood account
  r.login(username, password)

  equity = 0

  while(1):
    # If we want to check every 6 hours
    if(validTime):
      # Current and old portfolio information 
      old_equity = equity
      portfolio = r.profiles.load_portfolio_profile()
      equity = float(portfolio['equity'])

      # Checks new and old equity -> email if changed
      handleEquity(old_equity, equity)

      # Need:
      # quantity            how much of it I own
      # average_buy_price   how much I bought it for
      positions = r.get_open_stock_positions()

      # Gets symbols
      tickers = [r.get_symbol_by_url(item["instrument"]) for item in positions]

      # Need:
      # symbol             what stock it is
      # ask_price          how much it is selling for rn
      # prev_close(?)      how much it closed for yesterday
      quotes = r.get_quotes(tickers)

      # Creates a new table every iteration
      table = PrettyTable()
      table.field_names = ["Stock", "Quantity", "Buy Price", "Total Buy Value", "Total Current Value", "Profit"]
      profit = equity

      # Gathers individual stock info and populates table
      for stock in positions:
        name                = stock['symbol']
        last_price          = getLastPrice(quotes, stock)
        quantity            = round(float(stock['quantity']), 3)
        buy_price           = round(float(stock['average_buy_price']), 3)
        total_buy_value     = round(float(stock['quantity']) * float(stock['average_buy_price']), 3)
        total_current_value = round(float(stock['quantity']) * last_price, 3)
        profit_per_stock    = round(total_current_value - total_buy_value, 3)
        profit              = profit - total_buy_value

        table.add_row([name, quantity, buy_price, total_buy_value, total_current_value, profit_per_stock])

      # Prints table every iteration
      show(table, equity, profit)

      # Skip a minute so that we don't run it twice on the same interval
      time.sleep(60)

    # Skips 6 hours - should work but might not
    time.sleep(60 * 60 * 6)

if __name__ == "__main__":
  main()