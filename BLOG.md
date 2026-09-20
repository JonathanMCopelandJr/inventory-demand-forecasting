# Forecasting Retail Demand: What XGBoost Taught Me About Inventory Planning

*A deep dive into benchmarking six forecasting models across a simulated multi-SKU retail dataset - and why the "best" model depends entirely on how you define best.*

## The Problem

Every buyer or planner faces the same core question: how much should we order, and when? Get it wrong in one direction and you're sitting on dead stock; get it wrong in the other and you're apologizing to customers for empty shelves. The answer to that question starts with a demand forecast, but not all forecasts are created equal.

This project set out to answer a more specific question: for realistic retail demand data - with trend, weekly patterns, seasonal swings, holiday spikes, and promotional lifts all layered together - which forecasting approach actually performs best, and by how much?

## Building a Realistic Testbed

Rather than using a black-box public dataset, I generated a synthetic but carefully engineered dataset: two years of daily sales across six SKUs spanning six categories (Beverages, Snacks, Dairy, Frozen Foods, Household, and Personal Care). Each SKU's demand was built from several overlapping signals:

- A gradual upward trend
- Weekly seasonality, with demand rising toward weekends
- Annual seasonality, phase-shifted so each category peaks at a different time of year
- Holiday spikes around Thanksgiving, Christmas, New Year's, and July 4th
- Random promotional lifts of 30-80% on roughly 8% of days
- Gaussian noise, because real demand is never perfectly clean

The goal was a dataset that behaves like a real point-of-sale extract, so that any model that performs well here would plausibly perform well on the real thing.

## Six Models, One Fair Test

I benchmarked six forecasting approaches, ordered from simplest to most sophisticated:

1. Naive - tomorrow's demand equals today's
2. Seasonal naive - tomorrow's demand equals the same weekday last week
3. Moving average (7-day and 28-day) - a simple rolling mean
4. SARIMA - a seasonal ARIMA model tuned to the weekly cycle
5. XGBoost - a gradient-boosted tree model trained on lag features (1, 2, 3, 7, 14, and 28 days back), rolling means, and calendar features (day of week, month, day)

To keep the comparison honest, every model was evaluated with rolling-origin backtesting: three separate 28-day holdout windows per SKU, where each model only ever sees data that would have actually been available at that point in time. No peeking into the future - the same discipline you'd want from any forecast you'd actually act on.

## The Results

Averaged across all six SKUs and all three backtest folds:

| Model | MAE | RMSE | MAPE (%) | WAPE (%) |
|---|---|---|---|---|
| XGBoost | 13.53 | 17.62 | 18.99 | 19.11 |
| SARIMA | 14.38 | 17.98 | 20.24 | 20.42 |
| Moving Average (28-day) | 16.73 | 21.10 | 25.67 | 24.19 |
| Moving Average (7-day) | 17.42 | 21.48 | 27.11 | 25.02 |
| Seasonal Naive | 17.67 | 23.34 | 26.53 | 25.46 |
| Naive | 20.82 | 25.26 | 30.55 | 28.68 |

XGBoost won on every metric. It cut WAPE roughly a third relative to the naive baseline (19.1% vs. 28.7%), and edged out SARIMA by about 1.3 percentage points.

## Why XGBoost Won

The gap between XGBoost and SARIMA isn't huge, and that's informative in itself - SARIMA's explicit seasonal structure captures most of the signal in this data. But XGBoost's edge comes from flexibility: its lag and rolling-mean features let it react to the sharp, somewhat irregular demand spikes created by random promotions, something a smoother seasonal model isn't built to anticipate as sharply.

The bigger takeaway is the size of the gap between the two "real" models (XGBoost, SARIMA) and the baselines. Both clear the naive benchmark by a wide margin, which is the real validation here - it confirms they're learning genuine trend and seasonal structure, not just averaging noise. A model that can't beat "assume tomorrow looks like last week" by a meaningful margin isn't worth deploying.

## From Forecast to Decision

A forecast alone doesn't move inventory - it needs to become a policy. I converted the SARIMA forecasts into safety stock and reorder point recommendations using a standard service-level approach:

```
Safety Stock = z x sigma(demand) x sqrt(lead time)
Reorder Point = (avg daily demand x lead time) + Safety Stock
```

Using a 95% service level (z is approximately 1.645) and a 7-day assumed supplier lead time, each SKU gets a concrete reorder point in units - the number a buyer would actually punch into a purchasing system. This is the step that's easy to skip in a forecasting project but is really the entire point: uncertainty quantification only matters once it's translated into an action.

## What I'd Do Differently at Scale

This dataset has six SKUs; a real retail or CPG portfolio might have thousands. A few things I'd change moving from this prototype to production:

- Model selection per SKU, not globally. A single model rarely wins across an entire portfolio - low-volume, intermittent-demand SKUs often favor simpler models, while high-volume SKUs with more signal reward the complexity of XGBoost or SARIMA.
- Hierarchical reconciliation. Category-level and total-level forecasts should be consistent with SKU-level ones, not independently estimated.
- Automated retraining. In this project, that's handled by a GitHub Actions pipeline that regenerates data and reruns the full model comparison whenever the source code changes - a small taste of the CI/CD discipline that real forecasting systems need at scale.

## Try It Yourself

The full project - data generator, EDA scripts, all six models, the backtesting harness, and the inventory policy calculator - is open source:

[github.com/JonathanMCopelandJr/inventory-demand-forecasting](https://github.com/JonathanMCopelandJr/inventory-demand-forecasting)

Clone it, run `python src/generate_data.py`, and you'll have the exact same dataset and results in under a minute.

---

*Jonathan M. Copeland Jr. is a Buyer Planner and Data Analytics graduate student focused on SQL, Python, forecasting, and supply chain analytics. Find more at [jonathanmcopelandjr.com](https://jonathanmcopelandjr.com/).*
