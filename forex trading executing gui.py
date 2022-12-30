import logging
import pymysql
import requests
import json
from PyQt5 import QtWidgets, QtGui

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load the API key and account ID from a configuration file
with open('config.json') as f:
    config = json.load(f)
API_KEY = config['api_key']
ACCOUNT_ID = config['account_id']

# Set the base URL for the API
BASE_URL = 'https://api-fxpractice.oanda.com'

# Set the headers for the API request
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_KEY}'
}

# Connect to the database
try:
  connection = pymysql.connect(host='localhost', user='user', password='password', db='tick_data')
except Exception as e:
  logging.error(f'Error connecting to database: {e}')
  exit(1)

# Function to get the current price of a currency pair
def get_current_price(instrument):
  # Make the API request to get the current price
  try:
      response = requests.get(f'{BASE_URL}/v3/instruments/{instrument}/candles', headers=headers)
      response.raise_for_status()
  except requests.exceptions.RequestException as e:
      logging.error(f'Error getting current price: {e}')
      return None

  # Parse the response data
  data = response.json()
  current_price = data['candles'][0]['mid']['c']
  return current_price

# Function to calculate the potential profit or loss of a trade
def calculate_profit_loss(instrument, units, order_price, take_profit, stop_loss):
  # Get the current price of the currency pair
  current_price = get_current_price(instrument)
  if current_price is None:
    return None

  # Calculate the profit or loss based on the current price and the specified order price, take profit, and stop loss values
  if take_profit is not None and current_price >= take_profit:
    profit_loss = (take_profit - order_price) * units
  elif stop_loss is not None and current_price <= stop_loss:
    profit_loss = (stop_loss - order_price) * units
  else:
    profit_loss = (current_price - order_price) * units
  return profit_loss

class TradeApplication(QtWidgets.QWidget):
  def __init__(self):
    super().__init__()

    # Set up the UI elements
    self.instrument_label = QtWidgets.QLabel('Instrument:')
    self.instrument_combobox = QtWidgets.QComboBox()
    self.instrument_combobox.addItems(['EUR_USD', 'GBP_USD', 'USD_JPY', 'AUD_USD'])

    self.units_label = QtWidgets.QLabel('Units:')
