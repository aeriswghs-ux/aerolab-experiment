"""Command line access to a reproducible wind-tunnel analysis."""
from __future__ import annotations
import argparse
from pathlib import Path
from dataclasses import asdict
from .io import read_config, read_measurements, write_results
from .physics import analyze_measurement
from .plotting import make_plots
from . import __version__


def build_parser():
    parser = argparse.ArgumentParser(prog="aerolab", description="Experimental low-speed wind-tunnel data reduction")
    parser.add_argument("--version", action="version", version=f"aerolab-experiment {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze", help="Reduce SI CSV data into aerodynamic coefficients")
    analyze.add_argument("input_csv", type=Path)
    analyze.add_argument("--config", required=True, type=Path, help="JSON measurement configuration")
    analyze.add_argument("--out", default=Path("outputs"), type=Path)
    analyze.add_argument("--plots", action="store_true", help="Generate PNG graphs (requires matplotlib)")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "analyze":
            config = read_config(args.config)
            rows = read_measurements(args.input_csv)
            results = [analyze_measurement(r, config) for r in rows]
            manifest = write_results(args.out, args.input_csv, args.config, config, results)
            if args.plots:
                make_plots(results, args.out, dataset_kind=config.dataset_kind)
            print(
                f"Analyzed {manifest['input_rows']} rows into "
                f"{manifest['angle_groups']} angle groups; outputs: {args.out}"
            )
            print("Data type:", config.dataset_kind, "| No claims of independent experimental validation.")
            return 0
    except (ValueError, RuntimeError) as exc:
        parser.exit(2, f"AeroLab error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
