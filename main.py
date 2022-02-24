from strategy import *


def run_bot(ticker_pair, timeframe, quantity):
    # Create a dataframe with price data + technical indicators
    dataframe = get_minute_data(ticker_pair, timeframe, "100")
    apply_technical_indicators(dataframe)
    # print(dataframe)

    # Find buy signals
    inst = Signals(dataframe, 25)
    inst.decide()
    # print(dataframe[dataframe.Buy == 1])

    # Run Strategy to find close price for current trade
    # Does not actually trade anything
    while True:
        strategy(ticker_pair, quantity)
        time.sleep(1)


if __name__ == '__main__':
    run_bot("ADAUSDT", "1m", 50)
