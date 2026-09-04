import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from trading_environment import TradingEnvironment
from dqn_agent import DQNAgent


# ============================================================
# CONFIGURATION
# ============================================================

STOCK = "RELIANCE"

DATA_FILE = f"data/features/{STOCK}.csv"

MODEL_FILE = f"models/{STOCK}_dqn.pth"

INITIAL_CASH = 100000.0

TRANSACTION_COST = 0.001


# ============================================================
# HEADER
# ============================================================

print()

print("=" * 70)

print(
    "                 NEUROTRADE BACKTEST"
)

print("=" * 70)

print()


# ============================================================
# CHECK FILES
# ============================================================

if not os.path.exists(DATA_FILE):

    raise FileNotFoundError(
        f"Dataset not found:\n{DATA_FILE}"
    )


if not os.path.exists(MODEL_FILE):

    raise FileNotFoundError(
        f"Trained model not found:\n{MODEL_FILE}\n\n"
        "Train the model first using train_dqn.py."
    )


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(
    DATA_FILE
)

print(
    "Total rows:",
    len(df)
)


if df.empty:

    raise ValueError(
        "Dataset is empty."
    )


# ============================================================
# FIND DATE COLUMN
# ============================================================

date_column = None

for column in [
    "trade_date",
    "date",
    "Date"
]:

    if column in df.columns:

        date_column = column

        break


# ============================================================
# FIND PRICE COLUMN
# ============================================================

price_column = None

for column in [
    "close",
    "Close",
    "CLOSE",
    "adj_close",
    "Adj Close",
    "Adj_Close"
]:

    if column in df.columns:

        price_column = column

        break


if price_column is None:

    raise ValueError(
        "Could not find a close price column."
    )


# ============================================================
# CLEAN DATA
# ============================================================

df = df.replace(
    [np.inf, -np.inf],
    np.nan
)

df = df.dropna(
    subset=[price_column]
)

df = df.reset_index(
    drop=True
)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

split_index = int(
    len(df) * 0.80
)

train_df = df.iloc[
    :split_index
].copy()

test_df = df.iloc[
    split_index:
].copy()


print()

print("=" * 70)

print(
    "                    DATA SPLIT"
)

print("=" * 70)

print()

print(
    f"Training rows : {len(train_df)}"
)

print(
    f"Testing rows  : {len(test_df)}"
)


if date_column is not None:

    print()

    print(
        "Training period:"
    )

    print(
        train_df[
            date_column
        ].iloc[0],

        "->",

        train_df[
            date_column
        ].iloc[-1]
    )

    print()

    print(
        "Testing period:"
    )

    print(
        test_df[
            date_column
        ].iloc[0],

        "->",

        test_df[
            date_column
        ].iloc[-1]
    )


# ============================================================
# SAVE TEST DATA
# ============================================================

TEST_FILE = (
    f"data/features/{STOCK}_test.csv"
)

os.makedirs(
    "data/features",
    exist_ok=True
)

test_df.to_csv(
    TEST_FILE,
    index=False
)


# ============================================================
# CREATE ENVIRONMENT
# ============================================================

print()

print(
    "Creating test environment..."
)

env = TradingEnvironment(

    TEST_FILE,

    initial_cash=INITIAL_CASH,

    transaction_cost=TRANSACTION_COST,

    random_start=False
)


# ============================================================
# RESET ENVIRONMENT
# ============================================================

reset_result = env.reset()


# Support both:

# state

# and

# (state, info)

if isinstance(
    reset_result,
    tuple
):

    state = reset_result[0]

else:

    state = reset_result


state = np.asarray(
    state,
    dtype=np.float32
)


# ============================================================
# STATE / ACTION SIZE
# ============================================================

STATE_SIZE = len(
    state
)

ACTION_SIZE = 3


print()

print(
    "State size:",
    STATE_SIZE
)

print(
    "Action size:",
    ACTION_SIZE
)

print()

print(
    "Actions:"
)

print(
    "0 = HOLD"
)

print(
    "1 = BUY"
)

print(
    "2 = SELL"
)


# ============================================================
# CREATE DQN AGENT
# ============================================================

agent = DQNAgent(

    state_size=STATE_SIZE,

    action_size=ACTION_SIZE
)


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

print()

print(
    "Loading trained model..."
)

agent.load(
    MODEL_FILE
)

print(
    "Model loaded successfully."
)


# ============================================================
# DISABLE EXPLORATION
# ============================================================

agent.epsilon = 0.0

print()

print(
    "Exploration disabled."
)

