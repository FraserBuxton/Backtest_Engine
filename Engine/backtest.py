import pandas as pd

from Execution.execution import ExecutionEngine
from Execution.order import Order
from Portfolio.portfolio import Portfolio


class BacktestEngine:
    
    def __init__(self, data_handler, strategy, initial_cash, symbol, quantity, slippage_model, commission_model):
        
        if not isinstance(quantity, int) or isinstance(quantity, bool):
            raise TypeError('quantity must be an integer')
        
        # Positive quantity
        if quantity <= 0:
            raise ValueError('quantity must be strictly positive')
        
        self.data_handler = data_handler
        self.strategy = strategy
        self.execution_engine = ExecutionEngine(slippage_model, commission_model)
        self.initial_cash = initial_cash
        self.portfolio = Portfolio(initial_cash)
        self.symbol = symbol
        self.quantity = quantity
        self.results = None
        
    def run(self):
        data = self.data_handler.get_all()
        
        if len(data) < 2:
            raise ValueError('data must contain at least two lines')
        
        self.portfolio = Portfolio(self.initial_cash)
        results = []
        self.fills = []
        self.rejected_orders = []
        
        for i in range(len(data) - 1):
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
                
                fill = self.execution_engine.execute(order, execution_price, next_date)

                if self.portfolio.can_afford(fill):
                    self.portfolio.apply_fill(fill)
                    self.fills.append(fill)
                else:
                    self.rejected_orders.append((next_date, order))
                
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