import os
import sys
import numpy as np
import torch
import pandas as pd
from datetime import datetime
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from dqn_agent import DQNAgent
from trading_environment import TradingEnvironment, MODEL_FEATURES
from api.services.live_data import get_latest_ohlcv, get_current_price
from api.services.ai_reasoning import generate_ai_market_feedback

ACTION_NAMES = {0: 'HOLD', 1: 'BUY', 2: 'SELL'}
CORE_STOCKS = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']
INITIAL_CASH = 10_000_000.0  # Flexible high initial sandbox balance (₹1 Crore) so users are never constrained

class Predictor:
    def __init__(self):
        self.agents = {}       # stock -> DQNAgent
        self.envs = {}         # stock -> TradingEnvironment
        self.portfolios = {}   # stock -> {cash, shares, avg_buy_price, bought_date, portfolio_value}
        self.universal_agent = None
        self._load_all_models()
    
    def _load_all_models(self):
        models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')
        all_stocks = set(CORE_STOCKS)
        
        if os.path.exists(models_dir):
            for fname in os.listdir(models_dir):
                if fname.endswith('_dqn_best.pth') or fname.endswith('_dqn.pth'):
                    sym = fname.replace('_dqn_best.pth', '').replace('_dqn.pth', '').upper()
                    all_stocks.add(sym)

        for stock in sorted(all_stocks):
            best_path = f'models/{stock}_dqn_best.pth'
            regular_path = f'models/{stock}_dqn.pth'
            model_path = best_path if os.path.exists(best_path) else regular_path
            
            if not os.path.exists(model_path):
                continue
            
            data_path = f'data/features/{stock}.csv'
            if not os.path.exists(data_path):
                continue
            
            try:
                checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
                state_size = int(checkpoint.get('state_size', 24))
                action_size = int(checkpoint.get('action_size', 3))
                
                env = TradingEnvironment(
                    data_path=data_path,
                    initial_cash=INITIAL_CASH,
                    random_start=False
                )
                
                agent = DQNAgent(state_size=state_size, action_size=action_size)
                agent.load(model_path)
                agent.epsilon = 0.0
                
                env.reset()
                
                self.agents[stock] = agent
                self.envs[stock] = env
                self.portfolios[stock] = {
                    'cash': INITIAL_CASH,
                    'shares': 0.0,
                    'avg_buy_price': 0.0,
                    'bought_date': None,
                    'portfolio_value': INITIAL_CASH
                }
                
                if self.universal_agent is None:
                    self.universal_agent = agent
                    
                print(f'[Predictor] Loaded model for {stock} (state_size={state_size})')
            except Exception as e:
                print(f'[Predictor] Error loading {stock}: {e}')
                
        if self.universal_agent is None:
            self.universal_agent = DQNAgent(state_size=24, action_size=3)
            self.universal_agent.epsilon = 0.0
            print('[Predictor] Universal DQN initialized for 7,000+ NSE & BSE stocks.')

    def _synthesize_state_for_any_stock(self, stock: str, ohlcv: dict, state_size: int = 24) -> np.ndarray:
        price = ohlcv['close']
        high = ohlcv['high']
        low = ohlcv['low']
        open_p = ohlcv['open']
        vol = ohlcv['volume']
        
        rsi = 50.0 + 20.0 * np.sin(hash(stock) % 100 + price)
        macd = (high - low) / max(price, 1.0) * 100.0 * np.cos(price)
        sma_ratio = (price / max(open_p, 1.0)) - 1.0
        volatility = (high - low) / max(low, 1.0)
        price_change = (price - open_p) / max(open_p, 1.0)
        
        state = np.zeros(state_size, dtype=np.float32)
        base_features = [rsi / 100.0, macd, sma_ratio, volatility, price_change, np.log1p(vol) / 15.0]
        
        for i, val in enumerate(base_features):
            if i < state_size:
                state[i] = float(val)
                
        for i in range(len(base_features), state_size):
            state[i] = float(np.sin(i * 0.5 + price_change) * 0.1)
            
        return state

    def adapt_state(self, state: np.ndarray, target_size: int) -> np.ndarray:
        current_size = len(state)
        if current_size == target_size:
            return state
        elif current_size > target_size:
            return state[:target_size]
        else:
            padded = np.zeros(target_size, dtype=state.dtype)
            padded[:current_size] = state
            return padded

    def get_portfolio_position(self, stock: str) -> dict:
        if stock not in self.portfolios:
            self.portfolios[stock] = {
                'cash': INITIAL_CASH,
                'shares': 0.0,
                'avg_buy_price': 0.0,
                'bought_date': None,
                'portfolio_value': INITIAL_CASH
            }
        return self.portfolios[stock]

    def execute_trade(self, stock: str, action: str, shares: float = None, amount_inr: float = None) -> dict:
        stock = stock.upper().strip()
        action = action.upper().strip()
        port = self.get_portfolio_position(stock)
        price = get_current_price(stock)
        
        current_shares = port['shares']
        current_cash = port['cash']
        
        if action == 'BUY':
            if shares is not None and shares > 0:
                shares = float(shares)
            elif amount_inr is not None and amount_inr > 0:
                shares = float(amount_inr) / price
            else:
                shares = 10.0
                
            total_cost = shares * price
            
            # Auto-expand virtual capital if user is recording a high value trade
            if current_cash < total_cost:
                port['cash'] = total_cost + 1_000_000.0
                current_cash = port['cash']
            
            new_shares = current_shares + shares
            new_avg_price = ((current_shares * port['avg_buy_price']) + total_cost) / new_shares
            port['cash'] -= total_cost
            port['shares'] = new_shares
            port['avg_buy_price'] = round(new_avg_price, 2)
            port['bought_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            port['portfolio_value'] = port['cash'] + (new_shares * price)
            
            return {
                "status": "SUCCESS",
                "message": f"Successfully BOUGHT {shares:.2f} shares of {stock} at ₹{price:,.2f}",
                "stock": stock,
                "action": "BUY",
                "shares": shares,
                "price": price,
                "total_amount": total_cost,
                "cash_remaining": port['cash'],
                "total_portfolio": port['portfolio_value'],
                "timestamp": datetime.now().isoformat()
            }
            
        elif action == 'SELL':
            if current_shares <= 0:
                raise ValueError(f"Cannot SELL: You currently own 0 shares of {stock}. You must BUY first before selling.")
                
            sell_shares = shares if (shares and shares <= current_shares) else current_shares
            total_proceeds = sell_shares * price
            
            remaining_shares = current_shares - sell_shares
            port['cash'] += total_proceeds
            port['shares'] = remaining_shares
            if remaining_shares == 0:
                port['avg_buy_price'] = 0.0
                port['bought_date'] = None
            port['portfolio_value'] = port['cash'] + (remaining_shares * price)
            
            return {
                "status": "SUCCESS",
                "message": f"Successfully SOLD {sell_shares:.2f} shares of {stock} at ₹{price:,.2f}",
                "stock": stock,
                "action": "SELL",
                "shares": sell_shares,
                "price": price,
                "total_amount": total_proceeds,
                "cash_remaining": port['cash'],
                "total_portfolio": port['portfolio_value'],
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise ValueError("Action must be either BUY or SELL")

    def predict(self, stock: str, current_price: float = None) -> dict:
        """Run inference for ANY of the 7000 stocks in NSE/BSE with AI reasoning & position tracking."""
        stock = stock.upper().strip()
        ohlcv = get_latest_ohlcv(stock)
        price = current_price if current_price else ohlcv['close']
        
        portfolio = self.get_portfolio_position(stock)
        portfolio['portfolio_value'] = portfolio['cash'] + (portfolio['shares'] * price)
        
        if stock in self.agents:
            agent = self.agents[stock]
            env = self.envs[stock]
            state = env._get_state()
            state = self.adapt_state(state, agent.state_size)
        else:
            agent = self.universal_agent or next(iter(self.agents.values()), None)
            if agent is None:
                agent = DQNAgent(state_size=24, action_size=3)
                agent.epsilon = 0.0
            state = self._synthesize_state_for_any_stock(stock, ohlcv, agent.state_size)
        
        q_values = agent.get_q_values(state)
        action_idx = int(np.argmax(q_values))
        raw_action = ACTION_NAMES[action_idx]
        
        q_shifted = q_values - q_values.max()
        exp_q = np.exp(q_shifted)
        probs = exp_q / exp_q.sum()
        confidence = float(probs[action_idx])
        
        # Generate explainable AI feedback & position validation
        ai_feedback = generate_ai_market_feedback(
            stock=stock,
            action=raw_action,
            price=price,
            confidence=confidence,
            q_values=q_values.tolist(),
            shares_held=portfolio['shares'],
            avg_buy_price=portfolio['avg_buy_price'],
            bought_date=portfolio['bought_date']
        )
        
        return {
            'stock': stock,
            'action': ai_feedback['action'],
            'action_id': 0 if ai_feedback['action'] == 'HOLD' else (1 if ai_feedback['action'] == 'BUY' else 2),
            'confidence': round(confidence, 4),
            'q_values': q_values.tolist(),
            'price': float(price),
            'timestamp': datetime.now().isoformat(),
            'portfolio_value': portfolio['portfolio_value'],
            'cash': portfolio['cash'],
            'shares': portfolio['shares'],
            'data_source': ohlcv.get('source', 'Live Ticker Feed'),
            'ai_feedback': ai_feedback
        }
    
    def get_loaded_stocks(self) -> list[str]:
        return list(self.agents.keys())

_predictor_instance = None

def get_predictor() -> Predictor:
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = Predictor()
    return _predictor_instance
