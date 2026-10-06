import random

import pytest

from Execution.fill import Fill
from Portfolio.portfolio import Portfolio


def make_fill(
    symbol="AAPL",
    quantity=50,
    price=100,
    timestamp="2026-01-05",
    commission=0.0
):
    return Fill(
        symbol=symbol,
        quantity=quantity,
        price=price,
        timestamp=timestamp,
        commission=commission
    )


def test_portfolio_initialises():

    portfolio = Portfolio(10_000)

    assert portfolio.initial_cash == 10_000
    assert portfolio.cash == 10_000
    assert portfolio.positions == {}
    assert portfolio.average_entry_price == {}
    assert portfolio.realised_pnl == 0


def test_initial_cash_must_be_numeric():

    with pytest.raises(
        TypeError,
        match="initial_cash must be a number"
    ):
        Portfolio("10000")


def test_initial_cash_must_be_positive():

    with pytest.raises(
        ValueError,
        match="initial_cash must be strictly positive"
    ):
        Portfolio(0)


def test_negative_initial_cash_rejected():

    with pytest.raises(
        ValueError,
        match="initial_cash must be strictly positive"
    ):
        Portfolio(-1)


def test_get_position_when_no_position():

    portfolio = Portfolio(10_000)

    assert portfolio.get_position("AAPL") == 0


def test_buy_fill_updates_position():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(make_fill(quantity=50, price=100))

    assert portfolio.get_position("AAPL") == 50


def test_buy_fill_reduces_cash():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(make_fill(quantity=50, price=100))

    assert portfolio.cash == 5_000


def test_buy_fill_updates_average_entry_price():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(make_fill(quantity=50, price=100))

    assert portfolio.average_entry_price["AAPL"] == 100


def test_cannot_buy_without_enough_cash():

    portfolio = Portfolio(1_000)

    fill = make_fill(quantity=20, price=100)

    with pytest.raises(
        ValueError,
        match="Insufficient cash"
    ):
        portfolio.apply_fill(fill)


def test_multiple_buys_increase_position():

    portfolio = Portfolio(20_000)

    portfolio.apply_fill(make_fill(quantity=50, price=100))
    portfolio.apply_fill(make_fill(quantity=25, price=120))

    assert portfolio.get_position("AAPL") == 75


def test_average_entry_price_after_multiple_buys():

    portfolio = Portfolio(20_000)

    portfolio.apply_fill(make_fill(quantity=50, price=100))
    portfolio.apply_fill(make_fill(quantity=50, price=120))

    assert portfolio.average_entry_price["AAPL"] == 110


def test_average_entry_price_weighted_correctly():

    portfolio = Portfolio(20_000)

    portfolio.apply_fill(make_fill(quantity=20, price=100))
    portfolio.apply_fill(make_fill(quantity=80, price=120))

    assert portfolio.average_entry_price["AAPL"] == 116


def test_multiple_symbols_tracked_independently():

    portfolio = Portfolio(20_000)

    portfolio.apply_fill(
        make_fill(symbol="AAPL", quantity=50, price=100)
    )

    portfolio.apply_fill(
        make_fill(symbol="MSFT", quantity=25, price=200)
    )

    assert portfolio.get_position("AAPL") == 50
    assert portfolio.get_position("MSFT") == 25
    assert portfolio.average_entry_price["AAPL"] == 100
    assert portfolio.average_entry_price["MSFT"] == 200


def test_position_value():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(make_fill(quantity=50, price=100))

    assert portfolio.get_position_value(
        "AAPL",
        120
    ) == 6_000


def test_position_value_zero_for_unheld_symbol():

    portfolio = Portfolio(10_000)

    assert portfolio.get_position_value(
        "AAPL",
        100
    ) == 0


def test_position_value_rejects_zero_price():

    portfolio = Portfolio(10_000)

    with pytest.raises(
        ValueError,
        match="Price must be strictly positive"
    ):
        portfolio.get_position_value("AAPL", 0)


def test_position_value_rejects_negative_price():

    portfolio = Portfolio(10_000)

    with pytest.raises(
        ValueError,
        match="Price must be strictly positive"
    ):
        portfolio.get_position_value("AAPL", -100)


def test_equity_after_buy():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(make_fill(quantity=50, price=100))

    equity = portfolio.get_equity({
        "AAPL": 100
    })

    assert equity == 10_000


