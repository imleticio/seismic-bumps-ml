#!/usr/bin/env python3
"""Generate a Seaborn-based alternative figure set for Seismic-Bumps.

The script reads the local ARFF file only to validate the class support and
absence of missing values. The confusion-matrix counts are the confirmed
10-fold cross-validation summary supplied with the report; no model is fit
and no additional result is inferred from the dataset.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd
import seaborn as sns


EXPECTED_ROWS = 2_584
EXPECTED_CLASS_COUNTS = {"0": 2_414, "1": 170}

# Confirmed 10-fold CV summary. Rows are true classes and columns are
# predicted classes in this candidate's heatmap convention.
CONFUSION_MATRIX = np.array([[2_394, 20], [165, 5]], dtype=int)

CLASS_LABELS = ["0 — No peligrosa", "1 — Peligrosa"]
OKABE_ITO = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
    "black": "#000000",
}


def parse_args() -> argparse.Namespace:
    """Parse paths while keeping a reproducible repository-local default."""

    candidate_dir = Path(__file__).resolve().parent
    repository_root = candidate_dir.parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=repository_root / "seismic-bumps.arff",
        help="Path to seismic-bumps.arff (default: repository root).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=candidate_dir,
        help="Directory for PDF and PNG outputs (default: this directory).",
    )
    return parser.parse_args()


def read_class_support(dataset_path: Path) -> Counter[str]:
    """Read and validate row count, missing values, and final class field."""

    counts: Counter[str] = Counter()
    row_count = 0
    missing_values = 0
    in_data = False

    with dataset_path.open("r", encoding="utf-8", newline="") as dataset:
        for raw_line in dataset:
            line = raw_line.strip()
            if not line or line.startswith("%"):
                continue
            if line.lower() == "@data":
                in_data = True
                continue
            if not in_data or line.startswith("@"):
                continue

            fields = next(csv.reader([line], skipinitialspace=True), [])
            if not fields:
                continue
            row_count += 1
            missing_values += sum(field.strip() == "?" for field in fields)
            label = fields[-1].strip().strip("'\"")
            if label not in EXPECTED_CLASS_COUNTS:
                raise ValueError(f"Unexpected class label {label!r}")
            counts[label] += 1

    if row_count != EXPECTED_ROWS:
        raise ValueError(f"Expected {EXPECTED_ROWS} rows, found {row_count}")
    if missing_values:
        raise ValueError(f"Expected no missing values, found {missing_values}")
    if dict(counts) != EXPECTED_CLASS_COUNTS:
        raise ValueError(
            "Unexpected class support: "
            f"expected {EXPECTED_CLASS_COUNTS}, found {dict(counts)}"
        )
    return counts


def format_integer(value: int) -> str:
    """Format an integer with the Spanish thousands separator."""

    return f"{value:,}".replace(",", ".")


def format_percent(value: float) -> str:
    """Format a percentage with two decimal places and a decimal comma."""

    return f"{value:.2f}".replace(".", ",") + "%"


def configure_style() -> None:
    """Apply a sober, colorblind-safe style suitable for print and grayscale."""

    sns.set_theme(style="ticks", context="paper", font_scale=1.05)
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "axes.titlesize": 10,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7.5,
            "axes.linewidth": 0.7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": "white",
            "figure.facecolor": "white",
        }
    )


def save_figure(fig: mpl.figure.Figure, output_dir: Path, stem: str) -> None:
    """Save one figure as a vector PDF and a 300 dpi PNG."""

    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output_dir / f"{stem}.pdf",
        format="pdf",
        bbox_inches="tight",
        metadata={"Creator": "generate_seaborn_figures.py"},
    )
    fig.savefig(
        output_dir / f"{stem}.png",
        format="png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


def add_bar_labels(
    ax: mpl.axes.Axes,
    bars: list[mpl.patches.Rectangle],
    labels: list[str],
    *,
    x_offset: float = 0.02,
) -> None:
    """Place exact values just beyond horizontal bars."""

    maximum = max(bar.get_width() for bar in bars)
    for bar, label in zip(bars, labels):
        ax.text(
            bar.get_width() + maximum * x_offset,
            bar.get_y() + bar.get_height() / 2,
            label,
            va="center",
            ha="left",
            fontsize=8,
        )


def make_support_figure(counts: Counter[str], output_dir: Path) -> None:
    """Show support and class imbalance without compressing the minority bar."""

    total = sum(counts.values())
    support = pd.DataFrame(
        {
            "class": CLASS_LABELS,
            "records": [counts["0"], counts["1"]],
            "share": [counts["0"] / total * 100, counts["1"] / total * 100],
        }
    )

    fig, ax = plt.subplots(figsize=(6.25, 2.8))
    palette = [OKABE_ITO["blue"], OKABE_ITO["vermillion"]]
    sns.barplot(
        data=support,
        x="records",
        y="class",
        hue="class",
        order=CLASS_LABELS,
        hue_order=CLASS_LABELS,
        palette=palette,
        legend=False,
        dodge=False,
        ax=ax,
    )
    for patch, hatch in zip(ax.patches, ["", "//"]):
        patch.set_hatch(hatch)
        patch.set_edgecolor(OKABE_ITO["black"])
        patch.set_linewidth(0.35)

    bars = list(ax.patches)
    labels = [
        f"n = {format_integer(row.records)}  ({format_percent(row.share)})"
        for row in support.itertuples()
    ]
    add_bar_labels(ax, bars, labels)
    ax.set_title("A. Soporte y desbalance de clases", loc="left", fontweight="bold")
    ax.set_xlabel("Registros")
    ax.set_ylabel("")
    ax.set_xlim(0, max(support["records"]) * 1.28)
    ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda value, _: format_integer(int(value))))
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.55)
    ax.grid(axis="y", visible=False)
    sns.despine(ax=ax, left=False, bottom=False)
    ratio = counts["0"] / counts["1"]
    fig.text(
        0.5,
        0.01,
        f"Desbalance de soporte: clase 0 : clase 1 = {ratio:.1f}".replace(".", ",") + ":1",
        ha="center",
        va="bottom",
        fontsize=7.5,
        color="#444444",
    )
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save_figure(fig, output_dir, "01_soporte_desbalance")


def make_positive_error_figure(output_dir: Path) -> None:
    """Contrast omissions and false alarms among cases involving class 1."""

    tn, fp = CONFUSION_MATRIX[0]
    fn, tp = CONFUSION_MATRIX[1]
    groups = ["Clase verdadera 1\n(n = 170)", "Clase predicha 1\n(n = 25)"]
    segments = [
        ("TP · acierto", [0, tp], OKABE_ITO["green"], ""),
        ("FN · omisión", [fn, 0], OKABE_ITO["vermillion"], "//"),
        ("FP · falsa alarma", [0, fp], OKABE_ITO["orange"], "\\\\"),
    ]

    fig, ax = plt.subplots(figsize=(6.25, 3.55))
    bottoms = np.zeros(2, dtype=float)
    handles: list[Patch] = []
    for label, values, color, hatch in segments:
        values_array = np.asarray(values, dtype=float)
        bars = ax.bar(
            groups,
            values_array,
            bottom=bottoms,
            color=color,
            edgecolor=OKABE_ITO["black"],
            linewidth=0.35,
            hatch=hatch,
            width=0.58,
            label=label,
        )
        for group_index, (bar, value, bottom) in enumerate(zip(bars, values_array, bottoms)):
            if value <= 0:
                continue
            group_total = 170 if bar.get_x() < 0 else 25
            share = value / group_total * 100
            if value <= 8:
                # Small TP segments cannot contain a two-line annotation at
                # print size. Keep the exact count and percentage on one line.
                label_text = f"{format_integer(int(value))} ({format_percent(share)})"
                if label == "TP · acierto" and group_index == 1:
                    # Lift the tiny TP annotation above the segment so its
                    # baseline remains separated from the x-axis after LaTeX scaling.
                    label_y = bottom + value + 2.5
                    label_va = "bottom"
                    label_color = OKABE_ITO["black"]
                else:
                    label_y = bottom + value / 2
                    label_va = "center"
                    label_color = "white" if color == OKABE_ITO["green"] else OKABE_ITO["black"]
                label_size = 6.5
            elif group_index == 1:
                # The 20-record FP segment is clearer as an external label
                # than as text compressed into the short predicted-positive bar.
                label_text = f"{format_integer(int(value))} ({format_percent(share)})"
                label_y = bottom + value + 5
                label_va = "center"
                label_color = OKABE_ITO["black"]
                label_size = 7.2
            else:
                label_text = f"{format_integer(int(value))}\n{format_percent(share)}"
                label_y = bottom + value / 2
                label_va = "center"
                label_color = "white" if color == OKABE_ITO["vermillion"] else OKABE_ITO["black"]
                label_size = 7.7
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                label_y,
                label_text,
                ha="center",
                va=label_va,
                fontsize=label_size,
                fontweight="bold" if value <= 20 else "normal",
                color=label_color,
            )
        bottoms += values_array
        handles.append(Patch(facecolor=color, edgecolor=OKABE_ITO["black"], hatch=hatch, label=label))

    ax.set_title("B. Errores que involucran la clase positiva", loc="left", fontweight="bold")
    ax.set_ylabel("Registros")
    ax.set_xlabel("")
    ax.set_ylim(0, 185)
    ax.set_yticks([0, 50, 100, 150])
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda value, _: format_integer(int(value))))
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.55)
    ax.grid(axis="x", visible=False)
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.19), ncol=3, frameon=False)
    sns.despine(ax=ax)
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    save_figure(fig, output_dir, "02_errores_clase_positiva")


def make_confusion_heatmap(output_dir: Path) -> None:
    """Create raw-count and true-class-normalized annotated heatmaps."""

    row_totals = CONFUSION_MATRIX.sum(axis=1, keepdims=True)
    normalized = CONFUSION_MATRIX / row_totals * 100
    count_labels = np.vectorize(format_integer)(CONFUSION_MATRIX)
    annotations = np.empty(CONFUSION_MATRIX.shape, dtype=object)
    for row in range(CONFUSION_MATRIX.shape[0]):
        for column in range(CONFUSION_MATRIX.shape[1]):
            annotations[row, column] = (
                f"n = {count_labels[row, column]}\n"
                f"{format_percent(normalized[row, column])} de la fila"
            )

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.55), constrained_layout=True)
    heatmap_kwargs = {
        "xticklabels": CLASS_LABELS,
        "yticklabels": CLASS_LABELS,
        "linewidths": 1.2,
        "linecolor": "white",
        "cbar_kws": {"label": "Registros"},
        "square": True,
    }
    sns.heatmap(
        pd.DataFrame(CONFUSION_MATRIX, index=CLASS_LABELS, columns=CLASS_LABELS),
        annot=count_labels,
        fmt="",
        cmap="cividis",
        vmin=0,
        vmax=CONFUSION_MATRIX.max(),
        ax=axes[0],
        **heatmap_kwargs,
    )
    sns.heatmap(
        pd.DataFrame(normalized, index=CLASS_LABELS, columns=CLASS_LABELS),
        annot=annotations,
        fmt="",
        cmap="cividis",
        vmin=0,
        vmax=100,
        ax=axes[1],
        cbar_kws={"label": "% por clase verdadera"},
        xticklabels=CLASS_LABELS,
        yticklabels=False,
        linewidths=1.2,
        linecolor="white",
        square=True,
    )
    axes[0].set_title("C1. Conteos", loc="left", fontweight="bold")
    axes[1].set_title("C2. Normalización por fila", loc="left", fontweight="bold")
    for ax in axes:
        ax.set_xlabel("Clase predicha")
        ax.tick_params(axis="x", rotation=35)
        ax.tick_params(axis="y", rotation=0)
    axes[0].set_ylabel("Clase verdadera")
    axes[1].set_ylabel("")
    fig.suptitle("Matriz de confusión del árbol de decisión", y=1.03, fontsize=10.5, fontweight="bold")
    save_figure(fig, output_dir, "03_heatmap_confusion_anotado")


def main() -> None:
    args = parse_args()
    counts = read_class_support(args.dataset)
    if not np.array_equal(CONFUSION_MATRIX.sum(), EXPECTED_ROWS):
        raise ValueError("The supplied confusion matrix does not sum to the dataset size")

    configure_style()
    make_support_figure(counts, args.output_dir)
    make_positive_error_figure(args.output_dir)
    make_confusion_heatmap(args.output_dir)
    print(f"Validated {sum(counts.values())} rows from {args.dataset}")
    print(f"Wrote six figures to {args.output_dir}")


if __name__ == "__main__":
    main()
