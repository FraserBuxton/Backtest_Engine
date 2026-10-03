import pandas as pd
import pytest

from Engine.backtest import BacktestEngine
from Execution.commission import NoCommission, PercentageCommission
from Execution.slippage import NoSlippage, PercentageSlippage
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


class SignalStrategy:

    def __init__(self, signals):
        self.signals = signals

    def generate_signal(self, data):

        i = len(data) - 1

        if i < 0 or i >= len(self.signals):
            return 0

        return self.signals[i]


def create_engine(
    data=None,
    strategy=None,
    initial_cash=10_000,
    quantity=10,
    slippage_model=None,
    commission_model=None
):

    if data is None:
        data = create_test_data()

    if strategy is None:
        strategy = MovingAverageStrategy(
            short_window=2,
            long_window=3
        )

    if slippage_model is None:
        slippage_model = NoSlippage()

    if commission_model is None:
        commission_model = NoCommission()

    return BacktestEngine(
        data_handler=DummyDataHandler(data),
        strategy=strategy,
        initial_cash=initial_cash,
        symbol="AAPL",
        quantity=quantity,
        slippage_model=slippage_model,
        commission_model=commission_model
    )


def test_backtest_initialises():

    engine = create_engine()

    assert engine.symbol == "AAPL"
    assert engine.quantity == 10
    assert engine.portfolio.cash == 10_000


def test_quantity_must_be_positive():

    with pytest.raises(
        ValueError,
        match="quantity must be strictly positive"
    ):

        create_engine(quantity=0)


def test_backtest_returns_dataframe():

    engine = create_engine()

    results = engine.run()

    assert isinstance(results, pd.DataFrame)


def test_backtest_results_have_expected_columns():

    engine = create_engine()

    results = engine.run()

    assert list(results.columns) == [
        "Equity",
        "Cash",
        "Position",
        "Signal"
    ]


def test_backtest_results_have_expected_length():

    data = create_test_data()
    engine = create_engine(data=data)

    results = engine.run()

    assert len(results) == len(data) - 1


def test_backtest_preserves_chronological_order():

    engine = create_engine()

    results = engine.run()

    assert results.index.is_monotonic_increasing


def test_backtest_does_not_use_future_data():

    data = create_test_data()

    engine_1 = create_engine(data=data)
    results_1 = engine_1.run()

    modified_data = data.copy()

    modified_data.iloc[
        -1,
        modified_data.columns.get_loc("Close")
    ] = 10_000

    engine_2 = create_engine(data=modified_data)
    results_2 = engine_2.run()

    assert results_1.iloc[:-1]["Signal"].equals(
        results_2.iloc[:-1]["Signal"]
    )


def test_backtest_fill_has_timestamp():

    engine = create_engine()

    engine.run()

    for fill in engine.fills:
        assert isinstance(fill.timestamp, pd.Timestamp)


def test_backtest_fill_timestamp_is_execution_date():

    data = create_test_data()
    engine = create_engine(data=data)

    engine.run()

    for fill in engine.fills:
        assert fill.timestamp in data.index


def test_backtest_fill_executes_on_next_day():

    data = create_test_data()
    engine = create_engine(data=data)

    engine.run()

    for fill in engine.fills:

        execution_date = fill.timestamp
        execution_index = data.index.get_loc(execution_date)

        assert execution_index > 0


def test_backtest_fill_price_matches_execution_date_open():

    data = create_test_data()
    engine = create_engine(data=data)

    engine.run()

    for fill in engine.fills:

        expected_price = float(
            data.loc[fill.timestamp, "Open"]
        )

        assert fill.price == expected_price


def test_backtest_buy_creates_position():

    strategy = SignalStrategy(
        signals=[0, 0, 1, 1, 1, 1]
    )

    engine = create_engine(
        strategy=strategy,
        quantity=10
    )

    results = engine.run()

    assert len(engine.fills) == 1

    fill = engine.fills[0]

    assert fill.quantity == 10
    assert fill.symbol == "AAPL"
    assert fill.price == 110.0

    assert results.iloc[2]["Position"] == 10
    assert results.iloc[3]["Position"] == 10


def test_backtest_does_not_buy_again_while_already_long():

    strategy = SignalStrategy(
        signals=[0, 0, 1, 1, 1, 1]
    )

    engine = create_engine(
        strategy=strategy,
        quantity=10
    )

    engine.run()

    assert len(engine.fills) == 1
    assert engine.fills[0].quantity == 10


