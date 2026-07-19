#!/usr/bin/env python3
"""Generate an independent publication-ready figure proposal.

The script validates the supplied ARFF file, uses the confirmed evaluation
summary, and writes only to the candidate directory. It does not import or
modify the canonical figure generator or the existing ``output/figures``.

Requirements: Python 3.10+ and the ``pdftoppm`` executable available in the
Codex runtime or on ``PATH``. The plots are written as vector PDFs and as
300-dpi PNG renderings without third-party Python packages.
"""

from __future__ import annotations

import argparse
import csv
import math
import shutil
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


# Okabe–Ito palette, with redundant hatching and marker shapes for grayscale.
COLORS = {
    "blue": "#0072B2",
    "sky": "#56B4E9",
    "green": "#009E73",
    "orange": "#E69F00",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
    "black": "#1A1A1A",
    "gray": "#5A5A5A",
    "grid": "#D2D6D9",
    "paper": "#FFFFFF",
}

EXPECTED_CLASS_COUNTS = Counter({"0": 2414, "1": 170})
EXPECTED_RECORDS = 2584
EXPECTED_MISSING = 0

# Rows are predictions; columns are true classes.
CONFUSION_MATRIX = ((2394, 165), (20, 5))


@dataclass(frozen=True)
class DatasetSummary:
    records: int
    class_counts: Counter[str]
    rows_with_missing: int


@dataclass(frozen=True)
class Metric:
    label: str
    value: float
    uncertainty: float | None
    value_text: str
    uncertainty_text: str | None = None


GLOBAL_METRICS = (
    Metric("Exactitud\n(CV 10-fold)", 92.84, 0.27, "92,84 %", "0,27 p.p."),
    Metric("AUC optimista", 86.0, 4.1, "86,0 %", "4,1 p.p."),
)

POSITIVE_METRICS = (
    Metric("Precisión", 20.0, None, "20,00 %"),
    Metric("Recall\n(promedio micro)", 2.94, None, "2,94 %"),
    Metric("F-measure", 5.13, None, "5,13 %"),
)


def format_number(value: float, decimals: int = 0) -> str:
    """Format a number with Spanish decimal and thousands separators."""

    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def parse_arff(dataset_path: Path) -> DatasetSummary:
    """Parse class labels and missing-value status from ARFF data rows."""

    in_data = False
    records = 0
    missing_rows = 0
    class_counts: Counter[str] = Counter()

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
            if len(fields) != 19:
                raise ValueError(
                    f"Expected 19 fields in ARFF row, found {len(fields)}: {line!r}"
                )

            records += 1
            if any(field.strip() in {"", "?"} for field in fields):
                missing_rows += 1

            label = fields[-1].strip().strip("'\"")
            if label not in {"0", "1"}:
                raise ValueError(f"Unexpected class label {label!r}")
            class_counts[label] += 1

    return DatasetSummary(records, class_counts, missing_rows)


def validate_inputs(summary: DatasetSummary) -> None:
    """Fail fast if the dataset or confirmed evaluation table has drifted."""

    if summary.records != EXPECTED_RECORDS:
        raise ValueError(
            f"Expected {EXPECTED_RECORDS} records, found {summary.records}"
        )
    if summary.class_counts != EXPECTED_CLASS_COUNTS:
        raise ValueError(
            f"Expected class counts {dict(EXPECTED_CLASS_COUNTS)}, "
            f"found {dict(summary.class_counts)}"
        )
    if summary.rows_with_missing != EXPECTED_MISSING:
        raise ValueError(
            f"Expected {EXPECTED_MISSING} rows with missing values, "
            f"found {summary.rows_with_missing}"
        )

    matrix_total = sum(sum(row) for row in CONFUSION_MATRIX)
    if matrix_total != summary.records:
        raise ValueError(
            f"Confusion matrix total {matrix_total} does not match "
            f"dataset total {summary.records}"
        )

    true_class_0 = CONFUSION_MATRIX[0][0] + CONFUSION_MATRIX[1][0]
    true_class_1 = CONFUSION_MATRIX[0][1] + CONFUSION_MATRIX[1][1]
    if true_class_0 != summary.class_counts["0"]:
        raise ValueError("Confusion matrix class-0 total does not match ARFF")
    if true_class_1 != summary.class_counts["1"]:
        raise ValueError("Confusion matrix class-1 total does not match ARFF")

    # These are consistency checks only; no additional metric is plotted.
    tn, fn = CONFUSION_MATRIX[0]
    fp, tp = CONFUSION_MATRIX[1]
    derived = {
        "accuracy": 100 * (tn + tp) / matrix_total,
        "precision": 100 * tp / (tp + fp),
        "recall_micro": 100 * tp / (tp + fn),
        "f_measure": 100 * (2 * tp) / (2 * tp + fp + fn),
    }
    supplied = {
        "accuracy": 92.84,
        "precision": 20.00,
        "recall_micro": 2.94,
        "f_measure": 5.13,
    }
    for key, expected in supplied.items():
        if not math.isclose(derived[key], expected, abs_tol=0.011):
            raise ValueError(
                f"Confirmed metric {key}={expected} does not agree with "
                f"the confusion matrix ({derived[key]:.4f})"
            )


