import os
import numpy as np
import argparse

from trading_environment import TradingEnvironment
from dqn_agent import DQNAgent


# ============================================================
# CLI ARGUMENTS
# ============================================================

parser = argparse.ArgumentParser(description='NeuroTrade DQN Training')
parser.add_argument('--stock', type=str, default='RELIANCE', help='Stock symbol to train on')
parser.add_argument('--episodes', type=int, default=200, help='Number of training episodes')
parser.add_argument('--episode-length', type=int, default=252, help='Steps per episode')
args = parser.parse_args()


# ============================================================
# CONFIGURATION
# ============================================================

STOCK = args.stock

DATA_PATH = f"data/features/{STOCK}.csv"

MODEL_FOLDER = "models"

INITIAL_CASH = 100000.0

EPISODES = args.episodes

EPISODE_LENGTH = args.episode_length


# ============================================================
# TRAINING CONFIGURATION
# ============================================================

TRANSACTION_COST = 0.001

SLIPPAGE = 0.0005


# ============================================================
# HEADER
# ============================================================

print()
print("=" * 70)

print(
    "                 NEUROTRADE DQN TRAINING"
)

print("=" * 70)

print()

print(
    f"Stock           : {STOCK}"
)

print(
    f"Data            : {DATA_PATH}"
)

print(
    f"Episodes        : {EPISODES}"
)

print(
    f"Episode length  : {EPISODE_LENGTH}"
)

print(
    f"Initial cash    : {INITIAL_CASH}"
)

print(
    f"Transaction cost: {TRANSACTION_COST}"
)

print(
    f"Slippage        : {SLIPPAGE}"
)


# ============================================================
# CREATE MODEL DIRECTORY
# ============================================================

os.makedirs(
    MODEL_FOLDER,
    exist_ok=True
)


# ============================================================
# CREATE ENVIRONMENT
# ============================================================

env = TradingEnvironment(
    data_path=DATA_PATH,
    initial_cash=INITIAL_CASH,
    random_start=True,
    transaction_cost=TRANSACTION_COST,
    slippage=SLIPPAGE
)


# ============================================================
# ENVIRONMENT INFORMATION
# ============================================================

print()
print("=" * 70)

print(
    "ENVIRONMENT"
)

print("=" * 70)

print()

print(
    "State size :", env.state_size
)

print(
    "Action size:", env.action_size
)

print()

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
    state_size=env.state_size,
    action_size=env.action_size
)


# ============================================================
# TRAINING STATISTICS
# ============================================================

episode_rewards = []

episode_returns = []

episode_profits = []

best_return = -float("inf")

best_profit = -float("inf")

best_reward = -float("inf")

average_loss = 0.0


# ============================================================
# TRAINING
# ============================================================

print()
print("=" * 70)

print(
    "STARTING TRAINING"
)

print("=" * 70)

print()


