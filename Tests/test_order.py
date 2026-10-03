
import pytest
from Execution.order import Order


def test_valid_buy_order():

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="BUY"
    )

    assert order.symbol == "AAPL"
    assert order.quantity == 100
    assert order.side == "BUY"


def test_valid_sell_order():

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="SELL"
    )

    assert order.side == "SELL"


def test_side_is_converted_to_uppercase():

    order = Order(
        symbol="AAPL",
        quantity=100,
        side="buy"
    )

    assert order.side == "BUY"


def test_symbol_must_be_string():

    with pytest.raises(
        TypeError,
        match="symbol must be a string"
    ):
        Order(
            symbol=123,
            quantity=100,
            side="BUY"
        )


def test_symbol_cannot_be_empty():

    with pytest.raises(
        ValueError,
        match="symbol cannot be empty"
    ):
        Order(
            symbol="",
            quantity=100,
            side="BUY"
        )


def test_quantity_must_be_integer():

    with pytest.raises(
        TypeError,
        match="quantity must be an integer"
    ):
        Order(
            symbol="AAPL",
            quantity=100.5,
            side="BUY"
        )


def test_quantity_must_be_positive():

    with pytest.raises(
        ValueError,
        match="quantity must be strictly positive"
    ):
        Order(
            symbol="AAPL",
            quantity=0,
            side="BUY"
        )


def test_side_must_be_valid():

    with pytest.raises(
        ValueError,
        match="side must be either BUY or SELL"
    ):
        Order(
            symbol="AAPL",
            quantity=100,
            side="HOLD"
        )