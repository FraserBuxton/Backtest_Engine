import pytest
from Execution.fill import Fill


def test_valid_buy_fill():
    fill = Fill(
        symbol="AAPL",
        quantity=100,
        side="BUY",
        price=150
    )

    assert fill.symbol == "AAPL"
    assert fill.quantity == 100
    assert fill.side == "BUY"
    assert fill.price == 150.0


def test_valid_sell_fill():
    fill = Fill(
        symbol="AAPL",
        quantity=100,
        side="SELL",
        price=150
    )

    assert fill.side == "SELL"


def test_side_is_converted_to_uppercase():
    fill = Fill(
        symbol="AAPL",
        quantity=100,
        side="buy",
        price=150
    )

    assert fill.side == "BUY"


def test_symbol_must_be_string():
    with pytest.raises(TypeError, match="Symbol must be a string"):
        Fill(
            symbol=123,
            quantity=100,
            side="BUY",
            price=150
        )


def test_symbol_cannot_be_empty():
    with pytest.raises(ValueError, match="Symbol cannot be empty"):
        Fill(
            symbol="",
            quantity=100,
            side="BUY",
            price=150
        )


def test_quantity_must_be_integer():
    with pytest.raises(TypeError, match="Quantity must be an integer"):
        Fill(
            symbol="AAPL",
            quantity=100.5,
            side="BUY",
            price=150
        )


def test_quantity_must_be_positive():
    with pytest.raises(ValueError, match="Quantity must be strictly positive"):
        Fill(
            symbol="AAPL",
            quantity=0,
            side="BUY",
            price=150
        )


def test_side_must_be_valid():
    with pytest.raises(
        ValueError,
        match="Side must be either BUY or SELL"
    ):
        Fill(
            symbol="AAPL",
            quantity=100,
            side="HOLD",
            price=150
        )


def test_price_must_be_numeric():
    with pytest.raises(TypeError, match="Price must be a number"):
        Fill(
            symbol="AAPL",
            quantity=100,
            side="BUY",
            price="150"
        )


def test_price_must_be_positive():
    with pytest.raises(ValueError, match="Price must be strictly positive"):
        Fill(
            symbol="AAPL",
            quantity=100,
            side="BUY",
            price=0
        )


def test_integer_price_is_stored_as_float():
    fill = Fill(
        symbol="AAPL",
        quantity=100,
        side="BUY",
        price=150
    )

    assert isinstance(fill.price, float)