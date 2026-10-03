import pandas as pd
import pytest

from Execution.fill import Fill


def test_valid_buy_fill():

    fill = Fill(
        symbol="AAPL",
        quantity=100,
        price=150,
        timestamp="2026-01-05",
        commission=0.0
    )

    assert fill.symbol == "AAPL"
    assert fill.quantity == 100
    assert fill.price == 150.0
    assert fill.timestamp == pd.Timestamp("2026-01-05")
    assert fill.commission == 0.0


def test_valid_sell_fill():

    fill = Fill(
        symbol="AAPL",
        quantity=-100,
        price=150,
        timestamp="2026-01-05",
        commission=0.0
    )

    assert fill.symbol == "AAPL"
    assert fill.quantity == -100
    assert fill.price == 150.0
    assert fill.timestamp == pd.Timestamp("2026-01-05")
    assert fill.commission == 0.0


def test_fill_accepts_zero_commission():

    fill = Fill(
        symbol="AAPL",
        quantity=100,
        price=150,
        timestamp="2026-01-05",
        commission=0
    )

    assert fill.commission == 0.0


def test_fill_accepts_positive_commission():

    fill = Fill(
        symbol="AAPL",
        quantity=100,
        price=150,
        timestamp="2026-01-05",
        commission=25
    )

    assert fill.commission == 25.0


def test_symbol_must_be_string():

    with pytest.raises(
        TypeError,
        match="Symbol must be a string"
    ):
        Fill(
            symbol=123,
            quantity=100,
            price=150,
            timestamp="2026-01-05",
            commission=0.0
        )


def test_symbol_cannot_be_empty():

    with pytest.raises(
        ValueError,
        match="Symbol cannot be empty"
    ):
        Fill(
            symbol="",
            quantity=100,
            price=150,
            timestamp="2026-01-05",
            commission=0.0
        )


def test_symbol_with_multiple_characters_is_accepted():

    fill = Fill(
        symbol="MSFT",
        quantity=10,
        price=200,
        timestamp="2026-01-05",
        commission=0.0
    )

    assert fill.symbol == "MSFT"


def test_quantity_must_be_integer():

    with pytest.raises(
        TypeError,
        match="Quantity must be an integer"
    ):
        Fill(
            symbol="AAPL",
            quantity=100.5,
            price=150,
            timestamp="2026-01-05",
            commission=0.0
        )


def test_quantity_must_not_be_zero():

    fill = Fill(
        symbol="AAPL",
        quantity=0,
        price=150,
        timestamp="2026-01-05",
        commission=0.0
    )

    assert fill.quantity == 0


def test_positive_quantity_is_accepted():

    fill = Fill(
        symbol="AAPL",
        quantity=1,
        price=150,
        timestamp="2026-01-05",
        commission=0.0
    )

    assert fill.quantity == 1


def test_negative_quantity_is_accepted():

    fill = Fill(
        symbol="AAPL",
        quantity=-1,
        price=150,
        timestamp="2026-01-05",
        commission=0.0
    )

    assert fill.quantity == -1


def test_large_positive_quantity_is_accepted():

    fill = Fill(
        symbol="AAPL",
        quantity=1_000_000,
        price=150,
        timestamp="2026-01-05",
        commission=0.0
    )

    assert fill.quantity == 1_000_000


def test_large_negative_quantity_is_accepted():

    fill = Fill(
        symbol="AAPL",
        quantity=-1_000_000,
        price=150,
        timestamp="2026-01-05",
        commission=0.0
    )

    assert fill.quantity == -1_000_000


def test_price_must_be_numeric():

    with pytest.raises(
        TypeError,
        match="Price must be a number"
    ):
        Fill(
            symbol="AAPL",
            quantity=100,
            price="150",
            timestamp="2026-01-05",
            commission=0.0
        )


def test_price_must_be_positive():

    with pytest.raises(
        ValueError,
        match="Price must be strictly positive"
    ):
        Fill(
            symbol="AAPL",
            quantity=100,
            price=0,
            timestamp="2026-01-05",
            commission=0.0
        )


