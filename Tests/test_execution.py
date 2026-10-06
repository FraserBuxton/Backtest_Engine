import pandas as pd
import pytest

from Execution.commission import (
    CommissionModel,
    NoCommission,
    PercentageCommission,
)
from Execution.execution import ExecutionEngine
from Execution.fill import Fill
from Execution.order import Order
from Execution.slippage import (
    NoSlippage,
    PercentageSlippage,
    SlippageModel,
)


def create_engine(
    slippage_model=None,
    commission_model=None
):
    if slippage_model is None:
        slippage_model = NoSlippage()

    if commission_model is None:
        commission_model = NoCommission()

    return ExecutionEngine(
        slippage_model,
        commission_model
    )


def create_buy_order(
    symbol="AAPL",
    quantity=100
):
    return Order(
        symbol=symbol,
        quantity=quantity,
        side="BUY"
    )


def create_sell_order(
    symbol="AAPL",
    quantity=100
):
    return Order(
        symbol=symbol,
        quantity=quantity,
        side="SELL"
    )


def test_execution_engine_initialises():

    engine = create_engine()

    assert isinstance(engine, ExecutionEngine)
    assert isinstance(engine.slippage_model, NoSlippage)
    assert isinstance(engine.commission_model, NoCommission)


def test_execution_engine_stores_supplied_models():

    slippage = PercentageSlippage(0.01)
    commission = PercentageCommission(0.02)

    engine = create_engine(
        slippage_model=slippage,
        commission_model=commission
    )

    assert engine.slippage_model is slippage
    assert engine.commission_model is commission


def test_buy_order_creates_fill():

    engine = create_engine()
    order = create_buy_order()

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


def test_buy_execution_fills_entire_order():

    engine = create_engine()
    order = create_buy_order(quantity=250)

    fill = engine.execute(
        order,
        100,
        "2026-01-05"
    )

    assert fill.quantity == order.quantity


def test_buy_execution_preserves_symbol():

    engine = create_engine()
    order = create_buy_order(symbol="MSFT")

    fill = engine.execute(
        order,
        200,
        "2026-01-05"
    )

    assert fill.symbol == "MSFT"


def test_buy_execution_converts_price_to_float():

    engine = create_engine()
    order = create_buy_order()

    fill = engine.execute(
        order,
        150,
        "2026-01-05"
    )

    assert isinstance(fill.price, float)
    assert fill.price == 150.0


def test_sell_order_creates_fill():

    engine = create_engine()
    order = create_sell_order(quantity=50)

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


def test_sell_execution_fills_negative_quantity():

    engine = create_engine()
    order = create_sell_order(quantity=100)

    fill = engine.execute(
        order,
        150,
        "2026-01-05"
    )

    assert fill.quantity == -order.quantity


def test_sell_execution_preserves_symbol():

    engine = create_engine()
    order = create_sell_order(symbol="MSFT")

    fill = engine.execute(
        order,
        200,
        "2026-01-05"
    )

    assert fill.symbol == "MSFT"


def test_order_must_be_an_order():

    engine = create_engine()

    with pytest.raises(
        TypeError,
        match="order must be an Order"
    ):
        engine.execute(
            "not an order",
            150,
            "2026-01-05"
        )


def test_none_order_is_rejected():

    engine = create_engine()

    with pytest.raises(
        TypeError,
        match="order must be an Order"
    ):
        engine.execute(
            None,
            150,
            "2026-01-05"
        )


def test_price_must_be_numeric():

    engine = create_engine()
    order = create_buy_order()

    with pytest.raises(
        TypeError,
        match="price must be a number"
    ):
        engine.execute(
            order,
            "150",
            "2026-01-05"
        )


def test_none_price_is_rejected():

    engine = create_engine()
    order = create_buy_order()

    with pytest.raises(
        TypeError,
        match="price must be a number"
    ):
        engine.execute(
            order,
            None,
            "2026-01-05"
        )


def test_price_must_be_positive():

    engine = create_engine()
    order = create_buy_order()

    with pytest.raises(
        ValueError,
        match="price must be strictly positive"
    ):
        engine.execute(
            order,
            0,
            "2026-01-05"
        )


def test_negative_price_is_rejected():

    engine = create_engine()
    order = create_buy_order()

    with pytest.raises(
        ValueError,
        match="price must be strictly positive"
    ):
        engine.execute(
            order,
            -100,
            "2026-01-05"
        )


def test_float_price_is_accepted():

    engine = create_engine()
    order = create_buy_order()

    fill = engine.execute(
        order,
        152.37,
        "2026-01-05"
    )

    assert fill.price == 152.37


def test_execution_preserves_timestamp():

    engine = create_engine()
    order = create_buy_order(quantity=10)

    timestamp = pd.Timestamp("2026-02-10")

    fill = engine.execute(
        order,
        100,
        timestamp
    )

    assert fill.timestamp == timestamp


def test_execution_converts_string_timestamp():

    engine = create_engine()
    order = create_buy_order(quantity=10)

    fill = engine.execute(
        order,
        100,
        "2026-02-10"
    )

    assert fill.timestamp == pd.Timestamp("2026-02-10")


def test_invalid_timestamp_is_rejected():

    engine = create_engine()
    order = create_buy_order(quantity=10)

    with pytest.raises(ValueError):
        engine.execute(
            order,
            100,
            "not-a-date"
        )


