from fastapi import APIRouter, HTTPException
from datetime import datetime
import os
import re
from api.models.schemas import BacktestMetrics

router = APIRouter()


def _parse_report(text: str, stock: str) -> BacktestMetrics:
    """Parse the validation report text into structured metrics."""

    def extract(pattern, default=0.0):
        m = re.search(pattern, text)
        if m:
            try:
                return float(m.group(1).replace(',', '').replace('₹', '').strip())
            except Exception:
                return default
        return default

    def extract_int(pattern, default=0):
        m = re.search(pattern, text)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                return default
        return default

    initial  = extract(r'Initial Capital[:\s₹]+([0-9,\.]+)', 100000.0)
    final    = extract(r'Final Portfolio[:\s₹]+([0-9,\.]+)', initial)
    total_r  = extract(r'Total Return[:\s]+([-+]?[0-9\.]+)%', 0.0)
    ann_r    = extract(r'Annualised Return[:\s]+([-+]?[0-9\.]+)%', 0.0)
    bnh      = extract(r'Buy-and-Hold Return[:\s]+([-+]?[0-9\.]+)%', 0.0)
    vs_bnh   = extract(r'vs Buy-and-Hold[:\s]+([-+]?[0-9\.]+)', 0.0)
    sharpe   = extract(r'Sharpe Ratio[:\s]+([-+]?[0-9\.]+)', 0.0)
    sortino  = extract(r'Sortino Ratio[:\s]+([-+]?[0-9\.]+)', 0.0)
    mdd      = extract(r'Max Drawdown[:\s]+([-+]?[0-9\.]+)%', 0.0)
    calmar   = extract(r'Calmar Ratio[:\s]+([-+]?[0-9\.]+)', 0.0)
    win_rate = extract(r'Win Rate[:\s]+([-+]?[0-9\.]+)%', 0.0)
    pf       = extract(r'Profit Factor[:\s]+([-+]?[0-9\.]+)', 0.0)
    n_hold   = extract_int(r'HOLD[:\s]+(\d+)', 0)
    n_buy    = extract_int(r'BUY[:\s]+(\d+)', 0)
    n_sell   = extract_int(r'SELL[:\s]+(\d+)', 0)

    return BacktestMetrics(
        stock=stock,
        total_return_pct=total_r,
        annualised_return_pct=ann_r,
        buy_and_hold_return_pct=bnh,
        vs_buy_and_hold_pp=vs_bnh,
        sharpe_ratio=sharpe,
        sortino_ratio=sortino,
        max_drawdown_pct=mdd,
        calmar_ratio=calmar,
        win_rate_pct=win_rate,
        profit_factor=pf,
        n_hold=n_hold,
        n_buy=n_buy,
        n_sell=n_sell,
        initial_capital=initial,
        final_portfolio=final,
        report_text=text.strip()
    )


@router.get('/backtest/{stock}', response_model=BacktestMetrics)
def get_backtest_results(stock: str):
    stock = stock.upper()
    report_path = f'results/{stock}_validation_report.txt'

    if not os.path.exists(report_path):
        raise HTTPException(
            status_code=404,
            detail=(
                f'No backtest report found for {stock}. '
                f'Run: python validate_model.py --stock {stock}'
            )
        )

    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return _parse_report(content, stock)
