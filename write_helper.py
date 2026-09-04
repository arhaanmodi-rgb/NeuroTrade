content = r'''"""
train_all_stocks.py - NeuroTrade multi-stock training orchestrator

Trains a separate DQN model for each stock by calling train_dqn.py
as a subprocess.

Usage:
    python train_all_stocks.py                         # train all missing models
    python train_all_stocks.py --force                 # retrain all stocks
    python train_all_stocks.py --stocks RELIANCE TCS   # specific stocks only
    python train_all_stocks.py --episodes 300          # custom episode count
"""

import argparse
import os
import subprocess
import sys
import time

# ============================================================
# CONFIGURATION
# ============================================================

ALL_STOCKS = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]

# ============================================================
# CLI ARGUMENTS
# ============================================================

parser = argparse.ArgumentParser(
    description="NeuroTrade - Train DQN models for multiple stocks sequentially"
)
parser.add_argument(
    "--stocks",
    type=str,
    nargs="+",
    default=None,
    metavar="STOCK",
    help="Stocks to train (default: all). Choices: RELIANCE TCS INFY HDFCBANK ICICIBANK",
)
parser.add_argument(
    "--force",
    action="store_true",
    help="Retrain even if a saved model already exists",
)
parser.add_argument(
    "--episodes",
    type=int,
    default=200,
    help="Number of training episodes per stock (default: 200)",
)
parser.add_argument(
    "--episode-length",
    type=int,
    default=252,
    help="Steps per episode (default: 252)",
)
args = parser.parse_args()

# ============================================================
# RESOLVE STOCK LIST
# ============================================================

stocks_to_train = args.stocks if args.stocks else ALL_STOCKS

invalid = [s for s in stocks_to_train if s not in ALL_STOCKS]
if invalid:
    print("[ERROR] Unknown stock(s): " + ", ".join(invalid))
    print("        Valid choices: " + ", ".join(ALL_STOCKS))
    sys.exit(1)

# ============================================================
# HELPERS
# ============================================================

STATUS_TRAINED = "TRAINED"
STATUS_SKIPPED_MODEL = "SKIPPED (model exists)"
STATUS_SKIPPED_DATA = "SKIPPED (no data)"
STATUS_FAILED = "FAILED"


def features_path(stock):
    return os.path.join("data", "features", stock + ".csv")


def model_path(stock):
    return os.path.join("models", stock + "_dqn_best.pth")


def print_header(stock, index, total):
    print()
    print("=" * 70)
    print("  [" + str(index) + "/" + str(total) + "] Training: " + stock)
    print("=" * 70)


def fmt_duration(seconds):
    if seconds < 60:
        return str(round(seconds, 1)) + "s"
    m, s = divmod(int(seconds), 60)
    if m < 60:
        return str(m) + "m " + str(s) + "s"
    h, m = divmod(m, 60)
    return str(h) + "h " + str(m) + "m " + str(s) + "s"


# ============================================================
# MAIN LOOP
# ============================================================

results = []  # list of dicts: {stock, status, duration}

total = len(stocks_to_train)
print()
print("=" * 70)
print("          NEUROTRADE - MULTI-STOCK DQN TRAINING")
print("=" * 70)
print("  Stocks      : " + ", ".join(stocks_to_train))
print("  Episodes    : " + str(args.episodes))
print("  Ep. Length  : " + str(args.episode_length) + " steps")
print("  Force mode  : " + ("ON" if args.force else "OFF"))
print("=" * 70)

for idx, stock in enumerate(stocks_to_train, start=1):

    # -- Check 1: feature data exists ------------------------------------------
    if not os.path.isfile(features_path(stock)):
        print()
        print("[WARNING] " + stock + ": Feature file not found at '" + features_path(stock) + "'. Skipping.")
        results.append({"stock": stock, "status": STATUS_SKIPPED_DATA, "duration": None})
        continue

    # -- Check 2: model already trained ----------------------------------------
    if os.path.isfile(model_path(stock)) and not args.force:
        print()
        print("[INFO] " + stock + ": Model already exists at '" + model_path(stock) + "'. Skipping.")
        print("       Use --force to retrain.")
        results.append({"stock": stock, "status": STATUS_SKIPPED_MODEL, "duration": None})
        continue

    # -- Train -----------------------------------------------------------------
    print_header(stock, idx, total)

    cmd = [
        sys.executable,
        "train_dqn.py",
        "--stock", stock,
        "--episodes", str(args.episodes),
        "--episode-length", str(args.episode_length),
    ]

    print("  Command     : " + " ".join(cmd))
    print()

    t_start = time.time()
    elapsed = 0.0
    status = STATUS_FAILED
    try:
        proc = subprocess.run(cmd, check=False)
        elapsed = time.time() - t_start

        if proc.returncode == 0:
            status = STATUS_TRAINED
            print()
            print("[OK] " + stock + " finished in " + fmt_duration(elapsed) + " (exit code 0).")
        else:
            status = STATUS_FAILED
            print()
            print("[FAIL] " + stock + " exited with code " + str(proc.returncode) +
                  " after " + fmt_duration(elapsed) + ". Continuing with next stock.")
    except Exception as exc:
        elapsed = time.time() - t_start
        status = STATUS_FAILED
        print("[ERROR] " + stock + ": Unexpected error - " + str(exc))

    results.append({"stock": stock, "status": status, "duration": elapsed})

# ============================================================
# SUMMARY TABLE
# ============================================================

print()
print("=" * 70)
print("                       TRAINING SUMMARY")
print("=" * 70)
print("  " + "STOCK".ljust(14) + "STATUS".ljust(26) + "DURATION")
print("  " + "-" * 14 + " " + "-" * 26 + " " + "-" * 10)

trained_count = 0
failed_count = 0
skipped_count = 0

for r in results:
    dur_str = fmt_duration(r["duration"]) if r["duration"] is not None else "-"
    print("  " + r["stock"].ljust(14) + r["status"].ljust(26) + dur_str)
    if r["status"] == STATUS_TRAINED:
        trained_count += 1
    elif r["status"] == STATUS_FAILED:
        failed_count += 1
    else:
        skipped_count += 1

print("  " + "-" * 14 + " " + "-" * 26 + " " + "-" * 10)
print("  Trained: " + str(trained_count) + "   Skipped: " + str(skipped_count) + "   Failed: " + str(failed_count))
print("=" * 70)
print()

if failed_count > 0:
    sys.exit(1)
'''

with open("train_all_stocks.py", "w", newline="\n", encoding="utf-8") as f:
    f.write(content)

print("Done: train_all_stocks.py written successfully.")
