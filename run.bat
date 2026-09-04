@echo off
title NeuroTrade — AI Trading System
echo.
echo  ========================================
echo    NEUROTRADE AI TRADING SYSTEM
echo  ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install from python.org
    pause
    exit /b 1
)

REM Check if models exist
if not exist "models\RELIANCE_dqn_best.pth" (
    echo [WARNING] No trained models found.
    echo Run: python train_dqn.py  to train RELIANCE
    echo Run: python train_all_stocks.py  to train all stocks
    echo.
)

REM Start FastAPI backend in background
echo [1/2] Starting FastAPI backend on http://localhost:8000 ...
start "NeuroTrade API" cmd /k "python -m uvicorn api.main:app --reload --port 8000"

REM Wait 3 seconds for API to start
timeout /t 3 /nobreak > nul

REM Start React frontend
echo [2/2] Starting React dashboard on http://localhost:5173 ...
if exist "frontend\node_modules" (
    start "NeuroTrade Dashboard" cmd /k "cd frontend && npm run dev"
) else (
    echo [INFO] Installing frontend dependencies first...
    cd frontend
    npm install
    cd ..
    start "NeuroTrade Dashboard" cmd /k "cd frontend && npm run dev"
)

REM Open browser after 4 seconds
timeout /t 4 /nobreak > nul
echo.
echo  Opening dashboard in browser...
start http://localhost:5173

echo.
echo  ========================================
echo    NEUROTRADE RUNNING!
echo    Dashboard : http://localhost:5173
echo    API       : http://localhost:8000
echo    API Docs  : http://localhost:8000/docs
echo  ========================================
echo.
echo  Close the terminal windows to stop.
pause
