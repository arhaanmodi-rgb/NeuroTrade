# -*- coding: utf-8 -*-
"""
NeuroTrade Live Predictor
Runs DQN inference on all trained stocks and announces signals.

Usage:
    python live_predictor.py           # run every 60 seconds
    python live_predictor.py --once    # run once and exit
    python live_predictor.py --stock RELIANCE --once
    python live_predictor.py --no-voice
"""

import sys
import os
import argparse
import time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import torch

from dqn_agent import DQNAgent
from trading_environment import TradingEnvironment
from voice.speaker import get_speaker
from api.services.live_data import get_current_price
from api.services.trade_log import init_db, log_trade


# ============================================================
# CONFIGURATION
# ============================================================

ALL_STOCKS = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']
INITIAL_CASH = 100_000.0
ACTION_NAMES = {0: 'HOLD', 1: 'BUY', 2: 'SELL'}
POLL_INTERVAL = 60  # seconds


# ============================================================
# CLI ARGUMENTS
# ============================================================

parser = argparse.ArgumentParser(description='NeuroTrade Live Predictor')
parser.add_argument('--stock', type=str, default=None, help='Single stock to predict (default: all)')
parser.add_argument('--once', action='store_true', help='Run once and exit')
parser.add_argument('--no-voice', action='store_true', help='Disable voice output')
parser.add_argument('--announce-hold', action='store_true', help='Also announce HOLD signals')
args = parser.parse_args()

STOCKS = [args.stock.upper()] if args.stock else ALL_STOCKS


# ============================================================
# HELPER
# ============================================================

def adapt_state(state: np.ndarray, target_size: int) -> np.ndarray:
    state = np.asarray(state, dtype=np.float32)
    if len(state) == target_size:
        return state
    if len(state) > target_size:
        return state[:target_size]
    padded = np.zeros(target_size, dtype=np.float32)
    padded[:len(state)] = state
    return padded


# ============================================================
# LOAD MODELS
# ============================================================

def load_models(stocks):
    agents = {}
    envs = {}

    for stock in stocks:
        best_path = f'models/{stock}_dqn_best.pth'
        regular_path = f'models/{stock}_dqn.pth'
        model_path = best_path if os.path.exists(best_path) else regular_path
        data_path = f'data/features/{stock}.csv'

        if not os.path.exists(model_path):
            print(f'  [SKIP] {stock}: model not found')
            continue
        if not os.path.exists(data_path):
            print(f'  [SKIP] {stock}: feature data not found')
            continue

        try:
            checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
            state_size = int(checkpoint.get('state_size', 24))
            action_size = int(checkpoint.get('action_size', 3))

            env = TradingEnvironment(data_path=data_path, initial_cash=INITIAL_CASH, random_start=False)
            env.reset()

            agent = DQNAgent(state_size=state_size, action_size=action_size)
            agent.load(model_path)
            agent.epsilon = 0.0

            agents[stock] = agent
            envs[stock] = env
            print(f'  [OK] {stock} loaded (state_size={state_size})')
        except Exception as e:
            print(f'  [ERROR] {stock}: {e}')

    return agents, envs


# ============================================================
# RUN PREDICTIONS
# ============================================================

def run_predictions(agents, envs, speaker):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print()
    print('=' * 60)
    print(f'  NEUROTRADE SIGNALS  |  {timestamp}')
    print('=' * 60)

    for stock, agent in agents.items():
        try:
            env = envs[stock]
            state = env._get_state()
            state = adapt_state(state, agent.state_size)

            q_values = agent.get_q_values(state)
            action = int(np.argmax(q_values))
            action_name = ACTION_NAMES[action]

            # Softmax confidence
            q_shifted = q_values - q_values.max()
            probs = np.exp(q_shifted) / np.exp(q_shifted).sum()
            confidence = float(probs[action])

            # Get price
            try:
                price = get_current_price(stock)
            except Exception:
                step_idx = min(env.current_step, len(env.prices) - 1)
                price = float(env.prices[step_idx])

            # Print
            signal_color = {'BUY': '\033[92m', 'SELL': '\033[91m', 'HOLD': '\033[93m'}.get(action_name, '')
            reset = '\033[0m'
            print(f'  {stock:<12} {signal_color}{action_name:<5}{reset}  Price: \u20b9{price:>10,.2f}  Confidence: {confidence*100:5.1f}%')
            print(f'              Q[HOLD={q_values[0]:+.4f}  BUY={q_values[1]:+.4f}  SELL={q_values[2]:+.4f}]')

            # Voice announcement
            speaker.speak_signal(stock, action_name, price, confidence)

            # Log BUY/SELL to DB
            if action_name in ('BUY', 'SELL'):
                portfolio_value = float(env.cash + env.shares * price)
                log_trade(
                    stock=stock,
                    action=action_name,
                    price=price,
                    shares=float(env.shares),
                    portfolio_value=portfolio_value,
                    cash=float(env.cash),
                    timestamp=datetime.now().isoformat()
                )

        except Exception as e:
            print(f'  [ERROR] {stock}: {e}')

    print('=' * 60)


# ============================================================
# MAIN
# ============================================================

def main():
    print()
    print('=' * 60)
    print('       NEUROTRADE LIVE PREDICTOR')
    print('=' * 60)
    print()

    # Init DB
    init_db()

    # Init voice
    speaker = get_speaker(announce_hold=args.announce_hold)
    if args.no_voice:
        speaker.set_enabled(False)
        print('[Voice] Disabled by --no-voice flag')
    else:
        print(f'[Voice] TTS {"enabled" if speaker.enabled else "unavailable (install pyttsx3)"}')

    # Load models
    print()
    print('Loading models...')
    agents, envs = load_models(STOCKS)

    if not agents:
        print('[ERROR] No models loaded. Train models first with train_dqn.py')
        sys.exit(1)

    print(f'\nLoaded {len(agents)} model(s): {list(agents.keys())}')

    # Speak startup
    if not args.no_voice:
        speaker.speak_alert(f'NeuroTrade started. Monitoring {len(agents)} stocks.')

    # Run
    if args.once:
        run_predictions(agents, envs, speaker)
    else:
        print(f'\nPolling every {POLL_INTERVAL} seconds. Press Ctrl+C to stop.')
        while True:
            run_predictions(agents, envs, speaker)
            time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n[NeuroTrade] Stopped.')
