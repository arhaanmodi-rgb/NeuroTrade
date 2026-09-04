from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from api.database import get_db
from api.models.schemas import TradeExecutionRequest, TradeExecutionResponse
from api.services.predictor import get_predictor
from api.services.live_data import get_current_price
from api.services.trade_log import log_trade, init_db
from api.services.auth import get_optional_user
from api.models.db_models import User, UserHolding, UserTrade

router = APIRouter(prefix="/trades", tags=["Trade Execution & Portfolio Positions"])

@router.post("/execute", response_model=TradeExecutionResponse)
def execute_order(
    req: TradeExecutionRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    sym = req.stock.upper().strip()
    action = req.action.upper().strip()
    
    # Strictly validate that the stock is a real NSE/BSE listed company
    try:
        live_price = get_current_price(sym)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Stock '{sym}' is not a listed Indian company on NSE or BSE. Orders can only be placed on real listed stocks."
        )
        
    price = req.price if (req.price and req.price > 0) else live_price
    predictor = get_predictor()

    if action == "SELL":
        # 1. Sum total shares owned by this user across all holding records
        holdings = []
        user_shares = 0.0

        if current_user:
            holdings = db.query(UserHolding).filter(
                UserHolding.user_id == current_user.id,
                UserHolding.stock_symbol == sym
            ).all()
            user_shares = sum(float(h.shares) for h in holdings)
        else:
            # Check all holdings in DB matching symbol as fallback
            all_db_holdings = db.query(UserHolding).filter(UserHolding.stock_symbol == sym).all()
            if all_db_holdings:
                user_shares = sum(float(h.shares) for h in all_db_holdings)
                holdings = all_db_holdings

        # Fallback to predictor in-memory portfolio if no DB holding
        if user_shares <= 0:
            port = predictor.get_portfolio_position(sym)
            user_shares = float(port.get('shares', 0.0))

        if user_shares <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot SELL: You currently own 0 shares of {sym}. You must add or buy shares first before selling."
            )

        sell_shares = float(req.shares) if (req.shares and float(req.shares) > 0 and float(req.shares) <= user_shares) else user_shares
        total_proceeds = round(sell_shares * price, 2)

        # Deduct sell_shares across user holdings (FIFO)
        shares_to_deduct = sell_shares
        for h in holdings:
            if shares_to_deduct <= 0:
                break
            if h.shares <= shares_to_deduct + 0.001:
                shares_to_deduct -= h.shares
                db.delete(h)
            else:
                h.shares = round(h.shares - shares_to_deduct, 2)
                shares_to_deduct = 0
        db.commit()

        # Update in-memory predictor state
        port = predictor.get_portfolio_position(sym)
        port['cash'] += total_proceeds
        port['shares'] = max(0.0, port['shares'] - sell_shares)
        if port['shares'] <= 0:
            port['avg_buy_price'] = 0.0
            port['bought_date'] = None
        port['portfolio_value'] = port['cash'] + (port['shares'] * price)

        # Log into trade audit history
        init_db()
        log_trade(
            stock=sym,
            action="SELL",
            price=price,
            shares=sell_shares,
            portfolio_value=port['portfolio_value'],
            cash=port['cash'],
            timestamp=datetime.now().isoformat()
        )

        if current_user:
            db_trade = UserTrade(
                user_id=current_user.id,
                stock_symbol=sym,
                action="SELL",
                price=price,
                shares=sell_shares,
                portfolio_value=port['portfolio_value'],
                cash=port['cash'],
                timestamp=datetime.utcnow()
            )
            db.add(db_trade)
            db.commit()

        return TradeExecutionResponse(
            status="SUCCESS",
            message=f"Successfully SOLD {sell_shares:.2f} shares of {sym} @ ₹{price:,.2f} for ₹{total_proceeds:,.2f} proceeds",
            stock=sym,
            action="SELL",
            shares=sell_shares,
            price=price,
            total_amount=total_proceeds,
            cash_remaining=port['cash'],
            total_portfolio=port['portfolio_value'],
            timestamp=datetime.now().isoformat()
        )

    elif action == "BUY":
        buy_shares = float(req.shares) if (req.shares and float(req.shares) > 0) else 10.0
        total_cost = round(buy_shares * price, 2)
        target = req.target_price if (req.target_price and req.target_price > 0) else round(price * 1.08, 2)
        stop = req.stop_loss if (req.stop_loss and req.stop_loss > 0) else round(price * 0.95, 2)

        if current_user:
            holding = db.query(UserHolding).filter(
                UserHolding.user_id == current_user.id,
                UserHolding.stock_symbol == sym
            ).first()

            if holding:
                new_shares = holding.shares + buy_shares
                new_avg = ((holding.shares * holding.buy_price) + total_cost) / new_shares
                holding.shares = round(new_shares, 2)
                holding.buy_price = round(new_avg, 2)
                holding.target_price = target
                holding.stop_loss = stop
            else:
                holding = UserHolding(
                    user_id=current_user.id,
                    stock_symbol=sym,
                    buy_price=price,
                    shares=buy_shares,
                    target_price=target,
                    stop_loss=stop,
                    buy_date=datetime.utcnow().strftime("%Y-%m-%d"),
                    exchange="NSE",
                    created_at=datetime.utcnow()
                )
                db.add(holding)
            db.commit()

        port = predictor.get_portfolio_position(sym)
        new_shares = port['shares'] + buy_shares
        new_avg = ((port['shares'] * port['avg_buy_price']) + total_cost) / new_shares
        port['cash'] = max(0.0, port['cash'] - total_cost)
        port['shares'] = new_shares
        port['avg_buy_price'] = round(new_avg, 2)
        port['bought_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        port['portfolio_value'] = port['cash'] + (new_shares * price)

        init_db()
        log_trade(
            stock=sym,
            action="BUY",
            price=price,
            shares=buy_shares,
            portfolio_value=port['portfolio_value'],
            cash=port['cash'],
            timestamp=datetime.now().isoformat()
        )

        if current_user:
            db_trade = UserTrade(
                user_id=current_user.id,
                stock_symbol=sym,
                action="BUY",
                price=price,
                shares=buy_shares,
                target_price=target,
                stop_loss=stop,
                portfolio_value=port['portfolio_value'],
                cash=port['cash'],
                timestamp=datetime.utcnow()
            )
            db.add(db_trade)
            db.commit()

        return TradeExecutionResponse(
            status="SUCCESS",
            message=f"Successfully BOUGHT {buy_shares:.2f} shares of {sym} @ ₹{price:,.2f}",
            stock=sym,
            action="BUY",
            shares=buy_shares,
            price=price,
            total_amount=total_cost,
            cash_remaining=port['cash'],
            total_portfolio=port['portfolio_value'],
            timestamp=datetime.now().isoformat()
        )
    else:
        raise HTTPException(status_code=400, detail="Action must be BUY or SELL")
