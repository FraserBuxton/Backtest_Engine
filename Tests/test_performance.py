import numpy as np
import pandas as pd
import pytest

from Performance import PerformanceAnalyser

INITIAL = 10000
PPY = 252

def make(equity, initial=INITIAL, ppy=PPY):
    index = pd.date_range("2020-01-01", periods=len(equity), freq="B")
    results = pd.DataFrame({"Equity": equity}, index=index)
    return PerformanceAnalyser(results, initial, ppy)


def growth_curve(rate, periods, initial=INITIAL):
    # Equity compounding at exactly `rate` per period
    return [initial * (1 + rate) ** (i + 1) for i in range(periods)]


# ----------------------------------------------------------------------
# Constructor validation
# ----------------------------------------------------------------------

def test_results_must_be_dataframe():
    with pytest.raises(TypeError):
        PerformanceAnalyser([10000, 10100], INITIAL, PPY)


def test_results_must_have_equity_column():
    with pytest.raises(ValueError):
        PerformanceAnalyser(pd.DataFrame({"Cash": [10000]}), INITIAL, PPY)


def test_initial_cash_must_be_number():
    with pytest.raises(TypeError):
        PerformanceAnalyser(pd.DataFrame({"Equity": [10000]}), "10000", PPY)


@pytest.mark.parametrize("bad", [0, -1, -10000])
def test_initial_cash_must_be_positive(bad):
    with pytest.raises(ValueError):
        PerformanceAnalyser(pd.DataFrame({"Equity": [10000]}), bad, PPY)


@pytest.mark.parametrize("bad", [252.0, "252", None])
def test_ppy_must_be_integer(bad):
    with pytest.raises(TypeError):
        PerformanceAnalyser(pd.DataFrame({"Equity": [10000]}), INITIAL, bad)


@pytest.mark.parametrize("bad", [0, -252])
def test_ppy_must_be_positive(bad):
    with pytest.raises(ValueError):
        PerformanceAnalyser(pd.DataFrame({"Equity": [10000]}), INITIAL, bad)


def test_results_cannot_be_empty():
    with pytest.raises(ValueError):
        PerformanceAnalyser(pd.DataFrame({"Equity": []}), INITIAL, PPY)


def test_equity_cannot_contain_nan():
    with pytest.raises(ValueError):
        make([10000, np.nan, 10100])


@pytest.mark.parametrize("bad", [0, -100])
def test_equity_must_be_strictly_positive(bad):
    with pytest.raises(ValueError):
        make([10000, bad, 10100])


def test_accepts_valid_input():
    analyser = make([10000, 10100])
    assert isinstance(analyser, PerformanceAnalyser)


def test_results_are_copied():
    results = pd.DataFrame({"Equity": [10000.0, 10100.0]})
    analyser = PerformanceAnalyser(results, INITIAL, PPY)
    results.loc[1, "Equity"] = 1.0
    assert analyser.equity.iloc[1] == 10100.0


# ----------------------------------------------------------------------
# Properties
# ----------------------------------------------------------------------

def test_equity_property_returns_equity_series():
    analyser = make([10000, 10100, 10200])
    assert list(analyser.equity) == [10000, 10100, 10200]


def test_returns_length_matches_equity_length():
    # First return is measured from initial cash
    analyser = make([10100, 10201, 10303.01])
    assert len(analyser.returns) == 3


def test_first_return_is_measured_from_initial_cash():
    analyser = make([9000, 9000])
    assert analyser.returns.iloc[0] == pytest.approx(-0.10)


def test_returns_values():
    analyser = make([10500, 10500, 10080])
    expected = [0.05, 0.0, -0.04]
    assert list(analyser.returns) == pytest.approx(expected)


# ----------------------------------------------------------------------
# Total return
# ----------------------------------------------------------------------

def test_total_return_gain():
    assert make([10000, 11000]).total_return() == pytest.approx(0.10)


def test_total_return_loss():
    assert make([10000, 8000]).total_return() == pytest.approx(-0.20)


def test_total_return_flat():
    assert make([10000, 10000]).total_return() == pytest.approx(0.0)


def test_total_return_uses_initial_cash_not_first_equity():
    # First equity differs from initial cash (first-day move)
    assert make([10500, 11000]).total_return() == pytest.approx(0.10)


# ----------------------------------------------------------------------
# Annualised return
# ----------------------------------------------------------------------

def test_annualised_return_constant_growth():
    analyser = make(growth_curve(0.01, 252))
    assert analyser.annualised_return() == pytest.approx(1.01 ** 252 - 1)


