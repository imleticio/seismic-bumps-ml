#!/usr/bin/env python3
"""Reproducibly create publication figures for the Seismic-Bumps dataset.

Run from the repository root or from ``testGraph``.  Only the Python standard
library, NumPy, and Matplotlib are required.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


OKABE_ITO = {
    "orange": "#E69F00",
    "sky": "#56B4E9",
    "green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
    "black": "#000000",
}

EXPECTED_FIELDS = 19
EXPECTED_ROWS = 2584
EXPECTED_COUNTS = {"0": 2414, "1": 170}
MATRICES = {
    "Decision Tree base": np.array([[2394, 20], [165, 5]], dtype=int),
    "Naive Bayes base": np.array([[2120, 294], [100, 70]], dtype=int),
}


def parse_arff(path: Path) -> tuple[list[str], list[list[str]]]:
    attributes: list[str] = []
    rows: list[list[str]] = []
    in_data = False
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("%"):
                continue
            if line.lower() == "@data":
                in_data = True
                continue
            if not in_data:
                match = re.match(r"@attribute\s+([^\s]+)", line, re.I)
                if match:
                    attributes.append(match.group(1))
                continue
            row = next(csv.reader([line], skipinitialspace=True))
            rows.append([item.strip() for item in row])
    return attributes, rows


def validate_dataset(path: Path, fields: list[str], rows: list[list[str]]) -> None:
    if len(fields) != EXPECTED_FIELDS:
        raise ValueError(f"Expected {EXPECTED_FIELDS} fields, found {len(fields)}")
    if len(rows) != EXPECTED_ROWS:
        raise ValueError(f"Expected {EXPECTED_ROWS} rows, found {len(rows)}")
    if any(len(row) != EXPECTED_FIELDS for row in rows):
        raise ValueError("At least one row does not have 19 fields")
    if any(value in {"", "?"} for row in rows for value in row):
        raise ValueError("Dataset contains missing values")
    counts = {label: sum(row[-1] == label for row in rows) for label in ("0", "1")}
    if counts != EXPECTED_COUNTS:
        raise ValueError(f"Expected class counts {EXPECTED_COUNTS}, found {counts}")
    print(f"Validated {path}: {len(rows)} rows, {len(fields)} fields, class counts 0={counts['0']}, 1={counts['1']}, no missing values")


def configure_style() -> None:
    mpl.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.labelsize": 9,
        "axes.titlesize": 10,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def save_figure(fig: mpl.figure.Figure, output: Path, stem: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for extension in ("svg", "pdf", "png"):
        fig.savefig(output / f"{stem}.{extension}", dpi=600, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    proportion = successes / total
    denominator = 1 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    half_width = z * np.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total)) / denominator
    return centre - half_width, centre + half_width


def bootstrap_mean_ci(values: np.ndarray, rng: np.random.Generator, draws: int = 4000) -> tuple[float, float]:
    # Process in small chunks so the 2,414-observation majority class does not
    # require a large temporary (draws x observations) allocation.
    means = np.empty(draws)
    for start in range(0, draws, 100):
        stop = min(start + 100, draws)
        samples = rng.choice(values, size=(stop - start, values.size), replace=True)
        means[start:stop] = samples.mean(axis=1)
    return tuple(np.quantile(means, [0.025, 0.975]))  # type: ignore[return-value]


def figure_class_balance(classes: np.ndarray) -> mpl.figure.Figure:
    counts = np.array([np.sum(classes == 0), np.sum(classes == 1)])
    fig, ax = plt.subplots(figsize=(4.8, 3.4), constrained_layout=True)
    bars = ax.bar(["No peligro (0)", "Peligro (1)"], counts,
                  color=[OKABE_ITO["sky"], OKABE_ITO["vermillion"]], width=0.62)
    ax.set_ylabel("Observaciones (n)")
    ax.set_title("Distribución de clases del conjunto Seismic-Bumps", loc="left", fontweight="bold")
    ax.set_ylim(0, max(counts) * 1.18)
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, count + max(counts) * 0.025,
                f"{count:,}\n({count / counts.sum():.1%})", ha="center", va="bottom")
    ax.text(0, -0.19, "Fuente: seismic-bumps.arff; n = 2,584", transform=ax.transAxes, fontsize=8)
    return fig


def figure_attributes(fields: list[str], rows: list[list[str]]) -> mpl.figure.Figure:
    index = {name: fields.index(name) for name in ("genergy", "gpuls", "energy")}
    classes = np.array([int(row[-1]) for row in rows])
    rng = np.random.default_rng(20260719)
    fig, axes = plt.subplots(1, 3, figsize=(10.0, 3.8), sharey=False, constrained_layout=True)
    labels = {"genergy": "genergy", "gpuls": "gpuls", "energy": "energy"}
    for ax, name in zip(axes, ("genergy", "gpuls", "energy")):
        raw = np.array([float(row[index[name]]) for row in rows])
        values = np.log10(raw + 1.0)
        for class_value, color, label in ((0, OKABE_ITO["sky"], "No peligro"), (1, OKABE_ITO["vermillion"], "Peligro")):
            observed = values[classes == class_value]
            x = class_value + rng.uniform(-0.17, 0.17, observed.size)
            ax.scatter(x, observed, s=8 if class_value == 0 else 13, alpha=0.28 if class_value == 0 else 0.65,
                       color=color, edgecolors="none", rasterized=True, label=label)
            mean = observed.mean()
            low, high = bootstrap_mean_ci(observed, rng)
            ax.errorbar(class_value, mean, yerr=[[mean - low], [high - mean]], fmt="o",
                        color=OKABE_ITO["black"], markerfacecolor="white", markersize=5,
                        capsize=3, linewidth=1.2, zorder=5)
            ax.text(class_value, ax.get_ylim()[1], f"n={observed.size}", ha="center", va="top", fontsize=8)
        ax.set_title(labels[name], fontweight="bold")
        ax.set_xticks([0, 1], ["No peligro", "Peligro"])
        ax.set_xlabel("Clase")
        ax.set_ylabel(r"$λ$ = log$_{10}$(valor + 1)")
        ax.grid(axis="y", color="#D9D9D9", linewidth=0.6, alpha=0.7)
        ax.set_axisbelow(True)
    axes[0].legend(frameon=False, loc="upper left")
    fig.suptitle("Atributos seleccionados por clase", x=0.01, ha="left", fontweight="bold")
    fig.text(0.01, -0.025, "Puntos: observaciones individuales. Círculo: media; barras: IC bootstrap del 95%. Transformación log10(valor + 1).",
             fontsize=8)
    return fig


def figure_recall() -> mpl.figure.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.8), sharey=True, constrained_layout=True)
    for ax, (name, matrix) in zip(axes, MATRICES.items()):
        false_negative, true_positive = int(matrix[1, 0]), int(matrix[1, 1])
        outcomes = np.array([0] * false_negative + [1] * true_positive)
        rng = np.random.default_rng(100 + true_positive)
        x = rng.uniform(-0.22, 0.22, outcomes.size)
        colors = np.where(outcomes == 1, OKABE_ITO["green"], OKABE_ITO["vermillion"])
        ax.scatter(x, outcomes, c=colors, s=17, alpha=0.7, edgecolors="white", linewidths=0.25, rasterized=True)
        recall = outcomes.mean()
        low, high = wilson_interval(true_positive, outcomes.size)
        ax.errorbar(0, recall, xerr=[[recall - low], [high - recall]], fmt="o", color=OKABE_ITO["black"],
                    markerfacecolor="white", markersize=6, capsize=3, linewidth=1.4, zorder=4)
        ax.set_title(name, fontweight="bold")
        ax.set_xlim(-0.45, 0.45)
        ax.set_ylim(-0.18, 1.35)
        ax.set_xticks([])
        ax.set_yticks([0, 1], ["FN (0)", "TP (1)"])
        ax.grid(axis="y", color="#D9D9D9", linewidth=0.6, alpha=0.7)
        ax.text(0, 1.22, f"Recall = {recall:.1%}\nWilson IC 95%: [{low:.1%}, {high:.1%}]",
                ha="center", va="center", fontsize=8,
                bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": "#BFBFBF"})
        ax.set_xlabel(f"n positivos = {outcomes.size}")
    axes[0].set_ylabel("Resultado por caso positivo real")
    fig.suptitle("Recall de la clase peligrosa", x=0.01, ha="left", fontweight="bold")
    fig.text(0.01, -0.025, "Puntos agrupados: resultados de casos positivos reales reconstruidos desde matrices agregadas; no son puntos de 10 folds.", fontsize=8)
    return fig


def figure_confusion() -> mpl.figure.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.8), constrained_layout=True)
    for ax, (name, matrix) in zip(axes, MATRICES.items()):
        row_percent = matrix / matrix.sum(axis=1, keepdims=True) * 100
        image = ax.imshow(matrix, cmap="cividis", vmin=0, vmax=max(np.max(m) for m in MATRICES.values()))
        ax.set_xticks([0, 1], ["Pred. 0", "Pred. 1"])
        ax.set_yticks([0, 1], ["Real 0", "Real 1"])
        ax.set_xlabel("Clase predicha")
        ax.set_ylabel("Clase real")
        ax.set_title(name, fontweight="bold")
        for i in range(2):
            for j in range(2):
                text_color = "white" if matrix[i, j] > np.max(matrix) * 0.45 else OKABE_ITO["black"]
                ax.text(j, i, f"{matrix[i, j]:,}\n({row_percent[i, j]:.1f}%)", ha="center", va="center",
                        color=text_color, fontsize=9, fontweight="bold")
        for edge in ax.spines.values():
            edge.set_visible(True)
            edge.set_color("white")
            edge.set_linewidth(1.2)
    fig.colorbar(image, ax=axes, shrink=0.82, label="Conteo")
    fig.suptitle("Matrices de confusión de modelos base", x=0.01, ha="left", fontweight="bold")
    fig.text(0.01, -0.025, "Cada celda muestra conteo y porcentaje por fila. Filas = clase real; columnas = clase predicha.", fontsize=8)
    return fig


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=None, help="ARFF path (default: ../seismic-bumps.arff from testGraph)")
    parser.add_argument("--output", type=Path, default=None, help="Output directory (default: testGraph)")
    args = parser.parse_args()
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    input_path = (args.input if args.input is not None else repo_root / "seismic-bumps.arff").resolve()
    output_path = (args.output if args.output is not None else script_dir).resolve()
    fields, rows = parse_arff(input_path)
    validate_dataset(input_path, fields, rows)
    configure_style()
    classes = np.array([int(row[-1]) for row in rows])
    save_figure(figure_class_balance(classes), output_path, "01_distribucion_clases")
    save_figure(figure_attributes(fields, rows), output_path, "02_atributos_por_clase")
    save_figure(figure_recall(), output_path, "03_recall_clase_peligrosa")
    save_figure(figure_confusion(), output_path, "04_matrices_confusion")
    print(f"Wrote 12 figures (SVG, PDF, PNG at 600 DPI) to {output_path}")


if __name__ == "__main__":
    main()
