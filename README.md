# RSI-MACD-Stoch-Binance-Crypto-Bot
Originally from this tutorial: https://www.youtube.com/watch?v=X50-c54BWV8&t=282s

## Strategy Buying Conditions:
- Stochastic (%K and %D) must be between 20 and 80
- MACD diff > 0
- In the last n time steps the %K and %D lines have to cross below 20

## Strategy Selling Conditions
- Stop loss: X amount (99.5%?) of selling price
- Take profit: 1.005 * buying price