for episode in range(
    1,
    EPISODES + 1
):

    # --------------------------------------------------------
    # RESET ENVIRONMENT
    # --------------------------------------------------------

    state = env.reset()

    state = np.asarray(
        state,
        dtype=np.float32
    )


    # --------------------------------------------------------
    # EPISODE VARIABLES
    # --------------------------------------------------------

    total_reward = 0.0

    total_loss = 0.0

    loss_count = 0

    steps = 0

    action_counts = {
        0: 0,
        1: 0,
        2: 0
    }


    # --------------------------------------------------------
    # RUN EPISODE
    # --------------------------------------------------------

    for step in range(
        EPISODE_LENGTH
    ):

        # ----------------------------------------------------
        # SELECT ACTION
        # ----------------------------------------------------

        action = agent.act(
            state,
            training=True
        )

        action_counts[action] += 1


        # ----------------------------------------------------
        # ENVIRONMENT STEP
        # ----------------------------------------------------

        result = env.step(
            action
        )


        # ----------------------------------------------------
        # SUPPORT 4-VALUE ENVIRONMENT
        # ----------------------------------------------------

        if len(result) == 4:

            next_state, reward, done, info = result


        # ----------------------------------------------------
        # SUPPORT 5-VALUE GYMNASIUM ENVIRONMENT
        # ----------------------------------------------------

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


        next_state = np.asarray(
            next_state,
            dtype=np.float32
        )


        # ----------------------------------------------------
        # STORE EXPERIENCE
        # ----------------------------------------------------

        agent.remember(
            state,
            action,
            reward,
            next_state,
            done
        )


        # ----------------------------------------------------
        # TRAIN AGENT
        # ----------------------------------------------------

        loss = agent.replay()


        if loss is not None:

            total_loss += float(
                loss
            )

            loss_count += 1


        # ----------------------------------------------------
        # UPDATE STATE
        # ----------------------------------------------------

        state = next_state

        total_reward += float(
            reward
        )

        steps += 1


        # ----------------------------------------------------
        # STOP IF ENVIRONMENT FINISHED
        # ----------------------------------------------------

        if done:

            break


    # ========================================================
    # EPISODE RESULTS
    # ========================================================

    final_portfolio = float(
        env.get_portfolio_value()
    )


    profit = (
        final_portfolio -
        INITIAL_CASH
    )


    return_pct = (
        profit /
        INITIAL_CASH
    ) * 100


    # --------------------------------------------------------
    # AVERAGE LOSS
    # --------------------------------------------------------

    if loss_count > 0:

        average_loss = (
            total_loss /
            loss_count
        )

    else:

        average_loss = 0.0


    # ========================================================
    # STORE STATISTICS
    # ========================================================

    episode_rewards.append(
        total_reward
    )

    episode_returns.append(
        return_pct
    )

    episode_profits.append(
        profit
    )


    # ========================================================
    # EPSILON DECAY
    # ========================================================

    # Decay after every episode so the agent gradually shifts
    # from random exploration (epsilon=1.0) to learned policy
    # (epsilon=epsilon_min=0.05).

    agent.decay_epsilon()


    # ========================================================
    # BEST MODEL CHECK
    # ========================================================

    model_saved = False


    if return_pct > best_return:

        best_return = return_pct

        best_profit = profit

        best_reward = total_reward

        best_model_path = os.path.join(
            MODEL_FOLDER,
            f"{STOCK}_dqn_best.pth"
        )

        agent.save(
            best_model_path
        )

        model_saved = True


    # --------------------------------------------------------
    # PERIODIC CHECKPOINT
    # --------------------------------------------------------

    if episode % 25 == 0:

        checkpoint_path = os.path.join(
            MODEL_FOLDER,
            f"{STOCK}_episode_{episode}.pth"
        )

        agent.save(
            checkpoint_path
        )

        model_saved = True


    # --------------------------------------------------------
    # REGULAR MODEL SAVE
    # --------------------------------------------------------

    if episode % 10 == 0:

        latest_model_path = os.path.join(
            MODEL_FOLDER,
            f"{STOCK}_dqn.pth"
        )

        agent.save(
            latest_model_path
        )

        model_saved = True


    # ========================================================
    # ACTION PERCENTAGES
    # ========================================================

    total_actions = sum(
        action_counts.values()
    )


    if total_actions > 0:

        hold_pct = (
            action_counts[0] /
            total_actions
        ) * 100

        buy_pct = (
            action_counts[1] /
            total_actions
        ) * 100

        sell_pct = (
            action_counts[2] /
            total_actions
        ) * 100

    else:

        hold_pct = 0.0

        buy_pct = 0.0

        sell_pct = 0.0


    # ========================================================
    # TRAINING PROGRESS
    # ========================================================

    print(
        f"Episode {episode:3d}/{EPISODES} | "
        f"Steps: {steps:3d} | "
        f"Reward: {total_reward:+.5f} | "
        f"Profit: ₹{profit:+,.2f} | "
        f"Return: {return_pct:+.2f}% | "
        f"Loss: {average_loss:.6f} | "
        f"Epsilon: {agent.epsilon:.4f}"
    )


    print(
        f"              "
        f"HOLD: {hold_pct:5.1f}% | "
        f"BUY: {buy_pct:5.1f}% | "
        f"SELL: {sell_pct:5.1f}%"
    )


    # --------------------------------------------------------
    # SHOW BEST RESULT
    # --------------------------------------------------------

    if model_saved:

        print(
            f"              "
            f"Best Return: {best_return:+.2f}%"
        )


# ============================================================
# FINAL MODEL SAVE
# ============================================================

final_model_path = os.path.join(
    MODEL_FOLDER,
    f"{STOCK}_dqn.pth"
)

agent.save(
    final_model_path
)


# ============================================================
# FINAL TRAINING SUMMARY
# ============================================================

print()
print("=" * 70)

print(
    "TRAINING COMPLETE"
)

print("=" * 70)

print()

print(
    f"Stock              : {STOCK}"
)

print(
    f"Episodes           : {EPISODES}"
)

print(
    f"Final epsilon      : {agent.epsilon:.4f}"
)

print(
    f"Best return        : {best_return:+.2f}%"
)

print(
    f"Best profit        : ₹{best_profit:+,.2f}"
)

print(
    f"Best reward        : {best_reward:+.5f}"
)

print()

print(
    f"Final model saved  : {final_model_path}"
)

print(
    f"Best model saved   : "
    f"models/{STOCK}_dqn_best.pth"
)

print()

print("=" * 70)