print(
    "Backtest is using learned policy only."
)


# ============================================================
# BACKTEST VARIABLES
# ============================================================

done = False

actions = []

portfolio_values = []

prices = []

rewards = []

q_value_history = []

cash_history = []

shares_history = []

dates = []

step = 0


# ============================================================
# BACKTEST LOOP
# ============================================================

while not done:

    step += 1


    # --------------------------------------------------------
    # GET Q VALUES
    # --------------------------------------------------------

    q_values = agent.get_q_values(
        state
    )


    # --------------------------------------------------------
    # CHOOSE ACTION
    # --------------------------------------------------------

    action = agent.choose_action(
        state,
        training=False
    )

    action = int(
        action
    )


    # --------------------------------------------------------
    # VALIDATE Q VALUES
    # --------------------------------------------------------

    if len(q_values) != 3:

        raise ValueError(
            "DQN returned an unexpected number "
            "of Q-values."
        )


    # --------------------------------------------------------
    # SAVE Q VALUES
    # --------------------------------------------------------

    q_value_history.append(
        q_values.copy()
    )


    # --------------------------------------------------------
    # PRINT FIRST 10 DECISIONS
    # --------------------------------------------------------

    if step <= 10:

        print()

        print(
            f"Step {step}:"
        )

        print(
            f"    HOLD = {q_values[0]:.6f}"
        )

        print(
            f"    BUY  = {q_values[1]:.6f}"
        )

        print(
            f"    SELL = {q_values[2]:.6f}"
        )


        # Show highest Q-value

        best_action = int(
            np.argmax(q_values)
        )


        if best_action == 0:

            best_name = "HOLD"

        elif best_action == 1:

            best_name = "BUY"

        else:

            best_name = "SELL"


        print(
            f"    HIGHEST Q = {best_name}"
        )


        if action == 0:

            print(
                "    ACTION = HOLD"
            )

        elif action == 1:

            print(
                "    ACTION = BUY"
            )

        elif action == 2:

            print(
                "    ACTION = SELL"
            )


    # --------------------------------------------------------
    # ENVIRONMENT STEP
    # --------------------------------------------------------

    result = env.step(
        action
    )


    # --------------------------------------------------------
    # SUPPORT 4 AND 5 VALUE ENVIRONMENTS
    # --------------------------------------------------------

    if len(result) == 4:

        next_state, reward, done, info = result

    elif len(result) == 5:

        (
            next_state,
            reward,
            terminated,
            truncated,
            info
        ) = result

        done = (
            terminated
            or
            truncated
        )

    else:

        raise ValueError(
            "Unexpected environment.step() output."
        )


    # --------------------------------------------------------
    # STORE ACTION
    # --------------------------------------------------------

    actions.append(
        action
    )


    # --------------------------------------------------------
    # STORE REWARD
    # --------------------------------------------------------

    rewards.append(
        float(reward)
    )


    # --------------------------------------------------------
    # STORE INFO
    # --------------------------------------------------------

    if isinstance(
        info,
        dict
    ):

        portfolio_value = info.get(
            "portfolio_value",
            info.get(
                "net_worth",
                INITIAL_CASH
            )
        )

        price = info.get(
            "price",
            np.nan
        )

        cash = info.get(
            "cash",
            np.nan
        )

        shares = info.get(
            "shares",
            info.get(
                "position",
                np.nan
            )
        )

    else:

        portfolio_value = INITIAL_CASH

        price = np.nan

        cash = np.nan

        shares = np.nan


    # --------------------------------------------------------
    # SAVE PORTFOLIO DATA
    # --------------------------------------------------------

    portfolio_values.append(
        float(
            portfolio_value
        )
    )

    prices.append(
        float(
            price
        )
    )

    cash_history.append(
        float(
            cash
        )
    )

    shares_history.append(
        float(
            shares
        )
    )


    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    test_index = step - 1


    if test_index < len(test_df):

        if date_column is not None:

            dates.append(
                test_df[
                    date_column
                ].iloc[
                    test_index
                ]
            )

        else:

            dates.append(
                test_index
            )


    # --------------------------------------------------------
    # NEXT STATE
    # --------------------------------------------------------

    state = np.asarray(
        next_state,
        dtype=np.float32
    )


# ============================================================
# CHECK RESULT
# ============================================================

if len(
    portfolio_values
) == 0:

    raise RuntimeError(
        "No portfolio values were generated."
    )


# ============================================================
# FINAL PORTFOLIO VALUE
# ============================================================

final_value = float(
    portfolio_values[-1]
)


