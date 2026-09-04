import numpy as np

def sharpe_ratio(returns: list[float], risk_free_rate: float = 0.05, periods_per_year: int = 252) -> float:
    """Annualised Sharpe ratio from daily returns."""
    if len(returns) == 0:
        return 0.0
    returns_arr = np.array(returns)
    daily_rf = (1 + risk_free_rate) ** (1 / periods_per_year) - 1
    excess_returns = returns_arr - daily_rf
    std = np.std(excess_returns)
    mean_excess = np.mean(excess_returns)
    if std == 0:
        # Constant returns above risk-free → very high Sharpe
        # Constant returns at or below risk-free → 0
        return 999.0 if mean_excess > 0 else 0.0
    return mean_excess / std * np.sqrt(periods_per_year)

def sortino_ratio(returns: list[float], risk_free_rate: float = 0.05, periods_per_year: int = 252) -> float:
    """Annualised Sortino ratio (only downside deviation)."""
    if len(returns) == 0:
        return 0.0
    returns_arr = np.array(returns)
    daily_rf = (1 + risk_free_rate) ** (1 / periods_per_year) - 1
    excess_returns = returns_arr - daily_rf
    downside_returns = excess_returns[excess_returns < 0]
    downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0.0
    if downside_std == 0:
        return 0.0
    return np.mean(excess_returns) / downside_std * np.sqrt(periods_per_year)

def max_drawdown(portfolio_values: list[float]) -> float:
    """Maximum peak-to-trough drawdown as a fraction (negative number)."""
    if not portfolio_values:
        return 0.0
    values = np.array(portfolio_values)
    peaks = np.maximum.accumulate(values)
    drawdowns = (values - peaks) / peaks
    return np.min(drawdowns)

def calmar_ratio(annualised_return: float, max_drawdown_value: float) -> float:
    """Calmar ratio = annualised return / abs(max drawdown)."""
    if max_drawdown_value == 0:
        return 0.0
    return annualised_return / abs(max_drawdown_value)

def win_rate(actions: list[int], rewards: list[float]) -> float:
    """Fraction of BUY/SELL steps that produced positive reward."""
    # Assuming actions: 0=HOLD, 1=BUY, 2=SELL
    active_trades = sum(1 for a in actions if a in (1, 2))
    if active_trades == 0:
        return 0.0
    winning_trades = sum(1 for a, r in zip(actions, rewards) if a in (1, 2) and r > 0)
    return winning_trades / active_trades

def profit_factor(rewards: list[float]) -> float:
    """Sum of positive rewards / abs(sum of negative rewards)."""
    if not rewards:
        return 0.0
    pos_sum = sum(r for r in rewards if r > 0)
    neg_sum = abs(sum(r for r in rewards if r < 0))
    if neg_sum == 0:
        return float('inf') if pos_sum > 0 else 0.0
    return pos_sum / neg_sum

def annualised_return(total_return_fraction: float, n_days: int, periods_per_year: int = 252) -> float:
    """Compound annualised return."""
    if n_days == 0:
        return 0.0
    return (1 + total_return_fraction) ** (periods_per_year / n_days) - 1

def buy_and_hold_return(start_price: float, end_price: float) -> float:
    """Simple buy-and-hold return as fraction."""
    if start_price == 0:
        return 0.0
    return (end_price - start_price) / start_price

def compute_all_metrics(portfolio_values, actions, rewards, initial_cash, start_price, end_price) -> dict:
    """Compute and return all metrics as a dict."""
    if not portfolio_values:
        return {}
        
    returns = []
    for i in range(1, len(portfolio_values)):
        prev = portfolio_values[i-1]
        returns.append((portfolio_values[i] - prev) / prev if prev != 0 else 0)
        
    total_ret_frac = (portfolio_values[-1] - initial_cash) / initial_cash
    n_days = len(portfolio_values)
    ann_ret = annualised_return(total_ret_frac, n_days)
    
    mdd = max_drawdown(portfolio_values)
    
    return {
        "total_return": total_ret_frac,
        "total_return_pct": total_ret_frac * 100,
        "annualised_return": ann_ret,
        "annualised_return_pct": ann_ret * 100,
        "buy_and_hold_return": buy_and_hold_return(start_price, end_price),
        "sharpe_ratio": sharpe_ratio(returns),
        "sortino_ratio": sortino_ratio(returns),
        "max_drawdown": mdd,
        "max_drawdown_pct": mdd * 100,
        "calmar_ratio": calmar_ratio(ann_ret, mdd),
        "win_rate": win_rate(actions, rewards),
        "win_rate_pct": win_rate(actions, rewards) * 100,
        "profit_factor": profit_factor(rewards)
    }
