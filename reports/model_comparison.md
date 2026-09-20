# Model Comparison Report

This report is generated automatically by `src/evaluate.py`.

Run the full pipeline to populate this file with real backtest results:

```bash
python src/generate_data.py
python src/forecasting_models.py
python src/evaluate.py
```

Expected columns once generated: Model, MAE, RMSE, MAPE (%), WAPE (%),
averaged across all SKUs over 3 rolling 28-day backtest folds.
