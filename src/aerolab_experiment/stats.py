"""Separate repeated-run scatter from instrument uncertainty."""
from __future__ import annotations
from collections import defaultdict
from statistics import mean, stdev
from math import sqrt
from .models import Result


def summarize(rows: list[Result]) -> list[dict]:
    groups: dict[float, list[Result]] = defaultdict(list)
    for row in rows:
        groups[row.alpha_deg].append(row)
    summaries: list[dict] = []
    for alpha, items in sorted(groups.items()):
        cl = [r.cl for r in items]
        cd = [r.cd for r in items]
        n = len(items)
        summaries.append({
            "alpha_deg": alpha,
            "n": n,
            "cl_mean": mean(cl),
            "cl_std_sample": stdev(cl) if n > 1 else "",
            "cl_sem": stdev(cl)/sqrt(n) if n > 1 else "",
            "cd_mean": mean(cd),
            "cd_std_sample": stdev(cd) if n > 1 else "",
            "cd_sem": stdev(cd)/sqrt(n) if n > 1 else "",
            "re_mean": mean(r.reynolds for r in items),
            "velocity_m_s_mean": mean(r.velocity_m_s for r in items),
        })
    return summaries
