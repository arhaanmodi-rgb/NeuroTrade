import sys
import os
import pandas as pd
import torch
import numpy as np
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding='utf-8')

from trading_environment import TradingEnvironment
from dqn_agent import DQNAgent
from metrics import compute_all_metrics

STOCK = "RELIANCE"
DATA_FILE = f"data/features/{STOCK}.csv"
TEST_FILE = f"data/features/{STOCK}_test.csv"
MODEL_FILE = f"models/{STOCK}_dqn_best.pth"

def main():
    os.makedirs('results', exist_ok=True)
    
    if not os.path.exists(TEST_FILE):
        df = pd.read_csv(DATA_FILE)
        split_index = int(len(df) * 0.8)
        test_df = df.iloc[split_index:].copy()
        test_df.to_csv(TEST_FILE, index=False)
    else:
        test_df = pd.read_csv(TEST_FILE)

    if len(test_df) < 250:
        df = pd.read_csv(DATA_FILE)
        test_df = df.iloc[-300:].copy()
        test_df.to_csv(TEST_FILE, index=False)

    checkpoint = torch.load(MODEL_FILE, map_location='cpu', weights_only=False)
    checkpoint_state_size = checkpoint['state_size']
    action_size = checkpoint['action_size']

    agent = DQNAgent(state_size=checkpoint_state_size, action_size=action_size)
    agent.load(MODEL_FILE)
    agent.epsilon = 0.0

    env = TradingEnvironment(TEST_FILE, random_start=False)

    def adapt_state(state, expected_size):
        if len(state) == expected_size:
            return state
        elif len(state) > expected_size:
            return state[:expected_size]
        else:
            pad = np.zeros(expected_size - len(state), dtype=np.float32)
            return np.concatenate((state, pad))

    state = env.reset()
    if isinstance(state, tuple):
        state = state[0]
    state = np.asarray(state, dtype=np.float32)

    done = False
    portfolio_values = [env.portfolio_value]
    actions = []
    rewards = []
    prices = [env.prices[env.current_step]]
    dates = [test_df['trade_date'].iloc[env.current_step] if 'trade_date' in test_df.columns else str(env.current_step)]

    while not done:
        adapted_state = adapt_state(state, checkpoint_state_size)
        action = agent.act(adapted_state, training=False)
        
        res = env.step(action)
        if len(res) == 4:
            next_state, reward, done, info = res
        else:
            next_state, reward, terminated, truncated, info = res
            done = terminated or truncated
            
        state = np.asarray(next_state, dtype=np.float32)
        
        pv = info.get('portfolio_value', env.portfolio_value)
        portfolio_values.append(pv)
        actions.append(action)
        rewards.append(reward)
        p = info.get('price', env.prices[env.current_step] if env.current_step < len(env.prices) else env.prices[-1])
        prices.append(p)
        
        if not done:
            dates.append(test_df['trade_date'].iloc[env.current_step] if 'trade_date' in test_df.columns else str(env.current_step))

    # Calculate metrics
    start_price = prices[0]
    end_price = prices[-1]
    initial_cash = portfolio_values[0]

    metrics = compute_all_metrics(portfolio_values, actions, rewards, initial_cash, start_price, end_price)
    
    total_actions = len(actions)
    hold_c = actions.count(0)
    buy_c = actions.count(1)
    sell_c = actions.count(2)

    report = f"""
{'='*50}
Validation Summary
{'='*50}
Initial Capital:        ₹{initial_cash:,.2f}
Final Portfolio:        ₹{portfolio_values[-1]:,.2f}
Total Return:           {metrics.get('total_return', 0)*100:.2f}%
Annualised Return:      {metrics.get('annualised_return', 0)*100:.2f}%
Buy-and-Hold Return:    {metrics.get('buy_and_hold_return', 0)*100:.2f}%
vs Buy-and-Hold:        {(metrics.get('total_return', 0) - metrics.get('buy_and_hold_return', 0))*100:.2f} percentage points

Sharpe Ratio:           {metrics.get('sharpe_ratio', 0):.2f}
Sortino Ratio:          {metrics.get('sortino_ratio', 0):.2f}
Max Drawdown:           {metrics.get('max_drawdown', 0)*100:.2f}%
Calmar Ratio:           {metrics.get('calmar_ratio', 0):.2f}

Win Rate:               {metrics.get('win_rate', 0)*100:.2f}%
Profit Factor:          {metrics.get('profit_factor', 0):.2f}

Action Counts:
HOLD: {hold_c} ({hold_c/total_actions*100:.1f}%)
BUY:  {buy_c} ({buy_c/total_actions*100:.1f}%)
SELL: {sell_c} ({sell_c/total_actions*100:.1f}%)
{'='*50}
"""
    print(report)
    
    with open('results/RELIANCE_validation_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)

    # Equity curve plot
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bh_values = [initial_cash * (p / start_price) for p in prices]
    
    ax.plot(portfolio_values, label='Agent Portfolio Value', color='cyan')
    ax.plot(bh_values, label='Buy-and-Hold Value', color='orange', alpha=0.7)
    
    buy_x = [i for i, a in enumerate(actions) if a == 1]
    buy_y = [portfolio_values[i+1] for i in buy_x]
    
    sell_x = [i for i, a in enumerate(actions) if a == 2]
    sell_y = [portfolio_values[i+1] for i in sell_x]
    
    ax.scatter(buy_x, buy_y, marker='^', color='green', s=100, label='BUY')
    ax.scatter(sell_x, sell_y, marker='v', color='red', s=100, label='SELL')
    
    ax.set_title('Validation Equity Curve')
    ax.set_xlabel('Steps')
    ax.set_ylabel('Portfolio Value (₹)')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.savefig('results/RELIANCE_validation.png', dpi=150, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    main()
