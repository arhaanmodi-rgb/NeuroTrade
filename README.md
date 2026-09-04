# 📈 NeuroTrade — Enterprise AI Trading & Risk Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Q--Network-EE4C2C.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST%20Engine-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18%20Vite-61DAFB.svg)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon%20Cloud-336791.svg)](https://neon.tech/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**NeuroTrade** is an institutional-grade algorithmic trading and portfolio risk management platform built for Indian stock exchanges (NSE & BSE). It leverages **Deep Reinforcement Learning (Double DQN)** across 88 custom-trained neural models, integrates with **BharatStock Official API** and **Exchange Gateways** for live price streaming, and persists all trades, holdings, and risk alarms to **Cloud PostgreSQL (Neon)**.

---

## 🏛️ Platform Architecture

```mermaid
graph TD
    A[Indian Equities Universe: 88 Verified Stocks] --> B[Hybrid Real-Time Market Feed Gateway]
    B -->|Tier 1: Institutional Financials| C[BharatStock Official API]
    B -->|Tier 2: Tick Streams & Candlesticks| D[NSE / BSE Exchange Gateway]
    
    C & D --> E[24-Feature Technical Engineering Engine]
    E --> F[PyTorch Deep Q-Networks DQN Models]
    
    F --> G[FastAPI Trading Backend API]
    G --> H[Neon Cloud PostgreSQL Database]
    G --> I[React + Vite TailAdmin Trading Terminal]
```

---

## 🌟 Key Features

* **🧠 88 Custom PyTorch Deep Q-Networks (`models/*.pth`)**:
  - Dedicated neural models trained on 5+ years of daily historical candlestick data.
  - Generates neural `BUY` / `HOLD` / `SELL` decisions with confidence ratings.
* **📡 Hybrid Market Data Stream**:
  - Direct integration with **BharatStock API** (`X-API-Key`) for 52-week highs/lows, PE ratios, and institutional metrics.
  - Multi-year candlestick technical charting studio (1W, 1M, 6M, 1Y, 2Y, 3Y, 5Y).
* **☁️ Cloud PostgreSQL Database (Neon.tech)**:
  - Real-time cloud persistence for user authentication (JWT), portfolio holdings, trade logs, and stop-loss breach alarms.
* **🛡️ Real-Time Risk & Stop-Loss Engine**:
  - Automatic trailing stop-loss, profit target breach monitoring, and interactive execution alerts.
* **🚫 Strict Real-Stock Validation**:
  - Eradicated synthetic/dummy stock generation. Unlisted or fake tickers are strictly rejected with HTTP 400/404 validation alerts.
* **🎨 TailAdmin Modern Dashboard**:
  - Collapsible stationary sidebar, global search, light/dark theme toggle, interactive notifications dropdown, and live portfolio distribution analytics.

---

## 📂 Project Structure

```
NeuroTrade/
├── api/                        # FastAPI Backend Application
│   ├── database.py             # Cloud PostgreSQL / SQLite Engine Connection
│   ├── main.py                 # API Root & Router Mounting
│   ├── models/
│   │   ├── db_models.py        # SQLAlchemy Cloud Database Schemas
│   │   └── schemas.py          # Pydantic Request & Response Models
│   ├── routes/
│   │   ├── auth.py             # User Signup, Login & JWT Tokens
│   │   ├── holdings.py         # Portfolio Management & AI Guidance
│   │   ├── predict.py          # Deep Q-Network Inference
│   │   ├── stocks.py           # Candlestick Data & Stock Search
│   │   └── trades.py           # Order Execution & Trade Ledger
│   └── services/
│       ├── ai_reasoning.py     # LLM / Rule-Based Portfolio Guidance
│       ├── auth.py             # Password Hashing (bcrypt) & JWT Handler
│       ├── live_data.py        # BharatStock & Exchange Feeds
│       ├── predictor.py        # Dynamic DQN Checkpoint Loader
│       └── stock_universe.py   # Verified 93 Indian Equities Directory
│
├── data/                       # Market Datasets & Features
│   ├── raw/                    # 5-Year Historical OHLCV Datasets
│   └── features/               # 24-Dimensional Technical Indicator Matrices
│
├── frontend/                   # React 18 + Vite Trading Terminal
│   ├── src/
│   │   ├── components/         # Modular Dashboard UI Components
│   │   │   ├── Sidebar.jsx
│   │   │   ├── TopNavbar.jsx
│   │   │   ├── TopStockCards.jsx
│   │   │   ├── StockHistoryChart.jsx
│   │   │   ├── SignalPanel.jsx
│   │   │   ├── RiskAlarms.jsx
│   │   │   ├── UserHoldingsTable.jsx
│   │   │   ├── TradeHistory.jsx
│   │   │   └── NotificationDropdown.jsx
│   │   ├── services/api.js     # Axios API Client
│   │   ├── App.jsx             # Master Dashboard Layout
│   │   └── index.css           # TailAdmin Design System & Theme Engine
│   └── package.json
│
├── models/                     # 88 Custom PyTorch Checkpoints (*_dqn_best.pth)
├── dqn_agent.py                # Deep Q-Network Agent Architecture
├── trading_environment.py      # Gymnasium Trading Environment (24 States)
├── feature_engineering.py      # Technical Indicator Calculations (RSI, MACD, etc.)
├── train_universe.py           # Automated Multi-Stock Batch Trainer
├── requirements.txt            # Python Dependencies
├── .env.example                # Safe Template for Environment Variables
└── .gitignore                  # Security Rules for Secrets & Artifacts
```

---

## ⚡ Quickstart Guide

### 1. Clone the Repository & Configure Environment

```bash
git clone https://github.com/YOUR_USERNAME/NeuroTrade.git
cd NeuroTrade

# Copy environment template to .env
cp .env.example .env
```

Edit your `.env` file with your credentials:
```ini
# BharatStock API Key
BHARAT_STOCK_API_KEY=your_bharat_stock_api_key_here

# Cloud Database (Neon / Supabase / PostgreSQL)
DATABASE_URL=postgresql://username:password@your-cloud-host.neon.tech/neondb?sslmode=require

# JWT Secret Key
SECRET_KEY=your_secure_random_jwt_secret_key_here
```

---

### 2. Backend Setup & Startup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Launch FastAPI Server
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Backend API will be live at: **`http://127.0.0.1:8000`**  
Interactive API Docs (Swagger UI): **`http://127.0.0.1:8000/docs`**

---

### 3. Frontend Setup & Startup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install Node dependencies
npm install

# 3. Launch Vite Dev Server
npm run dev
```

Frontend Dashboard will be live at: **`http://127.0.0.1:5173`**

---

## 🤖 Deep Q-Network Training Pipeline

To retrain or update neural models across all verified Indian equities:

```bash
# Train all verified stocks in the directory
python train_universe.py

# Train a single stock model
python train_dqn.py --stock RELIANCE --episodes 200
```

---

## 🛡️ Security & Privacy

* **Secret Isolation**: Real API keys, JWT secrets, and database connection strings are confined to `.env` and strictly excluded by `.gitignore`.
* **Database Encryption**: All database passwords and connections are transmitted over SSL/TLS (`sslmode=require`).
* **Authentication**: User passwords are encrypted using `bcrypt` with cryptographic salts.

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
