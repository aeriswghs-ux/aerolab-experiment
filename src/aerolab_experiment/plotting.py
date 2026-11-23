"""Optional noninteractive plots; matplotlib is an optional extra."""
from __future__ import annotations
from pathlib import Path
from .models import Result
from .stats import summarize


def make_plots(rows: list[Result], output_dir: Path, *, dataset_kind: str) -> list[Path]:
    if dataset_kind not in {"synthetic", "experimental"}:
        raise ValueError("dataset_kind must explicitly be synthetic or experimental")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("Plotting needs matplotlib. Install with: pip install -e '.[plot]'") from exc
    summary = summarize(rows)
    alphas = [s["alpha_deg"] for s in summary]
    cl = [s["cl_mean"] for s in summary]
    cd = [s["cd_mean"] for s in summary]
    paths: list[Path] = []
    for filename, x, y, xlabel, ylabel in [
        ("cl_vs_alpha.png", alphas, cl, "Angle of attack (deg)", "Mean CL"),
        ("cd_vs_alpha.png", alphas, cd, "Angle of attack (deg)", "Mean CD"),
        ("drag_polar.png", cd, cl, "Mean CD", "Mean CL"),
    ]:
        fig, ax = plt.subplots(figsize=(6.8, 4.5))
        ax.plot(x, y, marker="o", lw=1.5)
        ax.set(xlabel=xlabel, ylabel=ylabel, title="AeroLab: " + filename.replace("_", " ").replace(".png", ""))
        ax.grid(True, alpha=0.3)
        if dataset_kind == "synthetic":
            ax.text(.5, .5, "SYNTHETIC DATA — NOT VALIDATED",
                    transform=ax.transAxes, ha="center", va="center",
                    fontsize=12, alpha=.3, rotation=24, fontweight="bold")
        else:
            ax.text(.5, 1.02, "UNVERIFIED EXPERIMENTAL DATA",
                    transform=ax.transAxes, ha="center", va="bottom",
                    fontsize=9, alpha=.7)
        fig.tight_layout()
        path = output_dir / filename
        fig.savefig(path, dpi=170)
        plt.close(fig)
        paths.append(path)
    return paths