def test_backtest_buy_then_sell_lifecycle():

    strategy = SignalStrategy(
        signals=[0, 0, 1, 1, 0, 0]
    )

    engine = create_engine(
        strategy=strategy,
        quantity=10
    )

    results = engine.run()

    assert len(engine.fills) == 2

    buy_fill = engine.fills[0]
    sell_fill = engine.fills[1]

    assert buy_fill.quantity == 10
    assert buy_fill.price == 110.0

    assert sell_fill.quantity == -10
    assert sell_fill.price == 130.0

    assert results.iloc[-1]["Position"] == 0
    assert results.iloc[-1]["Cash"] == 10_200.0


def test_backtest_sell_closes_entire_position():

    strategy = SignalStrategy(
        signals=[0, 0, 1, 1, 0, 0]
    )

    engine = create_engine(
        strategy=strategy,
        quantity=10
    )

    engine.run()

    assert engine.portfolio.get_position("AAPL") == 0


def test_backtest_no_trade_produces_no_fills():

    strategy = SignalStrategy(
        signals=[0, 0, 0, 0, 0, 0]
    )

    engine = create_engine(
        strategy=strategy
    )

    results = engine.run()

    assert engine.fills == []
    assert (results["Position"] == 0).all()
    assert (results["Cash"] == 10_000).all()
    assert (results["Equity"] == 10_000).all()


def test_backtest_commission_reduces_cash():

    strategy = SignalStrategy(
        signals=[0, 0, 1, 1, 1, 1]
    )

    engine = create_engine(
        strategy=strategy,
        quantity=10,
        commission_model=PercentageCommission(0.01)
    )

    results = engine.run()

    fill = engine.fills[0]

    expected_commission = 110.0 * 10 * 0.01
    expected_cash = 10_000 - (110.0 * 10) - expected_commission

    assert fill.commission == expected_commission
    assert results.iloc[2]["Cash"] == expected_cash


def test_backtest_slippage_changes_buy_execution_price():

    strategy = SignalStrategy(
        signals=[0, 0, 1, 1, 1, 1]
    )

    engine = create_engine(
        strategy=strategy,
        quantity=10,
        slippage_model=PercentageSlippage(0.01)
    )

    engine.run()

    fill = engine.fills[0]

    expected_price = 110.0 * 1.01

    assert fill.price == pytest.approx(expected_price)


def test_backtest_slippage_changes_sell_execution_price():

    strategy = SignalStrategy(
        signals=[0, 0, 1, 1, 0, 0]
    )

    engine = create_engine(
        strategy=strategy,
        quantity=10,
        slippage_model=PercentageSlippage(0.01)
    )

    engine.run()

    sell_fill = engine.fills[1]

    expected_price = 130.0 * 0.99

    assert sell_fill.price == pytest.approx(expected_price)


def test_backtest_transaction_costs_affect_final_cash():

    strategy = SignalStrategy(
        signals=[0, 0, 1, 1, 0, 0]
    )

    no_cost_engine = create_engine(
        strategy=strategy,
        quantity=10
    )

    no_cost_results = no_cost_engine.run()

    cost_engine = create_engine(
        strategy=SignalStrategy(
            signals=[0, 0, 1, 1, 0, 0]
        ),
        quantity=10,
        slippage_model=PercentageSlippage(0.01),
        commission_model=PercentageCommission(0.01)
    )

    cost_results = cost_engine.run()

    assert cost_results.iloc[-1]["Cash"] < (
        no_cost_results.iloc[-1]["Cash"]
    )


def test_backtest_buy_fill_has_positive_quantity():

    strategy = SignalStrategy(
        signals=[0, 0, 1, 1, 1, 1]
    )

    engine = create_engine(
        strategy=strategy
    )

    engine.run()

    assert engine.fills[0].quantity > 0


def test_backtest_sell_fill_has_negative_quantity():

    strategy = SignalStrategy(
        signals=[0, 0, 1, 1, 0, 0]
    )

    engine = create_engine(
        strategy=strategy
    )

    engine.run()

    assert engine.fills[1].quantity < 0


def test_backtest_position_matches_portfolio():

    strategy = SignalStrategy(
        signals=[0, 0, 1, 1, 0, 0]
    )

    engine = create_engine(
        strategy=strategy
    )

    results = engine.run()

    for date, row in results.iterrows():

        assert row["Position"] == (
            engine.portfolio.get_position("AAPL")
            if date == results.index[-1]
            else row["Position"]
        )


def test_backtest_equity_equals_cash_plus_position_value():

    data = create_test_data()

    strategy = SignalStrategy(
        signals=[0, 0, 1, 1, 1, 1]
    )

    engine = create_engine(
        data=data,
        strategy=strategy,
        quantity=10
    )

    results = engine.run()

    for date, row in results.iterrows():

        expected_equity = (
            row["Cash"]
            + row["Position"] * data.loc[date, "Close"]
        )

        assert row["Equity"] == pytest.approx(expected_equity)