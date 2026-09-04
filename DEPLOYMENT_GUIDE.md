# 🚀 NeuroTrade Enterprise — Complete Cloud Deployment Guide

This guide walks you through deploying **NeuroTrade** with a **Free Cloud PostgreSQL Database** so all user logins, purchased holdings, Stop-Loss limits, and trade history persist safely in the cloud.

---

## 📦 Step 1: Create a Free Cloud Database (2 Minutes)

You can use **[Neon.tech](https://neon.tech)** (Serverless PostgreSQL) or **[Supabase](https://supabase.com)** (Free Tier):

### Option A: Neon.tech (Recommended — Fast & Free)
1. Go to **[https://neon.tech](https://neon.tech)** and click **Sign Up** (with GitHub or Google).
2. Click **Create Project** -> Name it `neurotrade-db`.
3. In the Dashboard, copy the **Connection String**:
   ```text
   postgresql://alex:AbCdEf12345@ep-cool-flower-789.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
   ```
4. Save this connection string — you will use it as your `DATABASE_URL`.

---

## ⚙️ Step 2: Connect the Database to Your Project

### Testing Cloud Database Locally:
In your project root directory (`NeuroTrade/`), create or edit `.env`:
```env
DATABASE_URL=postgresql://alex:AbCdEf12345@ep-cool-flower-789.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
JWT_SECRET_KEY=neurotrade_super_secret_jwt_key_2026_sebi_approved
MARKET_DATA_MODE=LIVE
```
When you start the server (`uvicorn api.main:app`), NeuroTrade will automatically connect to your Cloud PostgreSQL database, create all tables (`users`, `user_holdings`, `user_trades`, `user_watchlists`), and store all data in the cloud!

---

## 🌐 Step 3: Deploy Backend & Frontend Online (100% Free)

### Deploy on [Render.com](https://render.com):

1. Push your code to **GitHub**:
   ```bash
   git init
   git add .
   git commit -m "NeuroTrade Enterprise Production Build"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/neurotrade.git
   git push -u origin main
   ```

2. **Deploy Backend (Web Service)**:
   - Go to [dashboard.render.com](https://dashboard.render.com) -> **New Web Service**.
   - Connect your GitHub repository.
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - `DATABASE_URL`: *(Paste your Neon / Supabase connection string)*
     - `JWT_SECRET_KEY`: `your_random_secret_key`

3. **Deploy Frontend (Static Site or Vercel)**:
   - **On Render**:
     - **New Static Site** -> Connect your repo.
     - **Root Directory**: `frontend`
     - **Build Command**: `npm install && npm run build`
     - **Publish Directory**: `frontend/dist`
   - **On Vercel ([vercel.com](https://vercel.com))**:
     - Import repo -> Set root directory to `frontend` -> Click **Deploy**!

---

## 🔒 Security & Data Persistence Checklist

- [x] Passwords are encrypted with salted **Bcrypt** hashing.
- [x] Sessions use signed **JWT 256-bit** tokens.
- [x] Cloud Database runs with **SSL encryption** (`sslmode=require`).
- [x] Auto-reconnecting connection pool enabled via **SQLAlchemy ORM**.
