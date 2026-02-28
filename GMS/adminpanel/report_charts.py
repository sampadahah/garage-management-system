import base64
import math
from io import BytesIO

import matplotlib
matplotlib.use("Agg")  # server-safe (no GUI)

import matplotlib.pyplot as plt


def fig_to_base64(fig) -> str:
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _safe_numbers(values):
    """
    Convert values to safe floats.
    - None -> 0
    - NaN/inf -> 0
    - negatives -> 0 (for pie chart safety)
    """
    safe = []
    for v in values:
        if v is None:
            v = 0
        try:
            v = float(v)
        except Exception:
            v = 0
        if (not math.isfinite(v)) or math.isnan(v) or v < 0:
            v = 0
        safe.append(v)
    return safe


def make_pie_chart(labels, values, title: str) -> str:
    values = _safe_numbers(values)

    # If all values are 0, pie chart breaks -> show "No Data"
    if sum(values) <= 0:
        labels = ["No Data"]
        values = [1]

    fig = plt.figure()
    plt.title(title)
    plt.pie(values, labels=labels, autopct="%1.0f%%")
    return fig_to_base64(fig)


def make_bar_chart(labels, values, title: str, xlabel: str = "", ylabel: str = "") -> str:
    values = _safe_numbers(values)

    if not labels:
        labels = ["No Data"]
        values = [0]

    fig = plt.figure()
    plt.title(title)
    plt.bar(labels, values)

    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)

    plt.xticks(rotation=25, ha="right")
    return fig_to_base64(fig)