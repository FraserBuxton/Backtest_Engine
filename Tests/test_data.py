import pandas as pd
import pytest
from Data.data_handler import DataHandler

VALID_DATA = """Price,Close,High,Low,Open,Volume
                Ticker,AAPL,AAPL,AAPL,AAPL,AAPL
                Date,,,,,
                2020-01-02,75,76,74,75,1000
                2020-01-03,76,77,75,75,1100
                2020-01-06,77,78,76,76,1200
                2020-01-07,76,77,75,77,1300
                """


def create_csv(tmp_path, content=VALID_DATA):
    filepath = tmp_path / "test_data.csv"
    filepath.write_text(content)
    return filepath


def test_valid_data_loads(tmp_path):
    filepath = create_csv(tmp_path)

    handler = DataHandler(filepath)

    assert not handler.data.empty
    assert len(handler.data) == 4


def test_data_is_sorted_by_date(tmp_path):
    content = """Price,Close,High,Low,Open,Volume
    Ticker,AAPL,AAPL,AAPL,AAPL,AAPL
    Date,,,,,
    2020-01-06,77,78,76,76,1200
    2020-01-02,75,76,74,75,1000
    2020-01-03,76,77,75,75,1100
    """

    filepath = create_csv(tmp_path, content)

    handler = DataHandler(filepath)

    dates = handler.get_dates()

    assert dates.is_monotonic_increasing


def test_missing_required_column(tmp_path):
    content = """Price,Close,High,Low,Open
    Ticker,AAPL,AAPL,AAPL,AAPL
    Date,,,,
    2020-01-02,75,76,74,75
    """

    filepath = create_csv(tmp_path, content)

    with pytest.raises(ValueError, match="Missing required columns"):
        DataHandler(filepath)


def test_invalid_date(tmp_path):
    content = """Price,Close,High,Low,Open,Volume
    Ticker,AAPL,AAPL,AAPL,AAPL,AAPL
    Date,,,,,
    not-a-date,75,76,74,75,1000
    """

    filepath = create_csv(tmp_path, content)

    with pytest.raises(ValueError, match="Invalid date"):
        DataHandler(filepath)


def test_duplicate_dates(tmp_path):
    content = """Price,Close,High,Low,Open,Volume
    Ticker,AAPL,AAPL,AAPL,AAPL,AAPL
    Date,,,,,
    2020-01-02,75,76,74,75,1000
    2020-01-02,76,77,75,75,1100
    """

    filepath = create_csv(tmp_path, content)

    with pytest.raises(ValueError, match="Duplicate dates"):
        DataHandler(filepath)


def test_non_numeric_price(tmp_path):
    content = """Price,Close,High,Low,Open,Volume
    Ticker,AAPL,AAPL,AAPL,AAPL,AAPL
    Date,,,,,
    2020-01-02,not-a-number,76,74,75,1000
    """

    filepath = create_csv(tmp_path, content)

    with pytest.raises(ValueError, match="contains non-numeric values"):
        DataHandler(filepath)

def test_missing_value(tmp_path):
    content = """Price,Close,High,Low,Open,Volume
    Ticker,AAPL,AAPL,AAPL,AAPL,AAPL
    Date,,,,,
    2020-01-02,75,76,74,,1000
    """

    filepath = create_csv(tmp_path, content)

    with pytest.raises(ValueError, match="Missing values"):
        DataHandler(filepath)


def test_zero_price(tmp_path):
    content = """Price,Close,High,Low,Open,Volume
    Ticker,AAPL,AAPL,AAPL,AAPL,AAPL
    Date,,,,,
    2020-01-02,0,76,74,75,1000
    """

    filepath = create_csv(tmp_path, content)

    with pytest.raises(ValueError, match="Non-positive prices"):
        DataHandler(filepath)


def test_negative_price(tmp_path):
    content = """Price,Close,High,Low,Open,Volume
    Ticker,AAPL,AAPL,AAPL,AAPL,AAPL
    Date,,,,,
    2020-01-02,-75,76,74,75,1000
    """

    filepath = create_csv(tmp_path, content)

    with pytest.raises(ValueError, match="Non-positive prices"):
        DataHandler(filepath)


def test_negative_volume(tmp_path):
    content = """Price,Close,High,Low,Open,Volume
    Ticker,AAPL,AAPL,AAPL,AAPL,AAPL
    Date,,,,,
    2020-01-02,75,76,74,75,-1000
    """

    filepath = create_csv(tmp_path, content)

    with pytest.raises(ValueError, match="Negative volume"):
        DataHandler(filepath)


def test_high_lower_than_open(tmp_path):
    content = """Price,Close,High,Low,Open,Volume
    Ticker,AAPL,AAPL,AAPL,AAPL,AAPL
    Date,,,,,
    2020-01-02,75,74,73,75,1000
    """

    filepath = create_csv(tmp_path, content)

    with pytest.raises(ValueError, match="High < Open or Close"):
        DataHandler(filepath)


