from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


class IndicatorDetail(BaseModel):
    value: Any
    status: str
    note: str

class PositionDetail(BaseModel):
    is_holding: bool
    shares: float
    avg_buy_price: float
    bought_date: Optional[str] = None
    can_sell: bool
    can_buy: bool
    pnl_inr: float
    pnl_pct: float

class AIFeedback(BaseModel):
    action: str
    original_action: str
    headline: str
    rationale: str
    holding_context: str
    risk_level: str
    target_price: float
    stop_loss: float
    indicators: Dict[str, IndicatorDetail]
    position: PositionDetail

class SignalResponse(BaseModel):
    stock: str
    action: str           # "BUY", "HOLD", "SELL"
    action_id: int        # 0=HOLD, 1=BUY, 2=SELL
    confidence: float     # softmax probability of chosen action
    q_values: list[float] # [q_hold, q_buy, q_sell]
    price: float
    timestamp: str
    portfolio_value: float
    cash: float
    shares: float
    data_mode: Optional[str] = "DEMO"
    data_source: Optional[str] = "Live Feed"
    ai_feedback: Optional[AIFeedback] = None


# --- USER HOLDINGS SCHEMAS ---

class UserHoldingCreate(BaseModel):
    stock_symbol: str
    buy_price: float
    shares: float
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    buy_date: Optional[str] = None
    exchange: Optional[str] = "NSE"
    notes: Optional[str] = None

class UserHoldingUpdate(BaseModel):
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    notes: Optional[str] = None

class UserHoldingItem(BaseModel):
    id: int
    stock_symbol: str
    buy_price: float
    shares: float
    buy_date: str
    exchange: str
    current_price: float
    invested_value: float
    current_value: float
    pnl_inr: float
    pnl_pct: float
    target_price: float
    stop_loss: float
    alarm_status: str # "NORMAL", "STOP_LOSS_BREACH", "TARGET_REACHED"
    alarm_message: Optional[str] = None
    ai_action: str
    ai_rationale: str
    ai_confidence: float

class UserHoldingsResponse(BaseModel):
    total_invested: float
    total_current: float
    total_pnl_inr: float
    total_pnl_pct: float
    holdings_count: int
    alarms_count: int
    holdings: List[UserHoldingItem]


class TradeExecutionRequest(BaseModel):
    stock: str
    action: str # "BUY" or "SELL"
    shares: float
    price: Optional[float] = None
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None

class TradeExecutionResponse(BaseModel):
    status: str
    message: str
    stock: str
    action: str
    shares: float
    price: float
    total_amount: float
    cash_remaining: float
    total_portfolio: float
    timestamp: str


class StockSignalSummary(BaseModel):
    stock: str
    action: str
    confidence: float
    price: float
    portfolio_value: float
    timestamp: str


class AllSignalsResponse(BaseModel):
    signals: List[StockSignalSummary]
    timestamp: str


class MetricsResponse(BaseModel):
    stock: str
    total_return_pct: float
    annualised_return_pct: float
    sharpe_ratio: float
    max_drawdown_pct: float
    win_rate_pct: float
    buy_and_hold_return_pct: float
    n_trades: int


class TradeRecord(BaseModel):
    id: int
    stock: str
    action: str
    price: float
    shares: float
    portfolio_value: float
    cash: Optional[float] = 0.0
    timestamp: str


class PortfolioPosition(BaseModel):
    stock: str
    shares: float
    portfolio_value: float
    cash: float


class PortfolioResponse(BaseModel):
    total_value: float
    initial_capital: float
    cash: float
    positions: List[PortfolioPosition]
    total_return_pct: float
    total_return_inr: float


class BacktestMetrics(BaseModel):
    stock: str
    total_return_pct: float
    annualised_return_pct: float
    buy_and_hold_return_pct: float
    vs_buy_and_hold_pp: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown_pct: float
    calmar_ratio: float
    win_rate_pct: float
    profit_factor: float
    n_hold: int
    n_buy: int
    n_sell: int
    initial_capital: float
    final_portfolio: float
    report_text: str


class HealthResponse(BaseModel):
    status: str
    models_loaded: List[str]
    timestamp: str
    version: str = "2.0.0"
    data_mode: str = "DEMO"


# --- AUTH & USER SCHEMAS ---

class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    role: str
    created_at: Optional[datetime] = None

class WatchlistAdd(BaseModel):
    stock_symbol: str
    exchange: Optional[str] = "NSE"

class WatchlistResponse(BaseModel):
    id: int
    stock_symbol: str
    exchange: str
    added_at: Optional[datetime] = None
    latest_signal: Optional[StockSignalSummary] = None

class StockSearchItem(BaseModel):
    symbol: str
    name: str
    exchange: str
    sector: str
    category: str
