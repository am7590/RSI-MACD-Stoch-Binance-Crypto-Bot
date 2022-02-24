from binance import Client
import pandas as pd


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