profit = (

    final_value

    -

    INITIAL_CASH
)


return_percent = (

    profit

    /

    INITIAL_CASH

    *

    100
)


# ============================================================
# BUY AND HOLD
# ============================================================

start_price = float(

    test_df[
        price_column
    ].iloc[0]

)


end_price = float(

    test_df[
        price_column
    ].iloc[-1]

)


buy_hold_value = (

    INITIAL_CASH

    *

    end_price

    /

    start_price

)


buy_hold_profit = (

    buy_hold_value

    -

    INITIAL_CASH
)


buy_hold_return = (

    buy_hold_profit

    /

    INITIAL_CASH

    *

    100
)


# ============================================================
# ACTION COUNTS
# ============================================================

hold_count = sum(

    1

    for action in actions

    if action == 0
)


buy_count = sum(

    1

    for action in actions

    if action == 1
)


sell_count = sum(

    1

    for action in actions

    if action == 2
)


total_actions = len(
    actions
)


# ============================================================
# ACTION PERCENTAGES
# ============================================================

if total_actions > 0:

    hold_percent = (

        hold_count

        /

        total_actions

        *

        100
    )

    buy_percent = (

        buy_count

        /

        total_actions

        *

        100
    )

    sell_percent = (

        sell_count

        /

        total_actions

        *

        100
    )

else:

    hold_percent = 0.0

    buy_percent = 0.0

    sell_percent = 0.0


# ============================================================
# WIN RATE
# ============================================================

winning_steps = sum(

    1

    for reward in rewards

    if reward > 0
)


losing_steps = sum(

    1

    for reward in rewards

    if reward < 0
)


non_zero_rewards = (

    winning_steps

    +

    losing_steps
)


if non_zero_rewards > 0:

    win_rate = (

        winning_steps

        /

        non_zero_rewards

        *

        100
    )

else:

    win_rate = 0.0


# ============================================================
# MAXIMUM DRAWDOWN
# ============================================================

portfolio_array = np.asarray(

    portfolio_values,

    dtype=np.float64

)


running_max = np.maximum.accumulate(
    portfolio_array
)


drawdown = (

    portfolio_array

    -

    running_max

) / running_max


max_drawdown = (

    np.min(
        drawdown
    )

    *

    100
)


# ============================================================
# DAILY RETURNS
# ============================================================

portfolio_series = pd.Series(
    portfolio_values
)


daily_returns = (

    portfolio_series

    .pct_change()

    .replace(
        [np.inf, -np.inf],
        np.nan
    )

    .dropna()
)


# ============================================================
# SHARPE RATIO
# ============================================================

if (

    len(daily_returns) > 1

    and

    daily_returns.std() > 0

):

    sharpe_ratio = (

        daily_returns.mean()

        /

        daily_returns.std()

        *

        np.sqrt(252)
    )

else:

    sharpe_ratio = 0.0


# ============================================================
# TOTAL REWARD
# ============================================================

total_reward = sum(
    rewards
)


# ============================================================
# RESULTS
# ============================================================

print()

print("=" * 70)

print(
    "                         RESULTS"
)

print("=" * 70)

print()

print(
    f"Initial Capital      : ₹{INITIAL_CASH:,.2f}"
)

print(
    f"AI Final Value        : ₹{final_value:,.2f}"
)

print(
    f"AI Profit             : ₹{profit:,.2f}"
)

print(
    f"AI Return             : {return_percent:.2f}%"
)

print()

print(
    f"Buy & Hold Value      : ₹{buy_hold_value:,.2f}"
)

print(
    f"Buy & Hold Profit     : ₹{buy_hold_profit:,.2f}"
)

print(
    f"Buy & Hold Return     : {buy_hold_return:.2f}%"
)

print()

print(
    f"HOLD actions          : {hold_count}"
)

print(
    f"BUY actions           : {buy_count}"
)

print(
    f"SELL actions          : {sell_count}"
)

print()

print(
    f"HOLD percentage       : {hold_percent:.2f}%"
)

print(
    f"BUY percentage        : {buy_percent:.2f}%"
)

print(
    f"SELL percentage       : {sell_percent:.2f}%"
)

print()

print(
    f"Winning steps         : {winning_steps}"
)

print(
    f"Losing steps          : {losing_steps}"
)

print(
    f"Win Rate              : {win_rate:.2f}%"
)

print()

print(
    f"Total Reward          : {total_reward:.6f}"
)

print(
    f"Maximum Drawdown      : {max_drawdown:.2f}%"
)

