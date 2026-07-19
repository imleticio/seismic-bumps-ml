"""Create a publication-ready comparison of class-1 metrics."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import PercentFormatter


OUTPUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "output"
    / "figures"
    / "comparison_class1_metrics.pdf"
)


def main() -> None:
    data = pd.DataFrame(
        {
            "Modelo": [
                "Árbol de decisión",
                "Naive Bayes",
                "k-NN (k=5)",
                "Regresión logística",
            ],
            "Precisión": [0.2000, 0.1923, 0.3902, 0.2560],
            "Recall": [0.0294, 0.4118, 0.0941, 0.4412],
            "F1": [0.0513, 0.2622, 0.1517, 0.3240],
        }
    )
    long_data = data.melt(
        id_vars="Modelo", var_name="Métrica", value_name="Proporción"
    )

    sns.set_theme(
        style="whitegrid",
        context="paper",
        palette="colorblind",
        font="DejaVu Sans",
        font_scale=1.05,
    )
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    sns.barplot(
        data=long_data,
        x="Modelo",
        y="Proporción",
        hue="Métrica",
        hue_order=["Precisión", "Recall", "F1"],
        palette=sns.color_palette("colorblind", 3),
        errorbar=None,
        ax=ax,
    )

    ax.set_xlabel("")
    ax.set_ylabel("Valor agregado de la clase 1")
    ax.set_ylim(0, 0.50)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.tick_params(axis="x", rotation=12)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")

    for container in ax.containers:
        ax.bar_label(
            container,
            labels=[f"{bar.get_height() * 100:.1f}%" for bar in container],
            padding=2,
            fontsize=7.4,
        )

    ax.legend(
        title="Métrica",
        ncol=3,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.15),
        frameon=False,
    )
    sns.despine(ax=ax, left=False, bottom=False)
    fig.tight_layout()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, format="pdf", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
