"""
eda.py

Exploratory data analysis for the inventory demand dataset. Produces summary
statistics and diagnostic charts (trend/seasonality, weekday effects, promo
lift, per-category demand) saved to reports/figures/.

Run:
    python src/eda.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

DATA_PATH = os.path.join("data", "demand_data.csv")
FIG_DIR = os.path.join("reports", "figures")


def load_data(path=DATA_PATH):
    df = pd.read_csv(path, parse_dates=["date"])
    df["day_of_week"] = df["date"].dt.day_name()
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year
    return df


def summary_stats(df):
    print("=== Overall summary ===")
    print(df["units_sold"].describe())
    print()
    print("=== Per-SKU summary ===")
    print(df.groupby("sku_id")["units_sold"].agg(["mean", "std", "min", "max", "sum"]))
    print()
    print("=== Promo lift (mean units_sold, promo vs. no promo) ===")
    print(df.groupby(["sku_id", "promo_flag"])["units_sold"].mean().unstack())


def plot_time_series(df):
    os.makedirs(FIG_DIR, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 6))
    for sku_id, sub in df.groupby("sku_id"):
        daily = sub.groupby("date")["units_sold"].sum()
        ax.plot(daily.index, daily.values, label=sku_id, linewidth=1)
    ax.set_title("Daily Units Sold by SKU")
    ax.set_xlabel("Date")
    ax.set_ylabel("Units Sold")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "daily_demand_by_sku.png"), dpi=150)
    plt.close(fig)


def plot_weekday_seasonality(df):
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_avg = df.groupby("day_of_week")["units_sold"].mean().reindex(order)
    fig, ax = plt.subplots(figsize=(8, 5))
    weekday_avg.plot(kind="bar", ax=ax, color="steelblue")
    ax.set_title("Average Units Sold by Day of Week")
    ax.set_ylabel("Avg Units Sold")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "weekday_seasonality.png"), dpi=150)
    plt.close(fig)


def plot_monthly_seasonality(df):
    monthly_avg = df.groupby("month")["units_sold"].mean()
    fig, ax = plt.subplots(figsize=(8, 5))
    monthly_avg.plot(kind="bar", ax=ax, color="darkorange")
    ax.set_title("Average Units Sold by Month (Annual Seasonality)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Avg Units Sold")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "monthly_seasonality.png"), dpi=150)
    plt.close(fig)


def plot_category_totals(df):
    cat_totals = df.groupby("category")["units_sold"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    cat_totals.plot(kind="barh", ax=ax, color="seagreen")
    ax.set_title("Total Units Sold by Category (2-Year Total)")
    ax.set_xlabel("Total Units Sold")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "category_totals.png"), dpi=150)
    plt.close(fig)


def main():
    df = load_data()
    summary_stats(df)
    plot_time_series(df)
    plot_weekday_seasonality(df)
    plot_monthly_seasonality(df)
    plot_category_totals(df)
    print(f"\nSaved charts to {FIG_DIR}/")


if __name__ == "__main__":
    main()
