import pandas as pd
import pytest
from Strategy.strategy import MovingAverageStrategy, Strategy


def create_data(prices):
    """Create a DataFrame containing closing prices."""
    dates = pd.date_range(
        start="2020-01-01",
        periods=len(prices),
        freq="D"
    )

    return pd.DataFrame(
        {"Close": prices},
        index=dates
    )

def test_base_strategy_generate_signal():
    strategy = Strategy()
    data = create_data([100, 101, 102])

    with pytest.raises(
        NotImplementedError,
        match="must implement generate_signal"
    ):
        strategy.generate_signal(data)


def test_base_strategy_generate_all():
    strategy = Strategy()
    data = create_data([100, 101, 102])

    with pytest.raises(
        NotImplementedError,
        match="must implement generate_all"
    ):
        strategy.generate_all(data)


def test_strategy_initialises():
    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=3
    )

    assert strategy.short_window == 2
    assert strategy.long_window == 3


def test_short_window_must_be_integer():
    with pytest.raises(
        TypeError,
        match="short_window must be an integer"
    ):
        MovingAverageStrategy(
            short_window=2.5,
            long_window=5
        )


def test_long_window_must_be_integer():
    with pytest.raises(
        TypeError,
        match="long_window must be an integer"
    ):
        MovingAverageStrategy(
            short_window=2,
            long_window=5.5
        )


def test_short_window_must_be_positive():
    with pytest.raises(
        ValueError,
        match="short_window must be strictly positive"
    ):
        MovingAverageStrategy(
            short_window=0,
            long_window=5
        )


def test_long_window_must_be_positive():
    with pytest.raises(
        ValueError,
        match="long_window must be strictly positive"
    ):
        MovingAverageStrategy(
            short_window=2,
            long_window=0
        )


def test_short_window_must_be_less_than_long_window():
    with pytest.raises(
        ValueError,
        match="short_window must be less than long_window"
    ):
        MovingAverageStrategy(
            short_window=5,
            long_window=5
        )


def test_generate_signal_returns_zero_when_data_too_short():
    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([100, 101, 102])

    signal = strategy.generate_signal(data)

    assert signal == 0


def test_generate_signal_returns_one_when_short_ma_above_long_ma():
    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([
        100,
        100,
        100,
        120
    ])

    signal = strategy.generate_signal(data)

    assert signal == 1


def test_generate_signal_returns_zero_when_short_ma_below_long_ma():
    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([
        120,
        100,
        100,
        100
    ])

    signal = strategy.generate_signal(data)

    assert signal == 0


def test_generate_signal_returns_zero_when_moving_averages_equal():
    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([
        100,
        100,
        100,
        100
    ])

    signal = strategy.generate_signal(data)

    assert signal == 0


def test_generate_all_returns_series():
    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([
        100,
        100,
        100,
        120,
        130
    ])

    signals = strategy.generate_all(data)

    assert isinstance(signals, pd.Series)


def test_generate_all_has_same_index():
    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([
        100,
        100,
        100,
        120,
        130
    ])

    signals = strategy.generate_all(data)

    assert signals.index.equals(data.index)


def test_generate_all_has_same_length():
    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([
        100,
        100,
        100,
        120,
        130
    ])

    signals = strategy.generate_all(data)

    assert len(signals) == len(data)


def test_generate_all_returns_zero_before_long_window():
    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([
        100,
        100,
        100,
        120,
        130
    ])

    signals = strategy.generate_all(data)

    assert signals.iloc[0] == 0
    assert signals.iloc[1] == 0
    assert signals.iloc[2] == 0


def test_generate_all_identifies_long_position():
    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([
        100,
        100,
        100,
        120,
        130
    ])

    signals = strategy.generate_all(data)

    assert signals.iloc[4] == 1


def test_generate_all_identifies_flat_position():
    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([
        120,
        120,
        100,
        100,
        90
    ])

    signals = strategy.generate_all(data)

    assert signals.iloc[4] == 0

def test_generate_signal_only_uses_available_data():
    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([
        100,
        100,
        100,
        120
    ])

    extended_data = create_data([
        100,
        100,
        100,
        120,
        1000
    ])

    signal_1 = strategy.generate_signal(data)

    signal_2 = strategy.generate_signal(
        extended_data.iloc[:4]
    )

    assert signal_1 == signal_2
