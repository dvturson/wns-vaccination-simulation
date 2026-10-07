"""Summarise the vaccination-timing sweep exported from the NetLogo model.

Reads the twelve NetLogo plot exports in data/timing_sweep/ (one 10-year run
per vaccination month, 40% coverage), then writes:

    results/timing_sweep_summary.csv    one row of summary metrics per run
    figures/timing_sweep_trajectories.png
    figures/timing_sweep_summary.png

Usage:
    python analysis/analyze_timing_sweep.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "timing_sweep"
FIG_DIR = ROOT / "figures"
RESULTS_DIR = ROOT / "results"

# The model's year runs August -> July, one month = 30 ticks (days).
MONTHS = ["August", "September", "October", "November", "December", "January",
          "February", "March", "April", "May", "June", "July"]
SEASON = {
    **dict.fromkeys(["August", "September"], "Swarming"),
    **dict.fromkeys(["October", "November", "December", "January",
                     "February", "March", "April"], "Hibernation"),
    **dict.fromkeys(["May", "June", "July"], "Roosting"),
}
SEASON_COLOR = {"Swarming": "#eb6834", "Hibernation": "#2a78d6", "Roosting": "#1baf7a"}

DAYS_PER_YEAR = 360          # 12 model months of 30 ticks
LATE_WINDOW_START = 1800     # summary window: model years 6-10

INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e6e5e1"
SURFACE = "#fcfcfb"


def read_netlogo_plot_export(path):
    """Parse a NetLogo `export-plot` CSV into (settings, DataFrame[day, population])."""
    lines = path.read_text().splitlines()

    settings_at = lines.index('"MODEL SETTINGS"')
    names = [s.strip('"') for s in lines[settings_at + 1].split(",")]
    values = [s.strip('"') for s in lines[settings_at + 2].split(",")]
    settings = dict(zip(names, values))

    data_at = next(i for i, line in enumerate(lines) if line.startswith('"x","y"'))
    df = pd.read_csv(path, skiprows=data_at, usecols=["x", "y"])
    df = df.rename(columns={"x": "day", "y": "population"})
    return settings, df


def load_runs():
    runs = {}
    for path in sorted(DATA_DIR.glob("*.csv")):
        settings, df = read_netlogo_plot_export(path)
        runs[settings["vaccination_month"]] = (settings, df)
    missing = [m for m in MONTHS if m not in runs]
    if missing:
        raise SystemExit(f"No export found in {DATA_DIR} for: {', '.join(missing)}")
    return runs


def summarise(runs):
    rows = []
    for month in MONTHS:
        settings, df = runs[month]
        pop = df.set_index("day")["population"]
        initial = int(settings["number-of-drawers"])
        late = pop[pop.index > LATE_WINDOW_START]
        rows.append({
            "vaccination_month": month,
            "season": SEASON[month],
            "coverage": float(settings["vaccination-rate"]),
            "initial_population": initial,
            "peak_population": int(pop.max()),
            "min_population": int(pop.min()),
            "population_year_1": int(pop.loc[DAYS_PER_YEAR]),
            "population_year_5": int(pop.loc[5 * DAYS_PER_YEAR]),
            "final_population": int(pop.iloc[-1]),
            "mean_population_years_6_10": round(late.mean(), 1),
            "pct_of_initial_years_6_10": round(100 * late.mean() / initial, 1),
            "went_extinct": bool(pop.min() == 0),
        })
    return pd.DataFrame(rows)


def style_axes(ax):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK_MUTED, labelsize=8, length=0)


def season_legend(fig, **kwargs):
    handles = [Patch(color=c, label=s) for s, c in SEASON_COLOR.items()]
    legend = fig.legend(handles=handles, title="Season of vaccination", frameon=False,
                        ncol=3, fontsize=9, title_fontsize=9, **kwargs)
    legend.get_title().set_color(INK_SECONDARY)
    for text in legend.get_texts():
        text.set_color(INK_SECONDARY)


def plot_trajectories(runs, summary):
    fig, axes = plt.subplots(3, 4, figsize=(12, 7.5), sharex=True, sharey=True,
                             facecolor=SURFACE)
    initial = summary["initial_population"].iloc[0]
    y_max = summary["peak_population"].max() * 1.05

    for ax, month in zip(axes.flat, MONTHS):
        _, df = runs[month]
        style_axes(ax)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.axhline(initial, color=INK_MUTED, linewidth=0.8, linestyle=(0, (2, 3)))
        ax.plot(df["day"] / DAYS_PER_YEAR, df["population"],
                color=SEASON_COLOR[SEASON[month]], linewidth=1.6)
        ax.set_title(month, loc="left", fontsize=10, color=INK, pad=4)
        ax.set_xlim(0, 10.15)
        ax.set_xticks(range(0, 11, 2))
        ax.set_ylim(0, y_max)

    axes[0, 0].annotate("starting population", (10, initial), xytext=(0, 3),
                        textcoords="offset points", ha="right", fontsize=7.5,
                        color=INK_MUTED)
    fig.supxlabel("Years since start of simulation", fontsize=9, color=INK_SECONDARY)
    fig.supylabel("Bats alive", fontsize=9, color=INK_SECONDARY)
    fig.suptitle("Bat population over 10 years, by month of annual vaccination",
                 x=0.02, ha="left", fontsize=13, color=INK)
    fig.text(0.02, 0.925, "One simulation run per month · 40% of eligible bats "
             "vaccinated each year · 82 bats at start",
             fontsize=9, color=INK_SECONDARY)
    season_legend(fig, loc="upper right", bbox_to_anchor=(0.99, 1.0))
    fig.tight_layout(rect=(0.01, 0, 1, 0.94))
    fig.savefig(FIG_DIR / "timing_sweep_trajectories.png", dpi=200)
    plt.close(fig)


def plot_summary(summary):
    fig, ax = plt.subplots(figsize=(9, 4.8), facecolor=SURFACE)
    style_axes(ax)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)

    values = summary["mean_population_years_6_10"]
    colors = summary["season"].map(SEASON_COLOR)
    bars = ax.bar(summary["vaccination_month"].str[:3], values, color=colors, width=0.62)
    ax.bar_label(bars, labels=[f"{v:.0f}" for v in values], padding=3,
                 fontsize=9, color=INK)

    ax.tick_params(axis="x", labelsize=9, colors=INK_SECONDARY)
    ax.set_ylabel("Mean bats alive, years 6–10", fontsize=9, color=INK_SECONDARY)
    ax.set_xlabel("Month of annual vaccination", fontsize=9, color=INK_SECONDARY)
    ax.set_ylim(0, values.max() * 1.15)
    fig.suptitle("Long-run bat population by month of annual vaccination",
                 x=0.02, ha="left", fontsize=13, color=INK)
    fig.text(0.02, 0.885, "One simulation run per month · 40% coverage · "
             "82 bats at start", fontsize=9, color=INK_SECONDARY)
    season_legend(fig, loc="upper right", bbox_to_anchor=(0.99, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(FIG_DIR / "timing_sweep_summary.png", dpi=200)
    plt.close(fig)


def main():
    FIG_DIR.mkdir(exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)

    runs = load_runs()
    summary = summarise(runs)
    summary.to_csv(RESULTS_DIR / "timing_sweep_summary.csv", index=False)
    plot_trajectories(runs, summary)
    plot_summary(summary)

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
