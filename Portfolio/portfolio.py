from Execution.fill import Fill


class Portfolio:
    
    def __init__(self, initial_cash):
        
        # Number Cash
        if not isinstance(initial_cash, (int, float)):
            raise TypeError('initial_cash must be a number')
        
        # Positive Initial Cash
        if initial_cash <= 0:
            raise ValueError('initial_cash must be strictly positive')
        
        self.initial_cash = float(initial_cash)
        self.cash = float(initial_cash)
        self.positions = {}
        self.average_entry_price = {}
        self.realised_pnl = 0.0
    
    def get_position(self, symbol):
        return self.positions.get(symbol, 0)
    
    def get_position_value(self, symbol, price):
        # Strictly postitive price
        if price <= 0:
            raise ValueError('Price must be strictly positive')
        
        quantity = self.get_position(symbol)
        return quantity * price
    
    def get_unrealised_pnl(self, symbol, price):
        # Positive current price
        if price <= 0:
            raise ValueError('Price must be strictly positive')
            
        quantity = self.get_position(symbol)
        
        if quantity == 0:
            return 0.0
        
        entry_price = self.average_entry_price[symbol]
        
        return quantity * (price - entry_price)
    
    def get_equity(self, prices):
        equity = self.cash
        
        for symbol in self.positions:
            if symbol not in prices:
                raise ValueError(f'No price supplied for {symbol}')
            
            equity += self.get_position_value(symbol, prices[symbol])
            
        return equity
    
    def apply_fill(self, fill):
        
        if not isinstance(fill, Fill):
            raise TypeError('fill must be a Fill')
        
        price = fill.price
        
        if price <= 0:
            raise ValueError('Price must be strictly positive')
        
        symbol = fill.symbol
        quantity = fill.quantity
        
        current_position = self.get_position(symbol)
        
        if quantity > 0:
            cost = quantity * price
            total_cost = cost + fill.commission
            
            # Cannot afford
            if total_cost > self.cash:
                raise ValueError('Insufficient cash')
            
            if current_position == 0:
                new_average_price = price
            else:
                old_cost = current_position * self.average_entry_price[symbol]
                new_cost = quantity * price
                
                new_average_price = (old_cost + new_cost) / (current_position + quantity)
                
            self.cash -= total_cost
            self.positions[symbol] = current_position + quantity
            self.average_entry_price[symbol] = new_average_price
            
        elif quantity < 0:
            sell_quantity = quantity * -1
            
            # Cannot sell more than held
            if sell_quantity > current_position:
                raise ValueError('Cannot sell more shares than currently held')
            
            entry_price = self.average_entry_price[symbol]
            proceeds = sell_quantity * price
            realised = sell_quantity * (price - entry_price)
            
            self.cash += proceeds
            self.cash -= fill.commission
            self.realised_pnl += realised
            new_position = current_position - sell_quantity
            
            if new_position == 0:
                self.positions.pop(symbol, None)
                self.average_entry_price.pop(symbol)
            else:
                self.positions[symbol] = new_position
                
        else:
            raise ValueError('Fill quantity cannot be zero')
        
    
    
    
        