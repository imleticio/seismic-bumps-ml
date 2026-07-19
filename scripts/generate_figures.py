#!/usr/bin/env python3
"""Generate publication-ready figures for the Seismic-Bumps report.

The ARFF parser intentionally uses only Python's standard library. Matplotlib
is used for rendering the requested PDF and 300 dpi PNG figures.
"""

from __future__ import annotations

import argparse
import csv
import math
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

try:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover - selected only without plotting deps
    mpl = None  # type: ignore[assignment]
    plt = None  # type: ignore[assignment]
    HAS_MATPLOTLIB = False
else:
    HAS_MATPLOTLIB = True


EXPECTED_COUNTS = {"0": 2414, "1": 170}
CONFUSION_MATRIX = ((2394, 165), (20, 5))

# Okabe-Ito colors: distinguishable in common forms of color vision deficiency.
OKABE_ITO = {
    "blue": "#0072B2",
    "sky": "#56B4E9",
    "green": "#009E73",
    "yellow": "#F0E442",
    "orange": "#E69F00",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
    "black": "#000000",
}


def parse_class_counts(dataset_path: Path) -> Counter[str]:
    """Read the final field of each ARFF data row and count classes 0 and 1."""

    counts: Counter[str] = Counter()
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

            label = fields[-1].strip().strip("'\"")
            if label not in EXPECTED_COUNTS:
                raise ValueError(
                    f"Unexpected class label {label!r} in {dataset_path}"
                )
            counts[label] += 1

    if dict(counts) != EXPECTED_COUNTS:
        raise ValueError(
            f"Unexpected class counts in {dataset_path}: "
            f"expected {EXPECTED_COUNTS}, found {dict(counts)}"
        )
    return counts


def spanish_number(value: float, decimals: int = 2) -> str:
    """Format a number using Spanish decimal and thousands separators."""

    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def spanish_percent(value: float, decimals: int = 2) -> str:
    return f"{spanish_number(value, decimals)}%"


def configure_publication_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "axes.linewidth": 0.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": "white",
            "figure.facecolor": "white",
        }
    )


def style_axis(ax: mpl.axes.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.6)
    ax.set_axisbelow(True)


def save_figure(fig: mpl.figure.Figure, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"{stem}.pdf", format="pdf", bbox_inches="tight")
    fig.savefig(
        output_dir / f"{stem}.png",
        format="png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


def make_class_distribution_figure(
    counts: Counter[str], output_dir: Path
) -> None:
    total = sum(counts.values())
    classes = ["0", "1"]
    values = [counts[cls] for cls in classes]
    percentages = [100 * value / total for value in values]

    fig, ax = plt.subplots(figsize=(5.8, 3.4))
    positions = list(range(len(classes)))
    bars = ax.bar(
        positions,
        values,
        width=0.58,
        color=[OKABE_ITO["blue"], OKABE_ITO["vermillion"]],
        edgecolor="white",
        linewidth=0.8,
    )
    ax.set_title("Distribución de clases")
    ax.set_ylabel("Cantidad de registros")
    ax.set_xticks(positions)
    ax.set_xticklabels(["0\nNo peligrosa", "1\nPeligrosa"])
    ax.set_ylim(0, max(values) * 1.18)
    style_axis(ax)

    for bar, value, percentage in zip(bars, values, percentages):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + max(values) * 0.025,
            f"n = {spanish_number(value, 0)}\n{spanish_percent(percentage)}",
            ha="center",
            va="bottom",
            fontsize=8.5,
        )

    fig.tight_layout()
    save_figure(fig, output_dir, "distribucion_clases")


