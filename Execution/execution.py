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
        
        # Fill Quantity
        if order.side == 'BUY':
            fill_quantity = order.quantity
        elif order.side == 'SELL':
            fill_quantity = -order.quantity
        else:
            raise ValueError('Invalid order side')
        
        return Fill(order.symbol, fill_quantity, price, timestamp)