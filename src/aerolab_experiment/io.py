"""Strict CSV/JSON I/O and traceable output generation."""
from __future__ import annotations
import csv
import hashlib
import json
from dataclasses import asdict, fields
from pathlib import Path
from typing import Sequence

from .models import Config, Measurement, Result
from .stats import summarize
from . import __version__


def read_config(path: Path) -> Config:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"cannot read config {path}: {exc}") from exc
    if not isinstance(doc, dict):
        raise ValueError("config must be a JSON object")
    return Config.from_mapping(doc)


def read_measurements(path: Path) -> list[Measurement]:
    required = {f.name for f in fields(Measurement)}
    try:
        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames or set(reader.fieldnames) != required:
                raise ValueError(
                    f"CSV columns must be exactly {sorted(required)}; received {reader.fieldnames}"
                )
            results: list[Measurement] = []
            ids: set[str] = set()
            for lineno, row in enumerate(reader, start=2):
                try:
                    run_id = row["run_id"].strip()
                    m = Measurement(
                        run_id=run_id,
                        **{key: float(row[key]) for key in required - {"run_id"}}
                    )
                    if run_id in ids:
                        raise ValueError(f"duplicate run_id={run_id!r}")
                except (ValueError, TypeError, KeyError, AttributeError) as exc:
                    raise ValueError(f"CSV line {lineno}: {exc}") from exc
                ids.add(run_id)
                results.append(m)
    except OSError as exc:
        raise ValueError(f"cannot read CSV {path}: {exc}") from exc
    if not results:
        raise ValueError("input CSV must have at least one measurement row")
    return results


def _write_rows(path: Path, rows: Sequence[dict], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_results(
    output_dir: Path, input_csv: Path, input_config: Path,
    cfg: Config, results: list[Result]
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    analyzed = [asdict(r) for r in results]
    cols = [f.name for f in fields(Result)]
    _write_rows(output_dir / "analyzed.csv", analyzed, cols)
    summary = summarize(results)
    summary_cols = list(summary[0])
    _write_rows(output_dir / "polar_summary.csv", summary, summary_cols)

    manifest = {
        "software": "aerolab-experiment", "software_version": __version__,
        "data_kind": cfg.dataset_kind,
        "input_csv_sha256": _sha256(input_csv),
        "config_sha256": _sha256(input_config),
        "input_rows": len(results),
        "angle_groups": len(summary),
        "reference_area_m2": cfg.geometry.reference_area_m2,
        "uncertainty_convention": "independent standard uncertainties (k=1); shared offsets NOT averaged down",
        "assumptions": [
            "dry ideal air", "incompressible low-speed pitot-static relation",
            "rectangular planform reference area", "forces aligned with wind axes",
            "no wall, support, humidity, flow angularity, or dynamic correction",
        ],
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write_report(output_dir / "report.md", manifest, results, summary)
    return manifest


def _write_report(path: Path, manifest: dict, results: list[Result], summary: list[dict]):
    max_re = max(r.reynolds for r in results)
    min_re = min(r.reynolds for r in results)
    n_one = sum(s["n"] == 1 for s in summary)
    warnings = []
    if n_one:
        warnings.append(f"{n_one} angle groups have only one observation; sample standard deviation is undefined.")
    if any(r.drag_net_N < 0 for r in results):
        warnings.append("Negative net drag present; check signs and tare calibration before interpretation.")
    if any(r.u_cd >= abs(r.cd) for r in results):
        warnings.append("Some drag measurements have standard uncertainty as large as measured |Cd|.")
    if not warnings:
        warnings.append("No basic QC warnings; this is NOT experimental validation.")
    lines = [
        "# AeroLab Experiment Analysis", "",
        f"**Data type:** {manifest['data_kind'].upper()} — "
        + ("DEMONSTRATION ONLY; not real measurements." if manifest['data_kind'] == 'synthetic' else "User-labeled experimental; not independently verified."),
        f"**Rows:** {len(results)} | **Angle groups:** {len(summary)}",
        f"**Reference area:** {manifest['reference_area_m2']:.6g} m²",
        f"**Reynolds range:** {min_re:.4g}–{max_re:.4g}",
        "", "## Quality checks", "",
    ]
    lines.extend(f"- {x}" for x in warnings)
    lines += [
        "", "## Measurement model", "",
        "- Raw force values are **calibrated to newtons, but not yet tare-corrected**.",
        "- Lift/drag are in **wind axes**; convert balance axes upstream if necessary.",
        "- q = dp_raw − dp_tare, using pitot total-minus-static pressure in Pa.",
        "- Reference area = chord × span (rectangular specimen, m²).",
        "- CL = (L_raw − L_tare)/(q A); CD = (D_raw − D_tare)/(q A).",
        "- rho = p/(R T), dry ideal air; mu(T) from Sutherland's law.",
        "- U = sqrt(2q/rho); Re = rho U chord / mu.",
        "- u(CL), u(CD), u(U), u(Re) use first-order independent-input uncertainty propagation (k=1).",
        "- Repeated-angle sample standard deviations and SEM measure scatter **only**; they do not remove shared systematic uncertainties.",
        "", "## Important limitations", "",
        "- No actual sensor calibration, calibration certificate, or uncertainty budget has been independently verified.",
        "- No test-section velocity uniformity, turbulence intensity, pitot alignment, wall blockage, support interference, airfoil deformation, hysteresis, or force-frame rotation correction.",
        "- Zero and sign conventions must be validated by the experimenter.",
        "- These are **3D finite-span model coefficients**, not automatically comparable to 2D airfoil polars.",
        "- No proof of agreement with CFD, XFOIL, or literature is implied.",
        "", "## Provenance", "",
        f"- Input CSV SHA-256: `{manifest['input_csv_sha256']}`",
        f"- Configuration SHA-256: `{manifest['config_sha256']}`",
        f"- AeroLab version: {manifest['software_version']}", "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