def make_confusion_matrix_figure(output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(5.4, 4.3))
    image = ax.imshow(CONFUSION_MATRIX, cmap="cividis", aspect="equal")
    colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    colorbar.set_label("Registros", rotation=90, labelpad=8)

    class_labels = ["0\nNo peligrosa", "1\nPeligrosa"]
    ax.set_title("Matriz de confusión - árbol de decisión")
    ax.set_xlabel("Clase verdadera", labelpad=8)
    ax.set_ylabel("Clase predicha", labelpad=8)
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(class_labels)
    ax.set_yticklabels(class_labels)

    maximum = max(max(row) for row in CONFUSION_MATRIX)
    for row_index, row in enumerate(CONFUSION_MATRIX):
        for column_index, value in enumerate(row):
            text_color = "white" if value > maximum * 0.45 else OKABE_ITO["black"]
            ax.text(
                column_index,
                row_index,
                spanish_number(value, 0),
                ha="center",
                va="center",
                color=text_color,
                fontsize=13,
                fontweight="bold",
            )

    ax.set_xticks([-0.5, 0.5, 1.5], minor=True)
    ax.set_yticks([-0.5, 0.5, 1.5], minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    save_figure(fig, output_dir, "matriz_confusion_arbol")


def annotate_bars(
    ax: mpl.axes.Axes,
    bars: Iterable[mpl.patches.Rectangle],
    labels: Sequence[str],
    offsets: Sequence[float],
) -> None:
    for bar, label, offset in zip(bars, labels, offsets):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + offset,
            label,
            ha="center",
            va="bottom",
            fontsize=8.2,
        )


def make_metrics_figure(output_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.8))
    fig.subplots_adjust(wspace=0.34, bottom=0.22, top=0.84)

    # Panel A: the supplied uncertainty is retained, with AUC expressed in
    # percentage points (0.041 on the 0-1 scale equals 4.1 percentage points).
    global_values = [92.84, 86.0]
    global_errors = [0.27, 4.1]
    global_bars = axes[0].bar(
        [0, 1],
        global_values,
        yerr=global_errors,
        capsize=4,
        color=[OKABE_ITO["blue"], OKABE_ITO["orange"]],
        edgecolor="white",
        linewidth=0.8,
        error_kw={"elinewidth": 1.0, "capthick": 1.0, "ecolor": OKABE_ITO["black"]},
    )
    axes[0].set_title("A. Rendimiento global")
    axes[0].set_ylabel("Porcentaje (%)")
    axes[0].set_xticks([0, 1])
    axes[0].set_xticklabels(["Exactitud", "AUC\n(optimista)"])
    axes[0].set_ylim(0, 105)
    axes[0].set_yticks([0, 20, 40, 60, 80, 100])
    style_axis(axes[0])
    annotate_bars(
        axes[0],
        global_bars,
        ["92,84% ± 0,27 p.p.", "86,0% ± 4,1 p.p."],
        [3.5, 5.0],
    )

    # Panel B intentionally uses the micro-average recall and does not add
    # the separate fold-summary uncertainty to that value.
    positive_values = [20.0, 2.94, 5.13]
    positive_bars = axes[1].bar(
        [0, 1, 2],
        positive_values,
        color=[
            OKABE_ITO["green"],
            OKABE_ITO["vermillion"],
            OKABE_ITO["purple"],
        ],
        edgecolor="white",
        linewidth=0.8,
    )
    axes[1].set_title("B. Clase positiva (1)")
    axes[1].set_ylabel("Porcentaje (%)")
    axes[1].set_xticks([0, 1, 2])
    axes[1].set_xticklabels(["Precisión", "Recall\n(promedio micro)", "F-measure"])
    axes[1].set_ylim(0, 25)
    axes[1].set_yticks([0, 5, 10, 15, 20, 25])
    style_axis(axes[1])
    annotate_bars(
        axes[1],
        positive_bars,
        ["20,0%", "2,94%", "5,13%"],
        [1.0, 1.0, 1.0],
    )

    fig.text(
        0.5,
        0.03,
        "Barras de incertidumbre: únicamente medidas suministradas.",
        ha="center",
        va="bottom",
        fontsize=7.5,
        color="#444444",
    )
    save_figure(fig, output_dir, "metricas_arbol")


def pdf_number(value: float) -> str:
    return f"{value:.2f}"


def hex_to_rgb(color: str) -> tuple[float, float, float]:
    color = color.lstrip("#")
    return tuple(int(color[index : index + 2], 16) / 255 for index in (0, 2, 4))  # type: ignore[return-value]


def blend_hex(first: str, second: str, amount: float) -> str:
    first_rgb = hex_to_rgb(first)
    second_rgb = hex_to_rgb(second)
    rgb = [
        round((left + (right - left) * amount) * 255)
        for left, right in zip(first_rgb, second_rgb)
    ]
    return "#" + "".join(f"{channel:02X}" for channel in rgb)


def pdf_escape(text: str) -> bytes:
    encoded = text.encode("cp1252", errors="replace")
    return encoded.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")


