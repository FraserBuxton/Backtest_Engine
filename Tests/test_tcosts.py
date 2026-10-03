import pytest

from Execution.commission import (
    CommissionModel,
    NoCommission,
    PercentageCommission,
)
from Execution.slippage import (
    NoSlippage,
    PercentageSlippage,
    SlippageModel,
)


def test_no_slippage_buy():

    model = NoSlippage()

    result = model.get_execution_price(
        market_price=100.0,
        quantity=10
    )

    assert result == 100.0


def test_no_slippage_sell():

    model = NoSlippage()

    result = model.get_execution_price(
        market_price=100.0,
        quantity=-10
    )

    assert result == 100.0


def test_no_slippage_zero_quantity():

    model = NoSlippage()

    result = model.get_execution_price(
        market_price=100.0,
        quantity=0
    )

    assert result == 100.0


def test_no_slippage_preserves_different_prices():

    model = NoSlippage()

    assert model.get_execution_price(50.0, 10) == 50.0
    assert model.get_execution_price(250.75, 10) == 250.75
    assert model.get_execution_price(1000.0, -10) == 1000.0


def test_percentage_slippage_initialises():

    model = PercentageSlippage(0.01)

    assert model.rate == 0.01


def test_percentage_slippage_zero_rate_1():

    model = PercentageSlippage(0.0)

    assert model.rate == 0.0


def test_negative_slippage_rate_rejected():

    with pytest.raises(
        ValueError,
        match="Slippage rate must be non-negative"
    ):
        PercentageSlippage(-0.01)


def test_percentage_slippage_buy():

    model = PercentageSlippage(0.01)

    result = model.get_execution_price(
        market_price=100.0,
        quantity=10
    )

    assert result == 101.0


def test_percentage_slippage_sell():

    model = PercentageSlippage(0.01)

    result = model.get_execution_price(
        market_price=100.0,
        quantity=-10
    )

    assert result == 99.0


def test_percentage_slippage_zero_quantity():

    model = PercentageSlippage(0.01)

    result = model.get_execution_price(
        market_price=100.0,
        quantity=0
    )

    assert result == 100.0


def test_percentage_slippage_zero_rate_2():

    model = PercentageSlippage(0.0)

    assert model.get_execution_price(
        100.0,
        10
    ) == 100.0

    assert model.get_execution_price(
        100.0,
        -10
    ) == 100.0


def test_percentage_slippage_scales_with_price():

    model = PercentageSlippage(0.01)

    assert model.get_execution_price(
        200.0,
        10
    ) == 202.0

    assert model.get_execution_price(
        200.0,
        -10
    ) == 198.0


def test_percentage_slippage_scales_with_rate():

    model = PercentageSlippage(0.05)

    assert model.get_execution_price(
        100.0,
        10
    ) == 105.0

    assert model.get_execution_price(
        100.0,
        -10
    ) == 95.0


def test_percentage_slippage_is_symmetric():

    model = PercentageSlippage(0.01)

    buy_price = model.get_execution_price(
        100.0,
        10
    )

    sell_price = model.get_execution_price(
        100.0,
        -10
    )

    assert buy_price == 101.0
    assert sell_price == 99.0

    assert buy_price - 100.0 == 100.0 - sell_price


def test_percentage_slippage_is_independent_of_quantity_size():

    model = PercentageSlippage(0.01)

    buy_small = model.get_execution_price(
        100.0,
        1
    )

    buy_large = model.get_execution_price(
        100.0,
        1000
    )

    sell_small = model.get_execution_price(
        100.0,
        -1
    )

    sell_large = model.get_execution_price(
        100.0,
        -1000
    )

    assert buy_small == buy_large
    assert sell_small == sell_large


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


def test_no_commission_buy():

    model = NoCommission()

    assert model.calculate(
        100.0,
        10
    ) == 0.0


def test_no_commission_sell():

    model = NoCommission()

    assert model.calculate(
        100.0,
        -10
    ) == 0.0


def test_no_commission_zero_quantity():

    model = NoCommission()

    assert model.calculate(
        100.0,
        0
    ) == 0.0


def test_no_commission_is_independent_of_price():

    model = NoCommission()

    assert model.calculate(
        1.0,
        10
    ) == 0.0

    assert model.calculate(
        10000.0,
        -1000
    ) == 0.0


def test_percentage_commission_initialises():

    model = PercentageCommission(0.01)

    assert model.rate == 0.01


def test_percentage_commission_zero_rate_1():

    model = PercentageCommission(0.0)

    assert model.rate == 0.0


def test_negative_commission_rate_rejected():

    with pytest.raises(
        ValueError,
        match="Commission rate must be non-negative"
    ):
        PercentageCommission(-0.01)


def test_percentage_commission_buy():

    model = PercentageCommission(0.01)

    assert model.calculate(
        100.0,
        10
    ) == 10.0


def test_percentage_commission_sell():

    model = PercentageCommission(0.01)

    assert model.calculate(
        100.0,
        -10
    ) == 10.0


def test_percentage_commission_zero_quantity():

    model = PercentageCommission(0.01)

    assert model.calculate(
        100.0,
        0
    ) == 0.0


def test_percentage_commission_zero_rate_2():

    model = PercentageCommission(0.0)

    assert model.calculate(
        100.0,
        10
    ) == 0.0

    assert model.calculate(
        100.0,
        -10
    ) == 0.0


def test_percentage_commission_scales_with_price():

    model = PercentageCommission(0.01)

    assert model.calculate(
        200.0,
        10
    ) == 20.0


def test_percentage_commission_scales_with_quantity():

    model = PercentageCommission(0.01)

    assert model.calculate(
        100.0,
        20
    ) == 20.0

    assert model.calculate(
        100.0,
        50
    ) == 50.0


def test_percentage_commission_scales_with_rate():

    model = PercentageCommission(0.05)

    assert model.calculate(
        100.0,
        10
    ) == 50.0


def test_percentage_commission_uses_absolute_trade_value():

    model = PercentageCommission(0.01)

    buy_commission = model.calculate(
        100.0,
        10
    )

    sell_commission = model.calculate(
        100.0,
        -10
    )

    assert buy_commission == sell_commission


def test_percentage_commission_uses_execution_price():

    model = PercentageCommission(0.01)

    assert model.calculate(
        101.0,
        100
    ) == 101.0


def test_percentage_commission_large_trade():

    model = PercentageCommission(0.01)

    commission = model.calculate(
        500.0,
        1000
    )

    assert commission == 5000.0


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