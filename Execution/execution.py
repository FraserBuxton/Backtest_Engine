from Execution.fill import Fill
from Execution.order import Order


class ExecutionEngine:
    # Converts Orders into Fills
    def __init__(self, slippage_model, commission_model):
        self.slippage_model = slippage_model
        self.commission_model = commission_model
    
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
        
        execution_price = self.slippage_model.get_execution_price(price, fill_quantity)
        commission = self.commission_model.calculate(execution_price, fill_quantity)
        
        return Fill(order.symbol, fill_quantity, execution_price, timestamp, commission)