class PdfCanvas:
    """Small PDF writer used when Matplotlib is not installed."""

    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height
        self.commands: list[bytes] = []

    def command(self, value: str) -> None:
        self.commands.append(value.encode("ascii") + b"\n")

    def fill_color(self, color: str) -> None:
        red, green, blue = hex_to_rgb(color)
        self.command(f"{red:.4f} {green:.4f} {blue:.4f} rg")

    def stroke_color(self, color: str) -> None:
        red, green, blue = hex_to_rgb(color)
        self.command(f"{red:.4f} {green:.4f} {blue:.4f} RG")

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: str = "#000000",
        width: float = 0.8,
    ) -> None:
        self.stroke_color(color)
        self.command(f"{pdf_number(width)} w {pdf_number(x1)} {pdf_number(y1)} m {pdf_number(x2)} {pdf_number(y2)} l S")

    def rect(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        fill: str | None = None,
        stroke: str | None = None,
        line_width: float = 0.8,
    ) -> None:
        if fill:
            self.fill_color(fill)
        if stroke:
            self.stroke_color(stroke)
            self.command(f"{pdf_number(line_width)} w")
        operator = "B" if fill and stroke else "f" if fill else "S"
        self.command(
            f"{pdf_number(x)} {pdf_number(y)} {pdf_number(width)} {pdf_number(height)} re {operator}"
        )

    def text(
        self,
        x: float,
        y: float,
        value: str,
        size: float = 9,
        *,
        align: str = "left",
        bold: bool = False,
        color: str = "#000000",
        angle: float = 0,
        leading: float | None = None,
    ) -> None:
        lines = value.splitlines() or [""]
        leading = leading or size * 1.15
        factor = 0.56 if bold else 0.52
        cosine = math.cos(math.radians(angle))
        sine = math.sin(math.radians(angle))
        self.fill_color(color)
        for line_index, line in enumerate(lines):
            line_width = len(line) * size * factor
            text_x = x - line_width / 2 if align == "center" else x
            if align == "right":
                text_x = x - line_width
            text_y = y - line_index * leading
            self.commands.append(
                (
                    f"BT /{'F2' if bold else 'F1'} {pdf_number(size)} Tf "
                    f"{cosine:.5f} {sine:.5f} {-sine:.5f} {cosine:.5f} "
                ).encode("ascii")
                + f"{pdf_number(text_x)} {pdf_number(text_y)} Tm (".encode("ascii")
                + pdf_escape(line)
                + b") Tj ET\n"
            )

    def save(self, path: Path) -> None:
        stream = b"".join(self.commands)
        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {pdf_number(self.width)} {pdf_number(self.height)}] "
                "/Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>"
            ).encode("ascii"),
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
            b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"endstream",
        ]

        document = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets: list[int] = []
        for object_number, content in enumerate(objects, start=1):
            offsets.append(len(document))
            document.extend(f"{object_number} 0 obj\n".encode("ascii"))
            document.extend(content)
            document.extend(b"\nendobj\n")

        xref_offset = len(document)
        document.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        document.extend(b"0000000000 65535 f \n")
        for offset in offsets:
            document.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
        document.extend(
            (
                f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
                f"startxref\n{xref_offset}\n%%EOF\n"
            ).encode("ascii")
        )
        path.write_bytes(document)


def locate_pdftoppm() -> str:
    candidates = [
        shutil.which("pdftoppm"),
        "/Users/leonel/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    raise RuntimeError(
        "The fallback renderer needs pdftoppm to create the 300 dpi PNG files."
    )


