# -*- coding: utf-8 -*-
import os
import sys
import numpy as np

# ============================================================
# ENCODING FIX (Windows cp1252 → UTF-8)
# ============================================================

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from trading_environment import TradingEnvironment
from dqn_agent import DQNAgent


# ============================================================
# CONFIGURATION
# ============================================================

STOCK = "RELIANCE"

DATA_PATH = "data/features/RELIANCE.csv"

MODEL_PATH = "models/RELIANCE_dqn.pth"

INITIAL_CASH = 100000.0

MAX_STEPS = 252


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("                 NEUROTRADE DQN EVALUATION")
print("=" * 70)

print()

print("Stock           :", STOCK)

print("Data            :", DATA_PATH)

print("Model           :", MODEL_PATH)

print(
    "Initial cash    : ₹{:,.2f}".format(
        INITIAL_CASH
    )
)


# ============================================================
# CHECK FILES
# ============================================================

if not os.path.exists(DATA_PATH):

    raise FileNotFoundError(
        f"Data file not found: {DATA_PATH}"
    )


if not os.path.exists(MODEL_PATH):

    raise FileNotFoundError(
        f"Model file not found: {MODEL_PATH}"
    )


# ============================================================
# CREATE ENVIRONMENT
# ============================================================

print()
print("=" * 70)
print("CREATING ENVIRONMENT")
print("=" * 70)

env = TradingEnvironment(
    data_path=DATA_PATH,
    initial_cash=INITIAL_CASH,
    random_start=False
)


print()

print(
    "Environment state size :",
    env.state_size
)

print(
    "Environment action size:",
    env.action_size
)

print(
    "Environment features   :",
    len(env.feature_columns)
)


# ============================================================
# DISPLAY FEATURES
# ============================================================

print()
print("Features used by environment:")

for index, feature in enumerate(
    env.feature_columns,
    start=1
):

    print(
        f"  {index:02d}. {feature}"
    )


# ============================================================
# PEEK CHECKPOINT – read saved state/action sizes first
# ============================================================

import torch as _torch

_checkpoint = _torch.load(
    MODEL_PATH,
    map_location="cpu",
    weights_only=False
)

_saved_state_size = int(
    _checkpoint.get("state_size", env.state_size)
)

_saved_action_size = int(
    _checkpoint.get("action_size", env.action_size)
)

print()
print(
    f"Checkpoint state_size  : {_saved_state_size}"
)
print(
    f"Checkpoint action_size : {_saved_action_size}"
)

if _saved_state_size != env.state_size:

    print()
    print(
        "[WARNING] Model was trained with state_size="
        f"{_saved_state_size}, but the environment "
        f"currently has state_size={env.state_size}."
    )
    print(
        "          The agent is created with the "
        "model's original dimensions so weights load "
        "correctly. The state vector will be adapted "
        "(truncated or zero-padded) at inference time."
    )


# ============================================================
# CREATE AGENT
# ============================================================

print()
print("=" * 70)
print("CREATING DQN AGENT")
print("=" * 70)

agent = DQNAgent(
    state_size=_saved_state_size,
    action_size=_saved_action_size
)

# Track both sizes for state adaptation during inference.
AGENT_STATE_SIZE = _saved_state_size
ENV_STATE_SIZE = env.state_size


# ============================================================
# LOAD MODEL
# ============================================================

print()
print("=" * 70)
print("LOADING TRAINED DQN")
print("=" * 70)

agent.load(
    MODEL_PATH
)

print()

print(
    "Model loaded successfully."
)


# ============================================================
# STATE ADAPTER
# ============================================================

def adapt_state(raw_state):
    """
    Truncate or zero-pad `raw_state` so its length equals
    AGENT_STATE_SIZE.  This handles the case where the saved
    model was trained with a different feature count than the
    current environment produces.
    """
    s = np.asarray(raw_state, dtype=np.float32)
    if len(s) == AGENT_STATE_SIZE:
        return s
    if len(s) > AGENT_STATE_SIZE:
        return s[:AGENT_STATE_SIZE]
    # zero-pad
    padded = np.zeros(AGENT_STATE_SIZE, dtype=np.float32)
    padded[:len(s)] = s
    return padded


# ============================================================
# RESET ENVIRONMENT
# ============================================================

print()
print("=" * 70)
print("STARTING EVALUATION")
print("=" * 70)

state = env.reset()

state = adapt_state(state)


# ============================================================
# STATE VALIDATION
# ============================================================

if state.shape != (AGENT_STATE_SIZE,):

    raise ValueError(
        f"Invalid state shape: "
        f"{state.shape}, expected {(AGENT_STATE_SIZE,)}"
    )


if np.isnan(state).any():

    raise ValueError(
        "Initial state contains NaN values."
    )


