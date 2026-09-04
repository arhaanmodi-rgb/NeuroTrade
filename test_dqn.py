import numpy as np

from dqn_agent import DQNAgent


# ============================================================
# TEST DQN
# ============================================================

STATE_SIZE = 20

ACTION_SIZE = 3


print("=" * 60)

print(
    "           NEUROTRADE DQN TEST"
)

print("=" * 60)


# ------------------------------------------------------------
# CREATE AGENT
# ------------------------------------------------------------

agent = DQNAgent(

    STATE_SIZE,

    ACTION_SIZE

)


print()

print(
    "State size:",
    STATE_SIZE
)

print(
    "Action size:",
    ACTION_SIZE
)


# ------------------------------------------------------------
# RANDOM STATE
# ------------------------------------------------------------

state = np.random.randn(

    STATE_SIZE

).astype(
    np.float32
)


# ------------------------------------------------------------
# TEST ACTION
# ------------------------------------------------------------

action = agent.choose_action(

    state

)


print()

print(
    "Random test state:"
)

print(
    state
)


print()

print(
    "Selected action:",
    action
)


if action == 0:

    print(
        "Action = HOLD"
    )

elif action == 1:

    print(
        "Action = BUY"
    )

else:

    print(
        "Action = SELL"
    )


# ------------------------------------------------------------
# TEST MEMORY
# ------------------------------------------------------------

next_state = np.random.randn(

    STATE_SIZE

).astype(
    np.float32
)


agent.remember(

    state,

    action,

    0.01,

    next_state,

    False

)


print()

print(
    "Replay memory size:",
    len(agent.memory)
)


# ------------------------------------------------------------
# FINISH
# ------------------------------------------------------------

print()

print("=" * 60)

print(
    "DQN TEST COMPLETE"
)

print("=" * 60)