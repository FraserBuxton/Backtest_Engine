import pandas as pd
import pytest

from Engine.backtest import BacktestEngine
from Execution.commission import NoCommission
from Execution.slippage import NoSlippage
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


class DummyDataHandler:

    def __init__(self, data):
        self.data = data

    def get_all(self):
        return self.data.copy()


def test_backtest_initialises():

    data = create_test_data()
    data_handler = DummyDataHandler(data)

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=3
    )

    engine = BacktestEngine(
        data_handler=data_handler,
        strategy=strategy,
        initial_cash=10_000,
        symbol="AAPL",
        quantity=10,
        slippage_model=NoSlippage(),
        commission_model=NoCommission()
    )

    assert engine.symbol == "AAPL"
    assert engine.quantity == 10
    assert engine.portfolio.cash == 10_000


def test_quantity_must_be_positive():

    data = create_test_data()
    data_handler = DummyDataHandler(data)

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
            quantity=0,
            slippage_model=NoSlippage(),
            commission_model=NoCommission()
        )


def test_backtest_returns_dataframe():

    data = create_test_data()
    data_handler = DummyDataHandler(data)

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=3
    )

    engine = BacktestEngine(
        data_handler=data_handler,
        strategy=strategy,
        initial_cash=10_000,
        symbol="AAPL",
        quantity=10,
        slippage_model=NoSlippage(),
        commission_model=NoCommission()
    )

    results = engine.run()

    assert isinstance(results, pd.DataFrame)


def test_backtest_results_have_expected_columns():

    data = create_test_data()
    data_handler = DummyDataHandler(data)

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=3
    )

    engine = BacktestEngine(
        data_handler=data_handler,
        strategy=strategy,
        initial_cash=10_000,
        symbol="AAPL",
        quantity=10,
        slippage_model=NoSlippage(),
        commission_model=NoCommission()
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
    data_handler = DummyDataHandler(data)

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=3
    )

    engine = BacktestEngine(
        data_handler=data_handler,
        strategy=strategy,
        initial_cash=10_000,
        symbol="AAPL",
        quantity=10,
        slippage_model=NoSlippage(),
        commission_model=NoCommission()
    )

    results = engine.run()

    assert len(results) == len(data) - 1


def test_backtest_preserves_chronological_order():

    data = create_test_data()
    data_handler = DummyDataHandler(data)

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=3
    )

    engine = BacktestEngine(
        data_handler=data_handler,
        strategy=strategy,
        initial_cash=10_000,
        symbol="AAPL",
        quantity=10,
        slippage_model=NoSlippage(),
        commission_model=NoCommission()
    )

    results = engine.run()

    assert results.index.is_monotonic_increasing


def test_backtest_does_not_use_future_data():

    data = create_test_data()
    data_handler = DummyDataHandler(data)

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=3
    )

    engine = BacktestEngine(
        data_handler=data_handler,
        strategy=strategy,
        initial_cash=10_000,
        symbol="AAPL",
        quantity=10,
        slippage_model=NoSlippage(),
        commission_model=NoCommission()
    )

    results_1 = engine.run()

    # Change a future observation
    modified_data = data.copy()
    modified_data.iloc[-1, modified_data.columns.get_loc("Close")] = 10_000

    modified_handler = DummyDataHandler(modified_data)

    engine_2 = BacktestEngine(
        data_handler=modified_handler,
        strategy=MovingAverageStrategy(
            short_window=2,
            long_window=3
        ),
        initial_cash=10_000,
        symbol="AAPL",
        quantity=10,
        slippage_model=NoSlippage(),
        commission_model=NoCommission()
    )

    results_2 = engine_2.run()

    assert results_1.iloc[:-1]["Signal"].equals(
        results_2.iloc[:-1]["Signal"]
    )
    
def test_backtest_fill_has_timestamp():

    data = create_test_data()
    data_handler = DummyDataHandler(data)

    engine = BacktestEngine(
        data_handler=data_handler,
        strategy=MovingAverageStrategy(
            short_window=2,
            long_window=3
        ),
        initial_cash=10_000,
        symbol="AAPL",
        quantity=10,
        slippage_model=NoSlippage(),
        commission_model=NoCommission()
    )

    engine.run()

    for fill in engine.fills:
        assert isinstance(fill.timestamp, pd.Timestamp)


def test_backtest_fill_timestamp_is_execution_date():

    data = create_test_data()
    data_handler = DummyDataHandler(data)

    engine = BacktestEngine(
        data_handler=data_handler,
        strategy=MovingAverageStrategy(
            short_window=2,
            long_window=3
        ),
        initial_cash=10_000,
        symbol="AAPL",
        quantity=10,
        slippage_model=NoSlippage(),
        commission_model=NoCommission()
    )

    engine.run()

    for fill in engine.fills:
        assert fill.timestamp in data.index


def test_backtest_fill_executes_on_next_day():

    data = create_test_data()
    data_handler = DummyDataHandler(data)

    engine = BacktestEngine(
        data_handler=data_handler,
        strategy=MovingAverageStrategy(
            short_window=2,
            long_window=3
        ),
        initial_cash=10_000,
        symbol="AAPL",
        quantity=10,
        slippage_model=NoSlippage(),
        commission_model=NoCommission()
    )

    engine.run()

    for fill in engine.fills:

        execution_date = fill.timestamp
        execution_index = data.index.get_loc(execution_date)

        assert execution_index > 0


def test_backtest_fill_price_matches_execution_date_open():

    data = create_test_data()
    data_handler = DummyDataHandler(data)

    engine = BacktestEngine(
        data_handler=data_handler,
        strategy=MovingAverageStrategy(
            short_window=2,
            long_window=3
        ),
        initial_cash=10_000,
        symbol="AAPL",
        quantity=10,
        slippage_model=NoSlippage(),
        commission_model=NoCommission()
    )

    engine.run()

    for fill in engine.fills:

        expected_price = float(
            data.loc[fill.timestamp, "Open"]
        )

        assert fill.price == expected_price