def test_annualised_return_one_year_equals_total_return():
    # Exactly ppy periods, so annualised == total
    equity = list(np.linspace(10000, 11000, 252))
    analyser = make(equity)
    assert analyser.annualised_return() == pytest.approx(analyser.total_return())


def test_annualised_return_two_years_is_geometric():
    # 21% total over two years -> 10% per year
    equity = list(np.linspace(10000, 12100, 504))
    assert make(equity).annualised_return() == pytest.approx(0.10)


def test_annualised_return_half_year():
    # 5% over half a year -> 1.05**2 - 1
    equity = list(np.linspace(10000, 10500, 126))
    assert make(equity).annualised_return() == pytest.approx(1.05 ** 2 - 1)


def test_annualised_return_single_period():
    analyser = make([10100])
    assert analyser.annualised_return() == pytest.approx(1.01 ** PPY - 1)


def test_annualised_return_flat_is_zero():
    assert make([10000] * 10).annualised_return() == pytest.approx(0.0)


def test_annualised_return_loss_is_negative():
    assert make(list(np.linspace(10000, 9000, 252))).annualised_return() == pytest.approx(-0.10)


def test_annualised_return_scales_with_ppy():
    equity = list(np.linspace(10000, 11000, 12))
    monthly = make(equity, ppy=12)
    assert monthly.annualised_return() == pytest.approx(0.10)


# ----------------------------------------------------------------------
# Volatility
# ----------------------------------------------------------------------

def test_volatility_matches_manual_calculation():
    equity = [10100, 10000, 10300, 10200]
    analyser = make(equity)
    returns = analyser.returns.to_numpy()
    expected = np.std(returns, ddof=1) * np.sqrt(PPY)
    assert analyser.annualised_volatility() == pytest.approx(expected)


def test_volatility_zero_for_flat_equity():
    assert make([10000] * 10).annualised_volatility() == pytest.approx(0.0)


def test_volatility_zero_for_constant_growth():
    analyser = make(growth_curve(0.01, 50))
    assert analyser.annualised_volatility() == pytest.approx(0.0, abs=1e-12)


def test_volatility_single_observation_is_zero():
    assert make([10100]).annualised_volatility() == 0.0


def test_volatility_scales_with_sqrt_ppy():
    equity = [10100, 10000, 10300, 10200]
    daily = make(equity, ppy=252).annualised_volatility()
    weekly = make(equity, ppy=52).annualised_volatility()
    assert daily / weekly == pytest.approx(np.sqrt(252 / 52))


def test_volatility_is_non_negative():
    assert make([10100, 9900, 10300, 9800]).annualised_volatility() >= 0


# ----------------------------------------------------------------------
# Sharpe ratio
# ----------------------------------------------------------------------

def test_sharpe_matches_manual_calculation():
    analyser = make([10100, 10000, 10300, 10200])
    r = analyser.returns.to_numpy()
    expected = r.mean() / np.std(r, ddof=1) * np.sqrt(PPY)
    assert analyser.sharpe_ratio() == pytest.approx(expected)


def test_sharpe_with_risk_free_rate_matches_manual_calculation():
    analyser = make([10100, 10000, 10300, 10200])
    r = analyser.returns.to_numpy() - 0.03 / PPY
    expected = r.mean() / np.std(r, ddof=1) * np.sqrt(PPY)
    assert analyser.sharpe_ratio(rfr=0.03) == pytest.approx(expected)


def test_sharpe_decreases_as_risk_free_rate_rises():
    analyser = make([10100, 10000, 10300, 10200])
    assert analyser.sharpe_ratio(rfr=0.05) < analyser.sharpe_ratio(rfr=0.0)


def test_sharpe_positive_for_profitable_noisy_strategy():
    assert make([10100, 10050, 10300, 10250, 10500]).sharpe_ratio() > 0


def test_sharpe_negative_for_losing_noisy_strategy():
    assert make([9900, 9950, 9700, 9750, 9500]).sharpe_ratio() < 0


def test_sharpe_scales_with_sqrt_ppy():
    equity = [10100, 10000, 10300, 10200]
    daily = make(equity, ppy=252).sharpe_ratio()
    weekly = make(equity, ppy=52).sharpe_ratio()
    assert daily / weekly == pytest.approx(np.sqrt(252 / 52))


def test_sharpe_single_observation_is_zero():
    assert make([10100]).sharpe_ratio() == 0.0


