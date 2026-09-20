"""
evaluate.py

Walk-forward (rolling-origin) backtesting harness for the forecasting models
defined in forecasting_models.py. Computes MAE, RMSE, MAPE, and WAPE per SKU
per model, and writes a Markdown summary report to reports/model_comparison.md.

Run:
    python src/evaluate.py
"""

import os
import numpy as np
import pandas as pd

from forecasting_models import MODEL_REGISTRY, load_sku_series

DATA_PATH = os.path.join("data", "demand_data.csv")
REPORT_PATH = os.path.join("reports", "model_comparison.md")

HORIZON = 28
N_FOLDS = 3
STEP = 28


def mae(y_true, y_pred):
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true, y_pred):
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mape(y_true, y_pred):
    mask = y_true != 0
    if not mask.any():
        return np.nan
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def wape(y_true, y_pred):
    denom = np.sum(np.abs(y_true))
    if denom == 0:
        return np.nan
    return float(np.sum(np.abs(y_true - y_pred)) / denom * 100)


def backtest_sku(series, model_fn, horizon=HORIZON, n_folds=N_FOLDS, step=STEP):
    metrics = []
    total_len = len(series)
    for fold in range(n_folds):
        end_idx = total_len - fold * step
        train = series.iloc[: end_idx - horizon]
        test = series.iloc[end_idx - horizon: end_idx]
        if len(train) < 60 or len(test) < horizon:
            continue
        preds = model_fn(train, horizon)
        metrics.append({
            "mae": mae(test.values, preds),
            "rmse": rmse(test.values, preds),
            "mape": mape(test.values, preds),
            "wape": wape(test.values, preds),
        })
    if not metrics:
        return None
    return pd.DataFrame(metrics).mean().to_dict()


def main():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    sku_ids = sorted(df["sku_id"].unique())

    all_results = []
    for sku_id in sku_ids:
        series = load_sku_series(df, sku_id)
        for model_name, model_fn in MODEL_REGISTRY.items():
            result = backtest_sku(series, model_fn)
            if result is None:
                continue
            result.update({"sku_id": sku_id, "model": model_name})
            all_results.append(result)
            print(f"{sku_id:<10s} {model_name:<20s} "
                  f"MAE={result['mae']:.2f}  RMSE={result['rmse']:.2f}  "
                  f"MAPE={result['mape']:.2f}%  WAPE={result['wape']:.2f}%")

    results_df = pd.DataFrame(all_results)
    os.makedirs("reports", exist_ok=True)
    results_df.to_csv(os.path.join("reports", "backtest_results.csv"), index=False)

    summary = results_df.groupby("model")[["mae", "rmse", "mape", "wape"]].mean().sort_values("wape")

    with open(REPORT_PATH, "w") as f:
        f.write("# Model Comparison Report\n\n")
        f.write("Average backtest metrics across all SKUs and folds ")
        f.write(f"(horizon={HORIZON} days, {N_FOLDS} rolling folds).\n\n")
        f.write("| Model | MAE | RMSE | MAPE (%) | WAPE (%) |\n")
        f.write("|---|---|---|---|---|\n")
        for model_name, row in summary.iterrows():
            f.write(f"| {model_name} | {row['mae']:.2f} | {row['rmse']:.2f} | "
                     f"{row['mape']:.2f} | {row['wape']:.2f} |\n")
        f.write("\nLower WAPE indicates better overall forecast accuracy, weighted by volume.\n")
        f.write("\nFull per-SKU results are available in `reports/backtest_results.csv`.\n")

    print(f"\nWrote report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
