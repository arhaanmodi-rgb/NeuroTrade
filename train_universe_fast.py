import os
import sys
import time
import pandas as pd
import numpy as np
import torch
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed

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

def download_stock(sym: str) -> bool:
    csv_path = os.path.join(RAW_DIR, f"{sym}.csv")
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 3000:
        return True

    try:
        import yfinance as yf
        for ext in [".NS", ".BO"]:
            ticker = yf.Ticker(f"{sym}{ext}")
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

def build_features(sym: str) -> bool:
    raw_path = os.path.join(RAW_DIR, f"{sym}.csv")
    feat_path = os.path.join(FEAT_DIR, f"{sym}.csv")

    if os.path.exists(feat_path):
        try:
            df = pd.read_csv(feat_path)
            if all(c in df.columns for c in MODEL_FEATURES) and len(df) > 50:
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
        features.to_csv(feat_path, index=False)
        return True
    except Exception:
        return False

def train_single_stock(sym: str) -> tuple[str, bool, str]:
    model_path = os.path.join(MODELS_DIR, f"{sym}_dqn_best.pth")
    if os.path.exists(model_path) and os.path.getsize(model_path) > 40000:
        return (sym, True, "Already trained")

    # 1. Download
    dl_ok = download_stock(sym)
    if not dl_ok:
        return (sym, False, "Download failed")

    # 2. Features
    feat_ok = build_features(sym)
    if not feat_ok:
        return (sym, False, "Feature computation failed")

    feat_path = os.path.join(FEAT_DIR, f"{sym}.csv")
    try:
        env = TradingEnvironment(data_path=feat_path, initial_cash=1_000_000.0, random_start=True)
        agent = DQNAgent(state_size=env.state_size, action_size=env.action_size)
        best_val = 0.0

        for ep in range(1, 16):
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
            val = info.get('portfolio_value', 0.0)
            if val > best_val:
                best_val = val
                agent.save(model_path)

        if not os.path.exists(model_path):
            agent.save(model_path)

        return (sym, True, f"Trained (Portfolio: ₹{best_val:,.0f})")
    except Exception as e:
        return (sym, False, str(e))

def main():
    stocks = [s["symbol"] for s in STOCK_DIRECTORY]
    print(f"🚀 TURBO HIGH-SPEED TRAINING: Starting parallel training for {len(stocks)} stocks...")

    start_time = time.time()
    
    # Run multi-worker parallel execution
    workers = min(4, os.cpu_count() or 4)
    print(f"⚡ Utilizing {workers} parallel CPU training workers\n")

    completed = 0
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(train_single_stock, sym): sym for sym in stocks}
        for future in as_completed(futures):
            sym, ok, msg = future.result()
            completed += 1
            status_icon = "✅" if ok else "❌"
            print(f"[{completed:2d}/{len(stocks)}] {status_icon} {sym:12} -> {msg}", flush=True)

    elapsed = round(time.time() - start_time, 1)
    print(f"\n🎉 ALL TRAINING COMPLETE in {elapsed}s!")

if __name__ == "__main__":
    main()
