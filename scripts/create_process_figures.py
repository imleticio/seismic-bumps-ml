#!/usr/bin/env python3
"""Create clean, vector process diagrams used in the progress report.

The figures are schematic only: no observations, fitted values, or other
empirical results are embedded in them.  The script is intentionally offline
and derives its default output directory from its own location.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch
from matplotlib.text import Text

try:
    import seaborn as sns
except ImportError:  # Keep the generator usable in a minimal offline setup.
    sns = None


if sns is not None:
    COLORBLIND = list(sns.color_palette("colorblind", 8))
else:
    # The standard seaborn colorblind palette, kept as an offline fallback.
    COLORBLIND = [
        "#0173B2",
        "#DE8F05",
        "#029E73",
        "#D55E00",
        "#CC78BC",
        "#CA9161",
        "#FBAFE4",
        "#949494",
    ]


PAGE_FACE = "#FFFFFF"
TEXT = "#202124"
MUTED_TEXT = "#5F6368"


def configure_style() -> None:
    """Set paper-oriented typography and line weights."""

    if sns is not None:
        sns.set_theme(style="white", context="paper", font="sans-serif")
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [
                "DejaVu Sans",
                "Arial",
                "Liberation Sans",
                "sans-serif",
            ],
            "font.size": 10.5,
            "axes.facecolor": PAGE_FACE,
            "figure.facecolor": PAGE_FACE,
            "savefig.facecolor": PAGE_FACE,
            "pdf.fonttype": 42,
            "text.color": TEXT,
        }
    )


def draw_box(
    ax: plt.Axes,
    x: float,
    y: float,
    width: float,
    height: float,
    label: str,
    color: str,
    subtitle: str | None = None,
) -> None:
    """Draw one rounded process box with an optional explanatory subtitle."""

    box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.035,rounding_size=0.10",
        linewidth=1.4,
        edgecolor=color,
        facecolor=to_rgba(color, alpha=0.13),
        zorder=2,
    )
    ax.add_patch(box)
    center_x = x + width / 2
    center_y = y + height / 2
    if subtitle is None:
        ax.text(
            center_x,
            center_y,
            label,
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color=TEXT,
            zorder=3,
        )
    else:
        ax.text(
            center_x,
            center_y + 0.12,
            label,
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color=TEXT,
            zorder=3,
        )
        ax.text(
            center_x,
            center_y - 0.18,
            subtitle,
            ha="center",
            va="center",
            fontsize=8.5,
            color=MUTED_TEXT,
            zorder=3,
        )


def draw_arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    label: str | None = None,
    label_offset: tuple[float, float] = (0.0, 0.18),
) -> None:
    """Draw a clean, centered connector between process boxes."""

    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=13,
        linewidth=1.8,
        color=COLORBLIND[7],
        shrinkA=0,
        shrinkB=0,
        zorder=1,
    )
    ax.add_patch(arrow)
    if label:
        ax.text(
            (start[0] + end[0]) / 2 + label_offset[0],
            (start[1] + end[1]) / 2 + label_offset[1],
            label,
            ha="center",
            va="center",
            fontsize=8.5,
            color=MUTED_TEXT,
            zorder=3,
        )


def new_figure(xlim: tuple[float, float], ylim: tuple[float, float], figsize: tuple[float, float]):
    """Create a fixed-layout figure with explicit margins instead of tight cropping."""

    fig, ax = plt.subplots(figsize=figsize)
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.08, top=0.92)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    return fig, ax


def create_ai_studio_figure(path: Path) -> None:
    """Create Dataset -> Set Role -> Cross Validation -> Metrics."""

    fig, ax = new_figure((0.0, 10.0), (0.0, 3.0), (10.0, 2.8))
    y, width, height = 1.02, 1.70, 0.96
    boxes = [
        (0.55, "Dataset", COLORBLIND[0], "input data"),
        (2.80, "Set Role", COLORBLIND[4], "assign roles"),
        (5.05, "Cross Validation", COLORBLIND[1], "model evaluation"),
        (7.70, "Metrics", COLORBLIND[2], "summary"),
    ]
    for x, label, color, subtitle in boxes:
        draw_box(ax, x, y, width, height, label, color, subtitle)

    center_y = y + height / 2
    for left, right in zip(boxes, boxes[1:]):
        draw_arrow(
            ax,
            (left[0] + width + 0.10, center_y),
            (right[0] - 0.10, center_y),
        )

    save_figure(fig, path)


def create_cross_validation_figure(path: Path) -> None:
    """Create the cross-validation interior with explicit Training and Testing."""

    fig, ax = new_figure((0.0, 10.0), (0.0, 3.55), (10.0, 3.3))
    top_y, box_height = 1.92, 0.92
    top_boxes = [
        (0.40, 1.55, "Training", COLORBLIND[0], "training data"),
        (2.45, 1.85, "Decision Tree", COLORBLIND[2], "fit model"),
        (5.05, 1.85, "Apply Model", COLORBLIND[4], "predict"),
        (7.65, 1.85, "Performance", COLORBLIND[1], "evaluate"),
    ]
    for x, width, label, color, subtitle in top_boxes:
        draw_box(ax, x, top_y, width, box_height, label, color, subtitle)

    testing_x, testing_y, testing_width, testing_height = 5.05, 0.42, 1.85, 0.88
    draw_box(
        ax,
        testing_x,
        testing_y,
        testing_width,
        testing_height,
        "Testing",
        COLORBLIND[3],
        "test data",
    )

    top_center_y = top_y + box_height / 2
    draw_arrow(
        ax,
        (top_boxes[0][0] + top_boxes[0][1] + 0.10, top_center_y),
        (top_boxes[1][0] - 0.10, top_center_y),
    )
    draw_arrow(
        ax,
        (top_boxes[1][0] + top_boxes[1][1] + 0.10, top_center_y),
        (top_boxes[2][0] - 0.10, top_center_y),
        label="model",
    )
    draw_arrow(
        ax,
        (top_boxes[2][0] + top_boxes[2][1] + 0.10, top_center_y),
        (top_boxes[3][0] - 0.10, top_center_y),
    )
    draw_arrow(
        ax,
        (testing_x + testing_width / 2, testing_y + testing_height + 0.08),
        (testing_x + testing_width / 2, top_y - 0.08),
        label="test set",
        label_offset=(0.70, 0.0),
    )

    save_figure(fig, path)


def assert_artists_have_margin(fig: plt.Figure, ax: plt.Axes, margin_px: float = 3.0) -> None:
    """Fail early if a text or patch artist touches the page boundary."""

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    page = fig.bbox
    for artist in ax.get_children():
        if not isinstance(artist, (Text, Patch)) or not artist.get_visible():
            continue
        bbox = artist.get_window_extent(renderer=renderer)
        if not bbox.width or not bbox.height:
            continue
        if (
            bbox.x0 < page.x0 + margin_px
            or bbox.y0 < page.y0 + margin_px
            or bbox.x1 > page.x1 - margin_px
            or bbox.y1 > page.y1 - margin_px
        ):
            raise RuntimeError(f"Artist is too close to page edge: {artist!r}")


def save_figure(fig: plt.Figure, path: Path) -> None:
    """Validate layout, then save a vector PDF without tight cropping."""

    ax = fig.axes[0]
    assert_artists_have_margin(fig, ax)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, format="pdf", facecolor=PAGE_FACE)
    plt.close(fig)


def build_figures(output_dir: Path) -> Iterable[Path]:
    """Generate both requested PDFs and return their paths."""

    outputs = [
        output_dir / "proceso_ai_studio_clean.pdf",
        output_dir / "proceso_cross_validation_clean.pdf",
    ]
    create_ai_studio_figure(outputs[0])
    create_cross_validation_figure(outputs[1])
    return outputs


def main() -> None:
    configure_style()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "output" / "figures",
        help="Directory in which to write the generated vector PDFs.",
    )
    args = parser.parse_args()
    for output in build_figures(args.output_dir):
        print(output)


if __name__ == "__main__":
    main()
