"""
generate_data.py

Generates a realistic synthetic daily demand dataset for multiple retail SKUs.
Includes trend, weekly seasonality, annual seasonality, holiday spikes, and
random promotional lifts, so downstream forecasting models have realistic
signal and noise to work with.

Run:
    python src/generate_data.py
Output:
    data/demand_data.csv
"""

import os
import numpy as np
import pandas as pd

RANDOM_SEED = 42
N_DAYS = 730
START_DATE = "2024-01-01"

SKUS = [
    # sku_id, category, base_daily_demand, annual_seasonality_amplitude
    ("SKU-1001", "Beverages", 120, 0.35),
    ("SKU-1002", "Snacks", 80, 0.25),
    ("SKU-1003", "Dairy", 60, 0.15),
    ("SKU-1004", "Frozen Foods", 45, 0.30),
    ("SKU-1005", "Household", 30, 0.10),
    ("SKU-1006", "Personal Care", 25, 0.10),
]


def is_holiday_boost(date):
    """Return a demand multiplier for major US retail holidays/peaks."""
    if (date.month == 11 and 20 <= date.day <= 29):
        return 1.6
    if (date.month == 12 and 15 <= date.day <= 25):
        return 1.6
    if (date.month == 12 and 26 <= date.day <= 31):
        return 1.3
    if (date.month == 7 and 1 <= date.day <= 4):
        return 1.4
    return 1.0


def generate_sku_series(dates, base, seasonality_amp, rng):
    n = len(dates)
    trend = np.linspace(0, base * 0.15, n)
    weekly = 1 + 0.25 * np.sin(2 * np.pi * dates.dayofweek.values / 7)
    annual = 1 + seasonality_amp * np.sin(2 * np.pi * dates.dayofyear.values / 365.25 - np.pi / 2)
    holiday = np.array([is_holiday_boost(d) for d in dates])
    noise = rng.normal(0, base * 0.08, n)

    demand = (base + trend) * weekly * annual * holiday + noise
    return np.clip(demand, 0, None).round().astype(int)


def generate_dataset(random_seed=RANDOM_SEED, n_days=N_DAYS, start_date=START_DATE):
    rng = np.random.default_rng(random_seed)
    dates = pd.date_range(start_date, periods=n_days, freq="D")

    all_rows = []
    for sku_id, category, base, seasonality_amp in SKUS:
        demand = generate_sku_series(dates, base, seasonality_amp, rng)

        unit_price = round(float(rng.uniform(2.5, 15.0)), 2)
        promo_flag = rng.binomial(1, 0.08, n_days)
        promo_multiplier = rng.uniform(1.3, 1.8, n_days)
        demand = np.where(promo_flag == 1, (demand * promo_multiplier).astype(int), demand)

        sku_df = pd.DataFrame({
            "date": dates,
            "sku_id": sku_id,
            "category": category,
            "unit_price": unit_price,
            "promo_flag": promo_flag,
            "units_sold": demand,
        })
        all_rows.append(sku_df)

    return pd.concat(all_rows, ignore_index=True)


def main():
    df = generate_dataset()
    os.makedirs("data", exist_ok=True)
    out_path = os.path.join("data", "demand_data.csv")
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df):,} rows to {out_path}")
    print(df.groupby("sku_id")["units_sold"].agg(["mean", "std", "min", "max"]))


if __name__ == "__main__":
    main()
