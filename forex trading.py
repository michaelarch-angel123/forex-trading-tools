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

def train_model(df, features):
    # Extract the input and output features
    X = features.values
    y = df['return'].shift(-1).values
    # Split the data into training and testing sets
    split_index = int(0.8 * len(df))
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y[:split_index], y[split_index:]
    # Build and optimize the model using xgboost
    model = xgb.XGBRegressor(objective='reg:squarederror')
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], eval_metric='
