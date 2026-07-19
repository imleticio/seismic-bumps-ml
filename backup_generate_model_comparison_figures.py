#!/usr/bin/env python3
"""Generate reproducible, publication-ready figures for the four classifiers."""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


EXPECTED_CLASS_COUNTS = {"0": 2414, "1": 170}
MODELS = {
    "DT base": {
        "label": "Árbol de decisión base",
        "matrix": np.array([[2394, 20], [165, 5]], dtype=int),
        "accuracy": (92.84, 0.27),
        "auc": (0.860, 0.041),
    },
    "NB base": {
        "label": "Naive Bayes base",
        "matrix": np.array([[2120, 294], [100, 70]], dtype=int),
        "accuracy": (84.75, 4.31),
        "auc": (0.761, 0.043),
    },
    "DT + SMOTE": {
        "label": "Árbol de decisión + SMOTE",
        "matrix": np.array([[2005, 409], [81, 89]], dtype=int),
        "accuracy": (81.03, 4.01),
        "auc": (0.824, 0.068),
        "precision_header": (17.95, 4.15),
        "recall_header": (52.49, 16.03),
        "f1_header": (26.50, 6.39),
    },
    "NB + SMOTE": {
        "label": "Naive Bayes + SMOTE",
        "matrix": np.array([[1693, 721], [56, 114]], dtype=int),
        "accuracy": (69.94, 17.58),
        "auc": (0.748, 0.034),
        "precision_header": (15.24, 3.58),
        "recall_header": (67.04, 11.55),
        "f1_header": (24.49, 5.08),
    },
}

COLORS = ["#0072B2", "#56B4E9", "#009E73", "#D55E00"]


def spanish_number(value: float, decimals: int = 2) -> str:
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def spanish_percent(value: float, decimals: int = 2) -> str:
    return f"{spanish_number(value, decimals)}%"


def parse_class_counts(dataset_path: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    in_data = False
    with dataset_path.open(encoding="utf-8", newline="") as dataset:
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
            label = fields[-1].strip().strip("'\"")
            if label not in EXPECTED_CLASS_COUNTS:
                raise ValueError(f"Etiqueta inesperada: {label!r}")
            counts[label] += 1
    if dict(counts) != EXPECTED_CLASS_COUNTS:
        raise ValueError(f"Conteos inesperados: {dict(counts)}")
    return counts


def aggregate_metrics(matrix: np.ndarray) -> tuple[float, float, float]:
    precision = 100 * matrix[1, 1] / matrix[:, 1].sum()
    recall = 100 * matrix[1, 1] / matrix[1, :].sum()
    f1 = 2 * precision * recall / (precision + recall)
    return precision, recall, f1


def validate_results(class_counts: Counter[str]) -> None:
    total = sum(class_counts.values())
    if total != 2584:
        raise ValueError(f"Total inesperado: {total}")
    expected_aggregate = {
        "DT base": (20.00, 2.94, 5.13),
        "NB base": (19.23, 41.18, 26.22),
        "DT + SMOTE": (17.87, 52.35, 26.65),
        "NB + SMOTE": (13.65, 67.06, 22.69),
    }
    for name, data in MODELS.items():
        matrix = data["matrix"]
        if matrix.sum() != total or tuple(matrix.sum(axis=1)) != (2414, 170):
            raise ValueError(f"La matriz de {name} no conserva la distribución original")
        accuracy = 100 * (matrix[0, 0] + matrix[1, 1]) / total
        if not math.isclose(accuracy, data["accuracy"][0], abs_tol=0.02):
            raise ValueError(f"Exactitud inconsistente en {name}")
        aggregate = aggregate_metrics(matrix)
        for actual, expected in zip(aggregate, expected_aggregate[name]):
            if not math.isclose(actual, expected, abs_tol=0.02):
                raise ValueError(f"Métrica agregada inconsistente en {name}")


def configure_style() -> None:
    sns.set_theme(style="whitegrid", context="paper")
    mpl.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9,
        "axes.titlesize": 11, "axes.labelsize": 9,
        "xtick.labelsize": 8, "ytick.labelsize": 8,
        "legend.fontsize": 8, "pdf.fonttype": 42,
        "ps.fonttype": 42, "savefig.facecolor": "white",
        "figure.facecolor": "white",
    })