def test_equity_increases_when_price_rises():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(make_fill(quantity=50, price=100))

    equity = portfolio.get_equity({
        "AAPL": 120
    })

    assert equity == 11_000


def test_equity_decreases_when_price_falls():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(make_fill(quantity=50, price=100))

    equity = portfolio.get_equity({
        "AAPL": 80
    })

    assert equity == 9_000


def test_equity_with_multiple_symbols():

    portfolio = Portfolio(20_000)

    portfolio.apply_fill(
        make_fill(symbol="AAPL", quantity=50, price=100)
    )

    portfolio.apply_fill(
        make_fill(symbol="MSFT", quantity=25, price=200)
    )

    equity = portfolio.get_equity({
        "AAPL": 120,
        "MSFT": 220
    })

    assert equity == 21_500


def test_equity_requires_price_for_held_symbol():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(make_fill(quantity=50, price=100))

    with pytest.raises(
        ValueError,
        match="No price supplied for AAPL"
    ):
        portfolio.get_equity({})


def test_equity_with_no_positions_equals_cash():

    portfolio = Portfolio(10_000)

    assert portfolio.get_equity({}) == 10_000


def test_unrealised_pnl():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(make_fill(quantity=50, price=100))

    pnl = portfolio.get_unrealised_pnl(
        "AAPL",
        120
    )

    assert pnl == 1_000


def test_unrealised_pnl_can_be_negative():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(make_fill(quantity=50, price=100))

    pnl = portfolio.get_unrealised_pnl(
        "AAPL",
        80
    )

    assert pnl == -1_000


def test_unrealised_pnl_zero_for_unheld_symbol():

    portfolio = Portfolio(10_000)

    assert portfolio.get_unrealised_pnl(
        "AAPL",
        100
    ) == 0


def test_unrealised_pnl_rejects_zero_price():

    portfolio = Portfolio(10_000)

    with pytest.raises(
        ValueError,
        match="Price must be strictly positive"
    ):
        portfolio.get_unrealised_pnl("AAPL", 0)


def test_unrealised_pnl_rejects_negative_price():

    portfolio = Portfolio(10_000)

    with pytest.raises(
        ValueError,
        match="Price must be strictly positive"
    ):
        portfolio.get_unrealised_pnl("AAPL", -100)


def test_sell_fill_increases_cash():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(
        make_fill(quantity=50, price=100)
    )

    portfolio.apply_fill(
        make_fill(quantity=-50, price=120)
    )

    assert portfolio.cash == 11_000


def test_sell_fill_reduces_position():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(
        make_fill(quantity=50, price=100)
    )

    portfolio.apply_fill(
        make_fill(quantity=-20, price=120)
    )

    assert portfolio.get_position("AAPL") == 30


def test_sell_fill_removes_position_when_fully_closed():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(
        make_fill(quantity=50, price=100)
    )

    portfolio.apply_fill(
        make_fill(quantity=-50, price=120)
    )

    assert portfolio.get_position("AAPL") == 0
    assert "AAPL" not in portfolio.positions
    assert "AAPL" not in portfolio.average_entry_price


def test_partial_sell_preserves_average_entry_price():

    portfolio = Portfolio(20_000)

    portfolio.apply_fill(
        make_fill(quantity=100, price=100)
    )

    portfolio.apply_fill(
        make_fill(quantity=-40, price=120)
    )

    assert portfolio.get_position("AAPL") == 60
    assert portfolio.average_entry_price["AAPL"] == 100


def test_cannot_sell_more_than_position():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(
        make_fill(quantity=50, price=100)
    )

    with pytest.raises(
        ValueError,
        match="Cannot sell more shares than currently held"
    ):
        portfolio.apply_fill(
            make_fill(quantity=-51, price=100)
        )


def test_cannot_sell_without_position():

    portfolio = Portfolio(10_000)

    with pytest.raises(
        ValueError,
        match="Cannot sell more shares than currently held"
    ):
        portfolio.apply_fill(
            make_fill(quantity=-1, price=100)
        )


def test_selling_creates_realised_pnl():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(
        make_fill(quantity=50, price=100)
    )

    portfolio.apply_fill(
        make_fill(quantity=-50, price=120)
    )

    assert portfolio.realised_pnl == 1_000