def test_no_slippage_preserves_price_for_buy():

    engine = create_engine(
        slippage_model=NoSlippage()
    )

    order = create_buy_order()

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    assert fill.price == 100.0


def test_no_slippage_preserves_price_for_sell():

    engine = create_engine(
        slippage_model=NoSlippage()
    )

    order = create_sell_order()

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    assert fill.price == 100.0


def test_buy_execution_applies_slippage():

    engine = create_engine(
        slippage_model=PercentageSlippage(0.01)
    )

    order = create_buy_order()

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    assert fill.price == 101.0


def test_sell_execution_applies_slippage():

    engine = create_engine(
        slippage_model=PercentageSlippage(0.01)
    )

    order = create_sell_order()

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    assert fill.price == 99.0


def test_buy_slippage_scales_with_market_price():

    engine = create_engine(
        slippage_model=PercentageSlippage(0.02)
    )

    order = create_buy_order()

    fill = engine.execute(
        order,
        250.0,
        "2026-01-05"
    )

    assert fill.price == 255.0


def test_sell_slippage_scales_with_market_price():

    engine = create_engine(
        slippage_model=PercentageSlippage(0.02)
    )

    order = create_sell_order()

    fill = engine.execute(
        order,
        250.0,
        "2026-01-05"
    )

    assert fill.price == 245.0


def test_no_commission_produces_zero_commission():

    engine = create_engine(
        commission_model=NoCommission()
    )

    order = create_buy_order()

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    assert fill.commission == 0.0


def test_no_commission_applies_to_sell():

    engine = create_engine(
        commission_model=NoCommission()
    )

    order = create_sell_order()

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    assert fill.commission == 0.0


def test_buy_execution_applies_commission():

    engine = create_engine(
        commission_model=PercentageCommission(0.01)
    )

    order = create_buy_order(quantity=100)

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    assert fill.commission == 100.0


def test_sell_execution_applies_commission():

    engine = create_engine(
        commission_model=PercentageCommission(0.01)
    )

    order = create_sell_order(quantity=100)

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    assert fill.commission == 100.0


def test_zero_commission_rate_produces_zero_commission():

    engine = create_engine(
        commission_model=PercentageCommission(0.0)
    )

    order = create_buy_order()

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    assert fill.commission == 0.0


def test_buy_execution_applies_slippage_and_commission():

    engine = create_engine(
        slippage_model=PercentageSlippage(0.01),
        commission_model=PercentageCommission(0.01)
    )

    order = create_buy_order(quantity=100)

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    # Execution price:
    # 100 * 1.01 = 101
    assert fill.price == 101.0

    # Commission:
    # 101 * 100 * 0.01 = 101
    assert fill.commission == 101.0


def test_sell_execution_applies_slippage_and_commission():

    engine = create_engine(
        slippage_model=PercentageSlippage(0.01),
        commission_model=PercentageCommission(0.01)
    )

    order = create_sell_order(quantity=100)

    fill = engine.execute(
        order,
        100.0,
        "2026-01-05"
    )

    # Execution price:
    # 100 * 0.99 = 99
    assert fill.price == 99.0

    # Commission:
    # abs(99 * -100) * 0.01 = 99
    assert fill.commission == 99.0


def test_commission_is_based_on_execution_price():

    engine = create_engine(
        slippage_model=PercentageSlippage(0.02),
        commission_model=PercentageCommission(0.01)
    )

    order = create_buy_order(quantity=50)

    fill = engine.execute(
        order,
        200.0,
        "2026-01-05"
    )

    # Execution price:
    # 200 * 1.02 = 204
    assert fill.price == 204.0

    # Commission:
    # 204 * 50 * 0.01 = 102
    assert fill.commission == 102.0


def test_transaction_costs_change_fill_price_and_commission():

    engine = create_engine(
        slippage_model=PercentageSlippage(0.05),
        commission_model=PercentageCommission(0.02)
    )

    order = create_buy_order(quantity=20)

    fill = engine.execute(
        order,
        500.0,
        "2026-01-05"
    )

    # 500 * 1.05 = 525
    assert fill.price == 525.0

    # 525 * 20 * 0.02 = 210
    assert fill.commission == 210.0


def test_base_slippage_model_raises_not_implemented():

    model = SlippageModel()

    with pytest.raises(
        NotImplementedError,
        match="SlippageModel Subclasses"
    ):
        model.get_execution_price(
            100.0,
            10
        )


def test_base_commission_model_raises_not_implemented():

    model = CommissionModel()

    with pytest.raises(
        NotImplementedError,
        match="CommissionModel Subclasses"
    ):
        model.calculate(
            100.0,
            10
        )


# ----------------------------------------------------------------------
# Guard branches
# ----------------------------------------------------------------------


def test_execution_rejects_order_whose_side_was_changed_after_creation():
    order = Order("AAPL", 1, "BUY")
    order.side = "HOLD"
    engine = ExecutionEngine(NoSlippage(), NoCommission())
    with pytest.raises(ValueError, match="Invalid order side"):
        engine.execute(order, 100.0, "2020-01-01")


def test_execution_rejects_slippage_model_returning_non_positive_price():
    class BrokenSlippage(SlippageModel):
        def get_execution_price(self, market_price, quantity):
            return 0.0

    engine = ExecutionEngine(BrokenSlippage(), NoCommission())
    with pytest.raises(ValueError):
        engine.execute(Order("AAPL", 1, "BUY"), 100.0, "2020-01-01")
