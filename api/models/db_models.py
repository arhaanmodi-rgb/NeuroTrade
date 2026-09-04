import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from api.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    trades = relationship("UserTrade", back_populates="user", cascade="all, delete-orphan")
    holdings = relationship("UserHolding", back_populates="user", cascade="all, delete-orphan")


class UserHolding(Base):
    __tablename__ = "user_holdings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_symbol = Column(String, index=True, nullable=False)
    buy_price = Column(Float, nullable=False)
    shares = Column(Float, nullable=False)
    target_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    buy_date = Column(String, default=lambda: datetime.datetime.utcnow().strftime("%Y-%m-%d"))
    exchange = Column(String, default="NSE")
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="holdings")


class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_symbol = Column(String, index=True, nullable=False)
    exchange = Column(String, default="NSE")
    added_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="watchlists")


class UserTrade(Base):
    __tablename__ = "user_trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_symbol = Column(String, index=True, nullable=False)
    action = Column(String, nullable=False) # BUY, SELL, HOLD
    price = Column(Float, nullable=False)
    shares = Column(Float, nullable=False)
    target_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    portfolio_value = Column(Float, nullable=False)
    cash = Column(Float, nullable=True, default=0.0)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="trades")


class StockUniverse(Base):
    __tablename__ = "stock_universe"

    symbol = Column(String, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    exchange = Column(String, default="NSE")
    sector = Column(String, default="General")
    category = Column(String, default="Mainboard")
