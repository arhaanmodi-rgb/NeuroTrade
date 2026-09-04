import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'data', 'trades.db')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock TEXT,
                action TEXT,
                price REAL,
                shares REAL,
                portfolio_value REAL,
                cash REAL,
                timestamp TEXT
            )
        ''')
        conn.commit()

def log_trade(stock, action, price, shares, portfolio_value, cash, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO trades (stock, action, price, shares, portfolio_value, cash, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (stock, action, price, shares, portfolio_value, cash, timestamp))
        conn.commit()

def get_trades(stock=None, limit=100):
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if stock:
            cursor.execute('SELECT * FROM trades WHERE stock = ? ORDER BY id DESC LIMIT ?', (stock, limit))
        else:
            cursor.execute('SELECT * FROM trades ORDER BY id DESC LIMIT ?', (limit,))
        return [dict(row) for row in cursor.fetchall()]

def get_all_trades(limit=500):
    return get_trades(None, limit)
