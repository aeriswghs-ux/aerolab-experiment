import csv
import json
from pathlib import Path
import subprocess
import sys

import pytest
from aerolab_experiment.io import read_config, read_measurements, write_results
from aerolab_experiment.physics import analyze_measurement
from aerolab_experiment.stats import summarize

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "examples" / "config.synthetic.json"
CSV = ROOT / "examples" / "naca0018_SYNTHETIC.csv"


def test_example_csv_has_three_independent_runs_per_angle():
    rows = read_measurements(CSV)
    assert len(rows) == 27
    cfg = read_config(CFG)
    results = [analyze_measurement(r, cfg) for r in rows]
    groups = summarize(results)
    assert len(groups) == 9
    assert all(g["n"] == 3 for g in groups)
    assert all(g["cl_std_sample"] != "" for g in groups)


def test_singleton_group_does_not_fake_std_as_zero():
    cfg = read_config(CFG)
    r = analyze_measurement(read_measurements(CSV)[0], cfg)
    item = summarize([r])[0]
    assert item["n"] == 1
    assert item["cl_std_sample"] == item["cd_sem"] == ""


def test_error_on_missing_columns(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("run_id,alpha_deg,lift_N\na,0,0\n")
    with pytest.raises(ValueError, match="columns"):
        read_measurements(p)


def test_error_on_duplicate_run_ids(tmp_path):
    rows = CSV.read_text(encoding="utf-8").splitlines()
    p = tmp_path / "dupe.csv"
    p.write_text("\n".join([rows[0], rows[1], rows[1]]) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        read_measurements(p)


def test_error_on_nonfinite_measurement(tmp_path):
    rows = CSV.read_text(encoding="utf-8").splitlines()
    vals = rows[1].split(",")
    vals[2] = "NaN"
    p = tmp_path / "nan.csv"
    p.write_text("\n".join([rows[0], ",".join(vals)]) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="finite"):
        read_measurements(p)


def test_config_requires_explicit_uncertainty(tmp_path):
    doc = json.loads(CFG.read_text())
    del doc["uncertainty"]["drag_N"]
    p = tmp_path / "missing_uncertainty.json"
    p.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="config schema"):
        read_config(p)


def test_manifest_hash_and_data_label(tmp_path):
    cfg = read_config(CFG)
    result = [analyze_measurement(m, cfg) for m in read_measurements(CSV)]
    manifest = write_results(tmp_path, CSV, CFG, cfg, result)
    assert manifest["data_kind"] == "synthetic"
    assert len(manifest["input_csv_sha256"]) == 64
    assert "SYNTHETIC" in (tmp_path / "report.md").read_text()
    assert "std_sample" in (tmp_path / "polar_summary.csv").read_text()


def test_cli_integration(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "aerolab_experiment", "analyze", str(CSV),
         "--config", str(CFG), "--out", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "manifest.json").exists()
    assert (tmp_path / "analyzed.csv").exists()
    assert (tmp_path / "report.md").exists()


def test_plot_outputs(tmp_path):
    pytest.importorskip("matplotlib")
    from aerolab_experiment.plotting import make_plots
    cfg = read_config(CFG)
    rows = [analyze_measurement(r, cfg) for r in read_measurements(CSV)]
    paths = make_plots(rows, tmp_path, dataset_kind="synthetic")
    assert len(paths) == 3
    assert all(p.exists() and p.stat().st_size > 1000 for p in paths)
