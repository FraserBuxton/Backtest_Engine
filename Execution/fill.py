import pandas as pd


class Fill:
    
    def __init__(self, symbol, quantity, price, timestamp):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.timestamp = timestamp
            
        self.__post_init__()
        
    def __post_init__(self):
        
        # String symbol
        if not isinstance(self.symbol, str):
            raise TypeError('Symbol must be a string')
        
        # Empty symbol
        if not self.symbol:
            raise ValueError('Symbol cannot be empty')
        
        # Integer quantity
        if not isinstance(self.quantity, int):
            raise TypeError('Quantity must be an integer')
        
        # Numeric price
        if not isinstance(self.price, (int, float)):
            raise TypeError('Price must be a number')
        
        # Positive price
        if self.price <= 0:
            raise ValueError('Price must be strictly positive')
        
        self.price = float(self.price)
        
        try:
            self.timestamp = pd.Timestamp(self.timestamp)
        except (ValueError, TypeError) as e:
            raise ValueError(f'Invalid timestamp: {self.timestamp}') from e
        
        