def test_high_lower_than_close(tmp_path):
    content = """Price,Close,High,Low,Open,Volume
    Ticker,AAPL,AAPL,AAPL,AAPL,AAPL
    Date,,,,,
    2020-01-02,75,74,73,73,1000
    """

    filepath = create_csv(tmp_path, content)

    with pytest.raises(ValueError, match="High < Open or Close"):
        DataHandler(filepath)


def test_low_higher_than_open(tmp_path):
    content = """Price,Close,High,Low,Open,Volume
    Ticker,AAPL,AAPL,AAPL,AAPL,AAPL
    Date,,,,,
    2020-01-02,75,76,76,75,1000
    """

    filepath = create_csv(tmp_path, content)

    with pytest.raises(ValueError, match="Low > Open or Close"):
        DataHandler(filepath)


def test_low_higher_than_close(tmp_path):
    content = """Price,Close,High,Low,Open,Volume
    Ticker,AAPL,AAPL,AAPL,AAPL,AAPL
    Date,,,,,
    2020-01-02,76,77,76,75,1000
    """

    filepath = create_csv(tmp_path, content)

    with pytest.raises(ValueError, match="Low > Open or Close"):
        DataHandler(filepath)

def test_file_not_found(tmp_path):
    filepath = tmp_path / "does_not_exist.csv"

    with pytest.raises(FileNotFoundError, match="File not found"):
        DataHandler(filepath)


def test_path_is_directory(tmp_path):
    with pytest.raises(ValueError, match="Path is not a file"):
        DataHandler(tmp_path)


def test_empty_file(tmp_path):
    filepath = tmp_path / "empty.csv"
    filepath.write_text("")

    with pytest.raises(ValueError, match="Data file is empty"):
        DataHandler(filepath)


def test_get_close(tmp_path):
    filepath = create_csv(tmp_path)

    handler = DataHandler(filepath)

    close = handler.get_close("2020-01-02")

    assert close == 75


def test_get_close_with_timestamp(tmp_path):
    filepath = create_csv(tmp_path)

    handler = DataHandler(filepath)

    close = handler.get_close(pd.Timestamp("2020-01-03"))

    assert close == 76


def test_get_close_invalid_date(tmp_path):
    filepath = create_csv(tmp_path)

    handler = DataHandler(filepath)

    with pytest.raises(ValueError, match="Invalid date"):
        handler.get_close("not-a-date")


def test_get_close_date_not_found(tmp_path):
    filepath = create_csv(tmp_path)

    handler = DataHandler(filepath)

    with pytest.raises(KeyError, match="Date not found"):
        handler.get_close("2021-01-01")

def test_get_between(tmp_path):
    filepath = create_csv(tmp_path)

    handler = DataHandler(filepath)

    data = handler.get_between(
        "2020-01-02",
        "2020-01-06"
    )

    assert len(data) == 3
    assert data.index.min() == pd.Timestamp("2020-01-02")
    assert data.index.max() == pd.Timestamp("2020-01-06")


def test_get_between_single_day(tmp_path):
    filepath = create_csv(tmp_path)

    handler = DataHandler(filepath)

    data = handler.get_between(
        "2020-01-03",
        "2020-01-03"
    )

    assert len(data) == 1
    assert data.iloc[0]["Close"] == 76


def test_get_between_invalid_range(tmp_path):
    filepath = create_csv(tmp_path)

    handler = DataHandler(filepath)

    with pytest.raises(
        ValueError,
        match="Start date must be before end date"
    ):
        handler.get_between(
            "2020-01-06",
            "2020-01-02"
        )


def test_get_between_before_dataset(tmp_path):
    filepath = create_csv(tmp_path)

    handler = DataHandler(filepath)

    with pytest.raises(
        ValueError,
        match="before the dataset begins"
    ):
        handler.get_between(
            "2019-01-01",
            "2019-01-02"
        )


def test_get_between_after_dataset(tmp_path):
    filepath = create_csv(tmp_path)

    handler = DataHandler(filepath)

    with pytest.raises(
        ValueError,
        match="after the dataset ends"
    ):
        handler.get_between(
            "2021-01-01",
            "2021-01-02"
        )


def test_get_all(tmp_path):
    filepath = create_csv(tmp_path)

    handler = DataHandler(filepath)

    data = handler.get_all()

    assert len(data) == 4
    assert list(data.columns) == [
        "Close",
        "High",
        "Low",
        "Open",
        "Volume"
    ]


def test_get_all_returns_copy(tmp_path):
    filepath = create_csv(tmp_path)

    handler = DataHandler(filepath)

    data = handler.get_all()

    data.iloc[0, data.columns.get_loc("Close")] = 999999

    assert handler.get_close("2020-01-02") == 75


def test_get_dates(tmp_path):
    filepath = create_csv(tmp_path)

    handler = DataHandler(filepath)

    dates = handler.get_dates()

    assert len(dates) == 4
    assert dates[0] == pd.Timestamp("2020-01-02")
    assert dates[-1] == pd.Timestamp("2020-01-07")