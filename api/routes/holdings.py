from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from api.database import get_db
from api.models.db_models import User, UserHolding, UserTrade
from api.models.schemas import UserHoldingCreate, UserHoldingUpdate, UserHoldingItem, UserHoldingsResponse
from api.services.auth import get_current_user, get_optional_user
from api.services.live_data import get_current_price
from api.services.predictor import get_predictor
from api.services.trade_log import log_trade, init_db

router = APIRouter(prefix="/holdings", tags=["User Real Holdings & AI Portfolio Advisor"])

@router.get("", response_model=UserHoldingsResponse)
def get_user_holdings(
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    predictor = get_predictor()
    
    if not current_user:
        return UserHoldingsResponse(
            total_invested=0.0,
            total_current=0.0,
            total_pnl_inr=0.0,
            total_pnl_pct=0.0,
            holdings_count=0,
            alarms_count=0,
            holdings=[]
        )

    db_holdings = db.query(UserHolding).filter(UserHolding.user_id == current_user.id).order_by(UserHolding.created_at.desc()).all()
    
    total_invested = 0.0
    total_current = 0.0
    holding_items = []
    alarms_count = 0

    for h in db_holdings:
        sym = h.stock_symbol.upper().strip()
        current_price = get_current_price(sym, h.exchange or "NSE")
        
        # Sync to predictor portfolio position so SignalPanel and AI Reasoner know shares are held
        port = predictor.get_portfolio_position(sym)
        port['shares'] = h.shares
        port['avg_buy_price'] = h.buy_price
        port['bought_date'] = h.buy_date or str(h.created_at)[:10]
        port['portfolio_value'] = port['cash'] + (h.shares * current_price)

        invested = round(h.buy_price * h.shares, 2)
        curr_val = round(current_price * h.shares, 2)
        pnl_inr = round(curr_val - invested, 2)
        pnl_pct = round(((current_price - h.buy_price) / max(h.buy_price, 0.01)) * 100.0, 2)
        
        total_invested += invested
        total_current += curr_val

        # Target and Stop Loss
        target = h.target_price if (h.target_price and h.target_price > 0) else round(h.buy_price * 1.08, 2)
        stop = h.stop_loss if (h.stop_loss and h.stop_loss > 0) else round(h.buy_price * 0.95, 2)

        alarm_status = "NORMAL"
        alarm_message = None

        if current_price <= stop:
            alarm_status = "STOP_LOSS_BREACH"
            alarm_message = f"🚨 STOP LOSS HIT! Price ₹{current_price:,.2f} fell below Stop Loss ₹{stop:,.2f}. SELL immediately to protect capital!"
            alarms_count += 1
            ai_action = "🚨 EMERGENCY SELL (STOP LOSS)"
            ai_rationale = alarm_message
        elif current_price >= target:
            alarm_status = "TARGET_REACHED"
            alarm_message = f"🎯 TARGET REACHED! Price ₹{current_price:,.2f} surged past Target ₹{target:,.2f} (+{pnl_pct:.1f}%). Book profits now!"
            alarms_count += 1
            ai_action = "🎯 SELL & TAKE PROFIT"
            ai_rationale = alarm_message
        else:
            sig = predictor.predict(sym, current_price=current_price)
            raw_action = sig.get('action', 'HOLD')
            if raw_action == 'BUY' and pnl_pct >= 0:
                ai_action = "BUY MORE / ACCUMULATE"
                ai_rationale = f"Strong upward momentum confirming your entry (+{pnl_pct:.1f}%). Additional accumulation favored."
            elif pnl_pct >= 5.0:
                ai_action = "HOLD & RIDE (TRAILING SL)"
                ai_rationale = f"Position in healthy profit (+{pnl_pct:.1f}%). Keep trailing stop-loss near ₹{stop:,.2f}."
            else:
                ai_action = "HOLD & WAIT"
                ai_rationale = f"Consolidating within risk boundaries (SL: ₹{stop:,.2f} | Target: ₹{target:,.2f})."

        holding_items.append(UserHoldingItem(
            id=h.id,
            stock_symbol=sym,
            buy_price=round(h.buy_price, 2),
            shares=round(h.shares, 2),
            buy_date=h.buy_date or str(h.created_at)[:10],
            exchange=h.exchange or "NSE",
            current_price=round(current_price, 2),
            invested_value=invested,
            current_value=curr_val,
            pnl_inr=pnl_inr,
            pnl_pct=pnl_pct,
            target_price=target,
            stop_loss=stop,
            alarm_status=alarm_status,
            alarm_message=alarm_message,
            ai_action=ai_action,
            ai_rationale=ai_rationale,
            ai_confidence=0.88
        ))

    total_pnl_inr = round(total_current - total_invested, 2)
    total_pnl_pct = round((total_pnl_inr / max(total_invested, 0.01)) * 100.0, 2) if total_invested > 0 else 0.0

    return UserHoldingsResponse(
        total_invested=round(total_invested, 2),
        total_current=round(total_current, 2),
        total_pnl_inr=total_pnl_inr,
        total_pnl_pct=total_pnl_pct,
        holdings_count=len(holding_items),
        alarms_count=alarms_count,
        holdings=holding_items
    )


@router.post("", response_model=dict)
def add_holding(
    item: UserHoldingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sym = item.stock_symbol.upper().strip()
    if item.buy_price <= 0 or item.shares <= 0:
        raise HTTPException(status_code=400, detail="Buy price and quantity must be greater than zero")

    # Strictly validate that the stock is a real NSE/BSE listed company
    try:
        live_price = get_current_price(sym, item.exchange or "NSE")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Stock '{sym}' is not a listed Indian company on NSE or BSE. Please enter a valid stock symbol (e.g. RELIANCE, TATAMOTORS, INFY, TCS, HDFCBANK)."
        )

    target = item.target_price if (item.target_price and item.target_price > 0) else round(item.buy_price * 1.08, 2)
    stop = item.stop_loss if (item.stop_loss and item.stop_loss > 0) else round(item.buy_price * 0.95, 2)

    # 1. Save or update UserHolding
    holding = db.query(UserHolding).filter(
        UserHolding.user_id == current_user.id,
        UserHolding.stock_symbol == sym
    ).first()

    if holding:
        total_shares = holding.shares + item.shares
        avg_price = ((holding.shares * holding.buy_price) + (item.shares * item.buy_price)) / total_shares
        holding.shares = total_shares
        holding.buy_price = round(avg_price, 2)
        holding.target_price = target
        holding.stop_loss = stop
    else:
        holding = UserHolding(
            user_id=current_user.id,
            stock_symbol=sym,
            buy_price=item.buy_price,
            shares=item.shares,
            target_price=target,
            stop_loss=stop,
            buy_date=item.buy_date or datetime.utcnow().strftime("%Y-%m-%d"),
            exchange=item.exchange or "NSE",
            notes=item.notes,
            created_at=datetime.utcnow()
        )
        db.add(holding)

    db.commit()
    db.refresh(holding)

    # 2. Update Predictor internal position
    predictor = get_predictor()
    port = predictor.get_portfolio_position(sym)
    port['shares'] = holding.shares
    port['avg_buy_price'] = holding.buy_price
    port['bought_date'] = holding.buy_date
    port['portfolio_value'] = port['cash'] + (holding.shares * item.buy_price)

    # 3. Log into trade audit history
    init_db()
    log_trade(
        stock=sym,
        action="BUY",
        price=item.buy_price,
        shares=item.shares,
        portfolio_value=port['portfolio_value'],
        cash=port['cash'],
        timestamp=datetime.now().isoformat()
    )

    user_trade = UserTrade(
        user_id=current_user.id,
        stock_symbol=sym,
        action="BUY",
        price=item.buy_price,
        shares=item.shares,
        target_price=target,
        stop_loss=stop,
        portfolio_value=port['portfolio_value'],
        cash=port['cash'],
        timestamp=datetime.utcnow()
    )
    db.add(user_trade)
    db.commit()

    return {
        "status": "SUCCESS",
        "message": f"Recorded {item.shares} shares of {sym} @ ₹{item.buy_price:,.2f} into Portfolio & Trade History",
        "holding_id": holding.id
    }


@router.put("/{holding_id}", response_model=dict)
def update_holding_limits(
    holding_id: int,
    item: UserHoldingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    holding = db.query(UserHolding).filter(
        UserHolding.id == holding_id,
        UserHolding.user_id == current_user.id
    ).first()

    if not holding:
        raise HTTPException(status_code=404, detail="Holding record not found")

    if item.target_price is not None:
        holding.target_price = item.target_price
    if item.stop_loss is not None:
        holding.stop_loss = item.stop_loss
    if item.notes is not None:
        holding.notes = item.notes

    db.commit()
    return {"status": "SUCCESS", "message": f"Updated Stop-Loss (₹{holding.stop_loss}) and Target (₹{holding.target_price}) for {holding.stock_symbol}"}


@router.delete("/{holding_id}")
def remove_holding(
    holding_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    holding = db.query(UserHolding).filter(
        UserHolding.id == holding_id,
        UserHolding.user_id == current_user.id
    ).first()

    if not holding:
        raise HTTPException(status_code=404, detail="Holding record not found")

    sym = holding.stock_symbol
    shares = holding.shares
    price = get_current_price(sym)

    predictor = get_predictor()
    port = predictor.get_portfolio_position(sym)
    port['shares'] = 0.0
    port['avg_buy_price'] = 0.0
    port['bought_date'] = None

    # Log sell/closure into trade history
    init_db()
    log_trade(
        stock=sym,
        action="SELL",
        price=price,
        shares=shares,
        portfolio_value=port['portfolio_value'],
        cash=port['cash'],
        timestamp=datetime.now().isoformat()
    )

    db.delete(holding)
    db.commit()
    return {"status": "SUCCESS", "message": f"Removed {sym} holding from portfolio and recorded exit trade"}
