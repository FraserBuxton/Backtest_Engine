import pandas as pd

from Execution.execution import ExecutionEngine
from Execution.order import Order
from Portfolio.portfolio import Portfolio


class BacktestEngine:
    
    def __init__(self, data_handler, strategy, initial_cash, symbol, quantity):
        
        # Positive quantity
        if quantity <= 0:
            raise ValueError('quantity must be strictly positive')
        
        self.data_handler = data_handler
        self.strategy = strategy
        self.execution_engine = ExecutionEngine()
        self.portfolio = Portfolio(initial_cash)
        self.symbol = symbol
        self.quantity = quantity
        self.results = None
        
    def run(self):
        data = self.data_handler.get_all()
        results = []
        
        
        for i in range(len(data) - 1):
            # current_date = data.index[i]
            next_date = data.index[i+1]
            
            # Data available at current close
            available_data = data.iloc[:i + 1]
            
            # Generate signal
            signal = self.strategy.generate_signal(available_data)
            
            current_position = self.portfolio.get_position(self.symbol)
            
            # Create order
            order = None
            
            # Buy order
            if signal == 1 and current_position == 0:
                order = Order(self.symbol, self.quantity, side='BUY')
            
            # Sell order
            elif signal == 0 and current_position > 0:
                order = Order(self.symbol, current_position, 'SELL')
                
            # Execute order at next days open
            if order is not None:
                
                execution_price = float(data.iloc[i+1]['Open'])
                
                fill = self.execution_engine.execute(order, execution_price)

                self.portfolio.apply_fill(fill)
                
            prices = {self.symbol: data.iloc[i+1]['Close']}
            
            equity = self.portfolio.get_equity(prices)
            
            results.append({
                'Date': next_date,
                'Equity': equity,
                'Cash': self.portfolio.cash,
                'Position': self.portfolio.get_position(self.symbol),
                'Signal': signal
            })
        
        # Format Results
        self.results = pd.DataFrame(results)
        self.results = self.results.set_index('Date')
        
        return self.results