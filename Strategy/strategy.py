import pandas as pd


class Strategy:
    # Base Class for all Strategies
    
    def generate_signal(self, data):
        # Must be implemented
        raise NotImplementedError('Strategy Subclasses must implement generate_signal()')
    
    def generate_all(self, data):
            # Must be implemented
            raise NotImplementedError('Strategy Subclasses must implement generate_all()')
    

class MovingAverageStrategy(Strategy):
    # Simple moving average - Long when short ma is above long ma 
    
    def __init__(self, short_window, long_window):
        
        # Must be integers
        if not isinstance(short_window, int):
            raise TypeError('short_window must be an integer')
        if not isinstance(long_window, int):
                    raise TypeError('long_window must be an integer')
                
        # Must be positive
        if short_window <= 0:
            raise ValueError('short_window must be strictly positive')
        if long_window <= 0:
                    raise ValueError('long_window must be strictly positive')
        
        # Short must be less than long window
        if short_window >= long_window:
            raise ValueError('short_window must be less than long_window')
        
        self.short_window = short_window
        self.long_window = long_window
        
    def generate_signal(self, data):
        # Generates signal for next frequency
        
        # Data not long enough
        if len(data) < self.long_window:
            return 0
        
        # Find moving averages
        close = data['Close']
        short_ma = close.iloc[-self.short_window:].mean()
        long_ma = close.iloc[-self.long_window:].mean()
        
        # Long if short > long
        if short_ma > long_ma:
            return 1
        
        # Flat otherwise
        return 0
        
    def generate_all(self, data):
        # Generate signals for full data
        
        # Moving Averages
        close = data['Close']
        short_ma = close.rolling(self.short_window).mean()
        long_ma = close.rolling(self.long_window).mean()
        
        # Generate Signals
        signals = pd.Series(0, index=data.index, dtype=int)
        signals[short_ma > long_ma] = 1
        
        return signals  