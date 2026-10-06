import matplotlib.pyplot as plt

from Data import DataHandler
from Engine import BacktestEngine
from Execution import PercentageCommission, PercentageSlippage
from Performance import PerformanceAnalyser
from Strategy import MovingAverageStrategy

# Load Market Data
data_handler = DataHandler('AAPL.csv')

# Define Strategy
strategy = MovingAverageStrategy(short_window=30, long_window=50)

# T-Costs
slippage_model = PercentageSlippage(0.0005)
commission_model = PercentageCommission(0.0005)

# Create Backtest Engine
engine = BacktestEngine(data_handler, strategy, 10000, 'AAPL', 10, slippage_model, commission_model)

# Run the backtest
results = engine.run()

# Display the Results
print(results)

# Display Final Portfolio State
print(f'\nFinal Cash: {engine.portfolio.cash}')
print(f'Final Position: {engine.portfolio.get_position("AAPL")}')
print(f'Final Equity: {results["Equity"].iloc[-1]}')

# Equity Curve
results["Equity"].plot()

plt.title("AAPL Moving Average Strategy")
plt.xlabel("Date")
plt.ylabel("Portfolio Equity")

plt.savefig('Equity Curve.png')

# Perfromance Metrics
analyser = PerformanceAnalyser(results, 10000, 252)

print(analyser.summary())