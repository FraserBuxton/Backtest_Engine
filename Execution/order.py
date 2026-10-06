

class Order:
    
    def __init__(self, symbol, quantity, side):
        self.symbol = symbol
        self.quantity = quantity
        self.side = side
        
        self.__post_init__()
        
    def __post_init__(self):
        # String Symbol
        if not isinstance(self.symbol, str):
            raise TypeError('symbol must be a string')
        
        # Empty Symbol
        if not self.symbol:
            raise ValueError('symbol cannot be empty')
        
        # Integer quantity
        if not isinstance(self.quantity, int) or isinstance(self.quantity, bool):
            raise TypeError('quantity must be an integer')
        
        # Positive quantity
        if self.quantity <= 0:
            raise ValueError('quantity must be strictly positive')
        
        # String side
        if not isinstance(self.side, str):
            raise TypeError('Side must be a string')
        
        # Buy or Sell Side
        self.side = self.side.upper()
        
        if self.side not in ['BUY', 'SELL']:
            raise ValueError('side must be either BUY or SELL')