"""Generate FAKE example data for testing the pipeline, never research evidence."""
from pathlib import Path
import csv
import random

rng = random.Random(20261123)
path = Path(__file__).resolve().parents[1] / "examples" / "naca0018_SYNTHETIC.csv"
with path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["run_id", "alpha_deg", "lift_N", "drag_N", "dp_pa", "temp_c", "ambient_pressure_pa"])
    for alpha in [-9, -6, -3, 0, 3, 6, 9, 12, 15]:
        for i in range(3):
            # Deliberately simplistic algebraic curve, NOT empirical NACA 0018 data.
            cl = 0.085 * alpha if abs(alpha) <= 10 else (0.75 if alpha > 0 else -0.75)
            cd = 0.045 + 0.017 * (cl ** 2) + max(0, alpha - 10) * 0.018
            q = 27.0 + rng.gauss(0, 0.4)
            area = .1 * .2
            lift_raw = cl * q * area + 0.012 + rng.gauss(0, 0.004)
            drag_raw = cd * q * area + 0.006 + rng.gauss(0, 0.002)
            writer.writerow([
                f"synth-{alpha:+03d}-{i+1}", alpha, f"{lift_raw:.8f}",
                f"{drag_raw:.8f}", f"{q+0.3:.6f}",
                f"{22+rng.gauss(0,0.2):.3f}", f"{100800+rng.gauss(0,20):.1f}",
            ])
print(path)