def hex_rgb(color: str) -> tuple[float, float, float]:
    color = color.lstrip("#")
    return tuple(int(color[index : index + 2], 16) / 255 for index in (0, 2, 4))  # type: ignore[return-value]


def lighten(color: str, amount: float = 0.78) -> str:
    """Blend a palette color with white for readable cell annotations."""

    color = color.lstrip("#")
    channels = [int(color[i : i + 2], 16) for i in (0, 2, 4)]
    blended = [round(channel + (255 - channel) * amount) for channel in channels]
    return "#" + "".join(f"{channel:02X}" for channel in blended)


def pdf_number(value: float) -> str:
    return f"{value:.2f}"


def pdf_escape(value: str) -> bytes:
    encoded = value.encode("cp1252", errors="replace")
    return encoded.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(
        b")", b"\\)"
    )


class PdfCanvas:
    """Small dependency-free PDF canvas for vector scientific line art."""

    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height
        self.commands: list[bytes] = []

    def command(self, value: str) -> None:
        self.commands.append(value.encode("ascii") + b"\n")

    def fill_color(self, color: str) -> None:
        red, green, blue = hex_rgb(color)
        self.command(f"{red:.4f} {green:.4f} {blue:.4f} rg")

    def stroke_color(self, color: str) -> None:
        red, green, blue = hex_rgb(color)
        self.command(f"{red:.4f} {green:.4f} {blue:.4f} RG")

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: str = "#000000",
        width: float = 0.7,
    ) -> None:
        self.stroke_color(color)
        self.command(
            f"{pdf_number(width)} w {pdf_number(x1)} {pdf_number(y1)} m "
            f"{pdf_number(x2)} {pdf_number(y2)} l S"
        )

    def rect(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        fill: str | None = None,
        stroke: str | None = None,
        line_width: float = 0.7,
    ) -> None:
        if fill:
            self.fill_color(fill)
        if stroke:
            self.stroke_color(stroke)
            self.command(f"{pdf_number(line_width)} w")
        operator = "B" if fill and stroke else "f" if fill else "S"
        self.command(
            f"{pdf_number(x)} {pdf_number(y)} {pdf_number(width)} "
            f"{pdf_number(height)} re {operator}"
        )

    def polygon(
        self,
        points: list[tuple[float, float]],
        fill: str,
        stroke: str = "#000000",
        line_width: float = 0.5,
    ) -> None:
        self.fill_color(fill)
        self.stroke_color(stroke)
        self.command(f"{pdf_number(line_width)} w")
        first_x, first_y = points[0]
        self.command(f"{pdf_number(first_x)} {pdf_number(first_y)} m")
        for x, y in points[1:]:
            self.command(f"{pdf_number(x)} {pdf_number(y)} l")
        self.command("h B")

    def circle(
        self,
        x: float,
        y: float,
        radius: float,
        fill: str,
        stroke: str = "#000000",
        line_width: float = 0.5,
    ) -> None:
        k = 0.5522848 * radius
        self.fill_color(fill)
        self.stroke_color(stroke)
        self.command(f"{pdf_number(line_width)} w")
        self.command(f"{pdf_number(x + radius)} {pdf_number(y)} m")
        self.command(
            f"{pdf_number(x + radius)} {pdf_number(y + k)} "
            f"{pdf_number(x + k)} {pdf_number(y + radius)} "
            f"{pdf_number(x)} {pdf_number(y + radius)} c"
        )
        self.command(
            f"{pdf_number(x - k)} {pdf_number(y + radius)} "
            f"{pdf_number(x - radius)} {pdf_number(y + k)} "
            f"{pdf_number(x - radius)} {pdf_number(y)} c"
        )
        self.command(
            f"{pdf_number(x - radius)} {pdf_number(y - k)} "
            f"{pdf_number(x - k)} {pdf_number(y - radius)} "
            f"{pdf_number(x)} {pdf_number(y - radius)} c"
        )
        self.command(
            f"{pdf_number(x + k)} {pdf_number(y - radius)} "
            f"{pdf_number(x + radius)} {pdf_number(y - k)} "
            f"{pdf_number(x + radius)} {pdf_number(y)} c B"
        )

    def text(
        self,
        x: float,
        y: float,
        value: str,
        size: float = 8,
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
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {pdf_number(self.width)} "
                f"{pdf_number(self.height)}] /Resources << /Font << /F1 4 0 R "
                "/F2 5 0 R >> >> /Contents 6 0 R >>"
            ).encode("ascii"),
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"endstream",
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


