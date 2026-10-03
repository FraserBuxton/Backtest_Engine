from Execution.fill import Fill
from Execution.order import Order


class ExecutionEngine:
    # Converts Orders into Fills
    
    def execute(self, order, price, timestamp):
        
        # Check than an Order was supplied
        if not isinstance(order, Order):
            raise TypeError('order must be an Order')
        
        # Number price
        if not isinstance(price, (int, float)):
            raise TypeError('price must be a number')
        
        # Positive price
        if price <= 0:
            raise ValueError('price must be strictly positive')
        
        return Fill(order.symbol,order.quantity, order.side, price, timestamp)