from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import datetime

from api.database import get_db
from api.models.db_models import User, Watchlist
from api.models.schemas import (
    UserRegister, UserLogin, Token, UserResponse,
    WatchlistAdd, WatchlistResponse, StockSignalSummary
)
from api.services.auth import (
    get_password_hash, verify_password,
    create_access_token, get_current_user
)
from api.services.predictor import get_predictor
from api.services.live_data import get_current_price

router = APIRouter(prefix="/auth", tags=["Authentication & User"])

@router.post("/register", response_model=Token)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # Check email exists
    if db.query(User).filter(User.email == user_data.email.lower().strip()).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check username exists
    if db.query(User).filter(User.username == user_data.username.lower().strip()).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create user
    new_user = User(
        email=user_data.email.lower().strip(),
        username=user_data.username.lower().strip(),
        full_name=user_data.full_name or user_data.username,
        hashed_password=get_password_hash(user_data.password),
        created_at=datetime.datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Add default watchlist for new user
    for default_stock in ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]:
        db.add(Watchlist(user_id=new_user.id, stock_symbol=default_stock, exchange="NSE"))
    db.commit()

    # Generate token
    token = create_access_token(data={"sub": new_user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role
        }
    }


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    identifier = login_data.username_or_email.lower().strip()
    user = db.query(User).filter((User.username == identifier) | (User.email == identifier)).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.last_login = datetime.datetime.utcnow()
    db.commit()

    token = create_access_token(data={"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/watchlist")
def get_user_watchlist(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(Watchlist).filter(Watchlist.user_id == current_user.id).order_by(Watchlist.added_at.desc()).all()
    predictor = get_predictor()

    result = []
    for item in items:
        sig_summary = None
        try:
            res = predictor.predict(item.stock_symbol)
            sig_summary = {
                "stock": res["stock"],
                "action": res["action"],
                "confidence": res["confidence"],
                "price": res["price"],
                "portfolio_value": res["portfolio_value"],
                "timestamp": res["timestamp"]
            }
        except Exception:
            pass

        result.append({
            "id": item.id,
            "stock_symbol": item.stock_symbol,
            "exchange": item.exchange,
            "added_at": item.added_at,
            "latest_signal": sig_summary
        })
    return {"watchlist": result}


@router.post("/watchlist")
def add_to_watchlist(item: WatchlistAdd, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    symbol = item.stock_symbol.upper().strip()
    existing = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id,
        Watchlist.stock_symbol == symbol
    ).first()

    if existing:
        return {"message": f"{symbol} already in watchlist", "item_id": existing.id}

    new_item = Watchlist(
        user_id=current_user.id,
        stock_symbol=symbol,
        exchange=item.exchange or "NSE",
        added_at=datetime.datetime.utcnow()
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"message": f"Added {symbol} to watchlist", "item_id": new_item.id}


@router.delete("/watchlist/{stock_symbol}")
def remove_from_watchlist(stock_symbol: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    symbol = stock_symbol.upper().strip()
    item = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id,
        Watchlist.stock_symbol == symbol
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail=f"{symbol} not found in watchlist")

    db.delete(item)
    db.commit()
    return {"message": f"Removed {symbol} from watchlist"}
