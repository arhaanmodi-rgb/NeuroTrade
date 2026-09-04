import numpy as np

from trading_environment import TradingEnvironment


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "data/features/RELIANCE.csv"

INITIAL_CASH = 100000.0


# ============================================================
# HEADER
# ============================================================

print("=" * 60)
print("             NEUROTRADE ENVIRONMENT TEST")
print("=" * 60)


# ============================================================
# CREATE ENVIRONMENT
# ============================================================

print("\nCreating trading environment...")

env = TradingEnvironment(
    data_path=DATA_PATH,
    initial_cash=INITIAL_CASH,
    random_start=False
)


# ============================================================
# ENVIRONMENT INFORMATION
# ============================================================

print()
print("Environment loaded successfully.")

print(
    "Market features:",
    len(env.feature_columns)
)

print(
    "State size:",
    env.state_size
)

print(
    "Action size:",
    env.action_size
)

print(
    "Expected state size:",
    len(env.feature_columns) + 3
)


# ============================================================
# RESET
# ============================================================

print("\nTesting reset()...")

state = env.reset()

state = np.asarray(
    state,
    dtype=np.float32
)

print("Reset successful.")

print(
    "State shape:",
    state.shape
)

print(
    "Initial portfolio:",
    env.portfolio_value
)


# ============================================================
# EXPECTED STATE
# ============================================================

expected_state_size = (
    len(env.feature_columns) + 3
)

if state.shape != (
    expected_state_size,
):

    raise ValueError(
        f"Wrong state shape. "
        f"Expected "
        f"({expected_state_size},), "
        f"got {state.shape}"
    )

print(
    "State size check: PASSED"
)


# ============================================================
# STATE VALIDATION
# ============================================================

print("\nChecking state...")

print(
    "State min   :",
    np.min(state)
)

print(
    "State max   :",
    np.max(state)
)

print(
    "State mean  :",
    np.mean(state)
)

if np.isnan(state).any():

    raise ValueError(
        "State contains NaN values."
    )

print(
    "State contains no NaN values."
)

if np.isinf(state).any():

    raise ValueError(
        "State contains infinite values."
    )

print(
    "State contains no infinite values."
)


# ============================================================
# TEST ACTIONS
# ============================================================

print("\n" + "=" * 60)
print("                 TESTING ACTIONS")
print("=" * 60)

actions = {
    0: "HOLD",
    1: "BUY",
    2: "SELL"
}


state = env.reset()

print(
    "\nInitial state size:",
    len(state)
)

print(
    "Initial portfolio  : ₹{:,.2f}".format(
        env.portfolio_value
    )
)


# ============================================================
# RUN 10 STEPS
# ============================================================

for step_number in range(1, 11):

    action = (
        step_number - 1
    ) % 3

    action_name = actions[action]

    result = env.step(
        action
    )

    if len(result) == 4:

        (
            next_state,
            reward,
            done,
            info
        ) = result

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
            "Unexpected number of values "
            "returned by env.step()."
        )

    next_state = np.asarray(
        next_state,
        dtype=np.float32
    )

    if not np.all(
        np.isfinite(next_state)
    ):

        raise ValueError(
            f"Invalid state at step "
            f"{step_number}"
        )

    portfolio = env.get_portfolio_value()

    price = info.get(
        "price",
        None
    )

    if price is None:

        price_text = "N/A"

    else:

        price_text = (
            "₹{:,.2f}".format(
                float(price)
            )
        )

    print(
        f"\nStep {step_number}"
    )

    print(
        f"  Action     : {action_name}"
    )

    print(
        f"  Price      : {price_text}"
    )

    print(
        f"  Portfolio  : ₹{portfolio:,.2f}"
    )

    print(
        f"  Reward     : {float(reward):+.6f}"
    )

    print(
        f"  State size : {len(next_state)}"
    )

    print(
        f"  Done       : {done}"
    )

    state = next_state

    if done:

        break


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("             ENVIRONMENT TEST SUMMARY")
print("=" * 60)

final_portfolio = (
    env.get_portfolio_value()
)

profit_loss = (
    final_portfolio -
    INITIAL_CASH
)

return_pct = (
    profit_loss /
    INITIAL_CASH
) * 100


print(
    "\nInitial capital : ₹{:,.2f}".format(
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
    "Return          : {:.2f}%".format(
        return_pct
    )
)

print(
    "Trades          :",
    env.trade_count
)

print(
    "Buys            :",
    env.buy_count
)

print(
    "Sells           :",
    env.sell_count
)

print(
    "Holds           :",
    env.hold_count
)

print()
print(
    "Environment test completed successfully."
)

print("=" * 60)