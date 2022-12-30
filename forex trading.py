import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import pandas as pd
import numpy as np
import statsmodels.api as sm
import tsfresh
import xgboost as xgb
import pyfolio as pf
import backtrader as bt
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_score, GridSearchCV
import logging
import pickle

# Replace YOUR_API_KEY with your actual API key
API_KEY = 'YOUR_API_KEY'

# Set the base URL for the API
BASE_URL = 'https://api-fxtrade.oanda.com'

# Set the headers for the API request
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_KEY}'
}

def get_historical_data(instrument, start_time, end_time, granularity):
    # Set the parameters for the API request
    params = {
        'instrument': instrument,
        'start': start_time,
        'end': end_time,
        'granularity': granularity
    }
    # Create the API client
    client = oandapyV20.API(access_token=API_KEY)
    # Make the API request to get the historical data
    try:
        r = instruments.InstrumentsCandles(instrument=instrument, params=params)
        client.request(r)
        # Extract the historical data from the response
        df = pd.DataFrame(r.response['candles'])
    except Exception as e:
        print(f'An error occurred while getting the historical data: {e}')
        return None
    # Preprocess the data
    df['time'] = pd.to_datetime(df['time'])
    df = df[['time', 'mid']]
    df.columns = ['date', 'price']
    df['price'] = df['price'].apply(lambda x: x['c'])  # extract the close price from the mid dictionary
    df['volume'] = df['volume'].apply(lambda x: x['o'])  # extract the open interest from the volume dictionary
    df = df.set_index('date')  # set the date column as the index
    df['return'] = df['price'].pct_change()  # calculate the return
    df = df.dropna()  # drop rows with missing values
    return df

def decompose_ts(df):
    # Decompose the time series data into trend, seasonality, and noise
    decomposition = sm.tsa.seasonal_decompose(df['price'], model='additive')
    df['trend'] = decomposition.trend
    df['seasonality'] = decomposition.seasonal
    df['residual'] = decomposition.resid

def extract_features(df):
    # Extract relevant features from the time series data using tsfresh
    extracted_features = tsfresh.extract_features(df, column_id='date')
    return extracted_features

def train_model(df, model, input_features, output_feature, params, cv, cache_dir=None):
    # Set up logging
    logger = logging.getLogger(__name__)

    # Check if the features have already been extracted and cached
    cache_file = f'{cache_dir}/{input_features}_{output_feature}.pkl'
    if cache_dir is not None and os.path.exists(cache_file):
        logger.info(f'Loading features from cache: {cache_file}')
        with open(cache_file, 'rb') as f:
            X, y = pickle.load(f)
    else:
        # Extract the input and output features
        X = df[input_features].values
        y = df[output_feature].values
        # Cache the features
        if cache_dir is not None:
            os.makedirs(cache_dir, exist_ok=True)
            with open(cache_file, 'wb') as f:
                pickle.dump((X, y), f)

    # Use cross-validation to split the data into training and testing sets
    scores = cross_val_score(model, X, y, cv=cv)
    logger.info(f'Cross-validation scores: {scores}')
    logger.info(f'Mean score: {scores.mean():.2f}')
    logger.info(f'Standard deviation: {scores.std():.2f}')
    # Use grid search to tune the model parameters
    grid_search = GridSearchCV(model, params, cv=cv)
    grid_search.fit(X, y)
    logger.info(f'Best params: {grid_search.best_params_}')
    logger.info(f'Best score: {grid_search.best_score_:.2f}')
    # Return the best model found by the grid search
    return grid_search.best_estimator_