import os
import sys
import time
import pandas as pd
import numpy as np
import torch

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
FEAT_DIR = os.path.join(BASE_DIR, "data", "features")
MODELS_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(FEAT_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

from api.services.stock_universe import STOCK_DIRECTORY
from feature_engineering import create_features, MODEL_FEATURES
from dqn_agent import DQNAgent
from trading_environment import TradingEnvironment

SYMBOL_ALIASES = {
    "TATAMOTORS": ["TATAMOTORS.NS", "TATAMTR.NS", "500570.BO"],
    "M&M": ["M&M.NS", "500520.BO"],
    "L&TFH": ["L&TFH.NS", "533519.BO"],
    "BAJAJ-AUTO": ["BAJAJ-AUTO.NS", "532977.BO"]
}

def download_stock_history(sym: str) -> bool:
    """Download 5 years of daily OHLCV candlestick data."""
    csv_path = os.path.join(RAW_DIR, f"{sym}.csv")
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 5000:
        return True

    try:
        import yfinance as yf
        candidates = SYMBOL_ALIASES.get(sym, [f"{sym}.NS", f"{sym}.BO"])
        for yf_sym in candidates:
            ticker = yf.Ticker(yf_sym)
            hist = ticker.history(period="5y", interval="1d")
            if not hist.empty and len(hist) > 50:
                hist.reset_index(inplace=True)
                hist.rename(columns={
                    "Date": "trade_date",
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "volume"
                }, inplace=True)
                hist["symbol"] = sym
                hist["trade_date"] = hist["trade_date"].dt.strftime("%Y-%m-%d")
                hist[["trade_date", "open", "high", "low", "close", "volume", "symbol"]].to_csv(csv_path, index=False)
                return True
    except Exception:
        pass
    return False

def compute_technical_features(sym: str) -> bool:
    """Computes technical indicators using create_features."""
    raw_path = os.path.join(RAW_DIR, f"{sym}.csv")
    feat_path = os.path.join(FEAT_DIR, f"{sym}.csv")
    
    if os.path.exists(feat_path):
        try:
            df_existing = pd.read_csv(feat_path)
            # Check if all MODEL_FEATURES exist
            if all(col in df_existing.columns for col in MODEL_FEATURES) and len(df_existing) > 50:
                return True
        except Exception:
            pass

    if not os.path.exists(raw_path):
        return False

    try:
        df = pd.read_csv(raw_path)
        if len(df) < 50:
            return False

        features = create_features(df)
        if features is None or len(features) < 10:
            return False

        # Verify all required features exist
        missing = [c for c in MODEL_FEATURES if c not in features.columns]
        if missing:
            print(f"  [Missing features {sym}]: {missing}")
            return False

        features.to_csv(feat_path, index=False)
        return True
    except Exception as e:
        print(f"  [Feature Error {sym}]: {e}")
        return False

def train_dqn_agent(sym: str, episodes: int = 30) -> bool:
    """Trains a Deep Q-Network for the given stock and saves the weights."""
    model_path = os.path.join(MODELS_DIR, f"{sym}_dqn_best.pth")
    if os.path.exists(model_path) and os.path.getsize(model_path) > 50000:
        return True

    feat_path = os.path.join(FEAT_DIR, f"{sym}.csv")
    if not os.path.exists(feat_path):
        return False

    try:
        env = TradingEnvironment(data_path=feat_path, initial_cash=1_000_000.0, random_start=True)
        state_size = env.state_size
        action_size = env.action_size

        agent = DQNAgent(state_size=state_size, action_size=action_size)
        best_portfolio_val = 0.0

        for ep in range(1, episodes + 1):
            state = env.reset()
            done = False

            while not done:
                action = agent.act(state)
                next_state, reward, done, info = env.step(action)
                agent.remember(state, action, reward, next_state, done)
                state = next_state

                if len(agent.memory) > 64:
                    agent.replay()

            agent.decay_epsilon()
            final_val = info.get('portfolio_value', 0.0)

            if final_val > best_portfolio_val:
                best_portfolio_val = final_val
                agent.save(model_path)

        if not os.path.exists(model_path):
            agent.save(model_path)

        return True
    except Exception as e:
        print(f"  [Train Error {sym}]: {e}")
        return False

def main():
    stocks = [s["symbol"] for s in STOCK_DIRECTORY]
    print(f"Starting Multi-Stock Training Pipeline for {len(stocks)} Verified Indian Equities...")

    trained_count = 0
    for i, sym in enumerate(stocks, 1):
        print(f"[{i}/{len(stocks)}] Processing {sym}...", end=" ", flush=True)
        
        # 1. Download
        dl_ok = download_stock_history(sym)
        if not dl_ok:
            print("❌ Download failed")
            continue

        # 2. Features
        feat_ok = compute_technical_features(sym)
        if not feat_ok:
            print("❌ Features failed")
            continue

        # 3. Train
        train_ok = train_dqn_agent(sym, episodes=25)
        if train_ok:
            print("✅ Trained & Saved!")
            trained_count += 1
        else:
            print("❌ Training failed")

    print(f"\nCompleted! Successfully trained models for {trained_count}/{len(stocks)} stocks.")

if __name__ == "__main__":
    main()