def test_negative_price_is_rejected():

    with pytest.raises(
        ValueError,
        match="Price must be strictly positive"
    ):
        Fill(
            symbol="AAPL",
            quantity=100,
            price=-150,
            timestamp="2026-01-05",
            commission=0.0
        )


def test_integer_price_is_stored_as_float():

    fill = Fill(
        symbol="AAPL",
        quantity=100,
        price=150,
        timestamp="2026-01-05",
        commission=0.0
    )

    assert isinstance(fill.price, float)
    assert fill.price == 150.0


def test_float_price_is_stored_as_float():

    fill = Fill(
        symbol="AAPL",
        quantity=100,
        price=150.75,
        timestamp="2026-01-05",
        commission=0.0
    )

    assert isinstance(fill.price, float)
    assert fill.price == 150.75


def test_small_positive_price_is_accepted():

    fill = Fill(
        symbol="AAPL",
        quantity=1,
        price=0.000001,
        timestamp="2026-01-05",
        commission=0.0
    )

    assert fill.price == 0.000001


def test_fill_timestamp_conversion():

    fill = Fill(
        symbol="AAPL",
        quantity=10,
        price=100,
        timestamp="2026-01-05",
        commission=0.0
    )

    assert isinstance(fill.timestamp, pd.Timestamp)
    assert fill.timestamp == pd.Timestamp("2026-01-05")


def test_fill_accepts_timestamp_object():

    timestamp = pd.Timestamp("2026-01-05")

    fill = Fill(
        symbol="AAPL",
        quantity=10,
        price=100,
        timestamp=timestamp,
        commission=0.0
    )

    assert isinstance(fill.timestamp, pd.Timestamp)
    assert fill.timestamp == timestamp


def test_fill_accepts_datetime_string():

    fill = Fill(
        symbol="AAPL",
        quantity=10,
        price=100,
        timestamp="2026-01-05 14:30:00",
        commission=0.0
    )

    assert fill.timestamp == pd.Timestamp(
        "2026-01-05 14:30:00"
    )


def test_fill_invalid_timestamp():

    with pytest.raises(ValueError):

        Fill(
            symbol="AAPL",
            quantity=10,
            price=100,
            timestamp="not-a-date",
            commission=0.0
        )


def test_commission_must_be_numeric():

    with pytest.raises(
        TypeError,
        match="Commission must be a number"
    ):
        Fill(
            symbol="AAPL",
            quantity=100,
            price=150,
            timestamp="2026-01-05",
            commission="10"
        )


def test_commission_must_be_non_negative():

    with pytest.raises(
        ValueError,
        match="Commission must be non-negative"
    ):
        Fill(
            symbol="AAPL",
            quantity=100,
            price=150,
            timestamp="2026-01-05",
            commission=-10
        )


def test_integer_commission_is_stored_as_float():

    fill = Fill(
        symbol="AAPL",
        quantity=100,
        price=150,
        timestamp="2026-01-05",
        commission=10
    )

    assert isinstance(fill.commission, float)
    assert fill.commission == 10.0


def test_float_commission_is_stored_as_float():

    fill = Fill(
        symbol="AAPL",
        quantity=100,
        price=150,
        timestamp="2026-01-05",
        commission=10.50
    )

    assert isinstance(fill.commission, float)
    assert fill.commission == 10.50


def test_zero_commission_is_accepted():

    fill = Fill(
        symbol="AAPL",
        quantity=100,
        price=150,
        timestamp="2026-01-05",
        commission=0
    )

    assert fill.commission == 0.0


def test_buy_and_sell_fills_are_independent():

    buy_fill = Fill(
        symbol="AAPL",
        quantity=100,
        price=150,
        timestamp="2026-01-05",
        commission=5
    )

    sell_fill = Fill(
        symbol="AAPL",
        quantity=-50,
        price=160,
        timestamp="2026-01-06",
        commission=6
    )

    assert buy_fill.quantity == 100
    assert buy_fill.price == 150.0
    assert buy_fill.commission == 5.0

    assert sell_fill.quantity == -50
    assert sell_fill.price == 160.0
    assert sell_fill.commission == 6.0