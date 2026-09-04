import random
from collections import deque

import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

print(
    f"DQN device: {DEVICE}"
)


# ============================================================
# Q NETWORK
# ============================================================

class QNetwork(nn.Module):

    def __init__(
        self,
        state_size,
        action_size
    ):

        super().__init__()

        self.network = nn.Sequential(

            nn.Linear(
                state_size,
                128
            ),

            nn.ReLU(),

            nn.Linear(
                128,
                128
            ),

            nn.ReLU(),

            nn.Linear(
                128,
                64
            ),

            nn.ReLU(),

            nn.Linear(
                64,
                action_size
            )
        )

    def forward(self, state):

        return self.network(
            state
        )


# ============================================================
# DQN AGENT
# ============================================================

class DQNAgent:

    def __init__(
        self,
        state_size,
        action_size,
        learning_rate=0.0001,
        gamma=0.99,
        epsilon_start=1.0,
        epsilon_min=0.05,
        epsilon_decay=0.97,
        memory_size=100000,
        batch_size=64,
        target_update_frequency=500,
        warmup_steps=500
    ):

        self.state_size = int(
            state_size
        )

        self.action_size = int(
            action_size
        )

        self.learning_rate = float(
            learning_rate
        )

        self.gamma = float(
            gamma
        )

        self.epsilon = float(
            epsilon_start
        )

        self.epsilon_start = float(
            epsilon_start
        )

        self.epsilon_min = float(
            epsilon_min
        )

        self.epsilon_decay = float(
            epsilon_decay
        )

        self.batch_size = int(
            batch_size
        )

        self.target_update_frequency = int(
            target_update_frequency
        )

        self.warmup_steps = int(
            warmup_steps
        )

        self.training_steps = 0

        # ----------------------------------------------------
        # REPLAY MEMORY
        # ----------------------------------------------------

        self.memory = deque(
            maxlen=memory_size
        )

        # ----------------------------------------------------
        # NETWORKS
        # ----------------------------------------------------

        self.policy_net = QNetwork(
            self.state_size,
            self.action_size
        ).to(DEVICE)

        self.target_net = QNetwork(
            self.state_size,
            self.action_size
        ).to(DEVICE)

        self.target_net.load_state_dict(
            self.policy_net.state_dict()
        )

        self.target_net.eval()

        # ----------------------------------------------------
        # OPTIMIZER
        # ----------------------------------------------------

        self.optimizer = optim.AdamW(
            self.policy_net.parameters(),
            lr=self.learning_rate,
            weight_decay=1e-5
        )

        # ----------------------------------------------------
        # LOSS
        # ----------------------------------------------------

        self.loss_function = nn.SmoothL1Loss()

    # ========================================================
    # ACTION
    # ========================================================

    def act(
        self,
        state,
        training=True
    ):

        state = np.asarray(
            state,
            dtype=np.float32
        )

        if state.shape != (
            self.state_size,
        ):

            raise ValueError(
                f"Expected state shape "
                f"({self.state_size},), "
                f"got {state.shape}"
            )

        # ----------------------------------------------------
        # EXPLORATION
        # ----------------------------------------------------

        if training:

            if random.random() < self.epsilon:

                return random.randrange(
                    self.action_size
                )

        # ----------------------------------------------------
        # EXPLOITATION
        # ----------------------------------------------------

        state_tensor = torch.as_tensor(
            state,
            dtype=torch.float32,
            device=DEVICE
        ).unsqueeze(0)

        self.policy_net.eval()

        with torch.no_grad():

            q_values = self.policy_net(
                state_tensor
            )

        return int(
            torch.argmax(
                q_values,
                dim=1
            ).item()
        )

    # ========================================================
    # COMPATIBILITY
    # ========================================================

    def choose_action(
        self,
        state,
        training=True
    ):

        return self.act(
            state,
            training
        )

    # ========================================================
    # Q VALUES
    # ========================================================

    def get_q_values(
        self,
        state
    ):

        state = np.asarray(
            state,
            dtype=np.float32
        )

        if state.shape != (
            self.state_size,
        ):

            raise ValueError(
                f"Expected state shape "
                f"({self.state_size},), "
                f"got {state.shape}"
            )

        state_tensor = torch.as_tensor(
            state,
            dtype=torch.float32,
            device=DEVICE
        ).unsqueeze(0)

        self.policy_net.eval()

        with torch.no_grad():

            q_values = self.policy_net(
                state_tensor
            )

        return (
            q_values
            .cpu()
            .numpy()[0]
        )

    # ========================================================
    # REMEMBER
    # ========================================================

    def remember(
        self,
        state,
        action,
        reward,
        next_state,
        done
    ):

        state = np.asarray(
            state,
            dtype=np.float32
        )

        next_state = np.asarray(
            next_state,
            dtype=np.float32
        )

        if state.shape != (
            self.state_size,
        ):

            raise ValueError(
                "State shape mismatch."
            )

        if next_state.shape != (
            self.state_size,
        ):

            raise ValueError(
                "Next-state shape mismatch."
            )

        self.memory.append(
            (
                state,
                int(action),
                float(reward),
                next_state,
                bool(done)
            )
        )

    # ========================================================
    # REPLAY
    # ========================================================

    def replay(self):

        if (
            len(self.memory)
            <
            max(
                self.batch_size,
                self.warmup_steps
            )
        ):

            return None

        batch = random.sample(
            self.memory,
            self.batch_size
        )

        states = np.asarray(
            [
                item[0]
                for item in batch
            ],
            dtype=np.float32
        )

        actions = np.asarray(
            [
                item[1]
                for item in batch
            ],
            dtype=np.int64
        )

        rewards = np.asarray(
            [
                item[2]
                for item in batch
            ],
            dtype=np.float32
        )

        next_states = np.asarray(
            [
                item[3]
                for item in batch
            ],
            dtype=np.float32
        )

        dones = np.asarray(
            [
                item[4]
                for item in batch
            ],
            dtype=np.float32
        )

        states_tensor = torch.as_tensor(
            states,
            dtype=torch.float32,
            device=DEVICE
        )

        actions_tensor = torch.as_tensor(
            actions,
            dtype=torch.long,
            device=DEVICE
        ).unsqueeze(1)

        rewards_tensor = torch.as_tensor(
            rewards,
            dtype=torch.float32,
            device=DEVICE
        )

        next_states_tensor = torch.as_tensor(
            next_states,
            dtype=torch.float32,
            device=DEVICE
        )

        dones_tensor = torch.as_tensor(
            dones,
            dtype=torch.float32,
            device=DEVICE
        )

        # ----------------------------------------------------
        # CURRENT Q
        # ----------------------------------------------------

        self.policy_net.train()

        current_q = (
            self.policy_net(
                states_tensor
            )
            .gather(
                1,
                actions_tensor
            )
            .squeeze(1)
        )

        # ----------------------------------------------------
        # DOUBLE DQN TARGET
        # ----------------------------------------------------

        with torch.no_grad():

            next_actions = (
                self.policy_net(
                    next_states_tensor
                )
                .argmax(
                    dim=1,
                    keepdim=True
                )
            )

            next_q = (
                self.target_net(
                    next_states_tensor
                )
                .gather(
                    1,
                    next_actions
                )
                .squeeze(1)
            )

            target_q = (
                rewards_tensor
                +
                (
                    1.0 -
                    dones_tensor
                )
                *
                self.gamma
                *
                next_q
            )

        # ----------------------------------------------------
        # LOSS
        # ----------------------------------------------------

        loss = self.loss_function(
            current_q,
            target_q
        )

        # ----------------------------------------------------
        # BACKPROPAGATION
        # ----------------------------------------------------

        self.optimizer.zero_grad()

        loss.backward()

        torch.nn.utils.clip_grad_norm_(
            self.policy_net.parameters(),
            max_norm=1.0
        )

        self.optimizer.step()

        self.training_steps += 1

        # ----------------------------------------------------
        # TARGET UPDATE
        # ----------------------------------------------------

        if (
            self.training_steps
            %
            self.target_update_frequency
            == 0
        ):

            self.target_net.load_state_dict(
                self.policy_net.state_dict()
            )

        return float(
            loss.item()
        )

    # ========================================================
    # EPSILON DECAY
    # ========================================================

    def decay_epsilon(self):

        self.epsilon = max(
            self.epsilon_min,
            self.epsilon *
            self.epsilon_decay
        )

    # ========================================================
    # SAVE
    # ========================================================

    def save(
        self,
        filepath
    ):

        checkpoint = {

            "policy_net":
                self.policy_net.state_dict(),

            "target_net":
                self.target_net.state_dict(),

            "optimizer":
                self.optimizer.state_dict(),

            "epsilon":
                self.epsilon,

            "state_size":
                self.state_size,

            "action_size":
                self.action_size,

            "training_steps":
                self.training_steps
        }

        torch.save(
            checkpoint,
            filepath
        )

        print(
            f"Model saved: {filepath}"
        )

    # ========================================================
    # LOAD
    # ========================================================

    def load(
        self,
        filepath
    ):

        checkpoint = torch.load(
            filepath,
            map_location=DEVICE
        )

        saved_state_size = checkpoint.get(
            "state_size"
        )

        if (
            saved_state_size is not None
            and
            int(saved_state_size)
            != self.state_size
        ):

            raise ValueError(
                "Model state size mismatch: "
                f"model={saved_state_size}, "
                f"environment={self.state_size}"
            )

        saved_action_size = checkpoint.get(
            "action_size"
        )

        if (
            saved_action_size is not None
            and
            int(saved_action_size)
            != self.action_size
        ):

            raise ValueError(
                "Model action size mismatch: "
                f"model={saved_action_size}, "
                f"environment={self.action_size}"
            )

        self.policy_net.load_state_dict(
            checkpoint["policy_net"]
        )

        if "target_net" in checkpoint:

            self.target_net.load_state_dict(
                checkpoint["target_net"]
            )

        else:

            self.target_net.load_state_dict(
                self.policy_net.state_dict()
            )

        if "optimizer" in checkpoint:

            self.optimizer.load_state_dict(
                checkpoint["optimizer"]
            )

        if "epsilon" in checkpoint:

            self.epsilon = float(
                checkpoint["epsilon"]
            )

        if "training_steps" in checkpoint:

            self.training_steps = int(
                checkpoint[
                    "training_steps"
                ]
            )

        print(
            f"Model loaded: {filepath}"
        )

        print(
            f"Current epsilon: "
            f"{self.epsilon:.6f}"
        )