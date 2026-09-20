"""
forecasting_models.py

Defines and trains multiple forecasting approaches for SKU-level daily demand:
  1. Naive (last value) and seasonal naive (same weekday last week)
  2. Moving average baselines (7-day, 28-day)
  3. SARIMA (statsmodels) with weekly seasonal order
  4. XGBoost regression using lag, rolling-window, and calendar features

Each model exposes a `fit_predict(train_series, horizon)` style interface so
they can be swapped into the same backtesting harness in evaluate.py.

Run:
    python src/forecasting_models.py
"""

import os
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

DATA_PATH = os.path.join("data", "demand_data.csv")


def load_sku_series(df, sku_id):
    sub = df[df["sku_id"] == sku_id].sort_values("date")
    series = sub.set_index("date")["units_sold"].asfreq("D").fillna(method="ffill")
    return series


# ---------------------------------------------------------------------------
# Baseline models
# ---------------------------------------------------------------------------

def naive_forecast(train, horizon):
    last_value = train.iloc[-1]
    return np.full(horizon, last_value)


def seasonal_naive_forecast(train, horizon, season_length=7):
    last_season = train.iloc[-season_length:].values
    reps = int(np.ceil(horizon / season_length))
    return np.tile(last_season, reps)[:horizon]


def moving_average_forecast(train, horizon, window=7):
    avg = train.iloc[-window:].mean()
    return np.full(horizon, avg)


# ---------------------------------------------------------------------------
# SARIMA
# ---------------------------------------------------------------------------

def sarima_forecast(train, horizon, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7)):
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    model = SARIMAX(
        train,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    fitted = model.fit(disp=False)
    forecast = fitted.forecast(steps=horizon)
    return np.clip(forecast.values, 0, None)


# ---------------------------------------------------------------------------
# XGBoost with engineered features
# ---------------------------------------------------------------------------

def build_features(series, lags=(1, 2, 3, 7, 14, 28), roll_windows=(7, 14, 28)):
    df = pd.DataFrame({"y": series})
    df["dayofweek"] = df.index.dayofweek
    df["month"] = df.index.month
    df["day"] = df.index.day
    for lag in lags:
        df[f"lag_{lag}"] = df["y"].shift(lag)
    for w in roll_windows:
        df[f"roll_mean_{w}"] = df["y"].shift(1).rolling(w).mean()
    return df


def xgboost_forecast(train, horizon, lags=(1, 2, 3, 7, 14, 28), roll_windows=(7, 14, 28)):
    from xgboost import XGBRegressor

    feat_df = build_features(train, lags, roll_windows).dropna()
    feature_cols = [c for c in feat_df.columns if c != "y"]

    model = XGBRegressor(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
    )
    model.fit(feat_df[feature_cols], feat_df["y"])

    history = train.copy()
    preds = []
    for step in range(horizon):
        next_date = history.index[-1] + pd.Timedelta(days=1)
        extended = pd.concat([history, pd.Series([np.nan], index=[next_date])])
        feat_row = build_features(extended, lags, roll_windows).iloc[[-1]][feature_cols]
        pred = model.predict(feat_row)[0]
        pred = max(pred, 0)
        preds.append(pred)
        history.loc[next_date] = pred

    return np.array(preds)


MODEL_REGISTRY = {
    "naive": naive_forecast,
    "seasonal_naive": seasonal_naive_forecast,
    "moving_average_7": lambda train, h: moving_average_forecast(train, h, window=7),
    "moving_average_28": lambda train, h: moving_average_forecast(train, h, window=28),
    "sarima": sarima_forecast,
    "xgboost": xgboost_forecast,
}


def main():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    sku_id = df["sku_id"].unique()[0]
    series = load_sku_series(df, sku_id)

    horizon = 28
    train = series.iloc[:-horizon]
    test = series.iloc[-horizon:]

    print(f"Forecasting {sku_id} for last {horizon} days (holdout)")
    for name, fn in MODEL_REGISTRY.items():
        preds = fn(train, horizon)
        mae = np.mean(np.abs(preds - test.values))
        print(f"  {name:<20s} MAE={mae:8.2f}")


if __name__ == "__main__":
    main()
