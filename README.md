# 📈 NeuroTrade — AI-Powered Indian Stock Trading

NeuroTrade uses a **Double Deep Q-Network (DQN)** to generate BUY / HOLD / SELL signals for Indian stocks.

## Features

- 🧠 **DQN Agent** trained on 21 technical indicators
- 📊 **Backtesting** on historical NSE data with Sharpe ratio, drawdown metrics
- 🌐 **FastAPI backend** with REST endpoints
- ⚛️ **React dashboard** with live charts and signal panel
- 🔊 **Voice announcements** via pyttsx3 (offline TTS)
- 📡 **BharatStock API** integration for live prices
- 🏦 Supports: RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK

## Quick Start

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Install frontend dependencies
```bash
cd frontend
npm install
```

### 3. Train the models (if not already trained)
```bash
# Train one stock:
python train_dqn.py --stock RELIANCE --episodes 200

# Train all 5 stocks:
python train_all_stocks.py
```

### 4. Validate the model
```bash
python validate_model.py
```
Results saved to `results/RELIANCE_validation.png` and `results/RELIANCE_validation_report.txt`

### 5. Run backtest
```bash
python backtest.py
```

### 6. Launch everything (Windows)
```bash
run.bat
```
This starts the API on **port 8000** and dashboard on **port 5173** and opens the browser.

### 7. Or start manually:
```bash
# Terminal 1 — Backend
uvicorn api.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend && npm run dev

# Terminal 3 — Live predictor (optional)
python live_predictor.py

# Terminal 3 — Live predictor with voice
python live_predictor.py --announce-hold
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check + loaded models |
| GET | `/signal/{stock}` | Latest BUY/HOLD/SELL signal |
| GET | `/stocks` | List of available stocks |
| GET | `/portfolio` | Portfolio state |
| GET | `/trades` | Trade history |
| GET | `/backtest/{stock}` | Backtest report |
| GET | `/docs` | Interactive API docs (Swagger) |

## Project Structure

```
NeuroTrade/
├── train_dqn.py             # Train DQN for one stock
├── train_all_stocks.py      # Train all 5 stocks
├── validate_model.py        # Validate on test set
├── backtest.py              # Full backtest
├── live_predictor.py        # Live inference + voice
├── dqn_agent.py             # Double DQN agent
├── trading_environment.py   # Gym-style trading env
├── feature_engineering.py   # Technical indicators
├── metrics.py               # Sharpe, drawdown, etc.
├── api/                     # FastAPI backend
│   ├── main.py
│   ├── routes/
│   └── services/
├── frontend/                # React + Vite dashboard
│   └── src/
├── voice/                   # TTS module
├── models/                  # Trained .pth files
├── data/features/           # Feature-engineered CSVs
├── results/                 # Charts and reports
├── tests/                   # pytest tests
├── run.bat                  # One-click launcher
└── requirements.txt
```

## Configuration

Edit `.env` to configure:
```
MODE=DEMO                    # DEMO (CSV fallback) or LIVE
BHARATSTOCK_API_KEY=...      # Your BharatStock API key
```

## Disclaimer

This project is for **educational purposes only**. NeuroTrade does not constitute financial advice. Always consult a SEBI-registered advisor before trading.
