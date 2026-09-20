# Model Comparison Report

Average backtest metrics across all SKUs and folds (horizon=28 days, 3 rolling folds).

| Model | MAE | RMSE | MAPE (%) | WAPE (%) |
|---|---|---|---|---|
| xgboost | 13.53 | 17.62 | 18.99 | 19.11 |
| sarima | 14.38 | 17.98 | 20.24 | 20.42 |
| moving_average_28 | 16.73 | 21.10 | 25.67 | 24.19 |
| moving_average_7 | 17.42 | 21.48 | 27.11 | 25.02 |
| seasonal_naive | 17.67 | 23.34 | 26.53 | 25.46 |
| naive | 20.82 | 25.26 | 30.55 | 28.68 |

Lower WAPE indicates better overall forecast accuracy, weighted by volume.

Full per-SKU results are available in `reports/backtest_results.csv`.