def save_figure(fig: mpl.figure.Figure, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(output_dir / f"{stem}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def style_axis(ax: mpl.axes.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.6)
    ax.set_axisbelow(True)


def make_class_distribution(output_dir: Path, counts: Counter[str]) -> None:
    labels = ["No peligrosa (0)", "Peligrosa (1)"]
    values = [counts["0"], counts["1"]]
    fig, ax = plt.subplots(figsize=(5.4, 3.4))
    bars = ax.bar(labels, values, color=[COLORS[1], COLORS[3]], edgecolor="white")
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 35,
                f"{value}\n{spanish_percent(100 * value / sum(values))}",
                ha="center", va="bottom")
    ax.set_ylabel("Registros")
    ax.set_title("Distribución de la variable objetivo")
    ax.set_ylim(0, 2700)
    style_axis(ax)
    fig.tight_layout()
    save_figure(fig, output_dir, "distribucion_clases")


def make_confusion_matrix(output_dir: Path, key: str) -> None:
    matrix = MODELS[key]["matrix"]
    labels = ["0 - No peligrosa", "1 - Peligrosa"]
    row_percentages = 100 * matrix / matrix.sum(axis=1, keepdims=True)
    annotations = np.array([[f"{matrix[r, c]}\n{spanish_percent(row_percentages[r, c])}"
                             for c in range(2)] for r in range(2)])
    fig, ax = plt.subplots(figsize=(5.2, 4.1))
    sns.heatmap(matrix, annot=annotations, fmt="", cmap="cividis", square=True,
                linewidths=1.2, linecolor="white", cbar=True,
                cbar_kws={"label": "Registros"}, ax=ax)
    ax.set_title(f"Matriz de confusión: {MODELS[key]['label']}")
    ax.set_xlabel("Clase predicha")
    ax.set_ylabel("Clase verdadera")
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_yticklabels(labels, rotation=0)
    fig.tight_layout()
    save_figure(fig, output_dir, f"matriz_confusion_{key.lower().replace(' + ', '_').replace(' ', '_')}")


def make_model_comparison(output_dir: Path) -> None:
    names = list(MODELS)
    labels = [MODELS[name]["label"].replace("Árbol de decisión", "DT")
              .replace("Naive Bayes", "NB") for name in names]
    x = np.arange(len(names))
    metrics = ["accuracy", "auc"]
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.6))
    for metric, ax in zip(metrics, axes):
        values = np.array([MODELS[name][metric][0] * (100 if metric == "auc" else 1) for name in names])
        errors = np.array([MODELS[name][metric][1] * (100 if metric == "auc" else 1) for name in names])
        bars = ax.bar(x, values, yerr=errors, capsize=3, color=COLORS, edgecolor="white")
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(errors) * 0.18,
                    f"{spanish_number(value)}%", ha="center", va="bottom", fontsize=7.5)
        ax.set_xticks(x, labels, rotation=20, ha="right")
        ax.set_ylabel("Porcentaje (%)")
        ax.set_title("Exactitud" if metric == "accuracy" else "AUC")
        ax.set_ylim(0, 105)
        style_axis(ax)
    fig.suptitle("Comparación global de las cuatro variantes", fontweight="bold")
    fig.tight_layout()
    save_figure(fig, output_dir, "comparacion_modelos")

    class_metrics = np.array([aggregate_metrics(MODELS[name]["matrix"]) for name in names])
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    width = 0.19
    for index, (label, color) in enumerate(zip(labels, COLORS)):
        bars = ax.bar(np.arange(3) + (index - 1.5) * width, class_metrics[index],
                      width=width, label=label, color=color, edgecolor="white")
        for bar, value in zip(bars, class_metrics[index]):
            ax.text(bar.get_x() + bar.get_width() / 2, value + 0.8,
                    f"{spanish_number(value)}%", ha="center", va="bottom", fontsize=7)
    ax.set_xticks(np.arange(3), ["Precisión", "Recall (clase 1)", "F1 agregado"])
    ax.set_ylabel("Porcentaje (%)")
    ax.set_ylim(0, 78)
    ax.set_title("Métricas agregadas de la clase positiva")
    ax.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    style_axis(ax)
    fig.tight_layout()
    save_figure(fig, output_dir, "metricas_clase_positiva_cuatro_variantes")


def build_parser() -> argparse.ArgumentParser:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=root / "seismic-bumps.arff")
    parser.add_argument("--output-dir", type=Path, default=root / "output" / "figures")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    counts = parse_class_counts(args.dataset)
    validate_results(counts)
    configure_style()
    make_class_distribution(args.output_dir, counts)
    for key in MODELS:
        make_confusion_matrix(args.output_dir, key)
    make_model_comparison(args.output_dir)
    print(f"Conteos validados: clase 0 = {counts['0']}, clase 1 = {counts['1']}")
    print(f"Variantes validadas: {', '.join(MODELS)}")


if __name__ == "__main__":
    main()
