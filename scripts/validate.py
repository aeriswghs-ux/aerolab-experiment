"""Reproduce verification and reference sensitivity results; never tunnel validation."""
from pathlib import Path
import csv
import hashlib
import json
import platform
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from aerolab_experiment.io import read_config, read_measurements
from aerolab_experiment.physics import analyze_measurement
from aerolab_experiment.comparison import compare_pair

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'validation/results'
DATA = ROOT / 'data/reference/CLCD_Ladson_expdata.dat'


def reference_rows():
    rows = []
    for line in DATA.read_text().splitlines():
        if line.startswith('zone'):
            trip = line.split('"')[1]
        elif line and line[0] not in '#vz':
            a, cl, cd = map(float, line.split())
            rows.append(dict(airfoil='NACA0012', regime='steady', transition=trip,
                             coefficient_definition='section', reynolds=6e6,
                             alpha_deg=a, cl=cl, cd=cd, u_cl=None, u_cd=None))
    return rows


def numerical_verification():
    # Independent vector implementation: coefficients via rho*V^2, not q*A.
    cfg = read_config(ROOT/'examples/config.synthetic.json')
    m = read_measurements(ROOT/'examples/naca0018_SYNTHETIC.csv')[12]
    g, t, u = cfg.geometry, cfg.tare, cfg.uncertainty
    x = np.array([m.lift_N, m.drag_N, m.dp_pa, t.lift_N, t.drag_N,
                  t.dp_pa, g.chord_m, g.span_m, m.temp_c, m.ambient_pressure_pa])
    sigma = np.array([u.lift_N, u.drag_N, u.dp_pa, u.lift_tare_N, u.drag_tare_N,
                      u.dp_tare_pa, u.chord_m, u.span_m, u.temp_c, u.ambient_pressure_pa])
    def independent(x):
        L, D, dp, Lt, Dt, dpt, c, b, tc, p = x
        T = tc + 273.15
        rho = p / (287.05*T)
        V = (2*(dp-dpt)/rho)**0.5
        mu = 1.716e-5*(T/273.15)**1.5*(273.15+110.4)/(T+110.4)
        return np.array([2*(L-Lt)/(rho*V**2*c*b),
                         2*(D-Dt)/(rho*V**2*c*b), V, rho*V*c/mu])
    baseline = analyze_measurement(m, cfg)
    calculated = np.array([baseline.cl, baseline.cd, baseline.velocity_m_s, baseline.reynolds])
    analytic_u = np.array([baseline.u_cl, baseline.u_cd, baseline.u_velocity_m_s, baseline.u_reynolds])
    jac = []
    for i in range(len(x)):
        h = max(abs(x[i])*1e-5, 1e-7)
        dx = np.zeros(len(x)); dx[i] = h
        jac.append((independent(x+dx)-independent(x-dx))/(2*h))
    fd_u = np.sqrt((np.array(jac)**2 * sigma[:, None]**2).sum(axis=0))
    rng = np.random.default_rng(20261123)
    mc = independent(rng.normal(x[:, None], sigma[:, None], size=(10, 100000)))
    mc_u = mc.std(axis=1, ddof=1)
    results = []
    for i, name in enumerate(('cl', 'cd', 'velocity_m_s', 'reynolds')):
        results.append(dict(quantity=name, calculated=float(calculated[i]),
                            independent=float(independent(x)[i]),
                            absolute_difference=float(abs(calculated[i]-independent(x)[i])),
                            analytic_u=float(analytic_u[i]), finite_difference_u=float(fd_u[i]),
                            fd_relative_difference=float(abs(fd_u[i]/analytic_u[i]-1)),
                            monte_carlo_u=float(mc_u[i]),
                            mc_relative_difference=float(abs(mc_u[i]/analytic_u[i]-1))))
    assert np.allclose(calculated, independent(x), rtol=1e-12, atol=1e-14)
    assert np.allclose(analytic_u, fd_u, rtol=1e-6)
    assert np.allclose(analytic_u, mc_u, rtol=.03)
    return results


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = reference_rows()
    verification = numerical_verification()
    # Nearest-angle pairs, no interpolation/extrapolation; transition mismatch retained.
    pairs = []
    for a in [r for r in rows if r['transition']=='80 grit' and -4 <= r['alpha_deg'] <= 10]:
        b = min((r for r in rows if r['transition']=='180 grit'), key=lambda r: abs(a['alpha_deg']-r['alpha_deg']))
        result = compare_pair(a, b, alpha_atol=.25)
        pairs.append(dict(alpha_80=a['alpha_deg'], alpha_180=b['alpha_deg'], **result))
    cfg = read_config(ROOT/'examples/config.synthetic.json')
    demo = [analyze_measurement(m,cfg) for m in read_measurements(ROOT/'examples/naca0018_SYNTHETIC.csv')]
    mismatches = []
    for d in demo:
        ref = min(rows, key=lambda r: abs(r['alpha_deg']-d.alpha_deg))
        obs = dict(airfoil='NACA0018', regime='steady', transition=None,
                   coefficient_definition='finite_span', reynolds=d.reynolds, alpha_deg=d.alpha_deg,
                   cl=d.cl, cd=d.cd, u_cl=d.u_cl, u_cd=d.u_cd)
        mismatches.append(dict(run_id=d.run_id, **compare_pair(obs,ref)))
    summary = dict(status='SOFTWARE VERIFICATION ONLY; NO PHYSICAL VALIDATION',
        verification=verification, reference_rows=len(rows), sensitivity_pairs=pairs,
        sensitivity_metrics={k:dict(n=len(pairs),
            mae=float(np.mean([abs(p[k]['difference']) for p in pairs])),
            rmse=float(np.sqrt(np.mean([p[k]['difference']**2 for p in pairs])))) for k in ('cl','cd')},
        sensitivity_warning='Different trips; not matched validation. Source uncertainty unavailable; no confidence intervals.',
        synthetic_comparisons=mismatches, matched_synthetic_rows=sum(p['conditions_match'] for p in mismatches),
        synthetic_re_range=[min(d.reynolds for d in demo),max(d.reynolds for d in demo)],
        source_sha256=hashlib.sha256(DATA.read_bytes()).hexdigest(),
        python=platform.python_version(), numpy=np.__version__, seed=20261123, mc_samples=100000)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    with (OUT/'verification.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(verification[0])); w.writeheader(); w.writerows(verification)
    fig, axes = plt.subplots(1,2,figsize=(11,4.8))
    for trip in ('80 grit','120 grit','180 grit'):
        subset=[r for r in rows if r['transition']==trip]
        for ax,key in zip(axes,('cl','cd')):
            ax.plot([r['alpha_deg'] for r in subset],[r[key] for r in subset],'.-',label=trip)
            ax.set(xlabel='Angle of attack (deg)',ylabel=key.upper()); ax.grid(alpha=.2)
    axes[0].legend()
    fig.suptitle('Published NACA 0012 experiments | Re=6 million, M=0.15\nReference context ONLY — not AeroLab tunnel validation')
    fig.text(.5,.01,'Ladson, NASA TM 4074 (1988), via TMR | Source uncertainty unavailable; no error bars',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.04,1,.9)); fig.savefig(OUT/'published_reference.png',dpi=160); plt.close(fig)
    fig, ax=plt.subplots(figsize=(8,4.5))
    for key in ('cl','cd'):
        ax.plot([p['alpha_80'] for p in pairs],[p[key]['difference'] for p in pairs],'o-',label=key.upper())
    ax.set(xlabel='80-grit angle (deg)',ylabel='Coefficient difference: 80 minus 180 grit',
           title='Trip sensitivity — mismatched conditions, NOT validation\nNearest AoA within 0.25 deg; Re=6 million; no interpolation')
    ax.legend(); ax.grid(alpha=.2)
    fig.text(.5,.01,'Ladson (1988) | Uncertainty unknown; differences include angle mismatch',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,1)); fig.savefig(OUT/'trip_sensitivity.png',dpi=160); plt.close(fig)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('synthetic_comparisons','sensitivity_pairs')},indent=2))


if __name__ == '__main__':
    main()
