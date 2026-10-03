import pytest

from Execution.fill import Fill
from Portfolio.portfolio import Portfolio


def test_portfolio_initialises():

    portfolio = Portfolio(10_000)

    assert portfolio.initial_cash == 10_000
    assert portfolio.cash == 10_000
    assert portfolio.positions == {}
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


def test_get_position_when_no_position():

    portfolio = Portfolio(10_000)

    assert portfolio.get_position("AAPL") == 0


def test_buy_fill_updates_position():

    portfolio = Portfolio(10_000)

    fill = Fill(
        symbol="AAPL",
        quantity=50,
        side="BUY",
        price=100,
        timestamp='2026-01-05'
    )

    portfolio.apply_fill(fill)

    assert portfolio.get_position("AAPL") == 50


def test_buy_fill_reduces_cash():

    portfolio = Portfolio(10_000)

    fill = Fill(
        symbol="AAPL",
        quantity=50,
        side="BUY",
        price=100,
        timestamp='2026-01-05'
    )

    portfolio.apply_fill(fill)

    assert portfolio.cash == 5_000


def test_cannot_buy_without_enough_cash():

    portfolio = Portfolio(1_000)

    fill = Fill(
        symbol="AAPL",
        quantity=20,
        side="BUY",
        price=100,
        timestamp='2026-01-05'
    )

    with pytest.raises(
        ValueError,
        match="Insufficient cash"
    ):
        portfolio.apply_fill(fill)


def test_position_value():

    portfolio = Portfolio(10_000)

    fill = Fill(
        symbol="AAPL",
        quantity=50,
        side="BUY",
        price=100,
        timestamp='2026-01-05'
    )

    portfolio.apply_fill(fill)

    assert portfolio.get_position_value(
        "AAPL",
        120
    ) == 6_000


def test_equity_after_buy():

    portfolio = Portfolio(10_000)

    fill = Fill(
        symbol="AAPL",
        quantity=50,
        side="BUY",
        price=100,
        timestamp='2026-01-05'
    )

    portfolio.apply_fill(fill)

    equity = portfolio.get_equity({
        "AAPL": 100
    })

    assert equity == 10_000


def test_equity_increases_when_price_rises():

    portfolio = Portfolio(10_000)

    fill = Fill(
        symbol="AAPL",
        quantity=50,
        side="BUY",
        price=100,
        timestamp='2026-01-05'
    )

    portfolio.apply_fill(fill)

    equity = portfolio.get_equity({
        "AAPL": 120
    })

    assert equity == 11_000


def test_unrealised_pnl():

    portfolio = Portfolio(10_000)

    fill = Fill(
        symbol="AAPL",
        quantity=50,
        side="BUY",
        price=100,
        timestamp='2026-01-05'
    )

    portfolio.apply_fill(fill)

    pnl = portfolio.get_unrealised_pnl(
        "AAPL",
        120
    )

    assert pnl == 1_000


def test_unrealised_pnl_can_be_negative():

    portfolio = Portfolio(10_000)

    fill = Fill(
        symbol="AAPL",
        quantity=50,
        side="BUY",
        price=100,
        timestamp='2026-01-05'
    )

    portfolio.apply_fill(fill)

    pnl = portfolio.get_unrealised_pnl(
        "AAPL",
        80
    )

    assert pnl == -1_000


def test_sell_fill_increases_cash():

    portfolio = Portfolio(10_000)

    buy = Fill(
        symbol="AAPL",
        quantity=50,
        side="BUY",
        price=100,
        timestamp='2026-01-05'
    )

    sell = Fill(
        symbol="AAPL",
        quantity=50,
        side="SELL",
        price=120,
        timestamp='2026-01-05'
    )

    portfolio.apply_fill(buy)
    portfolio.apply_fill(sell)

    assert portfolio.cash == 11_000


def test_sell_fill_removes_position():

    portfolio = Portfolio(10_000)

    buy = Fill(
        symbol="AAPL",
        quantity=50,
        side="BUY",
        price=100,
        timestamp='2026-01-05'
    )

    sell = Fill(
        symbol="AAPL",
        quantity=50,
        side="SELL",
        price=120,
        timestamp='2026-01-05'
    )

    portfolio.apply_fill(buy)
    portfolio.apply_fill(sell)

    assert portfolio.get_position("AAPL") == 0


def test_selling_creates_realised_pnl():

    portfolio = Portfolio(10_000)

    buy = Fill(
        symbol="AAPL",
        quantity=50,
        side="BUY",
        price=100,
        timestamp='2026-01-05'
    )

    sell = Fill(
        symbol="AAPL",
        quantity=50,
        side="SELL",
        price=120,
        timestamp='2026-01-05'
    )

    portfolio.apply_fill(buy)
    portfolio.apply_fill(sell)

    assert portfolio.realised_pnl == 1_000


def test_cannot_sell_more_than_position():

    portfolio = Portfolio(10_000)

    buy = Fill(
        symbol="AAPL",
        quantity=50,
        side="BUY",
        price=100,
        timestamp='2026-01-05'
    )

    sell = Fill(
        symbol="AAPL",
        quantity=51,
        side="SELL",
        price=100,
        timestamp='2026-01-05'
    )

    portfolio.apply_fill(buy)

    with pytest.raises(
        ValueError,
        match="Cannot sell more shares"
    ):
        portfolio.apply_fill(sell)


def test_average_entry_price_after_multiple_buys():

    portfolio = Portfolio(20_000)

    first_buy = Fill(
        symbol="AAPL",
        quantity=50,
        side="BUY",
        price=100,
        timestamp='2026-01-05'
    )

    second_buy = Fill(
        symbol="AAPL",
        quantity=50,
        side="BUY",
        price=120,
        timestamp='2026-01-05'
    )

    portfolio.apply_fill(first_buy)
    portfolio.apply_fill(second_buy)

    assert portfolio.average_entry_price["AAPL"] == 110


def test_apply_fill_requires_fill():

    portfolio = Portfolio(10_000)

    with pytest.raises(
        TypeError,
        match="fill must be a Fill"
    ):
        portfolio.apply_fill("not a fill")
