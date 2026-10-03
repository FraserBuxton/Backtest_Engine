import pytest

from Execution.commission import NoCommission, PercentageCommission
from Execution.slippage import NoSlippage, PercentageSlippage


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


def test_percentage_slippage_zero_rate():
    model = PercentageSlippage(0.0)

    assert model.get_execution_price(100.0, 10) == 100.0
    assert model.get_execution_price(100.0, -10) == 100.0


def test_percentage_slippage_scales_with_price():
    model = PercentageSlippage(0.01)

    assert model.get_execution_price(200.0, 10) == 202.0
    assert model.get_execution_price(200.0, -10) == 198.0


def test_percentage_slippage_is_symmetric():
    model = PercentageSlippage(0.01)

    buy_price = model.get_execution_price(100.0, 10)
    sell_price = model.get_execution_price(100.0, -10)

    assert buy_price == 101.0
    assert sell_price == 99.0


def test_negative_slippage_rate_rejected():
    with pytest.raises(
        ValueError,
        match="Slippage rate must be non-negative"
    ):
        PercentageSlippage(-0.01)


def test_no_commission_buy():
    model = NoCommission()

    assert model.calculate(100.0, 10) == 0.0


def test_no_commission_sell():
    model = NoCommission()

    assert model.calculate(100.0, -10) == 0.0


def test_no_commission_zero_quantity():
    model = NoCommission()

    assert model.calculate(100.0, 0) == 0.0


def test_percentage_commission_buy():
    model = PercentageCommission(0.01)

    assert model.calculate(100.0, 10) == 10.0


def test_percentage_commission_sell():
    model = PercentageCommission(0.01)

    assert model.calculate(100.0, -10) == 10.0


def test_percentage_commission_zero_quantity():
    model = PercentageCommission(0.01)

    assert model.calculate(100.0, 0) == 0.0


def test_percentage_commission_zero_rate():
    model = PercentageCommission(0.0)

    assert model.calculate(100.0, 10) == 0.0
    assert model.calculate(100.0, -10) == 0.0


def test_percentage_commission_scales_with_price():
    model = PercentageCommission(0.01)

    assert model.calculate(200.0, 10) == 20.0


def test_percentage_commission_uses_absolute_trade_value():
    model = PercentageCommission(0.01)

    buy_commission = model.calculate(100.0, 10)
    sell_commission = model.calculate(100.0, -10)

    assert buy_commission == sell_commission


def test_negative_commission_rate_rejected():
    with pytest.raises(
        ValueError,
        match="Commission rate must be non-negative"
    ):
        PercentageCommission(-0.01)