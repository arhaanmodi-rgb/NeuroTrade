from fastapi import APIRouter
from api.services.predictor import get_predictor
from api.services.trade_log import get_all_trades, init_db
from api.models.schemas import PortfolioResponse, PortfolioPosition

router = APIRouter()

INITIAL_CASH_PER_STOCK = 100_000.0


@router.get('/portfolio', response_model=PortfolioResponse)
def get_portfolio():
    predictor = get_predictor()
    positions = []
    total_value = 0.0
    total_cash = 0.0
    n = max(len(predictor.get_loaded_stocks()), 1)
    initial_capital = INITIAL_CASH_PER_STOCK * n

    for stock in predictor.get_loaded_stocks():
        portfolio = predictor.portfolios.get(stock, {})
        pv    = float(portfolio.get('portfolio_value', INITIAL_CASH_PER_STOCK))
        cash  = float(portfolio.get('cash', INITIAL_CASH_PER_STOCK))
        shares = float(portfolio.get('shares', 0.0))
        total_value += pv
        total_cash  += cash
        positions.append(PortfolioPosition(
            stock=stock,
            shares=shares,
            portfolio_value=pv,
            cash=cash
        ))

    total_return_inr = total_value - initial_capital
    total_return_pct = (total_return_inr / initial_capital) * 100 if initial_capital > 0 else 0.0

    return PortfolioResponse(
        total_value=round(total_value, 2),
        initial_capital=round(initial_capital, 2),
        cash=round(total_cash, 2),
        positions=positions,
        total_return_pct=round(total_return_pct, 2),
        total_return_inr=round(total_return_inr, 2)
    )


@router.get('/trades')
def get_trade_history(limit: int = 100):
    init_db()
    trades = get_all_trades(limit=limit)
    return {'trades': trades, 'count': len(trades)}