def test_partial_sale_creates_partial_realised_pnl():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(
        make_fill(quantity=50, price=100)
    )

    portfolio.apply_fill(
        make_fill(quantity=-20, price=120)
    )

    assert portfolio.realised_pnl == 400


def test_loss_creates_negative_realised_pnl():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(
        make_fill(quantity=50, price=100)
    )

    portfolio.apply_fill(
        make_fill(quantity=-50, price=80)
    )

    assert portfolio.realised_pnl == -1_000


def test_realised_pnl_accumulates_across_sales():

    portfolio = Portfolio(20_000)

    portfolio.apply_fill(
        make_fill(quantity=100, price=100)
    )

    portfolio.apply_fill(
        make_fill(quantity=-25, price=120)
    )

    portfolio.apply_fill(
        make_fill(quantity=-25, price=110)
    )

    assert portfolio.realised_pnl == 750


def test_reopening_position_resets_average_entry_price():

    portfolio = Portfolio(20_000)

    portfolio.apply_fill(
        make_fill(quantity=50, price=100)
    )

    portfolio.apply_fill(
        make_fill(quantity=-50, price=120)
    )

    portfolio.apply_fill(
        make_fill(quantity=25, price=150)
    )

    assert portfolio.get_position("AAPL") == 25
    assert portfolio.average_entry_price["AAPL"] == 150


def test_reopening_position_does_not_use_old_entry_price():

    portfolio = Portfolio(20_000)

    portfolio.apply_fill(
        make_fill(quantity=50, price=100)
    )

    portfolio.apply_fill(
        make_fill(quantity=-50, price=120)
    )

    portfolio.apply_fill(
        make_fill(quantity=25, price=150)
    )

    portfolio.apply_fill(
        make_fill(quantity=-25, price=140)
    )

    assert portfolio.realised_pnl == 1_000 - 250


def test_buy_commission_reduces_cash():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(
        make_fill(
            quantity=50,
            price=100,
            commission=10.0
        )
    )

    assert portfolio.cash == 4_990


def test_sell_commission_reduces_cash():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(
        make_fill(
            quantity=50,
            price=100,
            commission=0.0
        )
    )

    portfolio.apply_fill(
        make_fill(
            quantity=-50,
            price=120,
            commission=10.0
        )
    )

    assert portfolio.cash == 10_990


def test_commission_does_not_change_position():

    portfolio = Portfolio(10_000)

    portfolio.apply_fill(
        make_fill(
            quantity=50,
            price=100,
            commission=10.0
        )
    )

    assert portfolio.get_position("AAPL") == 50


def test_apply_fill_requires_fill():

    portfolio = Portfolio(10_000)

    with pytest.raises(
        TypeError,
        match="fill must be a Fill"
    ):
        portfolio.apply_fill("not a fill")


def test_zero_quantity_fill_rejected():

    portfolio = Portfolio(10_000)

    fill = make_fill(
        quantity=0,
        price=100
    )

    with pytest.raises(
        ValueError,
        match="Fill quantity cannot be zero"
    ):
        portfolio.apply_fill(fill)


def test_non_positive_fill_price_rejected():

    with pytest.raises(
        ValueError,
        match="Price must be strictly positive"
    ):
        make_fill(
            quantity=50,
            price=0
        )


def test_negative_fill_price_rejected():

    with pytest.raises(
        ValueError,
        match="Price must be strictly positive"
    ):
        make_fill(
            quantity=50,
            price=-100
        )


# ----------------------------------------------------------------------
# Commission accounting, can_afford and cash boundaries
# ----------------------------------------------------------------------


def make_buy(price, quantity=1, commission=0.0):
    return make_fill(quantity=quantity, price=price, timestamp="2020-01-01", commission=commission)


def make_sell(price, quantity=1, commission=0.0):
    return make_fill(quantity=-quantity, price=price, timestamp="2020-01-02", commission=commission)


def test_apply_fill_rejects_price_corrupted_after_creation():
    fill = make_buy(100.0)
    fill.price = 0.0
    with pytest.raises(ValueError, match="Price must be strictly positive"):
        Portfolio(10000).apply_fill(fill)


def test_can_afford_true_when_cost_equals_cash_exactly():
    assert Portfolio(1000).can_afford(make_buy(100.0, quantity=10)) is True


