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


def get_minute_data(symbol, interval, lookback):
    client = connect_to_client()
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback + ' min ago UTC'))
    frame = frame.iloc[:,:6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)

    return frame


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    df = get_minute_data("ADAUSDT", "1m", "100")
    print(df)

