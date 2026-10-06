import math


class SlippageModel:
    # Base Class for all Slippage Models
    def get_execution_price(self, market_price, quantity):
        raise NotImplementedError('SlippageModel Subclasses must implement get_market_price()')
    
class NoSlippage(SlippageModel):
    def get_execution_price(self, market_price, quantity):
        return market_price
    
class PercentageSlippage(SlippageModel):
    def __init__(self, rate):
        if not math.isfinite(rate):
            raise ValueError('Slippage rate must be finite')
        
        if rate < 0:
            raise ValueError('Slippage rate must be non-negative')
        
        if rate >= 1:
            raise ValueError('Slippage rate must be less than 1')
        
        self.rate = rate
        
    def get_execution_price(self, market_price, quantity):
        if quantity > 0:
            return market_price * (1 + self.rate)
        
        if quantity < 0:
            return market_price * (1 - self.rate)
        
        return market_price