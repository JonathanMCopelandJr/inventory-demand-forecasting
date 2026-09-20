# Inventory Demand Forecasting — Full Walkthrough

This markdown notebook walks through the full analysis: data generation, EDA,
model training, backtesting, and inventory policy — in the order you'd run
the corresponding scripts in `src/`. Copy blocks into a Jupyter/Colab notebook
to run interactively, or run the .py scripts directly.

## 1. Generate the dataset

```python
from src.generate_data import generate_dataset
df = generate_dataset()
df.to_csv("data/demand_data.csv", index=False)
df.head()
```

The dataset simulates 6 SKUs across 6 categories over 2 years of daily sales,
with trend, weekly seasonality, annual seasonality, holiday spikes, and
promotional lifts baked in.

## 2. Exploratory data analysis

```python
from src.eda import load_data, summary_stats, plot_time_series

df = load_data("data/demand_data.csv")
summary_stats(df)
plot_time_series(df)
```

Key things to look for:
- Weekend vs. weekday demand differences (weekly seasonality)
- November/December spikes (holiday effect)
- Promo days showing a clear lift over baseline demand
- Category-level demand concentration (Beverages and Snacks dominate volume)

## 3. Train and compare forecasting models

```python
from src.forecasting_models import MODEL_REGISTRY, load_sku_series

series = load_sku_series(df, "SKU-1001")
train, test = series.iloc[:-28], series.iloc[-28:]

for name, model_fn in MODEL_REGISTRY.items():
    preds = model_fn(train, 28)
    print(name, preds[:5])
```

Models included:
- Naive and seasonal naive baselines
- 7-day / 28-day moving averages
- SARIMA(1,1,1)(1,1,1,7) — captures weekly seasonality explicitly
- XGBoost regressor with lag features (1, 2, 3, 7, 14, 28 days) and rolling
  means (7, 14, 28 days), plus calendar features (day-of-week, month, day)

## 4. Backtest with rolling-origin cross-validation

```python
from src.evaluate import backtest_sku
from src.forecasting_models import sarima_forecast

result = backtest_sku(series, sarima_forecast)
print(result)
```

The full harness in `evaluate.py` runs this across all SKUs and all models,
using 3 rolling folds of a 28-day holdout each, and reports MAE, RMSE, MAPE,
and WAPE. WAPE is the primary metric since it is robust to low-volume SKUs
where MAPE can be distorted by near-zero actuals.

## 5. Translate forecasts into inventory policy

```python
from src.inventory_policy import compute_policy_for_sku

policy = compute_policy_for_sku(series)
print(policy)
```

This produces a safety-stock and reorder-point recommendation per SKU, using
a 95% service level and a 7-day assumed lead time — the same type of
calculation a buyer/planner would use to set purchasing triggers in an ERP
system.

## Interpreting results

- If SARIMA or XGBoost substantially beats the naive/moving-average
  baselines on WAPE, that's evidence the model is capturing real seasonal
  and trend signal rather than just noise.
- Compare `reports/model_comparison.md` across SKUs: models often perform
  differently on high-volume vs. low-volume SKUs, which mirrors real-world
  planning where a single model rarely wins across an entire portfolio.
- The `reports/inventory_policy.csv` output is the actionable deliverable —
  it converts a forecast into a concrete number a buyer would act on.
