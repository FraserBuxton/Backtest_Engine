import pandas as pd
import pytest

from Execution.commission import NoCommission, PercentageCommission
from Execution.execution import ExecutionEngine
from Execution.fill import Fill
from Execution.order import Order
from Execution.slippage import NoSlippage, PercentageSlippage


def test_execution_engine_initialises():
    engine = ExecutionEngine(
        NoSlippage(),
        NoCommission()
    )

    assert isinstance(engine, ExecutionEngine)


def test_buy_order_creates_fill():
    engine = ExecutionEngine(
        NoSlippage(),
        NoCommission()
    )

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    fill = engine.execute(
        order,
        150,
        "2026-01-05"
    )

    assert isinstance(fill, Fill)
    assert fill.symbol == "AAPL"
    assert fill.quantity == 100
    assert fill.price == 150.0
    assert fill.timestamp == pd.Timestamp("2026-01-05")
    assert fill.commission == 0.0


def test_sell_order_creates_fill():
    engine = ExecutionEngine(
        NoSlippage(),
        NoCommission()
    )

    order = Order(
        symbol="AAPL",
        quantity=50,
        side="SELL"
    )

    fill = engine.execute(
        order,
        150,
        "2026-01-05"
    )

    assert isinstance(fill, Fill)
    assert fill.symbol == "AAPL"
    assert fill.quantity == -50
    assert fill.price == 150.0
    assert fill.timestamp == pd.Timestamp("2026-01-05")
    assert fill.commission == 0.0


def test_order_must_be_an_order():
    engine = ExecutionEngine(
        NoSlippage(),
        NoCommission()
    )

    with pytest.raises(
        TypeError,
        match="order must be an Order"
    ):
        engine.execute(
            "not an order",
            150,
            "2026-01-05"
        )


def test_price_must_be_numeric():
    engine = ExecutionEngine(
        NoSlippage(),
        NoCommission()
    )

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    with pytest.raises(
        TypeError,
        match="price must be a number"
    ):
        engine.execute(
            order,
            "150",
            "2026-01-05"
        )


def test_price_must_be_positive():
    engine = ExecutionEngine(
        NoSlippage(),
        NoCommission()
    )

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    with pytest.raises(
        ValueError,
        match="price must be strictly positive"
    ):
        engine.execute(
            order,
            0,
            "2026-01-05"
        )


def test_execution_fills_entire_order():
    engine = ExecutionEngine(
        NoSlippage(),
        NoCommission()
    )

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    fill = engine.execute(
        order,
        150,
        "2026-01-05"
    )

    assert fill.quantity == order.quantity


def test_sell_execution_fills_negative_quantity():
    engine = ExecutionEngine(
        NoSlippage(),
        NoCommission()
    )

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="SELL"
    )

    fill = engine.execute(
        order,
        150,
        "2026-01-05"
    )

    assert fill.quantity == -order.quantity


def test_execution_price_matches_market_price():
    engine = ExecutionEngine(
        NoSlippage(),
        NoCommission()
    )

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    market_price = 152.37

    fill = engine.execute(
        order,
        market_price,
        "2026-01-05"
    )

    assert fill.price == market_price


def test_execution_preserves_timestamp():
    engine = ExecutionEngine(
        NoSlippage(),
        NoCommission()
    )

    order = Order(
        symbol="AAPL",
        quantity=10,
        side="BUY"
    )

    timestamp = pd.Timestamp("2026-02-10")

    fill = engine.execute(
        order,
        100,
        timestamp
    )

    assert fill.timestamp == timestamp


def test_buy_execution_applies_slippage():
    engine = ExecutionEngine(
        PercentageSlippage(0.01),
        NoCommission()
    )

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    assert fill.price == 101.0


def test_sell_execution_applies_slippage():
    engine = ExecutionEngine(
        PercentageSlippage(0.01),
        NoCommission()
    )

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="SELL"
    )

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    assert fill.price == 99.0


def test_no_slippage_preserves_price_for_buy():
    engine = ExecutionEngine(
        NoSlippage(),
        NoCommission()
    )

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    assert fill.price == 100.0


def test_no_slippage_preserves_price_for_sell():
    engine = ExecutionEngine(
        NoSlippage(),
        NoCommission()
    )

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="SELL"
    )

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    assert fill.price == 100.0


def test_buy_execution_applies_commission():
    engine = ExecutionEngine(
        NoSlippage(),
        PercentageCommission(0.01)
    )

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    assert fill.commission == 100.0


def test_sell_execution_applies_commission():
    engine = ExecutionEngine(
        NoSlippage(),
        PercentageCommission(0.01)
    )

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="SELL"
    )

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    assert fill.commission == 100.0


def test_zero_commission_is_applied_correctly():
    engine = ExecutionEngine(
        NoSlippage(),
        PercentageCommission(0.0)
    )

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    assert fill.commission == 0.0


def test_execution_applies_slippage_and_commission():
    engine = ExecutionEngine(
        PercentageSlippage(0.01),
        PercentageCommission(0.01)
    )

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    # Buy execution price:
    # 100 * 1.01 = 101
    assert fill.price == 101.0

    # Commission is calculated from the
    # actual execution price after slippage:
    # 101 * 100 * 0.01 = 101
    assert fill.commission == 101.0


def test_sell_execution_applies_slippage_and_commission():
    engine = ExecutionEngine(
        PercentageSlippage(0.01),
        PercentageCommission(0.01)
    )

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="SELL"
    )

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    # Sell execution price:
    # 100 * 0.99 = 99
    assert fill.price == 99.0

    # Commission:
    # abs(99 * -100) * 0.01 = 99
    assert fill.commission == 99.0


def test_commission_is_based_on_execution_price():
    engine = ExecutionEngine(
        PercentageSlippage(0.02),
        PercentageCommission(0.01)
    )

    order = Order(
        symbol="AAPL",
        quantity=50,
        side="BUY"
    )

    fill = engine.execute(
        order,
        200.0,
        "2026-01-05"
    )

    # Execution price = 200 * 1.02 = 204
    assert fill.price == 204.0

    # Commission = 204 * 50 * 0.01 = 102
    assert fill.commission == 102.0