def render_png(pdf_path: Path, png_path: Path) -> None:
    executable = locate_pdftoppm()
    prefix = png_path.with_suffix("")
    subprocess.run(
        [
            executable,
            "-png",
            "-r",
            "300",
            "-singlefile",
            str(pdf_path),
            str(prefix),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def save_fallback_figure(canvas: PdfCanvas, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"{stem}.pdf"
    png_path = output_dir / f"{stem}.png"
    canvas.save(pdf_path)
    render_png(pdf_path, png_path)


def draw_fallback_grid(
    canvas: PdfCanvas,
    x: float,
    y: float,
    width: float,
    height: float,
    ticks: Sequence[float],
    maximum: float,
    *,
    tick_format: int = 0,
) -> None:
    for tick in ticks:
        tick_y = y + height * tick / maximum
        canvas.line(x, tick_y, x + width, tick_y, color="#D9D9D9", width=0.5)
        label = spanish_number(tick, tick_format)
        canvas.text(x - 6, tick_y - 2.5, label, size=7.5, align="right", color="#444444")
    canvas.line(x, y, x, y + height, color="#222222", width=0.8)
    canvas.line(x, y, x + width, y, color="#222222", width=0.8)


def make_fallback_class_distribution(counts: Counter[str], output_dir: Path) -> None:
    width, height = 418, 245
    canvas = PdfCanvas(width, height)
    canvas.text(width / 2, height - 25, "Distribución de clases", size=12, bold=True, align="center")
    x, y, chart_width, chart_height = 64, 48, 322, 150
    maximum = 3000
    draw_fallback_grid(canvas, x, y, chart_width, chart_height, [0, 600, 1200, 1800, 2400], maximum)
    canvas.text(17, y + chart_height / 2, "Cantidad de registros", size=8.5, angle=90, align="center")

    colors = [OKABE_ITO["blue"], OKABE_ITO["vermillion"]]
    values = [counts["0"], counts["1"]]
    percentages = [100 * value / sum(values) for value in values]
    for index, (value, percentage, color) in enumerate(zip(values, percentages, colors)):
        bar_x = x + 82 + index * 154
        bar_height = chart_height * value / maximum
        canvas.rect(bar_x, y, 66, bar_height, fill=color, stroke="#FFFFFF", line_width=0.8)
        canvas.text(
            bar_x + 33,
            y + bar_height + 8,
            f"n = {spanish_number(value, 0)}\n{spanish_percent(percentage)}",
            size=8.2,
            align="center",
        )
        canvas.text(
            bar_x + 33,
            y - 14,
            "0\nNo peligrosa" if index == 0 else "1\nPeligrosa",
            size=8.5,
            align="center",
        )
    save_fallback_figure(canvas, output_dir, "distribucion_clases")


def make_fallback_confusion_matrix(output_dir: Path) -> None:
    width, height = 388, 310
    canvas = PdfCanvas(width, height)
    canvas.text(width / 2, height - 25, "Matriz de confusión - árbol de decisión", size=11.5, bold=True, align="center")
    x, y, cell = 112, 82, 82
    maximum = max(max(row) for row in CONFUSION_MATRIX)
    dark = "#00204C"
    light = "#FDEB7B"
    for row_index, row in enumerate(CONFUSION_MATRIX):
        for column_index, value in enumerate(row):
            bottom = y + (1 - row_index) * cell
            fill = blend_hex(dark, light, 1 - value / maximum)
            canvas.rect(x + column_index * cell, bottom, cell, cell, fill=fill, stroke="#FFFFFF", line_width=1.2)
            canvas.text(
                x + column_index * cell + cell / 2,
                bottom + cell / 2 - 5,
                spanish_number(value, 0),
                size=13,
                bold=True,
                align="center",
                color="#FFFFFF" if value > maximum * 0.45 else OKABE_ITO["black"],
            )
    labels = ["0\nNo peligrosa", "1\nPeligrosa"]
    for index, label in enumerate(labels):
        canvas.text(x + index * cell + cell / 2, y - 13, label, size=8.2, align="center")
        canvas.text(x - 11, y + (1 - index) * cell + cell / 2 - 5, label, size=8.2, align="right")
    canvas.text(x + cell, 44, "Clase verdadera", size=9, align="center")
    canvas.text(30, y + cell, "Clase predicha", size=9, angle=90, align="center")
    canvas.text(x + 2 * cell + 30, y + cell, "Registros", size=8.2, angle=90, align="center", color="#444444")
    save_fallback_figure(canvas, output_dir, "matriz_confusion_arbol")


def draw_fallback_metric_axes(
    canvas: PdfCanvas,
    x: float,
    y: float,
    width: float,
    height: float,
    maximum: float,
    ticks: Sequence[float],
) -> None:
    draw_fallback_grid(canvas, x, y, width, height, ticks, maximum)
    canvas.text(
        x - 28,
        y + height / 2,
        "Porcentaje (%)",
        size=8.2,
        angle=90,
        align="center",
        color="#444444",
    )


def make_fallback_metrics(output_dir: Path) -> None:
    width, height = 533, 274
    canvas = PdfCanvas(width, height)
    canvas.text(width / 2, height - 23, "Métricas del árbol de decisión", size=11.5, bold=True, align="center")

    left = (50, 52, 211, 164)
    right = (302, 52, 194, 164)
    for panel, ticks, maximum in ((left, [0, 20, 40, 60, 80, 100], 105), (right, [0, 5, 10, 15, 20, 25], 25)):
        draw_fallback_metric_axes(canvas, *panel, ticks=ticks, maximum=maximum)

    canvas.text(left[0] + left[2] / 2, 225, "A. Rendimiento global", size=9.5, bold=True, align="center")
    canvas.text(right[0] + right[2] / 2, 225, "B. Clase positiva (1)", size=9.5, bold=True, align="center")

    global_values = [92.84, 86.0]
    global_errors = [0.27, 4.1]
    global_labels = ["92,84% ± 0,27 p.p.", "86,0% ± 4,1 p.p."]
    for index, (value, error, label, color) in enumerate(
        zip(global_values, global_errors, global_labels, [OKABE_ITO["blue"], OKABE_ITO["orange"]])
    ):
        bar_x = left[0] + 47 + index * 96
        bar_width = 42
        bar_height = left[3] * value / 105
        canvas.rect(bar_x, left[1], bar_width, bar_height, fill=color, stroke="#FFFFFF", line_width=0.8)
        error_y = left[1] + left[3] * (value + error) / 105
        low_y = left[1] + left[3] * (value - error) / 105
        canvas.line(bar_x + bar_width / 2, low_y, bar_x + bar_width / 2, error_y, color="#000000", width=1)
        canvas.line(bar_x + bar_width / 2 - 5, error_y, bar_x + bar_width / 2 + 5, error_y, color="#000000", width=1)
        canvas.line(bar_x + bar_width / 2 - 5, low_y, bar_x + bar_width / 2 + 5, low_y, color="#000000", width=1)
        canvas.text(bar_x + bar_width / 2, error_y + 9, label, size=7.2, align="center")
        canvas.text(bar_x + bar_width / 2, 39, "Exactitud" if index == 0 else "AUC\n(optimista)", size=7.8, align="center")

    positive_values = [20.0, 2.94, 5.13]
    positive_labels = ["20,0%", "2,94%", "5,13%"]
    positive_colors = [OKABE_ITO["green"], OKABE_ITO["vermillion"], OKABE_ITO["purple"]]
    positive_names = ["Precisión", "Recall\n(promedio micro)", "F-measure"]
    for index, (value, label, color, name) in enumerate(zip(positive_values, positive_labels, positive_colors, positive_names)):
        bar_x = right[0] + 21 + index * 60
        bar_width = 34
        bar_height = right[3] * value / 25
        canvas.rect(bar_x, right[1], bar_width, bar_height, fill=color, stroke="#FFFFFF", line_width=0.8)
        canvas.text(bar_x + bar_width / 2, right[1] + bar_height + 6, label, size=7.5, align="center")
        canvas.text(bar_x + bar_width / 2, 39, name, size=7.4, align="center")

    canvas.text(width / 2, 15, "Barras de incertidumbre: únicamente medidas suministradas.", size=7.2, align="center", color="#444444")
    save_fallback_figure(canvas, output_dir, "metricas_arbol")


def build_parser() -> argparse.ArgumentParser:
    repository_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=repository_root / "seismic-bumps.arff",
        help="Path to the Seismic-Bumps ARFF file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=repository_root / "output" / "figures",
        help="Directory in which PDF and PNG figures will be written.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    counts = parse_class_counts(args.dataset)
    if HAS_MATPLOTLIB:
        configure_publication_style()
        make_class_distribution_figure(counts, args.output_dir)
        make_confusion_matrix_figure(args.output_dir)
        make_metrics_figure(args.output_dir)
        backend = "matplotlib"
    else:
        make_fallback_class_distribution(counts, args.output_dir)
        make_fallback_confusion_matrix(args.output_dir)
        make_fallback_metrics(args.output_dir)
        backend = "standard library PDF + pdftoppm"

    print(
        f"Verified class counts: class 0 = {counts['0']}, "
        f"class 1 = {counts['1']}"
    )
    print(f"Rendering backend: {backend}")
    for stem in (
        "distribucion_clases",
        "matriz_confusion_arbol",
        "metricas_arbol",
    ):
        print(f"Generated {args.output_dir / (stem + '.pdf')}")
        print(f"Generated {args.output_dir / (stem + '.png')}")


if __name__ == "__main__":
    main()
