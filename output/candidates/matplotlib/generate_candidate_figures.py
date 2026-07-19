#!/usr/bin/env python3
"""Generate an independent Matplotlib figure proposal for Seismic-Bumps.

The script validates the dataset before plotting and writes publication-oriented
PDF (vector) and 300 dpi PNG pairs into the selected output directory. It uses
only the confirmed class counts and supplied decision-tree evaluation values;
no model is retrained and no additional result is inferred for reporting.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter, MultipleLocator


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATASET = ROOT / "seismic-bumps.arff"
DEFAULT_OUTPUT = Path(__file__).resolve().parent
EXPECTED_RECORDS = 2_584
EXPECTED_CLASS_COUNTS = {"0": 2_414, "1": 170}
EXPECTED_FIELDS = 19

# Supplied 10-fold decision-tree aggregate, using rows = predicted class and
# columns = true class, matching the convention of the canonical figure.
CONFUSION = ((2_394, 165), (20, 5))

# Okabe-Ito-inspired, muted editorial palette. Markers and hatching also carry
# distinction so the figures remain interpretable in grayscale.
INK = "#20262D"
MUTED = "#66717A"
GRID = "#D7DDE0"
PANEL = "#F3F5F6"
BLUE = "#2F5D73"
RUST = "#A45B3A"
OLIVE = "#66755B"
PLUM = "#7D6474"
WHITE = "#FFFFFF"


@dataclass(frozen=True)
class Metric:
    label: str
    value: float
    error: float | None
    annotation: str
    marker: str
    color: str


def spanish_number(value: float, decimals: int = 2) -> str:
    """Format a number with Spanish thousands and decimal separators."""

    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def spanish_percent(value: float, decimals: int = 2) -> str:
    return f"{spanish_number(value, decimals)}%"


def parse_arff(path: Path) -> Counter[str]:
    """Validate the ARFF rows and return the observed class counts."""

    counts: Counter[str] = Counter()
    in_data = False
    records = 0

    with path.open("r", encoding="utf-8", newline="") as dataset:
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
            if len(fields) != EXPECTED_FIELDS:
                raise ValueError(
                    f"Expected {EXPECTED_FIELDS} fields per row; found {len(fields)} "
                    f"in record {records + 1}."
                )
            missing = [index + 1 for index, value in enumerate(fields) if value.strip() == "?"]
            if missing:
                raise ValueError(f"Missing values at fields {missing} in record {records + 1}.")

            label = fields[-1].strip().strip("'\"")
            if label not in EXPECTED_CLASS_COUNTS:
                raise ValueError(f"Unexpected class label {label!r} in {path}.")
            counts[label] += 1
            records += 1

    if records != EXPECTED_RECORDS:
        raise ValueError(f"Expected {EXPECTED_RECORDS} records; found {records}.")
    if dict(counts) != EXPECTED_CLASS_COUNTS:
        raise ValueError(
            f"Expected class counts {EXPECTED_CLASS_COUNTS}; found {dict(counts)}."
        )
    return counts


def validate_confusion(counts: Counter[str]) -> None:
    """Check that the supplied matrix is compatible with the dataset totals."""

    true_class_0 = CONFUSION[0][0] + CONFUSION[1][0]
    true_class_1 = CONFUSION[0][1] + CONFUSION[1][1]
    if (true_class_0, true_class_1) != (counts["0"], counts["1"]):
        raise ValueError("Confusion-matrix columns do not match the dataset class totals.")


def configure_publication_style() -> None:
    """Apply a compact, explicit style suitable for LaTeX inclusion."""

    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 10.5,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "axes.linewidth": 0.8,
            "axes.edgecolor": INK,
            "axes.labelcolor": INK,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "text.color": INK,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": WHITE,
            "figure.facecolor": WHITE,
            "savefig.bbox": "tight",
        }
    )


def style_axis(ax: mpl.axes.Axes, *, grid_axis: str = "x") -> None:
    """Remove nonessential framing and add a restrained guide grid."""

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(INK)
    ax.spines["bottom"].set_color(INK)
    ax.tick_params(length=3, width=0.7, pad=4)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.65)
    ax.set_axisbelow(True)


def save_figure(fig: mpl.figure.Figure, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"{stem}.pdf", format="pdf", metadata={"Creator": "Matplotlib"})
    fig.savefig(output_dir / f"{stem}.png", format="png", dpi=300)
    plt.close(fig)


def make_class_distribution(counts: Counter[str], output_dir: Path) -> None:
    """Create a horizontal count plot with direct share annotations."""

    total = sum(counts.values())
    labels = ["0 · No peligrosa", "1 · Peligrosa"]
    values = [counts["0"], counts["1"]]
    percentages = [100 * value / total for value in values]
    y_positions = [1, 0]

    fig = plt.figure(figsize=(7.2, 3.5))
    ax = fig.add_axes([0.19, 0.25, 0.75, 0.58])
    bars = ax.barh(
        y_positions,
        values,
        height=0.46,
        color=[BLUE, RUST],
        edgecolor=WHITE,
        linewidth=1.2,
        hatch=["", "///"],
    )
    ax.set_yticks(y_positions, labels)
    ax.set_xlim(0, 2_800)
    ax.xaxis.set_major_locator(MultipleLocator(600))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: spanish_number(value, 0)))
    ax.set_xlabel("Registros", labelpad=8)
    ax.set_title("Distribución de clases", loc="left", pad=12, fontweight="bold")
    style_axis(ax, grid_axis="x")

    for bar, value, percentage in zip(bars, values, percentages):
        ax.text(
            value + 35,
            bar.get_y() + bar.get_height() / 2,
            f"n = {spanish_number(value, 0)}   ·   {spanish_percent(percentage)}",
            va="center",
            ha="left",
            fontsize=8.6,
            color=INK,
        )

    ratio = values[0] / values[1]
    fig.text(
        0.19,
        0.10,
        f"Total: {spanish_number(total, 0)} registros   ·   Razón clase 0:1 = {spanish_number(ratio, 1)}:1",
        ha="left",
        va="bottom",
        fontsize=8,
        color=MUTED,
    )
    save_figure(fig, output_dir, "candidata_distribucion_clases")


def make_confusion_matrix(output_dir: Path) -> None:
    """Create a count matrix whose fill encodes within-true-class share."""

    tn, fn = CONFUSION[0]
    fp, tp = CONFUSION[1]
    matrix = [[tn, fn], [fp, tp]]
    true_totals = [tn + fp, fn + tp]
    normalized = [
        [matrix[row][column] / true_totals[column] for column in range(2)]
        for row in range(2)
    ]

    fig = plt.figure(figsize=(6.5, 5.2))
    ax = fig.add_axes([0.20, 0.26, 0.63, 0.59])
    norm = Normalize(0, 1)
    cmap = mpl.colormaps["Greys"]
    colorbar = fig.add_axes([0.87, 0.26, 0.035, 0.59])
    for segment in range(100):
        lower = segment / 100
        colorbar.add_patch(
            Rectangle(
                (0, lower),
                1,
                0.01,
                facecolor=cmap(norm(lower + 0.005)),
                edgecolor="none",
            )
        )
    colorbar.set_xlim(0, 1)
    colorbar.set_ylim(0, 1)
    colorbar.set_xticks([])
    colorbar.yaxis.tick_right()
    colorbar.yaxis.set_label_position("right")
    colorbar.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    colorbar.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    colorbar.set_ylabel("Proporción dentro de la clase verdadera", rotation=90, labelpad=28)
    colorbar.tick_params(length=3, width=0.7, pad=5)
    for spine in colorbar.spines.values():
        spine.set_color(INK)
        spine.set_linewidth(0.7)

    class_labels = ["0\nNo peligrosa", "1\nPeligrosa"]
    ax.set_xticks([0, 1], class_labels)
    ax.set_yticks([0, 1], class_labels)
    ax.set_xlabel("Clase verdadera", labelpad=11)
    ax.set_ylabel("Clase predicha", labelpad=11)
    ax.set_title("Matriz de confusión · árbol de decisión", loc="left", pad=12, fontweight="bold")
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(1.5, -0.5)
    ax.tick_params(length=0, pad=8)
    for spine in ax.spines.values():
        spine.set_visible(False)

    cell_names = [["TN", "FN"], ["FP", "TP"]]
    for row in range(2):
        for column in range(2):
            value = matrix[row][column]
            share = normalized[row][column]
            text_color = WHITE if share >= 0.5 else INK
            ax.add_patch(
                Rectangle(
                    (column - 0.5, row - 0.5),
                    1,
                    1,
                    facecolor=cmap(norm(share)),
                    edgecolor=WHITE,
                    linewidth=1.5,
                )
            )
            ax.text(
                column,
                row - 0.08,
                f"{cell_names[row][column]}\n{spanish_number(value, 0)}",
                ha="center",
                va="center",
                color=text_color,
                fontsize=13,
                fontweight="bold",
                linespacing=1.25,
            )
            ax.text(
                column,
                row + 0.30,
                f"{spanish_percent(100 * share)} de clase verdadera",
                ha="center",
                va="center",
                color=text_color,
                fontsize=7.4,
            )

    fig.text(
        0.20,
        0.035,
        "La normalización visual permite comparar ambas clases; los conteos permanecen explícitos.",
        ha="left",
        va="bottom",
        fontsize=7.8,
        color=MUTED,
    )
    save_figure(fig, output_dir, "candidata_matriz_confusion")


def plot_metric_panel(
    ax: mpl.axes.Axes,
    metrics: Sequence[Metric],
    *,
    x_max: float,
    ticks: Sequence[float],
    title: str,
    xlabel: str,
) -> None:
    """Draw a low-ink horizontal dot-and-interval metric panel."""

    y_positions = list(range(len(metrics) - 1, -1, -1))
    for y, metric in zip(y_positions, metrics):
        if metric.error is None:
            ax.errorbar(
                metric.value,
                y,
                fmt=metric.marker,
                markersize=8,
                markeredgewidth=0.9,
                markeredgecolor=INK,
                color=metric.color,
                zorder=3,
            )
        else:
            ax.errorbar(
                metric.value,
                y,
                xerr=metric.error,
                fmt=metric.marker,
                markersize=8,
                markeredgewidth=0.9,
                markeredgecolor=INK,
                color=metric.color,
                ecolor=INK,
                elinewidth=1.1,
                capsize=3.5,
                capthick=1.0,
                zorder=3,
            )
        candidate_x = metric.value + (metric.error or 0) + x_max * 0.025
        annotation_right = candidate_x > x_max * 0.72
        annotation_x = x_max * 0.98 if annotation_right else candidate_x
        ax.text(
            annotation_x,
            y + 0.17,
            metric.annotation,
            ha="right" if annotation_right else "left",
            va="bottom",
            fontsize=8.1,
            color=INK,
        )

    ax.set_yticks(y_positions, [metric.label for metric in metrics])
    ax.set_xlim(0, x_max)
    ax.set_ylim(-0.65, len(metrics) - 0.35)
    ax.set_xticks(ticks)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: spanish_number(value, 0)))
    ax.set_xlabel(xlabel, labelpad=8)
    ax.set_title(title, loc="left", pad=9, fontweight="bold")
    style_axis(ax, grid_axis="x")
    ax.tick_params(axis="y", length=0, pad=8)


def make_metrics(output_dir: Path) -> None:
    """Create a scale-aware summary of the supplied evaluation metrics."""

    global_metrics = [
        Metric("Exactitud", 92.84, 0.27, "92,84 ± 0,27 p.p.", "o", BLUE),
        Metric("AUC (optimista)", 86.0, 4.1, "86,0 ± 4,1 p.p.", "D", RUST),
    ]
    positive_metrics = [
        Metric("Precisión", 20.00, None, "20,00%", "o", OLIVE),
        Metric("Recall micro", 2.94, None, "2,94%", "s", RUST),
        Metric("F-measure", 5.13, None, "5,13%", "D", PLUM),
    ]

    fig = plt.figure(figsize=(8.5, 4.25))
    fig.text(
        0.08,
        0.96,
        "Indicadores de rendimiento reportados",
        ha="left",
        va="top",
        fontsize=12,
        fontweight="bold",
        color=INK,
    )
    ax_global = fig.add_axes([0.08, 0.28, 0.39, 0.57])
    ax_positive = fig.add_axes([0.58, 0.28, 0.34, 0.57])
    plot_metric_panel(
        ax_global,
        global_metrics,
        x_max=100,
        ticks=[0, 20, 40, 60, 80, 100],
        title="Rendimiento global",
        xlabel="Porcentaje (%)",
    )
    plot_metric_panel(
        ax_positive,
        positive_metrics,
        x_max=25,
        ticks=[0, 5, 10, 15, 20, 25],
        title="Clase positiva (1)",
        xlabel="Porcentaje (%)",
    )
    fig.text(
        0.08,
        0.095,
        "Nota: el AUC se expresa aquí en porcentaje (0,860 ± 0,041). El encabezado reporta recall = 3,05% ± 4,36%; el valor micro mostrado es 2,94%.",
        ha="left",
        va="bottom",
        fontsize=7.6,
        color=MUTED,
    )
    save_figure(fig, output_dir, "candidata_metricas_arbol")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
        help=f"Path to seismic-bumps.arff (default: {DEFAULT_DATASET})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Directory for PDF/PNG outputs (default: {DEFAULT_OUTPUT})",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    dataset = args.dataset.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    counts = parse_arff(dataset)
    validate_confusion(counts)
    configure_publication_style()
    make_class_distribution(counts, output_dir)
    make_confusion_matrix(output_dir)
    make_metrics(output_dir)
    print(f"Validated {sum(counts.values()):,} records from {dataset}.")
    print(f"Wrote six figures to {output_dir} using Matplotlib {mpl.__version__}.")


if __name__ == "__main__":
    main()
