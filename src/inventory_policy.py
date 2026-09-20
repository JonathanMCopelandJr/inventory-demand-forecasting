"""
inventory_policy.py

Translates demand forecasts and forecast error into actionable inventory
policy: safety stock and reorder point, using a service-level (z-score)
approach commonly used in buyer/planner workflows.

Safety Stock = z * sigma_demand_during_lead_time
Reorder Point = (avg_daily_demand * lead_time_days) + Safety Stock

Run:
    python src/inventory_policy.py
"""

import os
import numpy as np
import pandas as pd
from scipy.stats import norm

from forecasting_models import load_sku_series, sarima_forecast

DATA_PATH = os.path.join("data", "demand_data.csv")

SERVICE_LEVEL = 0.95   # 95% service level -> covers stockout risk
LEAD_TIME_DAYS = 7      # assumed supplier lead time
FORECAST_HORIZON = 28


def compute_policy_for_sku(series, lead_time_days=LEAD_TIME_DAYS,
                            service_level=SERVICE_LEVEL, horizon=FORECAST_HORIZON):
    forecast = sarima_forecast(series, horizon)
    avg_daily_demand = float(np.mean(forecast))

    residual_std = float(series.diff().std())
    z = norm.ppf(service_level)

    safety_stock = z * residual_std * np.sqrt(lead_time_days)
    reorder_point = avg_daily_demand * lead_time_days + safety_stock

    return {
        "avg_daily_demand_forecast": round(avg_daily_demand, 1),
        "demand_std": round(residual_std, 1),
        "service_level": service_level,
        "z_score": round(z, 3),
        "lead_time_days": lead_time_days,
        "safety_stock_units": round(safety_stock, 1),
        "reorder_point_units": round(reorder_point, 1),
    }


def main():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    sku_ids = sorted(df["sku_id"].unique())

    records = []
    for sku_id in sku_ids:
        series = load_sku_series(df, sku_id)
        policy = compute_policy_for_sku(series)
        policy["sku_id"] = sku_id
        records.append(policy)
        print(f"{sku_id}: reorder_point={policy['reorder_point_units']} units, "
              f"safety_stock={policy['safety_stock_units']} units")

    result_df = pd.DataFrame(records)
    os.makedirs("reports", exist_ok=True)
    out_path = os.path.join("reports", "inventory_policy.csv")
    result_df.to_csv(out_path, index=False)
    print(f"\nSaved inventory policy recommendations to {out_path}")


if __name__ == "__main__":
    main()
