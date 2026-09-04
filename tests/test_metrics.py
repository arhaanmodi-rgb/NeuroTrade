"""Unit tests for metrics.py"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from metrics import (
    sharpe_ratio, sortino_ratio, max_drawdown, calmar_ratio,
    win_rate, profit_factor, annualised_return, buy_and_hold_return,
    compute_all_metrics
)


def test_sharpe_positive_returns():
    returns = [0.01] * 252
    sr = sharpe_ratio(returns)
    assert sr > 0

def test_sharpe_zero_returns():
    returns = [0.0] * 100
    sr = sharpe_ratio(returns)
    assert sr == 0.0

def test_sharpe_empty():
    sr = sharpe_ratio([])
    assert sr == 0.0

def test_sortino_positive():
    returns = [0.01, -0.005, 0.01, 0.02, -0.001]
    sr = sortino_ratio(returns)
    assert isinstance(sr, float)

def test_max_drawdown_declining():
    values = [100, 90, 80, 70, 60]
    dd = max_drawdown(values)
    assert dd < 0
    assert abs(dd - (-0.4)) < 0.01

def test_max_drawdown_flat():
    values = [100, 100, 100]
    dd = max_drawdown(values)
    assert dd == 0.0

def test_max_drawdown_empty():
    dd = max_drawdown([])
    assert dd == 0.0

def test_win_rate_all_buy_positive():
    actions = [1, 1, 1]  # all BUY
    rewards = [0.01, 0.02, 0.005]
    wr = win_rate(actions, rewards)
    assert wr == 1.0

def test_win_rate_mixed():
    actions = [1, 2, 0, 1, 2]  # BUY, SELL, HOLD, BUY, SELL
    rewards = [0.01, -0.01, 0.0, 0.02, 0.01]
    wr = win_rate(actions, rewards)
    # BUY/SELL: indices 0,1,3,4 -> rewards: 0.01,-0.01,0.02,0.01 -> 3 positive
    assert abs(wr - 0.75) < 0.01

def test_profit_factor():
    rewards = [0.01, -0.005, 0.02, -0.003]
    pf = profit_factor(rewards)
    assert pf > 1.0

def test_profit_factor_no_losses():
    rewards = [0.01, 0.02]
    pf = profit_factor(rewards)
    assert pf == float('inf')

def test_annualised_return():
    r = annualised_return(0.10, 252)
    assert abs(r - 0.10) < 0.01

def test_buy_and_hold():
    r = buy_and_hold_return(100.0, 150.0)
    assert abs(r - 0.5) < 0.001

def test_compute_all_metrics():
    portfolio_values = [100000 * (1 + 0.001 * i) for i in range(100)]
    actions = [1 if i % 10 == 0 else 0 for i in range(99)]
    rewards = [0.001] * 99
    result = compute_all_metrics(
        portfolio_values=portfolio_values,
        actions=actions,
        rewards=rewards,
        initial_cash=100000,
        start_price=100.0,
        end_price=110.0
    )
    assert 'sharpe_ratio' in result
    assert 'max_drawdown' in result
    assert 'total_return_pct' in result