if np.isinf(state).any():

    raise ValueError(
        "Initial state contains infinite values."
    )


print()

print(
    "Initial state size :",
    len(state)
)

print(
    "Initial portfolio  : ₹{:,.2f}".format(
        env.portfolio_value
    )
)


# ============================================================
# ACTION NAMES
# ============================================================

actions = {

    0: "HOLD",

    1: "BUY",

    2: "SELL"

}


action_counts = {

    0: 0,

    1: 0,

    2: 0

}


# ============================================================
# EVALUATION LOOP
# ============================================================

total_reward = 0.0

steps_completed = 0

done = False


for step_number in range(
    1,
    MAX_STEPS + 1
):

    # --------------------------------------------------------
    # ALWAYS USE GREEDY ACTION
    # --------------------------------------------------------

    action = agent.act(
        state,
        training=False
    )

    action = int(action)

    action_counts[action] += 1


    # --------------------------------------------------------
    # ENVIRONMENT STEP
    # --------------------------------------------------------

    result = env.step(
        action
    )


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
            terminated or
            truncated
        )


    else:

        raise ValueError(
            "Unexpected number of values returned "
            f"by env.step(): {len(result)}"
        )


    next_state = adapt_state(next_state)


    # --------------------------------------------------------
    # VALIDATE NEXT STATE
    # --------------------------------------------------------

    if next_state.shape != (
        AGENT_STATE_SIZE,
    ):

        raise ValueError(
            f"Invalid next state shape: "
            f"{next_state.shape}, "
            f"expected {(AGENT_STATE_SIZE,)}"
        )


    if np.isnan(next_state).any():

        raise ValueError(
            f"NaN detected in state at step "
            f"{step_number}"
        )


    if np.isinf(next_state).any():

        raise ValueError(
            f"Infinity detected in state at step "
            f"{step_number}"
        )


    # --------------------------------------------------------
    # GET INFORMATION
    # --------------------------------------------------------

    price = info.get(
        "price",
        info.get(
            "current_price",
            env.prices[
                min(
                    env.current_step,
                    len(env.prices) - 1
                )
            ]
        )
    )


    portfolio = getattr(
        env,
        "portfolio_value",
        info.get(
            "portfolio_value",
            INITIAL_CASH
        )
    )


    total_reward += float(
        reward
    )


    steps_completed += 1


    # --------------------------------------------------------
    # PRINT STEP
    # --------------------------------------------------------

    print(
        f"\nStep {step_number}"
    )

    print(
        f"  Action     : {actions.get(action, 'UNKNOWN')}"
    )

    print(
        "  Price      : ₹{:,.2f}".format(
            float(price)
        )
    )

    print(
        "  Portfolio  : ₹{:,.2f}".format(
            float(portfolio)
        )
    )

    print(
        "  Reward     : {:+.6f}".format(
            float(reward)
        )
    )

    print(
        "  Q-values   :",
        np.round(
            agent.get_q_values(state),
            6
        )
    )


    state = next_state


    if done:

        print()

        print(
            "Environment reached the end."
        )

        break


# ============================================================
# FINAL PORTFOLIO
# ============================================================

final_portfolio = float(
    env.portfolio_value
)


profit_loss = (
    final_portfolio -
    INITIAL_CASH
)


return_pct = (
    profit_loss /
    INITIAL_CASH
) * 100


# ============================================================
# ACTION DISTRIBUTION
# ============================================================

print()
print("=" * 70)
print("                 ACTION DISTRIBUTION")
print("=" * 70)

if steps_completed > 0:

    for action_id in range(3):

        percentage = (
            action_counts[action_id] /
            steps_completed
        ) * 100

        print(
            f"{actions[action_id]:5s}: "
            f"{action_counts[action_id]:4d} "
            f"({percentage:5.1f}%)"
        )


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 70)
print("                 EVALUATION SUMMARY")
print("=" * 70)

print()

print(
    "Initial capital : ₹{:,.2f}".format(
        INITIAL_CASH
    )
)

print(
    "Final portfolio : ₹{:,.2f}".format(
        final_portfolio
    )
)

print(
    "Profit / Loss   : ₹{:,.2f}".format(
        profit_loss
    )
)

print(
    "Return          : {:+.2f}%".format(
        return_pct
    )
)

print(
    "Total reward    : {:+.6f}".format(
        total_reward
    )
)

print(
    "Steps evaluated :",
    steps_completed
)

print()

print(
    "HOLD actions    :",
    action_counts[0]
)

print(
    "BUY actions     :",
    action_counts[1]
)

print(
    "SELL actions    :",
    action_counts[2]
)

print()

print("=" * 70)
print("              EVALUATION COMPLETED")
print("=" * 70)