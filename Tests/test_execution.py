
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

    fill = engine.execute(order, 150)

    assert isinstance(fill, Fill)
    assert fill.symbol == "AAPL"
    assert fill.quantity == 100
    assert fill.side == "BUY"
    assert fill.price == 150.0


def test_sell_order_creates_fill():
    engine = ExecutionEngine()

    order = Order(
        symbol="AAPL",
        quantity=50,
        side="SELL"
    )

    fill = engine.execute(order, 150)

    assert isinstance(fill, Fill)
    assert fill.symbol == "AAPL"
    assert fill.quantity == 50
    assert fill.side == "SELL"
    assert fill.price == 150.0


def test_order_must_be_an_order():
    engine = ExecutionEngine()

    with pytest.raises(TypeError, match="order must be an Order"):
        engine.execute("not an order", 150)


def test_price_must_be_numeric():
    engine = ExecutionEngine()

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    with pytest.raises(TypeError, match="price must be a number"):
        engine.execute(order, "150")


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
        engine.execute(order, 0)


def test_execution_fills_entire_order():
    engine = ExecutionEngine()

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    fill = engine.execute(order, 150)

    assert fill.quantity == order.quantity


def test_execution_price_matches_market_price():
    engine = ExecutionEngine()

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    market_price = 152.37

    fill = engine.execute(order, market_price)

    assert fill.price == market_price