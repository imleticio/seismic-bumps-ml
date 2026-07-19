"""Create a clean vector diagram of the logistic-regression CV workflow."""

from pathlib import Path
import shutil
import subprocess

try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
    import seaborn as sns

    sns.set_theme(style="white", context="paper", font_scale=1.05)
    COLORS = sns.color_palette("colorblind")
    HAS_MATPLOTLIB = True
except ImportError:
    COLORS = ["#0173B2", "#DE8F05", "#029E73", "#D55E00"]
    HAS_MATPLOTLIB = False


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "figures" / "logistic_regression_cross_validation_clean.pdf"


def create_with_tikz():
    """Fallback vector renderer for environments without Matplotlib."""
    build_dir = ROOT / "tmp" / "latex-logistic-figure"
    build_dir.mkdir(parents=True, exist_ok=True)
    source = build_dir / "logistic_regression_cross_validation_clean.tex"
    source.write_text(
        r"""\documentclass{article}
\usepackage[paperwidth=28cm,paperheight=10cm,margin=0cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{xcolor}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning,fit,backgrounds}
\pagestyle{empty}
\definecolor{cbBlue}{HTML}{0173B2}
\definecolor{cbOrange}{HTML}{DE8F05}
\definecolor{cbGreen}{HTML}{029E73}
\definecolor{ink}{HTML}{303840}
\definecolor{muted}{HTML}{5D6872}
\definecolor{trainBg}{HTML}{F4F7FA}
\definecolor{testBg}{HTML}{FAF8F3}
\definecolor{modelBg}{HTML}{E7F1F8}
\definecolor{applyBg}{HTML}{E8F3E8}
\definecolor{perfBg}{HTML}{FFF0D5}
\begin{document}
\noindent\begin{tikzpicture}[x=1cm,y=1cm,>=Latex,font=\sffamily,
  box/.style={draw=muted,rounded corners=2mm,very thick,minimum height=2.35cm,align=center},
  flow/.style={-Latex,very thick},
  port/.style={font=\bfseries\small}]
  \fill[trainBg,rounded corners=2mm] (0.45,0.7) rectangle (12.25,9.15);
  \draw[gray!45,rounded corners=2mm] (0.45,0.7) rectangle (12.25,9.15);
  \fill[testBg,rounded corners=2mm] (12.75,0.7) rectangle (27.55,9.15);
  \draw[gray!45,rounded corners=2mm] (12.75,0.7) rectangle (27.55,9.15);
  \node[anchor=west,font=\bfseries\Large,text=ink] at (0.9,8.55) {Training};
  \node[anchor=west,font=\bfseries\Large,text=ink] at (13.2,8.55) {Testing};

  \node[box,fill=modelBg,minimum width=6.0cm] (glm) at (6.55,5.05)
    {\bfseries\large Generalized Linear Model\\[2mm]\small Binomial family $\cdot$ logit link};
  \draw[flow,cbBlue] (1.15,5.05) -- node[port,above,text=cbBlue] {tra} (glm.west);
  \draw[flow,cbGreen] (glm.east) -- node[port,above,text=cbGreen] {mod} (11.7,5.05);
  \node[font=\small,text=muted,align=center] at (12.5,6.65) {Model learned\\in each fold};

  \node[box,fill=applyBg,minimum width=4.1cm] (apply) at (18.0,5.05)
    {\bfseries\large Apply Model\\[2mm]\small Prediction};
  \node[box,fill=perfBg,minimum width=3.6cm] (perf) at (23.8,5.05)
    {\bfseries\large Performance\\[2mm]\small Evaluation};
  \draw[flow,cbGreen] (13.45,5.75) -- node[port,above,text=cbGreen] {mod} (apply.west |- 0,5.75);
  \draw[flow,cbBlue] (13.45,4.35) -- node[port,below,text=cbBlue] {tes} (apply.west |- 0,4.35);
  \draw[flow,cbBlue] (apply.east) -- node[port,above,text=cbBlue] {labeled examples} (perf.west);
  \draw[flow,cbOrange] (perf.east) -- node[port,above,text=cbOrange] {per} (27.1,5.05);
\end{tikzpicture}
\end{document}
""",
        encoding="utf-8",
    )
    pdflatex = Path("/Library/TeX/texbin/pdflatex")
    subprocess.run(
        [str(pdflatex), "-interaction=nonstopmode", "-halt-on-error", "-output-directory", str(build_dir), str(source)],
        check=True,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    shutil.copy2(build_dir / OUTPUT.name, OUTPUT)


def add_box(ax, xy, width, height, title, subtitle, facecolor, edgecolor="#3F4A54"):
    x, y = xy
    box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        linewidth=1.25,
        edgecolor=edgecolor,
        facecolor=facecolor,
        zorder=3,
    )
    ax.add_patch(box)
    ax.text(x + width / 2, y + height * 0.63, title, ha="center", va="center", weight="bold", fontsize=10.2)
    ax.text(x + width / 2, y + height * 0.32, subtitle, ha="center", va="center", fontsize=8.6, color="#3F4A54")
    return box


