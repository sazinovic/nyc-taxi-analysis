"""Consistent monthly figures with explicit units and metric definitions."""
from pathlib import Path
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd


def plot_monthly(df: pd.DataFrame, column: str, title: str, ylabel: str,
                 output: Path | None = None, highlights: tuple[str, ...] = ("first", "latest")):
    data = df.sort_values(["year", "month"]).copy()
    data["period"] = pd.to_datetime(dict(year=data.year, month=data.month, day=1))
    fig, ax = plt.subplots(figsize=(14, 7), layout="constrained")
    ax.plot(data.period, data[column], linewidth=2)
    ax.set_title(title, loc="left", fontsize=17, pad=34)
    ax.text(0, 1.02, f"Monthly observations, {data.period.min():%b %Y} – {data.period.max():%b %Y}", transform=ax.transAxes)
    ax.set_ylabel(ylabel)
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(axis="y", alpha=.2)
    ax.spines[["top", "right"]].set_visible(False)
    if column == "trip_count":
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x / 1e6:.0f}M"))
    elif column.endswith("share"):
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0f}%"))
    elif "amount" in column:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x:,.0f}"))
    positions = {"first": data.index[0], "latest": data.index[-1],
                 "peak": data[column].idxmax(), "low": data[column].idxmin()}
    for key in highlights:
        row = data.loc[positions[key]]
        value = row[column]
        label = f"{value / 1e6:.2f}M" if column == "trip_count" else (f"{value:.2f}%" if column.endswith("share") else f"${value:.2f}")
        ax.scatter(row.period, value, zorder=3)
        offset = (-100, 25) if key == "latest" else (25, 25 if key != "peak" else -40)
        ax.annotate(f"{key.title()} — {row.period:%b %Y}\n{label}", (row.period, value),
                    xytext=offset, textcoords="offset points", arrowprops={"arrowstyle": "->"})
    ax.margins(x=.04, y=.18)
    if column == "trip_count" or column.endswith("share"):
        ax.set_ylim(bottom=0)
    ax.set_xlabel("Source: NYC TLC • task-specific filters; see README for denominators", loc="left", fontsize=9)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, dpi=200, bbox_inches="tight")
    return fig, ax