def test_can_afford_false_when_commission_pushes_cost_over_cash():
    assert Portfolio(1000).can_afford(make_buy(100.0, quantity=10, commission=0.01)) is False


def test_can_afford_false_when_price_exceeds_cash():
    assert Portfolio(50).can_afford(make_buy(100.0)) is False


def test_can_afford_always_true_for_sells():
    portfolio = Portfolio(1)
    assert portfolio.can_afford(make_sell(100.0, commission=5.0)) is True


def test_buying_with_exactly_all_cash_leaves_zero_cash():
    portfolio = Portfolio(1000)
    portfolio.apply_fill(make_buy(100.0, quantity=10))
    assert portfolio.cash == pytest.approx(0.0)
    assert portfolio.get_position("AAPL") == 10


def test_buy_commission_is_included_in_average_entry_price():
    portfolio = Portfolio(10000)
    portfolio.apply_fill(make_buy(100.0, quantity=10, commission=10.0))
    assert portfolio.average_entry_price["AAPL"] == pytest.approx(101.0)


def test_sell_commission_is_subtracted_from_realised_pnl():
    portfolio = Portfolio(10000)
    portfolio.apply_fill(make_buy(100.0, quantity=10))
    portfolio.apply_fill(make_sell(110.0, quantity=10, commission=5.0))
    assert portfolio.realised_pnl == pytest.approx(95.0)


def test_round_trip_realised_pnl_equals_cash_change():
    portfolio = Portfolio(10000)
    portfolio.apply_fill(make_buy(100.0, quantity=10, commission=5.0))
    portfolio.apply_fill(make_sell(110.0, quantity=10, commission=5.0))
    assert portfolio.realised_pnl == pytest.approx(portfolio.cash - 10000)


def test_partial_sell_realised_pnl_with_commission():
    portfolio = Portfolio(10000)
    portfolio.apply_fill(make_buy(100.0, quantity=10, commission=10.0))  # avg entry 101
    portfolio.apply_fill(make_sell(111.0, quantity=4, commission=2.0))
    assert portfolio.realised_pnl == pytest.approx(4 * (111 - 101) - 2.0)
    assert portfolio.average_entry_price["AAPL"] == pytest.approx(101.0)


def test_unrealised_pnl_uses_fee_adjusted_entry_price():
    portfolio = Portfolio(10000)
    portfolio.apply_fill(make_buy(100.0, quantity=10, commission=10.0))
    assert portfolio.get_unrealised_pnl("AAPL", 100.0) == pytest.approx(-10.0)


def test_average_entry_price_cleared_when_position_closed():
    portfolio = Portfolio(10000)
    portfolio.apply_fill(make_buy(100.0, quantity=5))
    portfolio.apply_fill(make_sell(105.0, quantity=5))
    assert "AAPL" not in portfolio.average_entry_price
    assert "AAPL" not in portfolio.positions

# ----------------------------------------------------------------------
# Accounting invariant (randomised)
# ----------------------------------------------------------------------


@pytest.mark.parametrize("seed", range(20))
def test_equity_identity_holds_for_random_trading(seed):
    # equity == initial cash + realised P&L + unrealised P&L, always
    rng = random.Random(seed)
    initial = 100000.0
    portfolio = Portfolio(initial)

    for step in range(60):
        price = round(rng.uniform(50, 150), 2)
        commission = round(rng.uniform(0, 5), 2)
        position = portfolio.get_position("AAPL")

        if position == 0 or rng.random() < 0.5:
            quantity = rng.randint(1, 20)
            fill = make_fill(quantity=quantity, price=price, timestamp=f"2020-01-{step % 28 + 1:02d}", commission=commission)
            if portfolio.can_afford(fill):
                portfolio.apply_fill(fill)
        else:
            quantity = rng.randint(1, position)
            portfolio.apply_fill(
                make_fill(quantity=-quantity, price=price, timestamp=f"2020-01-{step % 28 + 1:02d}", commission=commission)
            )

        mark = round(rng.uniform(50, 150), 2)
        equity = portfolio.get_equity({"AAPL": mark})
        unrealised = portfolio.get_unrealised_pnl("AAPL", mark)
        assert equity == pytest.approx(initial + portfolio.realised_pnl + unrealised)
