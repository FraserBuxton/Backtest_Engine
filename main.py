import matplotlib.pyplot as plt
from Data.data_handler import DataHandler
from Engine.backtest import BacktestEngine
from Strategy.strategy import MovingAverageStrategy

# Load Market Data
data_handler = DataHandler('Backtest Engine/AAPL.csv')

# Define Strategy
strategy = MovingAverageStrategy(short_window=30, long_window=50)

# Create Backtest Engine
engine = BacktestEngine(data_handler, strategy, 10000, 'AAPL', 10)

# Run the backtest
results = engine.run()

# Display the Results
print(results)

# Display Final Portfolio State
print(f'\nFinal Cash: {engine.portfolio.cash}')
print(f'Final Position: {engine.portfolio.get_position('AAPL')}')
print(f'Final Equity: {results['Equity'].iloc[-1]}')

# Equity Curve
results["Equity"].plot()

plt.title("AAPL Moving Average Strategy")
plt.xlabel("Date")
plt.ylabel("Portfolio Equity")

plt.show()