def hatch_rect(
    canvas: PdfCanvas,
    x: float,
    y: float,
    width: float,
    height: float,
    direction: str = "/",
) -> None:
    """Draw clipped diagonal hatching inside a rectangle."""

    canvas.command("q")
    canvas.command(
        f"{pdf_number(x)} {pdf_number(y)} {pdf_number(width)} "
        f"{pdf_number(height)} re W n"
    )
    canvas.stroke_color(COLORS["gray"])
    canvas.command("0.55 w")
    step = 7.0
    if direction == "/":
        for offset in range(-int(height), int(width) + int(height), int(step)):
            canvas.command(
                f"{pdf_number(x - height + offset)} {pdf_number(y)} m "
                f"{pdf_number(x + offset)} {pdf_number(y + height)} l S"
            )
    else:
        for offset in range(0, int(width + height), int(step)):
            canvas.command(
                f"{pdf_number(x + offset)} {pdf_number(y)} m "
                f"{pdf_number(x + offset - height)} {pdf_number(y + height)} l S"
            )
    canvas.command("Q")


def locate_pdftoppm() -> str:
    candidates = [
        shutil.which("pdftoppm"),
        "/Users/leonel/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    raise RuntimeError("pdftoppm is required to create the 300-dpi PNG files")


def render_png(pdf_path: Path, png_path: Path) -> None:
    executable = locate_pdftoppm()
    subprocess.run(
        [
            executable,
            "-png",
            "-r",
            "300",
            "-singlefile",
            str(pdf_path),
            str(png_path.with_suffix("")),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def save_figure(canvas: PdfCanvas, output_dir: Path, stem: str) -> None:
    """Save a vector PDF and a 300-dpi PNG with the same composition."""

    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"{stem}.pdf"
    png_path = output_dir / f"{stem}.png"
    canvas.save(pdf_path)
    render_png(pdf_path, png_path)
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        raise RuntimeError(f"PDF export failed: {pdf_path}")
    if not png_path.exists() or png_path.stat().st_size == 0:
        raise RuntimeError(f"PNG export failed: {png_path}")


def draw_x_grid(
    canvas: PdfCanvas,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    ticks: list[float],
    maximum: float,
    label_y: float,
) -> None:
    for tick in ticks:
        x = x0 + (x1 - x0) * tick / maximum
        canvas.line(x, y0, x, y1, color=COLORS["grid"], width=0.45)
        canvas.text(x, label_y, format_number(tick), size=7, align="center", color=COLORS["gray"])
    canvas.line(x0, y0, x1, y0, color=COLORS["black"], width=0.75)


def draw_marker(canvas: PdfCanvas, x: float, y: float, marker: str, color: str) -> None:
    if marker == "o":
        canvas.circle(x, y, 3.6, color, COLORS["black"], 0.55)
    elif marker == "s":
        canvas.rect(x - 3.6, y - 3.6, 7.2, 7.2, fill=color, stroke=COLORS["black"], line_width=0.55)
    elif marker == "D":
        canvas.polygon([(x, y + 4.2), (x + 4.2, y), (x, y - 4.2), (x - 4.2, y)], color, COLORS["black"], 0.55)
    else:
        canvas.polygon([(x, y + 4.4), (x + 4.4, y - 3.6), (x - 4.4, y - 3.6)], color, COLORS["black"], 0.55)


def make_dataset_and_confusion_figure(summary: DatasetSummary, output_dir: Path) -> None:
    """Create a two-panel view of class imbalance and classification outcomes."""

    width, height = 522, 241
    canvas = PdfCanvas(width, height)

    # Panel A: horizontal bars keep the minority class visible on the raw scale.
    panel_x = 45
    plot_x0, plot_x1 = 103, 276
    plot_y0, plot_y1 = 78, 169
    canvas.text(panel_x, 220, "A. Composición de clases", size=10.5, bold=True)
    canvas.text((plot_x0 + plot_x1) / 2, 39, "Registros", size=8.5, align="center")
    draw_x_grid(canvas, plot_x0, plot_x1, plot_y0, plot_y1, [0, 600, 1200, 1800, 2400], 2900, 64)

    values = [summary.class_counts["0"], summary.class_counts["1"]]
    labels = ["0\nNo peligrosa", "1\nPeligrosa"]
    colors = [COLORS["blue"], COLORS["vermillion"]]
    centers = [145, 101]
    total = summary.records
    for value, label, color, center, direction in zip(
        values, labels, colors, centers, ["", "/"]
    ):
        bar_width = (plot_x1 - plot_x0) * value / 2900
        bar_y = center - 8.5
        canvas.rect(plot_x0, bar_y, bar_width, 17, fill=color, stroke=COLORS["paper"], line_width=0.8)
        if direction:
            hatch_rect(canvas, plot_x0, bar_y, bar_width, 17, direction)
            canvas.rect(plot_x0, bar_y, bar_width, 17, stroke=COLORS["paper"], line_width=0.8)
        canvas.text(plot_x0 - 6, center + 4, label, size=7.4, align="right", leading=8.1)
        percentage = 100 * value / total
        canvas.text(
            plot_x0 + bar_width + 6,
            center + 2.5,
            f"n = {format_number(value)} · {format_number(percentage, 2)} %",
            size=7.4,
            color=COLORS["black"],
        )

    # Panel B: categorical fills plus hatching avoid relying on color alone.
    matrix_x0, cell = 344, 54
    matrix_y0 = 84
    canvas.text(312, 220, "B. Matriz de confusión", size=10.5, bold=True)
    fills = (
        (lighten(COLORS["blue"]), lighten(COLORS["orange"])),
        (lighten(COLORS["vermillion"]), lighten(COLORS["green"])),
    )
    roles = (("TN", "FN"), ("FP", "TP"))
    hatches = ((None, "/"), ("\\", None))
    for row_index, row in enumerate(CONFUSION_MATRIX):
        for column_index, value in enumerate(row):
            x = matrix_x0 + column_index * cell
            y = matrix_y0 + (1 - row_index) * cell
            canvas.rect(x, y, cell, cell, fill=fills[row_index][column_index])
            if hatches[row_index][column_index]:
                hatch_rect(canvas, x, y, cell, cell, hatches[row_index][column_index])
            canvas.rect(x, y, cell, cell, stroke=COLORS["paper"], line_width=1.3)
            canvas.text(x + cell / 2, y + 34, roles[row_index][column_index], size=7.2, bold=True, align="center", color=COLORS["gray"])
            canvas.text(x + cell / 2, y + 16, format_number(value), size=12.5, bold=True, align="center")

    class_labels = ["0\nNo peligrosa", "1\nPeligrosa"]
    for column_index, label in enumerate(class_labels):
        canvas.text(matrix_x0 + cell * column_index + cell / 2, 68, label, size=7.3, align="center", leading=8.0)
    for row_index, label in enumerate(class_labels):
        canvas.text(matrix_x0 - 7, matrix_y0 + (1 - row_index) * cell + cell / 2 + 4, label, size=7.2, align="right", leading=8.0)
    canvas.text(matrix_x0 + cell, 35, "Clase verdadera", size=8.2, align="center")
    canvas.text(299, matrix_y0 + cell, "Clase predicha", size=8.2, align="center", angle=90)

    # Compact legend, separated from the axis labels.
    canvas.rect(332, 49, 8, 8, fill=lighten(COLORS["blue"]), stroke=COLORS["gray"], line_width=0.45)
    canvas.text(344, 51, "Acierto", size=6.7)
    canvas.rect(389, 49, 8, 8, fill=lighten(COLORS["orange"]), stroke=COLORS["gray"], line_width=0.45)
    hatch_rect(canvas, 389, 49, 8, 8, "/")
    canvas.text(401, 51, "Error", size=6.7)

    save_figure(canvas, output_dir, "01_datos_y_confusion")


def make_metrics_figure(output_dir: Path) -> None:
    """Create a two-panel metric profile without adding unreported results."""

    width, height = 522, 238
    canvas = PdfCanvas(width, height)

    # Panel A: supplied uncertainties are shown as horizontal error bars.
    canvas.text(45, 217, "A. Rendimiento global", size=10.5, bold=True)
    global_x0, global_x1 = 145, 294
    global_y0, global_y1 = 91, 169
    draw_x_grid(canvas, global_x0, global_x1, global_y0, global_y1, [0, 20, 40, 60, 80, 100], 104, 76)
    global_centers = [147, 108]
    global_colors = [COLORS["blue"], COLORS["orange"]]
    global_markers = ["o", "D"]
    for metric, center, color, marker in zip(GLOBAL_METRICS, global_centers, global_colors, global_markers):
        x = global_x0 + (global_x1 - global_x0) * metric.value / 104
        error = metric.uncertainty or 0
        error_px = (global_x1 - global_x0) * error / 104
        canvas.line(global_x0, center, x, center, color=color, width=2.8)
        canvas.line(x - error_px, center, x + error_px, center, color=COLORS["black"], width=0.85)
        canvas.line(x - error_px, center - 3.2, x - error_px, center + 3.2, color=COLORS["black"], width=0.85)
        canvas.line(x + error_px, center - 3.2, x + error_px, center + 3.2, color=COLORS["black"], width=0.85)
        draw_marker(canvas, x, center, marker, color)
        canvas.text(132, center + 4, metric.label, size=7.3, align="right", leading=8.0)
        canvas.text(294, center + 7, f"{metric.value_text} ± {metric.uncertainty_text}", size=7.2, align="right")
    canvas.text((global_x0 + global_x1) / 2, 50, "Porcentaje (%)", size=8.5, align="center")

    # Panel B: lollipop profile keeps small positive-class values visible.
    canvas.text(323, 217, "B. Clase positiva (1)", size=10.5, bold=True)
    positive_x0, positive_x1 = 399, 497
    positive_y0, positive_y1 = 83, 169
    draw_x_grid(canvas, positive_x0, positive_x1, positive_y0, positive_y1, [0, 5, 10, 15, 20, 25], 25.8, 68)
    positive_centers = [155, 126, 97]
    positive_colors = [COLORS["green"], COLORS["vermillion"], COLORS["purple"]]
    positive_markers = ["o", "s", "^"]
    for metric, center, color, marker in zip(POSITIVE_METRICS, positive_centers, positive_colors, positive_markers):
        x = positive_x0 + (positive_x1 - positive_x0) * metric.value / 25.8
        canvas.line(positive_x0, center, x, center, color=color, width=2.8)
        draw_marker(canvas, x, center, marker, color)
        canvas.text(389, center + 4, metric.label, size=7.3, align="right", leading=8.0)
        canvas.text(x + 6, center + 3.5, metric.value_text, size=7.2)
    canvas.text((positive_x0 + positive_x1) / 2, 47, "Porcentaje (%)", size=8.5, align="center")

    canvas.text(
        width / 2,
        26,
        "Barras de error: solo incertidumbres suministradas. Recall micro: 2,94 %; encabezado: 3,05 % ± 4,36 %.",
        size=6.3,
        color=COLORS["gray"],
        align="center",
    )
    save_figure(canvas, output_dir, "02_metricas_arbol")


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=repo_root / "seismic-bumps.arff",
        help="Path to the ARFF dataset (default: repository seismic-bumps.arff)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Candidate output directory (default: this script's directory)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset_path = args.dataset.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    repo_root = Path(__file__).resolve().parents[3]
    canonical_dir = (repo_root / "output" / "figures").resolve()

    if output_dir == canonical_dir:
        raise SystemExit(
            "Refusing to write to output/figures; use the candidate directory."
        )
    if not dataset_path.exists():
        raise FileNotFoundError(dataset_path)

    summary = parse_arff(dataset_path)
    validate_inputs(summary)
    make_dataset_and_confusion_figure(summary, output_dir)
    make_metrics_figure(output_dir)

    print(f"Validated {summary.records} records from {dataset_path}")
    print(f"Wrote PDF and PNG figures to {output_dir}")


if __name__ == "__main__":
    main()