def add_arrow(ax, start, end, color, label=None, label_offset=(0, 0.035)):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=12,
        linewidth=1.5,
        color=color,
        connectionstyle="arc3,rad=0",
        zorder=2,
    )
    ax.add_patch(arrow)
    if label:
        mx = (start[0] + end[0]) / 2 + label_offset[0]
        my = (start[1] + end[1]) / 2 + label_offset[1]
        ax.text(mx, my, label, ha="center", va="bottom", fontsize=8.6, weight="bold", color=color)


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    if not HAS_MATPLOTLIB:
        create_with_tikz()
        print(OUTPUT)
        return

    blue, orange, green = COLORS[0], COLORS[1], COLORS[2]
    fig, ax = plt.subplots(figsize=(11.2, 4.1))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Panel backgrounds and separator.
    ax.add_patch(FancyBboxPatch((0.015, 0.08), 0.435, 0.82, boxstyle="round,pad=0.012", facecolor="#F4F7FA", edgecolor="#C8D0D8", linewidth=1.0))
    ax.add_patch(FancyBboxPatch((0.475, 0.08), 0.51, 0.82, boxstyle="round,pad=0.012", facecolor="#FAF8F3", edgecolor="#C8D0D8", linewidth=1.0))
    ax.text(0.035, 0.845, "Training", fontsize=13, weight="bold", color="#303840")
    ax.text(0.495, 0.845, "Testing", fontsize=13, weight="bold", color="#303840")

    # Training workflow.
    model_x, model_y, model_w, model_h = 0.17, 0.37, 0.225, 0.27
    add_box(
        ax,
        (model_x, model_y),
        model_w,
        model_h,
        "Generalized Linear Model",
        "Binomial family · logit link",
        "#E7F1F8",
    )
    add_arrow(ax, (0.045, 0.505), (model_x, 0.505), blue, "tra")
    add_arrow(ax, (model_x + model_w, 0.505), (0.455, 0.505), green, "mod")

    # Testing workflow.
    apply_x, apply_y, apply_w, apply_h = 0.59, 0.42, 0.17, 0.22
    perf_x, perf_y, perf_w, perf_h = 0.80, 0.42, 0.14, 0.22
    add_box(ax, (apply_x, apply_y), apply_w, apply_h, "Apply Model", "Prediction", "#E8F3E8")
    add_box(ax, (perf_x, perf_y), perf_w, perf_h, "Performance", "Evaluation", "#FFF0D5")

    # Model and test-set inputs remain visually distinct and fully inside the page.
    add_arrow(ax, (0.49, 0.56), (apply_x, 0.56), green, "mod", (0, 0.025))
    add_arrow(ax, (0.49, 0.47), (apply_x, 0.47), blue, "tes", (0, -0.055))
    add_arrow(ax, (apply_x + apply_w, 0.53), (perf_x, 0.53), blue, "labeled examples", (0, 0.025))
    add_arrow(ax, (perf_x + perf_w, 0.53), (0.975, 0.53), orange, "per", (0, 0.025))

    # Clarify that the model output from training feeds the testing subprocess.
    ax.text(0.472, 0.69, "Model learned in each fold", ha="center", va="center", fontsize=8.2, color="#5D6872")

    fig.savefig(OUTPUT, format="pdf", bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    main()
