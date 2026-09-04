# -*- coding: utf-8 -*-
"""
NeuroTrade — Train All Stocks
Trains a separate DQN model for each stock sequentially.

Usage:
    python train_all_stocks.py                           # train missing models
    python train_all_stocks.py --force                   # retrain all
    python train_all_stocks.py --stocks RELIANCE TCS     # specific stocks
    python train_all_stocks.py --episodes 300            # custom episode count
"""

import sys
import os
import argparse
import subprocess
import time
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")


# ============================================================
# CLI ARGUMENTS
# ============================================================

parser = argparse.ArgumentParser(description="NeuroTrade — Train All Stocks")

parser.add_argument(
    "--stocks",
    nargs="+",
    default=["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"],
    help="Stocks to train (default: all 5)"
)

parser.add_argument(
    "--episodes",
    type=int,
    default=200,
    help="Training episodes per stock (default: 200)"
)

parser.add_argument(
    "--force",
    action="store_true",
    help="Retrain even if model already exists"
)

args = parser.parse_args()


# ============================================================
# HEADER
# ============================================================

print()
print("=" * 70)
print("           NEUROTRADE — MULTI-STOCK TRAINING")
print("=" * 70)
print()
print(f"Stocks    : {', '.join(args.stocks)}")
print(f"Episodes  : {args.episodes}")
print(f"Force     : {args.force}")
print(f"Started   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()


# ============================================================
# TRAINING RESULTS
# ============================================================

results = []


# ============================================================
# TRAIN EACH STOCK
# ============================================================

for stock in args.stocks:

    data_path = f"data/features/{stock}.csv"
    model_path = f"models/{stock}_dqn_best.pth"

    print()
    print("=" * 70)
    print(f"  STOCK: {stock}")
    print("=" * 70)
    print()


    # --------------------------------------------------------
    # CHECK DATA
    # --------------------------------------------------------

    if not os.path.exists(data_path):
        print(f"  [SKIP] Feature data not found: {data_path}")
        results.append({
            "stock": stock,
            "status": "SKIPPED",
            "reason": "Data not found",
            "duration": 0
        })
        continue


    # --------------------------------------------------------
    # CHECK EXISTING MODEL
    # --------------------------------------------------------

    if os.path.exists(model_path) and not args.force:
        print(f"  [SKIP] Model already exists: {model_path}")
        print(f"         Use --force to retrain.")
        results.append({
            "stock": stock,
            "status": "SKIPPED",
            "reason": "Model already exists",
            "duration": 0
        })
        continue


    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    print(f"  Training {stock} for {args.episodes} episodes...")
    print()

    start_time = time.time()

    cmd = [
        sys.executable,
        "train_dqn.py",
        "--stock", stock,
        "--episodes", str(args.episodes)
    ]

    try:
        proc = subprocess.run(
            cmd,
            check=False
        )

        duration = time.time() - start_time
        duration_str = f"{duration / 60:.1f} min"

        if proc.returncode == 0:
            print()
            print(f"  [OK] {stock} trained in {duration_str}")
            results.append({
                "stock": stock,
                "status": "TRAINED",
                "reason": f"Completed in {duration_str}",
                "duration": duration
            })
        else:
            print()
            print(f"  [ERROR] {stock} training failed (exit code {proc.returncode})")
            results.append({
                "stock": stock,
                "status": "FAILED",
                "reason": f"Exit code {proc.returncode}",
                "duration": duration
            })

    except Exception as e:
        duration = time.time() - start_time
        print(f"  [ERROR] {stock}: {e}")
        results.append({
            "stock": stock,
            "status": "FAILED",
            "reason": str(e),
            "duration": duration
        })


# ============================================================
# SUMMARY TABLE
# ============================================================

print()
print("=" * 70)
print("                    TRAINING SUMMARY")
print("=" * 70)
print()

header = f"{'Stock':<14} {'Status':<10} {'Duration':<12} {'Reason'}"
print(header)
print("-" * 70)

for r in results:
    dur = f"{r['duration'] / 60:.1f} min" if r["duration"] > 0 else "—"
    status_icon = {
        "TRAINED": "✓",
        "SKIPPED": "○",
        "FAILED": "✗"
    }.get(r["status"], "?")
    print(f"  {status_icon} {r['stock']:<12} {r['status']:<10} {dur:<12} {r['reason']}")

print()

trained = sum(1 for r in results if r["status"] == "TRAINED")
skipped = sum(1 for r in results if r["status"] == "SKIPPED")
failed  = sum(1 for r in results if r["status"] == "FAILED")

print(f"Trained: {trained}  |  Skipped: {skipped}  |  Failed: {failed}")
print()
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()
print("=" * 70)
