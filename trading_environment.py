import numpy as np
import pandas as pd


# ============================================================
# MODEL FEATURES
# ============================================================

MODEL_FEATURES = [
    "return_1d",
    "return_5d",
    "return_20d",

    "sma_20",
    "sma_50",
    "sma_200",

    "price_sma20",
    "price_sma50",
    "price_sma200",

    "ema_12",
    "ema_26",

    "macd",
    "macd_signal",
    "macd_histogram",

    "rsi_14",

    "volatility_20",

    "volume_ratio",

    "daily_range",
    "close_position",

    "sma20_sma50",
    "sma50_sma200"
]


# ============================================================
# TRADING ENVIRONMENT
# ============================================================

class TradingEnvironment:

    HOLD = 0
    BUY = 1
    SELL = 2

    def __init__(
        self,
        data_path,
        initial_cash=100000.0,
        random_start=False,
        transaction_cost=0.001,
        slippage=0.0005
    ):

        self.data_path = data_path

        self.initial_cash = float(
            initial_cash
        )

        self.transaction_cost = float(
            transaction_cost
        )

        self.slippage = float(
            slippage
        )

        self.random_start = bool(
            random_start
        )

        # ----------------------------------------------------
        # LOAD DATA
        # ----------------------------------------------------

        self.df = pd.read_csv(
            data_path
        )

        if self.df.empty:

            raise ValueError(
                "CSV file contains no data."
            )

        required_columns = [
            "trade_date",
            "close"
        ] + MODEL_FEATURES

        missing = [
            column
            for column in required_columns
            if column not in self.df.columns
        ]

        if missing:

            raise ValueError(
                "Missing required columns: "
                + ", ".join(missing)
            )

        # ----------------------------------------------------
        # DATE
        # ----------------------------------------------------

        self.df["trade_date"] = pd.to_datetime(
            self.df["trade_date"],
            errors="coerce"
        )

        self.df = (
            self.df
            .sort_values("trade_date")
            .reset_index(drop=True)
        )

        # ----------------------------------------------------
        # NUMERIC CONVERSION
        # ----------------------------------------------------

        numeric_columns = (
            MODEL_FEATURES +
            ["close"]
        )

        for column in numeric_columns:

            self.df[column] = pd.to_numeric(
                self.df[column],
                errors="coerce"
            )

        # ----------------------------------------------------
        # CLEAN INVALID DATA
        # ----------------------------------------------------

        self.df = self.df.replace(
            [np.inf, -np.inf],
            np.nan
        )

        self.df = self.df.dropna(
            subset=MODEL_FEATURES + ["close"]
        ).reset_index(drop=True)

        if len(self.df) < 250:

            raise ValueError(
                "Not enough valid rows after cleaning."
            )

        # ----------------------------------------------------
        # FEATURES
        # ----------------------------------------------------

        self.feature_columns = MODEL_FEATURES.copy()

        self.features = (
            self.df[
                self.feature_columns
            ]
            .astype(np.float32)
        )

        # ----------------------------------------------------
        # STANDARDIZATION
        # ----------------------------------------------------

        mean = self.features.mean()

        std = self.features.std()

        std = std.replace(
            0,
            1.0
        )

        self.features = (
            self.features - mean
        ) / std

        self.features = self.features.replace(
            [np.inf, -np.inf],
            np.nan
        )

        self.features = self.features.fillna(
            0.0
        )

        self.features = self.features.clip(
            -5.0,
            5.0
        )

        self.features = self.features.astype(
            np.float32
        )

        # ----------------------------------------------------
        # PRICE
        # ----------------------------------------------------

        self.prices = (
            self.df["close"]
            .astype(float)
            .values
        )

        if not np.all(
            np.isfinite(self.prices)
        ):

            raise ValueError(
                "Invalid close prices."
            )

        if np.any(
            self.prices <= 0
        ):

            raise ValueError(
                "Close prices must be positive."
            )

        # ----------------------------------------------------
        # STATE / ACTION
        # ----------------------------------------------------

        self.state_size = (
            len(self.feature_columns) + 3
        )

        self.action_size = 3

        # ----------------------------------------------------
        # PORTFOLIO
        # ----------------------------------------------------

        self.current_step = 0

        self.cash = self.initial_cash

        self.shares = 0.0

        self.portfolio_value = (
            self.initial_cash
        )

        self.previous_portfolio_value = (
            self.initial_cash
        )

        self.max_portfolio_value = (
            self.initial_cash
        )

        self.max_drawdown = 0.0

        self.trade_count = 0

        self.buy_count = 0

        self.sell_count = 0

        self.hold_count = 0

        self.trade_history = []

        print(
            f"Environment loaded: {len(self.df)} rows"
        )

        print(
            f"Features: {len(self.feature_columns)}"
        )

        print(
            f"State size: {self.state_size}"
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):

        if self.random_start:

            max_start = max(
                0,
                len(self.df) - 253
            )

            if max_start > 0:

                self.current_step = np.random.randint(
                    0,
                    max_start + 1
                )

            else:

                self.current_step = 0

        else:

            self.current_step = 0

        self.cash = self.initial_cash

        self.shares = 0.0

        self.portfolio_value = (
            self.initial_cash
        )

        self.previous_portfolio_value = (
            self.initial_cash
        )

        self.max_portfolio_value = (
            self.initial_cash
        )

        self.max_drawdown = 0.0

        self.trade_count = 0

        self.buy_count = 0

        self.sell_count = 0

        self.hold_count = 0

        self.trade_history = []

        return self._get_state()

    # ========================================================
    # STATE
    # ========================================================

    def _get_state(self):

        feature_state = (
            self.features
            .iloc[self.current_step]
            .values
            .astype(np.float32)
        )

        price = float(
            self.prices[
                self.current_step
            ]
        )

        stock_value = (
            self.shares * price
        )

        portfolio_value = (
            self.cash +
            stock_value
        )

        portfolio_value = max(
            portfolio_value,
            1.0
        )

        cash_ratio = (
            self.cash /
            portfolio_value
        )

        position_ratio = (
            stock_value /
            portfolio_value
        )

        time_ratio = (
            self.current_step /
            max(len(self.df) - 1, 1)
        )

        portfolio_state = np.array(
            [
                cash_ratio,
                position_ratio,
                time_ratio
            ],
            dtype=np.float32
        )

        state = np.concatenate(
            [
                feature_state,
                portfolio_state
            ]
        )

        return state.astype(
            np.float32
        )

    # ========================================================
    # BUY
    # ========================================================

    def _buy(self, current_price):

        # Target approximately 95% of portfolio
        # in the stock.

        portfolio_value = (
            self.cash +
            self.shares * current_price
        )

        target_value = (
            portfolio_value * 0.95
        )

        current_stock_value = (
            self.shares * current_price
        )

        additional_value = (
            target_value -
            current_stock_value
        )

        if additional_value <= 0:

            return

        execution_price = (
            current_price *
            (1 + self.slippage)
        )

        total_cost_per_share = (
            execution_price *
            (1 + self.transaction_cost)
        )

        shares_to_buy = (
            additional_value /
            total_cost_per_share
        )

        max_affordable = (
            self.cash /
            total_cost_per_share
        )

        shares_to_buy = min(
            shares_to_buy,
            max_affordable
        )

        if shares_to_buy <= 0:

            return

        gross_cost = (
            shares_to_buy *
            execution_price
        )

        transaction_fee = (
            gross_cost *
            self.transaction_cost
        )

        total_cost = (
            gross_cost +
            transaction_fee
        )

        self.cash -= total_cost

        self.shares += shares_to_buy

        self.buy_count += 1

        self.trade_count += 1

        self.trade_history.append(
            {
                "step": self.current_step,
                "date": self.df[
                    "trade_date"
                ].iloc[
                    self.current_step
                ],
                "action": "BUY",
                "price": current_price,
                "execution_price": execution_price,
                "shares": shares_to_buy,
                "transaction_cost": transaction_fee,
                "cash": self.cash
            }
        )

    # ========================================================
    # SELL
    # ========================================================

    def _sell(self, current_price):

        if self.shares <= 0:

            return

        execution_price = (
            current_price *
            (1 - self.slippage)
        )

        sold_shares = self.shares

        gross_proceeds = (
            sold_shares *
            execution_price
        )

        transaction_fee = (
            gross_proceeds *
            self.transaction_cost
        )

        net_proceeds = (
            gross_proceeds -
            transaction_fee
        )

        self.cash += net_proceeds

        self.shares = 0.0

        self.sell_count += 1

        self.trade_count += 1

        self.trade_history.append(
            {
                "step": self.current_step,
                "date": self.df[
                    "trade_date"
                ].iloc[
                    self.current_step
                ],
                "action": "SELL",
                "price": current_price,
                "execution_price": execution_price,
                "shares": sold_shares,
                "transaction_cost": transaction_fee,
                "cash": self.cash
            }
        )

    # ========================================================
    # STEP
    # ========================================================

    def step(self, action):

        action = int(action)

        if action not in (
            self.HOLD,
            self.BUY,
            self.SELL
        ):

            raise ValueError(
                "Action must be 0, 1 or 2."
            )

        if (
            self.current_step >=
            len(self.df) - 1
        ):

            raise RuntimeError(
                "Episode is finished. "
                "Call reset()."
            )

        current_price = float(
            self.prices[
                self.current_step
            ]
        )

        old_value = (
            self.cash +
            self.shares * current_price
        )

        # ----------------------------------------------------
        # ACTION
        # ----------------------------------------------------

        if action == self.HOLD:

            self.hold_count += 1

        elif action == self.BUY:

            self._buy(
                current_price
            )

        elif action == self.SELL:

            self._sell(
                current_price
            )

        # ----------------------------------------------------
        # MOVE TO NEXT DAY
        # ----------------------------------------------------

        self.current_step += 1

        done = (
            self.current_step >=
            len(self.df) - 1
        )

        next_price = float(
            self.prices[
                self.current_step
            ]
        )

        # ----------------------------------------------------
        # NEW PORTFOLIO VALUE
        # ----------------------------------------------------

        self.portfolio_value = (
            self.cash +
            self.shares * next_price
        )

        # ----------------------------------------------------
        # RETURN
        # ----------------------------------------------------

        portfolio_return = (
            self.portfolio_value -
            old_value
        ) / max(
            old_value,
            1.0
        )

        # ----------------------------------------------------
        # MAX VALUE
        # ----------------------------------------------------

        self.max_portfolio_value = max(
            self.max_portfolio_value,
            self.portfolio_value
        )

        # ----------------------------------------------------
        # DRAWDOWN
        # ----------------------------------------------------

        drawdown = (
            self.portfolio_value -
            self.max_portfolio_value
        ) / max(
            self.max_portfolio_value,
            1.0
        )

        self.max_drawdown = min(
            self.max_drawdown,
            drawdown
        )

        # ----------------------------------------------------
        # REWARD
        # ----------------------------------------------------

        reward = portfolio_return

        # Penalize large drawdowns moderately.

        if drawdown < -0.10:

            reward -= (
                abs(drawdown) * 0.10
            )

        self.previous_portfolio_value = (
            self.portfolio_value
        )

        # ----------------------------------------------------
        # INFO
        # ----------------------------------------------------

        info = {
            "step": self.current_step,
            "date": self.df[
                "trade_date"
            ].iloc[
                self.current_step
            ],
            "price": next_price,
            "cash": self.cash,
            "shares": self.shares,
            "portfolio_value":
                self.portfolio_value,
            "portfolio_return":
                portfolio_return,
            "drawdown":
                drawdown,
            "action":
                action,
            "trade_count":
                self.trade_count
        }

        return (
            self._get_state(),
            float(reward),
            done,
            info
        )

    # ========================================================
    # GET PORTFOLIO VALUE
    # ========================================================

    def portfolio_value_now(self):

        index = min(
            self.current_step,
            len(self.prices) - 1
        )

        price = float(
            self.prices[index]
        )

        return (
            self.cash +
            self.shares * price
        )

    def get_portfolio_value(self):

        return self.portfolio_value_now()

    # ========================================================
    # GET PROFIT
    # ========================================================

    def get_profit(self):

        return (
            self.portfolio_value_now()
            -
            self.initial_cash
        )

    # ========================================================
    # GET DRAWDOWN
    # ========================================================

    def get_drawdown(self):

        return self.max_drawdown

    # ========================================================
    # TRADE HISTORY
    # ========================================================

    def get_trade_history(self):

        return self.trade_history