def test_sharpe_flat_equity_is_zero_not_nan():
    # Zero volatility must not produce nan or inf
    assert make([10000] * 10).sharpe_ratio() == 0.0


def test_sharpe_rejects_non_numeric_rfr():
    with pytest.raises(TypeError):
        make([10100, 10200]).sharpe_ratio(rfr="0.02")


# ----------------------------------------------------------------------
# Cumulative returns
# ----------------------------------------------------------------------

def test_cumulative_returns_values():
    analyser = make([10500, 11000, 9000])
    assert list(analyser.cumulative_returns()) == pytest.approx([0.05, 0.10, -0.10])


def test_cumulative_returns_last_equals_total_return():
    analyser = make([10500, 11000, 9000])
    assert analyser.cumulative_returns().iloc[-1] == pytest.approx(analyser.total_return())


def test_cumulative_returns_preserves_index():
    analyser = make([10500, 11000, 9000])
    assert analyser.cumulative_returns().index.equals(analyser.equity.index)


# ----------------------------------------------------------------------
# Drawdowns
# ----------------------------------------------------------------------

def test_drawdowns_values():
    analyser = make([10000, 12000, 9000, 9900])
    assert list(analyser.drawdowns()) == pytest.approx([0.0, 0.0, -0.25, -0.175])


def test_drawdowns_never_positive():
    analyser = make([10100, 10500, 10200, 11000, 10000])
    assert (analyser.drawdowns() <= 0).all()


def test_drawdowns_zero_for_monotonic_growth():
    assert (make(growth_curve(0.01, 20)).drawdowns() == 0).all()


def test_drawdowns_preserve_index():
    analyser = make([10100, 10500, 10200])
    assert analyser.drawdowns().index.equals(analyser.equity.index)


def test_drawdown_counts_first_day_loss():
    # Starts below initial cash, so the first day is already a drawdown
    assert make([9000, 9500]).maximum_drawdown() == pytest.approx(-0.10)


def test_drawdown_recovery_returns_to_zero():
    analyser = make([10000, 9000, 10000, 10500])
    assert analyser.drawdowns().iloc[-1] == 0.0


def test_maximum_drawdown_picks_worst_peak_to_trough():
    # Two drawdowns: -10% then -25%
    analyser = make([10000, 9000, 10000, 12000, 9000, 13000])
    assert analyser.maximum_drawdown() == pytest.approx(-0.25)


def test_maximum_drawdown_flat_is_zero():
    assert make([10000] * 5).maximum_drawdown() == 0.0


def test_maximum_drawdown_is_non_positive():
    assert make([10100, 9500, 10300]).maximum_drawdown() <= 0


# ----------------------------------------------------------------------
# Calmar ratio
# ----------------------------------------------------------------------

def test_calmar_matches_manual_calculation():
    analyser = make([10000, 12000, 9000, 11000] * 63)
    expected = analyser.annualised_return() / abs(analyser.maximum_drawdown())
    assert analyser.calmar_ratio() == pytest.approx(expected)


def test_calmar_zero_when_no_drawdown():
    assert make(growth_curve(0.01, 20)).calmar_ratio() == 0.0


def test_calmar_negative_for_losing_strategy():
    assert make(list(np.linspace(10000, 8000, 252))).calmar_ratio() < 0


# ----------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------

def test_summary_has_expected_keys():
    summary = make([10100, 10000, 10300]).summary()
    assert set(summary) == {
        "Total Return",
        "Annualised Return",
        "Annualised Volatility",
        "Sharpe Ratio",
        "Maximum Drawdown",
        "Calmar Ratio",
    }


def test_summary_values_match_individual_methods():
    analyser = make([10100, 10000, 10300, 10200])
    summary = analyser.summary()
    assert summary["Total Return"] == pytest.approx(analyser.total_return())
    assert summary["Annualised Return"] == pytest.approx(analyser.annualised_return())
    assert summary["Annualised Volatility"] == pytest.approx(analyser.annualised_volatility())
    assert summary["Sharpe Ratio"] == pytest.approx(analyser.sharpe_ratio())
    assert summary["Maximum Drawdown"] == pytest.approx(analyser.maximum_drawdown())
    assert summary["Calmar Ratio"] == pytest.approx(analyser.calmar_ratio())


def test_summary_values_are_finite():
    summary = make([10100, 10000, 10300, 10200]).summary()
    assert all(np.isfinite(v) for v in summary.values())


def test_summary_finite_for_flat_equity():
    summary = make([10000] * 10).summary()
    assert all(np.isfinite(v) for v in summary.values())
