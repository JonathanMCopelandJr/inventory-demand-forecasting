# Inventory Demand Forecasting

A comprehensive, end-to-end demand forecasting project for retail inventory planning. Built to demonstrate a realistic supply-chain analytics workflow: from synthetic multi-SKU sales data generation, through exploratory data analysis, to classical statistical and machine-learning forecasting models, backtesting, and business-facing evaluation.

## Project Motivation

Retail and CPG buyers/planners need reliable SKU-level demand forecasts to set reorder points, safety stock, and purchase quantities. This project simulates that workflow using a synthetic but realistic dataset (trend, weekly seasonality, annual seasonality, holiday spikes, and promotions) and benchmarks several forecasting approaches side by side.

## Repository Structure

```
inventory-demand-forecasting/
├── data/
│   └── demand_data.csv          # Synthetic daily SKU-level sales data (2 years, 6 SKUs)
├── src/
│   ├── generate_data.py         # Synthetic data generator (trend/seasonality/promos/holidays)
│   ├── eda.py                   # Exploratory data analysis + chart generation
│   ├── forecasting_models.py    # Naive, Moving Average, SARIMA, and XGBoost models
│   ├── evaluate.py              # Backtesting harness + MAE/RMSE/MAPE/WAPE metrics
│   └── inventory_policy.py      # Safety stock & reorder point calculations from forecasts
├── notebooks/
│   └── 01_eda_and_modeling.md   # Walkthrough notebook (markdown/code cells) of the full analysis
├── reports/
│   └── model_comparison.md      # Model benchmark results template
├── requirements.txt
├── .gitignore
└── README.md
```

## Dataset

`data/demand_data.csv` contains 4,380 rows: daily unit sales for 6 SKUs across 6 categories (Beverages, Snacks, Dairy, Frozen Foods, Household, Personal Care) from 2024-01-01 through 2025-12-30.

| Column | Description |
|---|---|
| `date` | Calendar date (daily granularity) |
| `sku_id` | Unique SKU identifier |
| `category` | Product category |
| `unit_price` | Unit price in USD |
| `promo_flag` | 1 if a promotion was active that day, else 0 |
| `units_sold` | Target variable — daily units sold |

The data embeds an upward trend, day-of-week seasonality, annual seasonality (with a phase shift so each category peaks at a different time of year), holiday demand spikes (Thanksgiving/Christmas/New Year/July 4th), random promotional lifts, and Gaussian noise — designed to resemble real POS extracts.

## Methodology

1. **Data generation** (`generate_data.py`): builds the synthetic panel dataset described above so the project is fully reproducible without needing a private data source.
2. **EDA** (`eda.py`): computes summary statistics, decomposes trend/seasonality, and visualizes demand by SKU, category, weekday, and promotion status.
3. **Forecasting models** (`forecasting_models.py`):
   - **Naive / seasonal naive** baseline (last value, last-week-same-day)
   - **Moving average** baselines (7-day, 28-day rolling windows)
   - **SARIMA** (statsmodels) capturing weekly seasonality
   - **XGBoost regressor** using lag, rolling-window, and calendar features
4. **Evaluation** (`evaluate.py`): walk-forward backtesting (rolling-origin cross-validation) with MAE, RMSE, MAPE, and WAPE, reported per SKU and in aggregate.
5. **Inventory policy** (`inventory_policy.py`): converts forecasts and forecast error into safety stock and reorder-point recommendations using a service-level (z-score) approach.

## Key Metrics

Forecast accuracy is evaluated with:

- **MAE** (Mean Absolute Error) — average magnitude of forecast error in units
- **RMSE** (Root Mean Squared Error) — penalizes large misses more heavily
- **MAPE** (Mean Absolute Percentage Error) — scale-independent accuracy
- **WAPE** (Weighted Absolute Percentage Error) — more robust than MAPE for intermittent/low-volume SKUs

Results for each model, per SKU, are written to `reports/model_comparison.md`.

## Getting Started

```bash
git clone https://github.com/JonathanMCopelandJr/inventory-demand-forecasting.git
cd inventory-demand-forecasting
pip install -r requirements.txt

python src/generate_data.py        # regenerate data/demand_data.csv
python src/eda.py                  # run EDA, save charts to reports/figures/
python src/forecasting_models.py   # train and forecast with all models
python src/evaluate.py             # backtest and produce reports/model_comparison.md
python src/inventory_policy.py     # compute safety stock / reorder points
```

## Tech Stack

- **Python**: pandas, NumPy for data wrangling
- **Statsmodels**: SARIMA time-series modeling
- **XGBoost**: gradient-boosted tree regression with engineered lag/calendar features
- **scikit-learn**: preprocessing and evaluation metrics
- **Matplotlib**: exploratory and diagnostic visualizations

## Business Application

This mirrors a real buyer/planner workflow: generate SKU-level forecasts, quantify forecast uncertainty, then translate that uncertainty into safety stock and reorder points so purchasing decisions are grounded in both expected demand and its variability, rather than a single point estimate.

## Author

**Jonathan M. Copeland Jr.** — Buyer Planner | Data Analytics M.S. | SQL, Python, Excel, Forecasting, Supply Chain Analytics
[Portfolio site](https://jonathanmcopelandjr.com/)

## License

MIT License — free to use, modify, and build upon with attribution.
