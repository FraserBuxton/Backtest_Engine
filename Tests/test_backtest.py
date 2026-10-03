import pandas as pd
import pytest
from Engine.backtest import BacktestEngine
from Strategy.strategy import MovingAverageStrategy


def create_test_data():

    dates = pd.date_range(
        start="2020-01-01",
        periods=6,
        freq="D"
    )

    return pd.DataFrame(
        {
            "Open": [
                100,
                101,
                102,
                110,
                120,
                130
            ],
            "High": [
                101,
                102,
                103,
                111,
                121,
                131
            ],
            "Low": [
                99,
                100,
                101,
                109,
                119,
                129
            ],
            "Close": [
                100,
                101,
                102,
                110,
                120,
                130
            ],
            "Volume": [
                1000,
                1000,
                1000,
                1000,
                1000,
                1000
            ]
        },
        index=dates
    )


class TestDataHandler:

    def __init__(self, data):
        self.data = data

    def get_all(self):
        return self.data.copy()


def test_backtest_initialises():

    data = create_test_data()
    data_handler = TestDataHandler(data)

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=3
    )

    engine = BacktestEngine(
        data_handler=data_handler,
        strategy=strategy,
        initial_cash=10_000,
        symbol="AAPL",
        quantity=10
    )

    assert engine.symbol == "AAPL"
    assert engine.quantity == 10
    assert engine.portfolio.cash == 10_000


def test_quantity_must_be_positive():

    data = create_test_data()
    data_handler = TestDataHandler(data)

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=3
    )

    with pytest.raises(
        ValueError,
        match="quantity must be strictly positive"
    ):
        BacktestEngine(
            data_handler=data_handler,
            strategy=strategy,
            initial_cash=10_000,
            symbol="AAPL",
            quantity=0
        )


def test_backtest_returns_dataframe():

    data = create_test_data()
    data_handler = TestDataHandler(data)

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=3
    )

    engine = BacktestEngine(
        data_handler=data_handler,
        strategy=strategy,
        initial_cash=10_000,
        symbol="AAPL",
        quantity=10
    )

    results = engine.run()

    assert isinstance(results, pd.DataFrame)


def test_backtest_results_have_expected_columns():

    data = create_test_data()
    data_handler = TestDataHandler(data)

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=3
    )

    engine = BacktestEngine(
        data_handler=data_handler,
        strategy=strategy,
        initial_cash=10_000,
        symbol="AAPL",
        quantity=10
    )

    results = engine.run()

    assert list(results.columns) == [
        "Equity",
        "Cash",
        "Position",
        "Signal"
    ]


def test_backtest_results_have_expected_length():

    data = create_test_data()
    data_handler = TestDataHandler(data)

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=3
    )

    engine = BacktestEngine(
        data_handler=data_handler,
        strategy=strategy,
        initial_cash=10_000,
        symbol="AAPL",
        quantity=10
    )

    results = engine.run()

    # Last day cannot generate a trade for the
    # following day because there is no following day.
    assert len(results) == len(data) - 1


def test_backtest_preserves_chronological_order():

    data = create_test_data()
    data_handler = TestDataHandler(data)

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=3
    )

    engine = BacktestEngine(
        data_handler=data_handler,
        strategy=strategy,
        initial_cash=10_000,
        symbol="AAPL",
        quantity=10
    )

    results = engine.run()

    assert results.index.is_monotonic_increasing


def test_backtest_does_not_use_future_data():

    data = create_test_data()
    data_handler = TestDataHandler(data)

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=3
    )

    engine = BacktestEngine(
        data_handler=data_handler,
        strategy=strategy,
        initial_cash=10_000,
        symbol="AAPL",
        quantity=10
    )

    results_1 = engine.run()

    # Change a future observation
    modified_data = data.copy()
    modified_data.iloc[-1, modified_data.columns.get_loc("Close")] = 10_000

    modified_handler = TestDataHandler(modified_data)

    engine_2 = BacktestEngine(
        data_handler=modified_handler,
        strategy=MovingAverageStrategy(
            short_window=2,
            long_window=3
        ),
        initial_cash=10_000,
        symbol="AAPL",
        quantity=10
    )

    results_2 = engine_2.run()

    # Earlier results should not depend on the final
    # observation that was not yet available.
    assert results_1.iloc[:-1]["Signal"].equals(
        results_2.iloc[:-1]["Signal"]
    )