print(
    f"Sharpe Ratio          : {sharpe_ratio:.3f}"
)

print()


# ============================================================
# STRATEGY COMPARISON
# ============================================================

print("=" * 70)

print()

if return_percent > buy_hold_return:

    difference = (

        return_percent

        -

        buy_hold_return
    )

    print(
        f"AI performed BETTER than Buy & Hold "
        f"by {difference:.2f} percentage points."
    )

elif return_percent < buy_hold_return:

    difference = (

        buy_hold_return

        -

        return_percent
    )

    print(
        f"AI performed WORSE than Buy & Hold "
        f"by {difference:.2f} percentage points."
    )

else:

    print(
        "AI and Buy & Hold produced the same return."
    )


# ============================================================
# POLICY DIAGNOSTIC
# ============================================================

print()

print("=" * 70)

print(
    "                     POLICY DIAGNOSTIC"
)

print("=" * 70)

print()


if sell_count == 0:

    print(
        "WARNING: The agent NEVER selected SELL."
    )

    print(
        "The policy appears to have a strong BUY bias."
    )

elif buy_count > total_actions * 0.80:

    print(
        "WARNING: The agent has a strong BUY bias."
    )

elif sell_count > total_actions * 0.80:

    print(
        "WARNING: The agent has a strong SELL bias."
    )

else:

    print(
        "Action distribution looks more balanced."
    )


# ============================================================
# Q-VALUE ANALYSIS
# ============================================================

if len(
    q_value_history
) > 0:

    q_array = np.asarray(
        q_value_history,
        dtype=np.float64
    )


    print()

    print("=" * 70)

    print(
        "                     Q-VALUE ANALYSIS"
    )

    print("=" * 70)

    print()


    print(
        f"Average HOLD Q-value : "
        f"{q_array[:, 0].mean():.6f}"
    )

    print(
        f"Average BUY Q-value  : "
        f"{q_array[:, 1].mean():.6f}"
    )

    print(
        f"Average SELL Q-value : "
        f"{q_array[:, 2].mean():.6f}"
    )

    print()


    # Count which action has the highest Q-value

    highest_actions = np.argmax(
        q_array,
        axis=1
    )


    q_hold_count = np.sum(
        highest_actions == 0
    )

    q_buy_count = np.sum(
        highest_actions == 1
    )

    q_sell_count = np.sum(
        highest_actions == 2
    )


    print(
        "Highest-Q action distribution:"
    )

    print(
        f"    HOLD : {q_hold_count}"
    )

    print(
        f"    BUY  : {q_buy_count}"
    )

    print(
        f"    SELL : {q_sell_count}"
    )

    print()

    print(
        "These values show what the DQN "
        "believes each action is worth."
    )


# ============================================================
# SAVE BACKTEST RESULTS
# ============================================================

results_df = pd.DataFrame({

    "date":
        dates,

    "price":
        prices,

    "action":
        actions,

    "reward":
        rewards,

    "portfolio_value":
        portfolio_values,

    "cash":
        cash_history,

    "shares":
        shares_history

})


os.makedirs(
    "results",
    exist_ok=True
)


RESULT_FILE = (
    f"results/{STOCK}_backtest.csv"
)


results_df.to_csv(
    RESULT_FILE,
    index=False
)


print()

print(
    "Backtest data saved to:"
)

print(
    RESULT_FILE
)


# ============================================================
# PLOT 1
# DQN VS BUY & HOLD
# ============================================================

plt.figure(
    figsize=(13, 6)
)


plt.plot(
    portfolio_values,
    label="DQN Portfolio"
)


buy_hold_curve = [

    INITIAL_CASH
    *
    price
    /
    start_price

    for price in prices

]


plt.plot(
    buy_hold_curve,
    label="Buy & Hold"
)


plt.axhline(
    INITIAL_CASH,
    linestyle="--",
    label="Initial Capital"
)


plt.title(
    f"{STOCK} - DQN vs Buy & Hold"
)

plt.xlabel(
    "Trading Day"
)

plt.ylabel(
    "Portfolio Value (₹)"
)

plt.legend()

plt.grid(
    True
)

plt.tight_layout()

plt.show()


# ============================================================
# PLOT 2
# STOCK PRICE + TRADING ACTIONS
# ============================================================

plt.figure(
    figsize=(13, 6)
)


plt.plot(
    prices,
    label="Stock Price"
)


buy_indices = [

    i

    for i, action in enumerate(actions)

    if action == 1

]


sell_indices = [

    i

    for i, action in enumerate(actions)

    if action == 2

]


