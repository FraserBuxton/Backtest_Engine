

class CommissionModel:
    def calculate(self, price, quantity):
            raise NotImplementedError('CommissionModel Subclasses must implement calculate()')
        
class NoCommission(CommissionModel):
    def calculate(self, price, quantity):
        return 0.0
    
class PercentageCommission(CommissionModel):
    def __init__(self, rate):
        if rate < 0:
            raise ValueError('Commission rate must be non-negative')
        
        self.rate = rate
        
    def calculate(self, price, quantity):
        return abs(price * quantity) * self.rate