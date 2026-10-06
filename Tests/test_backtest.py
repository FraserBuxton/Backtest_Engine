import runpy
from itertools import pairwise
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import pytest

from Data import DataHandler
from Engine.backtest import BacktestEngine
from Execution.commission import NoCommission, PercentageCommission
from Execution.order import Order
from Execution.slippage import NoSlippage, PercentageSlippage
from Performance import PerformanceAnalyser
from Strategy.strategy import MovingAverageStrategy, Strategy


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


# ----------------------------------------------------------------------
# Rejected orders and data-length edge cases
# ----------------------------------------------------------------------


def make_frame(opens):
    index = pd.date_range("2020-01-01", periods=len(opens), freq="D")
    return pd.DataFrame(
        {
            "Open": opens,
            "High": [p + 1 for p in opens],
            "Low": [p - 1 for p in opens],
            "Close": opens,
            "Volume": [1000] * len(opens),
        },
        index=index,
    )


class AlwaysLong(Strategy):
    def generate_signal(self, data):
        return 1


def make_engine(opens, cash=10000, quantity=1, strategy=None):
    return create_engine(
        data=make_frame(opens),
        strategy=strategy or AlwaysLong(),
        initial_cash=cash,
        quantity=quantity,
    )


def test_unaffordable_order_is_rejected_without_crashing():
    engine = make_engine([100, 100, 100, 100], cash=50)
    results = engine.run()
    assert len(results) == 3
    assert len(engine.fills) == 0
    assert len(engine.rejected_orders) > 0
    assert engine.portfolio.get_position("AAPL") == 0


def test_rejected_order_is_recorded_with_date_and_order():
    engine = make_engine([100, 100, 100], cash=50)
    engine.run()
    date, order = engine.rejected_orders[0]
    assert date == pd.Timestamp("2020-01-02")
    assert isinstance(order, Order)
    assert order.side == "BUY"


def test_rejected_buy_is_retried_while_signal_stays_long():
    engine = make_engine([100, 100, 100, 100], cash=50)
    engine.run()
    assert len(engine.rejected_orders) == 3


def test_cash_is_unchanged_when_every_order_is_rejected():
    engine = make_engine([100, 100, 100], cash=50)
    results = engine.run()
    assert (results["Cash"] == 50).all()
    assert (results["Equity"] == 50).all()


def test_order_exactly_affordable_is_accepted():
    engine = make_engine([100, 100, 100], cash=100)
    engine.run()
    assert len(engine.fills) == 1
    assert len(engine.rejected_orders) == 0


def test_rejected_orders_reset_at_start_of_run():
    engine = make_engine([100, 100, 100], cash=50)
    engine.run()
    first = len(engine.rejected_orders)
    engine.run()
    assert len(engine.rejected_orders) == first


def test_two_rows_produce_a_single_result_row():
    results = make_engine([100, 101]).run()
    assert len(results) == 1


def test_final_equity_marks_open_position_to_last_close():
    engine = make_engine([100, 100, 110, 120], cash=1000, quantity=2)
    results = engine.run()
    # Bought 2 at day-2 open (100); last close is 120
    assert results["Equity"].iloc[-1] == pytest.approx(800 + 2 * 120)


def test_last_bars_signal_is_never_traded():
    # Signal flips on the final bar only; there is no next bar to fill on
    class LastBarOnly(Strategy):
        def generate_signal(self, data):
            return 1 if len(data) == 4 else 0

    engine = make_engine([100, 100, 100, 100], strategy=LastBarOnly())
    engine.run()
    assert len(engine.fills) == 0


def test_results_signal_column_records_signal_at_prior_close():
    class FromDay3(Strategy):
        def generate_signal(self, data):
            return 1 if len(data) >= 3 else 0

    results = make_engine([100, 100, 100, 100, 100], strategy=FromDay3()).run()
    assert list(results["Signal"]) == [0, 0, 1, 1]


def test_signal_to_flat_does_nothing_when_already_flat():
    class NeverLong(Strategy):
        def generate_signal(self, data):
            return 0

    engine = make_engine([100, 101, 102, 103], strategy=NeverLong())
    engine.run()
    assert engine.fills == []
    assert engine.rejected_orders == []

# ----------------------------------------------------------------------
# End-to-end: golden master, consistency checks and main.py
# ----------------------------------------------------------------------


ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "AAPL.csv"


@pytest.fixture(scope="module")
def aapl_backtest():
    data_handler = DataHandler(DATA_FILE)
    engine = BacktestEngine(
        data_handler,
        MovingAverageStrategy(30, 50),
        10000,
        "AAPL",
        10,
        PercentageSlippage(0.0005),
        PercentageCommission(0.0005),
    )
    results = engine.run()
    return data_handler, engine, results


