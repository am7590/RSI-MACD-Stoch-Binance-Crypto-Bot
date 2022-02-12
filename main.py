import binance
from binance import Client
import pandas as pd
import ta
import numpy as np
import time


def connect_to_client():
    # API Key, API Private
    client = Client("CDbwg0t1i5U8PmfMwhhwPr9EMjj6v2rRpQ88P50mLHEZs5CNNfSCCZJ3KPKfW3Hd",
                    "xFKfmX4IqtGh790vBzmkDb7xwm790EhcBsZMjWa5pllJroJm9e57xH8bBTU8gxHg")
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


if __name__ == '__main__':
    df = get_minute_data("ADAUSDT", "1m", "100")
    apply_technical_indicators(df)
    # print(df)

    inst = Signals(df, 25)
    inst.decide()
    print(df[df.Buy == 1])

