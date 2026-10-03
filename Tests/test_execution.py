
import pandas as pd
import pytest

from Execution.execution import ExecutionEngine
from Execution.fill import Fill
from Execution.order import Order


def test_execution_engine_initialises():
    engine = ExecutionEngine()

    assert isinstance(engine, ExecutionEngine)


def test_buy_order_creates_fill():
    engine = ExecutionEngine()

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    fill = engine.execute(order, 150, '2026-01-05')

    assert isinstance(fill, Fill)
    assert fill.symbol == "AAPL"
    assert fill.quantity == 100
    assert fill.side == "BUY"
    assert fill.price == 150.0
    assert fill.timestamp == pd.Timestamp('2026-01-05')


def test_sell_order_creates_fill():
    engine = ExecutionEngine()

    order = Order(
        symbol="AAPL",
        quantity=50,
        side="SELL"
    )

    fill = engine.execute(order, 150, '2026-01-05')

    assert isinstance(fill, Fill)
    assert fill.symbol == "AAPL"
    assert fill.quantity == 50
    assert fill.side == "SELL"
    assert fill.price == 150.0
    assert fill.timestamp == pd.Timestamp('2026-01-05')


def test_order_must_be_an_order():
    engine = ExecutionEngine()

    with pytest.raises(TypeError, match="order must be an Order"):
        engine.execute("not an order", 150, '2026-01-05')


def test_price_must_be_numeric():
    engine = ExecutionEngine()

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    with pytest.raises(TypeError, match="price must be a number"):
        engine.execute(order, "150", '2026-01-05')


def test_price_must_be_positive():
    engine = ExecutionEngine()

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    with pytest.raises(
        ValueError,
        match="price must be strictly positive"
    ):
        engine.execute(order, 0, '2026-01-05')


def test_execution_fills_entire_order():
    engine = ExecutionEngine()

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    fill = engine.execute(order, 150, '2026-01-05')

    assert fill.quantity == order.quantity


def test_execution_price_matches_market_price():
    engine = ExecutionEngine()

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    market_price = 152.37

    fill = engine.execute(order, market_price, '2026-01-05')

    assert fill.price == market_price
    
def test_execute_preserves_timestamp():
    engine = ExecutionEngine()
    order = Order(symbol="AAPL", quantity=10, side="BUY")
    timestamp = pd.Timestamp("2026-02-10")
    fill = engine.execute(order, 100, timestamp) 
    assert fill.timestamp == timestamp