<h1 align="center">📦 Inventory Demand Forecasting</h1>

<p align="center">
  <em>End-to-end demand forecasting and inventory policy pipeline — from synthetic data generation to backtested models and reorder-point recommendations.</em>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="Forecasting" src="https://img.shields.io/badge/Forecasting-Time%20Series-orange">
  <img alt="CI" src="https://img.shields.io/github/actions/workflow/status/JonathanMCopelandJr/inventory-demand-forecasting/run-pipeline.yml?label=pipeline&logo=githubactions&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-lightgrey">
  <img alt="Status" src="https://img.shields.io/badge/Status-Active-brightgreen">
</p>

---

## 📌 Overview

This project builds a **reproducible demand-forecasting and inventory-planning pipeline**, the kind of
system a supply-chain or planning team uses to decide *how much stock to hold and when to reorder*. It
starts from synthetic demand data, walks through exploratory analysis, fits and backtests multiple
forecasting models, and translates the winning forecast into a concrete **inventory policy** (safety stock,
reorder point, reorder quantity).

Unlike a one-off notebook, the pipeline is automated end-to-end with **GitHub Actions**, so data generation
and model runs can be triggered and reproduced on demand rather than by hand.

| Stage | Component | Purpose |
|---|---|---|
| **Generate** | `src/generate_data.py` | Create synthetic demand history |
| **Explore** | `src/eda.py`, `notebooks/01_eda_and_modeling.md` | Understand trend, seasonality, and variability |
| **Model** | `src/forecasting_models.py` | Fit and compare forecasting models |
| **Evaluate** | `src/evaluate.py`, `reports/backtest_results.csv`, `reports/model_comparison.md` | Backtest accuracy across models |
| **Plan** | `src/inventory_policy.py`, `reports/inventory_policy.csv` | Convert forecasts into reorder policy |
| **Automate** | `.github/workflows/` | CI pipelines for data generation and full pipeline runs |

---

## 🗂️ Repository Structure

```
inventory-demand-forecasting/
├── .github/
│   └── workflows/
│       ├── generate-data.yml       # CI job: regenerate synthetic demand data
│       └── run-pipeline.yml        # CI job: run full forecasting pipeline
├── data/
│   └── demand_data.csv             # Synthetic demand history
├── notebooks/
│   └── 01_eda_and_modeling.md      # Exploratory analysis & modeling walkthrough
├── reports/
│   ├── backtest_results.csv        # Backtested forecast accuracy by model
│   ├── inventory_policy.csv        # Recommended safety stock / reorder point / reorder qty
│   └── model_comparison.md         # Model comparison write-up
├── src/
│   ├── generate_data.py            # Synthetic data generator
│   ├── eda.py                      # Exploratory data analysis
│   ├── forecasting_models.py       # Forecasting model definitions
│   ├── evaluate.py                 # Backtesting & accuracy evaluation
│   └── inventory_policy.py         # Safety stock / reorder point logic
├── BLOG.md                         # Narrative write-up of the project
├── LICENSE
├── requirements.txt
└── README.md
```

---

## 🔑 Key Questions Answered

- Which forecasting approach best captures the **trend and seasonality** in demand?
- How accurate is each model when backtested against held-out history?
- Given forecast uncertainty, what **safety stock and reorder point** should a planner set?
- Can the entire pipeline — from raw data to inventory policy — run automatically and reproducibly?

---

## ⚙️ How It Works

1. **Generate data** (`src/generate_data.py`) — Produce a synthetic but realistic demand series with trend,
   seasonality, and noise.
2. **Explore** (`src/eda.py`, `notebooks/01_eda_and_modeling.md`) — Visualize demand patterns and diagnose
   seasonality/variability before modeling.
3. **Model & evaluate** (`src/forecasting_models.py`, `src/evaluate.py`) — Fit multiple forecasting models
   and backtest them, logging results to `reports/backtest_results.csv` and summarizing findings in
   `reports/model_comparison.md`.
4. **Set inventory policy** (`src/inventory_policy.py`) — Use forecast error to size **safety stock**,
   **reorder point**, and **reorder quantity**, saved to `reports/inventory_policy.csv`.
5. **Automate** (`.github/workflows/`) — `generate-data.yml` and `run-pipeline.yml` let the whole process
   re-run in CI, so results stay reproducible without manual steps.

---

## 🚀 Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/JonathanMCopelandJr/inventory-demand-forecasting.git
cd inventory-demand-forecasting

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate synthetic demand data
python src/generate_data.py

# 4. Run exploratory analysis
python src/eda.py

# 5. Fit models and backtest
python src/forecasting_models.py
python src/evaluate.py

# 6. Compute the inventory policy
python src/inventory_policy.py
```

The same steps run automatically via GitHub Actions — see `.github/workflows/run-pipeline.yml`.

---

## 📊 Outputs

| File | Description |
|---|---|
| `reports/backtest_results.csv` | Forecast accuracy metrics per model, per backtest window |
| `reports/model_comparison.md` | Narrative comparison of model performance and selection rationale |
| `reports/inventory_policy.csv` | Recommended safety stock, reorder point, and reorder quantity |

For the full narrative walkthrough — motivation, modeling choices, and takeaways — see [`BLOG.md`](BLOG.md).

---

## 🧠 Skills Demonstrated

- Time-series demand forecasting and model comparison
- Backtesting methodology for forecast accuracy
- Inventory policy design (safety stock, reorder point, reorder quantity)
- Pipeline automation with GitHub Actions (CI/CD for data science)
- Reproducible, script-based analytics (vs. one-off notebooks)

---

## 👤 Author

**Jonathan M. Copeland Jr.**
Buyer Planner · M.S. Data Analytics · SQL · Python · Excel · Forecasting · Supply Chain Analytics

[Portfolio](https://jonathanmcopelandjr.com/) · [GitHub](https://github.com/JonathanMCopelandJr)

---

<p align="center"><sub>Built as part of a hands-on supply-chain analytics portfolio project.</sub></p>
