import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.database import engine, Base, apply_migrations
from api.models import db_models
from api.routes import health, predict, portfolio, backtest, auth, stocks, trades, holdings
from api.services.trade_log import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
        Base.metadata.create_all(bind=engine)
        apply_migrations()
        print('[NeuroTrade API] Database initialized & models loaded with column migrations.')
    except Exception as e:
        print(f'[NeuroTrade API] Notice: Database startup check: {e}')
    yield

app = FastAPI(
    title='NeuroTrade API',
    description='AI-powered Indian stock trading signals using Deep Q-Network for 7,000+ NSE & BSE stocks',
    version='2.0.0',
    lifespan=lifespan
)

# CORS for React frontend (Vercel, Render, local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app|http://localhost:.*|http://127.0.0.1:.*|https://.*\.onrender\.com",
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

# Routers
app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(trades.router)
app.include_router(holdings.router)
app.include_router(health.router, tags=['Health'])
app.include_router(predict.router, tags=['Signals'])
app.include_router(portfolio.router, tags=['Portfolio'])
app.include_router(backtest.router, tags=['Backtest'])

@app.get('/')
def root():
    return {
        'name': 'NeuroTrade AI Trading API',
        'version': '2.0.0',
        'docs': '/docs',
        'status': 'running',
        'supported_universe': '7,000+ Stocks (NSE / BSE / SME)'
    }