# Golden master: if you change the engine, cost models or metrics ON PURPOSE,
# re-run main.py and update these numbers.

def test_golden_number_of_trades(aapl_backtest):
    _, engine, results = aapl_backtest
    assert len(results) == 1692
    assert len(engine.fills) == 39
    assert len(engine.rejected_orders) == 0


def test_golden_first_trades(aapl_backtest):
    _, engine, _ = aapl_backtest
    first = [(str(f.timestamp.date()), f.quantity) for f in engine.fills[:4]]
    assert first == [
        ("2020-05-06", 10),
        ("2020-10-13", -10),
        ("2020-11-10", 10),
        ("2021-03-09", -10),
    ]


def test_golden_final_portfolio(aapl_backtest):
    _, engine, results = aapl_backtest
    assert engine.portfolio.cash == pytest.approx(8400.679990444418)
    assert engine.portfolio.get_position("AAPL") == 10
    assert results["Equity"].iloc[-1] == pytest.approx(11784.679929409262)
    assert engine.portfolio.realised_pnl == pytest.approx(1764.441316079099)


def test_golden_performance_summary(aapl_backtest):
    _, _, results = aapl_backtest
    summary = PerformanceAnalyser(results, 10000, 252).summary()
    assert summary["Total Return"] == pytest.approx(0.17846799294092608)
    assert summary["Annualised Return"] == pytest.approx(0.024759135757033368)
    assert summary["Annualised Volatility"] == pytest.approx(0.03489649457704256)
    assert summary["Sharpe Ratio"] == pytest.approx(0.7183405454480423)
    assert summary["Maximum Drawdown"] == pytest.approx(-0.057471563068234865)
    assert summary["Calmar Ratio"] == pytest.approx(0.43080672310299495)


def test_engine_signals_match_vectorised_signals(aapl_backtest):
    data_handler, _, results = aapl_backtest
    vectorised = MovingAverageStrategy(30, 50).generate_all(data_handler.get_all())
    # Results row i is dated bar i+1 and records the signal from bar i's close
    assert list(results["Signal"]) == list(vectorised.iloc[:-1])


def test_position_follows_signal_with_one_bar_lag(aapl_backtest):
    _, _, results = aapl_backtest
    long_signal = results["Signal"] == 1
    # Position is held whenever the previous bar's signal was long
    # (costs are tiny relative to cash, so every order is affordable)
    assert ((results["Position"] > 0) == long_signal).all()


def test_fills_alternate_between_buys_and_sells(aapl_backtest):
    _, engine, _ = aapl_backtest
    signs = [np.sign(f.quantity) for f in engine.fills]
    assert signs[0] == 1
    assert all(a != b for a, b in pairwise(signs))


def test_every_sell_closes_the_full_position(aapl_backtest):
    _, engine, _ = aapl_backtest
    assert all(abs(f.quantity) == 10 for f in engine.fills)


def test_results_index_is_strictly_increasing(aapl_backtest):
    _, _, results = aapl_backtest
    assert results.index.is_monotonic_increasing
    assert not results.index.has_duplicates


def test_equity_is_cash_plus_position_value_every_day(aapl_backtest):
    data_handler, _, results = aapl_backtest
    closes = data_handler.get_all()["Close"].loc[results.index]
    expected = results["Cash"] + results["Position"] * closes
    assert np.allclose(results["Equity"], expected)


def test_transaction_costs_reduce_final_equity():
    data_handler = DataHandler(DATA_FILE)
    strategy = MovingAverageStrategy(30, 50)

    def run(rate):
        engine = BacktestEngine(
            data_handler,
            strategy,
            10000,
            "AAPL",
            10,
            PercentageSlippage(rate),
            PercentageCommission(rate),
        )
        return engine.run()["Equity"].iloc[-1]

    assert run(0.0) > run(0.0005) > run(0.005)


def test_main_script_runs_end_to_end(monkeypatch, capsys):
    matplotlib.use("Agg")
    monkeypatch.chdir(ROOT)
    runpy.run_path(str(ROOT / "main.py"), run_name="__main__")
    output = capsys.readouterr().out
    assert "Final Equity" in output
    assert "Sharpe Ratio" in output


def test_run_twice_gives_identical_results():
    engine = make_engine([100, 101, 102, 103, 104])
    first = engine.run()
    first_fills = len(engine.fills)
    second = engine.run()
    assert len(engine.fills) == first_fills
    pd.testing.assert_frame_equal(first, second)

def test_single_row_of_data_raises_clear_error():
    with pytest.raises(ValueError, match="at least two"):
        make_engine([100]).run()

def test_float_quantity_rejected_at_construction():
    with pytest.raises(TypeError):
        make_engine([100, 101, 102], quantity=2.5)