if len(
    buy_indices
) > 0:

    plt.scatter(

        buy_indices,

        [
            prices[i]
            for i in buy_indices
        ],

        marker="^",

        s=80,

        label="BUY"
    )


if len(
    sell_indices
) > 0:

    plt.scatter(

        sell_indices,

        [
            prices[i]
            for i in sell_indices
        ],

        marker="v",

        s=80,

        label="SELL"
    )


plt.title(
    f"{STOCK} - DQN Trading Decisions"
)

plt.xlabel(
    "Trading Day"
)

plt.ylabel(
    "Price"
)

plt.legend()

plt.grid(
    True
)

plt.tight_layout()

plt.show()


# ============================================================
# PLOT 3
# ACTION DISTRIBUTION
# ============================================================

plt.figure(
    figsize=(8, 5)
)


action_names = [

    "HOLD",
    "BUY",
    "SELL"

]


action_counts = [

    hold_count,
    buy_count,
    sell_count

]


plt.bar(
    action_names,
    action_counts
)


plt.title(
    "DQN Action Distribution"
)

plt.xlabel(
    "Action"
)

plt.ylabel(
    "Number of Actions"
)

plt.grid(
    axis="y"
)

plt.tight_layout()

plt.show()


# ============================================================
# PLOT 4
# Q VALUES
# ============================================================

if len(
    q_value_history
) > 0:

    q_array = np.asarray(
        q_value_history
    )


    plt.figure(
        figsize=(13, 6)
    )


    plt.plot(

        q_array[:, 0],

        label="HOLD Q-value"
    )


    plt.plot(

        q_array[:, 1],

        label="BUY Q-value"
    )


    plt.plot(

        q_array[:, 2],

        label="SELL Q-value"
    )


    plt.title(
        "DQN Q-Values During Backtest"
    )

    plt.xlabel(
        "Trading Step"
    )

    plt.ylabel(
        "Q-value"
    )

    plt.legend()

    plt.grid(
        True
    )

    plt.tight_layout()

    plt.show()


# ============================================================
# COMPLETE
# ============================================================

print()

print("=" * 70)

print(
    "                 BACKTEST COMPLETE"
)

print("=" * 70)

print()

# ============================================================
# NEW METRICS & SAVING (ADDED FOR TASK 3)
# ============================================================
import sys
sys.stdout.reconfigure(encoding='utf-8')

from metrics import compute_all_metrics

metrics = compute_all_metrics(
    portfolio_values=portfolio_values,
    actions=actions,
    rewards=rewards,
    initial_cash=INITIAL_CASH,
    start_price=start_price,
    end_price=end_price
)

report = f"""
{'='*50}
Validation Summary (Backtest)
{'='*50}
Initial Capital:        ₹{INITIAL_CASH:,.2f}
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
HOLD: {hold_count} ({hold_percent:.1f}%)
BUY:  {buy_count} ({buy_percent:.1f}%)
SELL: {sell_count} ({sell_percent:.1f}%)
{'='*50}
"""
print(report)

plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(12, 6))
bh_values = [INITIAL_CASH * (p / start_price) for p in prices]
ax.plot(portfolio_values, label='Agent Portfolio Value', color='cyan')
ax.plot(bh_values, label='Buy-and-Hold Value', color='orange', alpha=0.7)

buy_x = [i for i, a in enumerate(actions) if a == 1]
buy_y = [portfolio_values[i+1] if i+1 < len(portfolio_values) else portfolio_values[-1] for i in buy_x]

sell_x = [i for i, a in enumerate(actions) if a == 2]
sell_y = [portfolio_values[i+1] if i+1 < len(portfolio_values) else portfolio_values[-1] for i in sell_x]

ax.scatter(buy_x, buy_y, marker='^', color='green', s=100, label='BUY')
ax.scatter(sell_x, sell_y, marker='v', color='red', s=100, label='SELL')

ax.set_title(f'{STOCK} - Backtest Equity Curve')
ax.set_xlabel('Steps')
ax.set_ylabel('Portfolio Value (₹)')
ax.grid(True, alpha=0.3)
ax.legend()
plt.savefig(f'results/{STOCK}_backtest.png', dpi=150, bbox_inches='tight')
plt.close()

# Save trade history
if hasattr(env, 'get_trade_history'):
    trade_hist = env.get_trade_history()
    if trade_hist:
        pd.DataFrame(trade_hist).to_csv(f'results/{STOCK}_backtest_trades.csv', index=False)
        print(f"Trade history saved to results/{STOCK}_backtest_trades.csv")