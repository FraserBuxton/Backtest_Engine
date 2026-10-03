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
    assert fill.timestamp == pd.Timestamp('2026-01-05')
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
    assert fill.timestamp == pd.Timestamp('2026-01-05')
    assert fill.commission == 0.0


def test_symbol_must_be_string():
    with pytest.raises(TypeError, match="Symbol must be a string"):
        Fill(
            symbol=123,
            quantity=100,
            price=150,
            timestamp="2026-01-05",
            commission=0.0
        )


def test_symbol_cannot_be_empty():
    with pytest.raises(ValueError, match="Symbol cannot be empty"):
        Fill(
            symbol="",
            quantity=100,
            price=150,
            timestamp="2026-01-05",
            commission=0.0
        )


def test_quantity_must_be_integer():
    with pytest.raises(TypeError, match="Quantity must be an integer"):
        Fill(
            symbol="AAPL",
            quantity=100.5,
            price=150,
            timestamp="2026-01-05",
            commission=0.0
        )


def test_price_must_be_numeric():
    with pytest.raises(TypeError, match="Price must be a number"):
        Fill(
            symbol="AAPL",
            quantity=100,
            price="150",
            timestamp="2026-01-05",
            commission=0.0
        )


def test_price_must_be_positive():
    with pytest.raises(ValueError, match="Price must be strictly positive"):
        Fill(
            symbol="AAPL",
            quantity=100,
            price=0,
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
    
def test_fill_timestamp_conversion():
    fill = Fill(
        symbol="AAPL",
        quantity=10,
        price=100,
        timestamp="2026-01-05",
        commission=0.0)
    
    assert isinstance(fill.timestamp, pd.Timestamp)
    
def test_fill_invalid_timestamp():
    with pytest.raises(ValueError):
        Fill(
            symbol="AAPL",
            quantity=10,
            price=100,
            timestamp="not-a-date",
            commission=0.0)
        
        