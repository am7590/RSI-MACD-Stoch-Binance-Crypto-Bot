from binance import Client
import pandas as pd
import ta
import numpy as np
import time
from datetime import datetime, timezone

import sheets
from sheets import *


def connect_to_client():
    # API Key, API Private (these are for paper trading on binance testnet)
    client = Client("sWIoOijOOt0TFLucOTcGXDE2vcHEbHFIqNI7mpPHneMm1NP8RNkJUAhIIpbAU5zu",
                    "DeAbORz62c8bLQW1Q7ehpOKTixL7gax8dy7kt33mUgbv0h0deeoYwpkCF0oevGt6")
    return client


# Example usage to find the last 100 1 minute bars for Cardano/USDTether:
# df = get_minute_data("ADAUSDT", "1m", "100")
def get_minute_data(symbol, interval, lookback):
    # Populate dataframe
    client = connect_to_client()
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback + ' min ago UTC'))

    # Edit dataframe appearance
    frame = frame.iloc[:, :6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)

    return frame


# Add K-line, D-line, RSI, and MACD columns to any dataframe
def apply_technical_indicators(df):
    df['%K'] = ta.momentum.stoch(df.High, df.Low, df.Close, window=14, smooth_window=3)

    # D-line is a SMA over the K-line (mean of 3 rolling time steps)
    df['%D'] = df['%K'].rolling(3).mean()
    df['rsi'] = ta.momentum.rsi(df.Close, window=14)
    df['macd'] = ta.trend.macd_diff(df.Close)
    df.dropna(inplace=True)


class Signals:
    # lags is steps back
    def __init__(self, df, lags):
        self.df = df
        self.lags = lags

    def get_trigger(self):
        dfx = pd.DataFrame()
        for i in range(self.lags + 1):
            # Check if %K, %D cross under 20
            mask = (self.df['%K'].shift(i) < 20) & (self.df['%D'].shift(i) < 20)

            # Append to dataframe
            dfx = dfx.append(mask, ignore_index=True)

        # Return sums of vertical rows
        return dfx.sum(axis=0)

    # Are all buying conditions and the trigger fulfilled?
    def decide(self):
        self.df['trigger'] = np.where(self.get_trigger(), 1, 0)

        # Check for 20 =< %K & %D =< 80, RSI > 50, MACD > 0
        self.df['Buy'] = np.where(
            (self.df.trigger) & (self.df['%K'].between(20, 80)) & (self.df['%D'].between(20, 80)) & (
                self.df['%D'].between(20, 80)) & (self.df.rsi > 50) & (self.df.macd > 0), 1, 0)


def get_time():
    now_utc = datetime.now(timezone.utc)
    return now_utc.strftime('%m/%d/%Y %H:%M:%S')


def strategy(pair, qty, open_position=False):
    df = get_minute_data(pair, '1m', '100')
    apply_technical_indicators(df)
    inst = Signals(df, 25)
    inst.decide()

    print(f"" + str(get_time()) + "\tBOT RUNNING: current close price for " + pair + " is " + str(
        df.Close.iloc[-1]))

    # If there is a buying signal in the last row, place an order
    client = connect_to_client()
    if df.Buy.iloc[-1]:
        print(f"\nNew market BUY order for " + str(qty) + " " + pair + "\n")
        aoa = [["BUY", pair, str(qty), str(get_time())]]
        sheets.update_sheet(aoa)
        # order = client.create_order(symbol=pair, side='BUY', type='MARKET', quantity=qty)
        # print(order)

        # Filter out price of the order to find official buying price
        buyprice = float(df.Close.iloc[-1])  # buyprice = float(order['fills'][0]['price'])
        open_position = True

    # Set parameters and close position
    while open_position:
        time.sleep(0.5)  # Avoid excessive requests to API
        df = get_minute_data(pair, '1m', '2')  # grab last 2 minutes of data
        print(f"Current Close: " + str(df.Close.iloc[-1]))
        print(f"Current Target: " + str(buyprice * 1.005))  # 0.5% take profit
        print(f"Current Stop loss is: " + str(buyprice * 0.995) + "\n")  # 0.5% stop loss

        # Check for stop loss
        if df.Close[-1] <= buyprice * 0.995 or df.Close[-1] >= 1.005 * buyprice:
            # Place sell order
            # order = client.create_order(symbol=pair, side='SELL', type='MARKET', quantity=qty)
            # print(order)
            print(f"\n New market SELL order for " + str(qty) + " " + pair + "\n")
            aoa = [["SELL", pair, str(qty), str(get_time())]]
            sheets.update_sheet(aoa)
            break


if __name__ == '__main__':
    # Create a dataframe with price data + technical indicators
    dataframe = get_minute_data("ADAUSDT", "1m", "100")
    apply_technical_indicators(dataframe)
    # print(dataframe)

    # Find buy signals
    inst = Signals(dataframe, 25)
    inst.decide()
    # print(dataframe[dataframe.Buy == 1])

    # Run Strategy to find close price for current trade
    # Does not actually trade anything
    # while True:
    # strategy('ADAUSDT', 50)
    # time.sleep(1)

    sheets.update_sheet()
