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


def test_base_strategy_initialises():

    strategy = Strategy()

    assert isinstance(strategy, Strategy)


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
        long_window=5
    )

    assert isinstance(strategy, MovingAverageStrategy)
    assert strategy.short_window == 2
    assert strategy.long_window == 5


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


def test_negative_short_window_is_rejected():

    with pytest.raises(
        ValueError,
        match="short_window must be strictly positive"
    ):
        MovingAverageStrategy(
            short_window=-1,
            long_window=5
        )


def test_negative_long_window_is_rejected():

    with pytest.raises(
        ValueError,
        match="long_window must be strictly positive"
    ):
        MovingAverageStrategy(
            short_window=2,
            long_window=-1
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


def test_short_window_cannot_exceed_long_window():

    with pytest.raises(
        ValueError,
        match="short_window must be less than long_window"
    ):
        MovingAverageStrategy(
            short_window=6,
            long_window=5
        )


def test_smallest_valid_window_configuration():

    strategy = MovingAverageStrategy(
        short_window=1,
        long_window=2
    )

    assert strategy.short_window == 1
    assert strategy.long_window == 2


def test_generate_signal_returns_zero_when_data_too_short():

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([
        100,
        101,
        102
    ])

    signal = strategy.generate_signal(data)

    assert signal == 0


def test_generate_signal_returns_zero_with_empty_data():

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([])

    signal = strategy.generate_signal(data)

    assert signal == 0


def test_generate_signal_returns_zero_with_exactly_short_window_data():

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([
        100,
        110
    ])

    signal = strategy.generate_signal(data)

    assert signal == 0


def test_generate_signal_returns_zero_with_exactly_long_window_data_if_equal():

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


def test_generate_signal_returns_only_zero_or_one():

    strategy = MovingAverageStrategy(
        short_window=3,
        long_window=5
    )

    data = create_data([
        100,
        105,
        110,
        115,
        120,
        110,
        100,
        90,
        80
    ])

    for i in range(len(data)):
        signal = strategy.generate_signal(data.iloc[:i + 1])

        assert signal in (0, 1)


def test_generate_signal_with_short_window_one():

    strategy = MovingAverageStrategy(
        short_window=1,
        long_window=3
    )

    data = create_data([
        100,
        100,
        120
    ])

    signal = strategy.generate_signal(data)

    assert signal == 1


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


def test_future_price_does_not_affect_current_signal():

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    base_data = create_data([
        100,
        100,
        100,
        120
    ])

    high_future_data = create_data([
        100,
        100,
        100,
        120,
        10_000
    ])

    low_future_data = create_data([
        100,
        100,
        100,
        120,
        1
    ])

    base_signal = strategy.generate_signal(base_data)

    high_future_signal = strategy.generate_signal(
        high_future_data.iloc[:4]
    )

    low_future_signal = strategy.generate_signal(
        low_future_data.iloc[:4]
    )

    assert base_signal == high_future_signal
    assert base_signal == low_future_signal


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


def test_generate_all_preserves_input_index_values():

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    dates = pd.to_datetime([
        "2025-01-03",
        "2025-01-05",
        "2025-01-10",
        "2025-01-20",
        "2025-02-01"
    ])

    data = pd.DataFrame(
        {
            "Close": [
                100,
                100,
                100,
                120,
                130
            ]
        },
        index=dates
    )

    signals = strategy.generate_all(data)

    assert signals.index.equals(data.index)


def test_generate_all_returns_numeric_signals():

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

    assert pd.api.types.is_numeric_dtype(signals)


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


def test_generate_all_first_valid_signal_is_generated_at_long_window():

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

    signals = strategy.generate_all(data)

    assert signals.iloc[3] == 1


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


def test_generate_all_returns_zero_for_constant_prices():

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([
        100,
        100,
        100,
        100,
        100,
        100
    ])

    signals = strategy.generate_all(data)

    assert (signals == 0).all()


def test_generate_all_can_switch_from_flat_to_long():

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([
        100,
        100,
        100,
        100,
        100,
        150,
        160
    ])

    signals = strategy.generate_all(data)

    assert signals.iloc[3] == 0
    assert signals.iloc[4] == 0
    assert signals.iloc[5] == 1
    assert signals.iloc[6] == 1


def test_generate_all_can_switch_from_long_to_flat():

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([
        100,
        100,
        100,
        150,
        160,
        90,
        80
    ])

    signals = strategy.generate_all(data)

    assert signals.iloc[3] == 1
    assert signals.iloc[4] == 1
    assert signals.iloc[5] == 0
    assert signals.iloc[6] == 0


def test_generate_all_matches_generate_signal():

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([
        100,
        105,
        110,
        120,
        130,
        125,
        100,
        90
    ])

    signals = strategy.generate_all(data)

    expected_signals = []

    for i in range(len(data)):
        expected_signals.append(
            strategy.generate_signal(
                data.iloc[:i + 1]
            )
        )

    expected_signals = pd.Series(
        expected_signals,
        index=data.index
    )

    pd.testing.assert_series_equal(
        signals,
        expected_signals
    )


def test_generate_all_does_not_modify_input_data():

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([
        100,
        105,
        110,
        120,
        130
    ])

    original_data = data.copy(deep=True)

    strategy.generate_all(data)

    pd.testing.assert_frame_equal(
        data,
        original_data
    )


def test_generate_signal_does_not_modify_input_data():

    strategy = MovingAverageStrategy(
        short_window=2,
        long_window=4
    )

    data = create_data([
        100,
        105,
        110,
        120
    ])

    original_data = data.copy(deep=True)

    strategy.generate_signal(data)

    pd.testing.assert_frame_equal(
        data,
        original_data
    )


def test_strategy_works_with_different_window_sizes():

    configurations = [
        (1, 2),
        (2, 3),
        (2, 5),
        (3, 7),
        (5, 10)
    ]

    data = create_data([
        100,
        101,
        102,
        103,
        104,
        105,
        106,
        107,
        108,
        109
    ])

    for short_window, long_window in configurations:

        strategy = MovingAverageStrategy(
            short_window=short_window,
            long_window=long_window
        )

        signals = strategy.generate_all(data)

        assert len(signals) == len(data)
        assert signals.index.equals(data.index)
        assert signals.isin([0, 1]).all()


def test_generate_all_with_exactly_long_window_observations():

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

    signals = strategy.generate_all(data)

    assert len(signals) == 4
    assert signals.iloc[0] == 0
    assert signals.iloc[1] == 0
    assert signals.iloc[2] == 0
    assert signals.iloc[3] == 1


def test_generate_all_contains_only_valid_signal_values():

    strategy = MovingAverageStrategy(
        short_window=3,
        long_window=5
    )

    data = create_data([
        100,
        105,
        110,
        115,
        120,
        115,
        110,
        105,
        100
    ])

    signals = strategy.generate_all(data)

    assert signals.isin([0, 1]).all()