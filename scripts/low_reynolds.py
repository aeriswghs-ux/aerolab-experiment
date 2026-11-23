"""UIUC reference analysis and provisional tunnel targets, not tunnel validation."""
from pathlib import Path
import csv
import hashlib
import json
import re
import statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from aerolab_experiment.physics import air_density_dry, air_viscosity_sutherland

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/reference/uiuc'
OUT=ROOT/'validation/low_reynolds'
SELECTED=('A18','E387 (A)','NACA 64A010')


def parse_drag(text):
    """Read declared run sizes and retain original run IDs and spanwise values."""
    runs=[]
    for section in text.split('Airfoil: ')[1:]:
        name=section.splitlines()[0].strip()
        comment=re.search(r'Comment:([^\r\n]*)',section).group(1).strip()
        expected=int(re.search(r"Number of Reynolds #'s:\s*(\d+)",section).group(1))
        blocks=section.split('Average Reynolds #:')[1:]
        if len(blocks)!=expected:
            raise ValueError('run count mismatch')
        for block in blocks:
            reynolds=int(block.strip().split()[0])
            n=int(re.search(r'Number of angles of attack:\s*(\d+)',block).group(1))
            body=block.split('>>>',1)[1].split('Tabulated from data',1)[0]
            points=[]
            for line in body.splitlines():
                if not line.strip(): continue
                values=list(map(float,line.split()))
                if len(values)<5: raise ValueError('missing spanwise data')
                a,cl,cd,*span=values
                points.append(dict(alpha_deg=a,cl=cl,cd=cd,spanwise_cd=span))
            if len(points)!=n: raise ValueError('point count mismatch')
            run_id=re.search(r'Tabulated from data in file (\S+)',block).group(1)
            runs.append(dict(airfoil=name,condition=comment,reynolds=reynolds,run_id=run_id,points=points))
    return runs


def verify_sources():
    p=json.loads((DATA/'provenance.json').read_text())
    for entry in p['files']:
        if hashlib.sha256((DATA/entry['file']).read_bytes()).hexdigest()!=entry['sha256']:
            raise ValueError('source integrity failure: '+entry['file'])
    return p


def main():
    provenance=verify_sources()
    runs=[r for r in parse_drag((DATA/'DRAG01.TXT').read_text())
          if r['airfoil'] in SELECTED and 30000<=r['reynolds']<=110000]
    OUT.mkdir(exist_ok=True,parents=True)
    summaries=[]; normalized=[]
    for run in runs:
        pts=run['points']
        best=min(pts,key=lambda p:p['cd'])
        ld=max(pts,key=lambda p:p['cl']/p['cd'])
        errs=[]
        for p in pts:
            mean=statistics.mean(p['spanwise_cd']); err=mean-p['cd']; errs.append(err)
            normalized.append(dict(airfoil=run['airfoil'],reynolds=run['reynolds'],run_id=run['run_id'],
                alpha_deg=p['alpha_deg'],cl=p['cl'],cd=p['cd'],spanwise_mean=mean,
                mean_minus_published=err,spanwise_sd=statistics.stdev(p['spanwise_cd']),
                standard_uncertainty='unknown'))
        summaries.append(dict(airfoil=run['airfoil'],reynolds=run['reynolds'],run_id=run['run_id'],n=len(pts),
            min_sampled_cd=best['cd'],alpha_at_min_cd=best['alpha_deg'],
            max_sampled_lift_drag=ld['cl']/ld['cd'],alpha_at_max_lift_drag=ld['alpha_deg'],
            max_drag_mean_discrepancy=max(map(abs,errs))))
    # Rounded spanwise and mean Cd values each have 0.00005 rounding bounds.
    # Their difference can therefore be 0.0001 without implying a reduction error.
    max_error=max(abs(p['mean_minus_published']) for p in normalized)
    assert max_error<=.00010000001
    pairs=[]
    for name in SELECTED:
        group=[r for r in runs if r['airfoil']==name]
        low,high=min(group,key=lambda r:r['reynolds']),max(group,key=lambda r:r['reynolds'])
        for p in low['points']:
            if not -2<=p['alpha_deg']<=8: continue
            q=min(high['points'],key=lambda q:abs(q['alpha_deg']-p['alpha_deg']))
            if abs(q['alpha_deg']-p['alpha_deg'])>.25: continue
            pairs.append(dict(airfoil=name,re_low=low['reynolds'],re_high=high['reynolds'],
                alpha_low=p['alpha_deg'],alpha_high=q['alpha_deg'],cl_difference=p['cl']-q['cl'],
                cd_difference=p['cd']-q['cd'],flag='reynolds_mismatch',combined_standard_uncertainty=None))
    rho=air_density_dry(101325,20); mu=air_viscosity_sutherland(20)
    targets=[]
    for reynolds in (40000,50000,60000,100000):
        speed=reynolds*mu/(rho*.1)
        targets.append(dict(reynolds=reynolds,chord_m=.1,speed_m_s=speed,q_pa=.5*rho*speed**2,
                            status='PROVISIONAL DESIGN TARGET; NOT MEASURED'))
    metrics={name:{key:dict(n=len(p:=[p for p in pairs if p['airfoil']==name]),
        mae=statistics.mean(abs(r[key+'_difference']) for r in p),
        rmse=(statistics.mean(r[key+'_difference']**2 for r in p))**.5)
        for key in ('cl','cd')} for name in SELECTED}
    report=dict(status='PUBLISHED LOW-RE REFERENCE RESULTS; NOT USER TUNNEL RESULTS',
        source=provenance,summary=summaries,drag_mean_max_absolute_difference=max_error,
        rounding_bound=.0001,reynolds_sensitivity_pairs=pairs,sensitivity_metrics=metrics,
        intended_targets=targets,uncertainty='unknown; spanwise SD is spatial variation, not standard measurement uncertainty')
    (OUT/'summary.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    for name,rows in [('reference_rows.csv',normalized),('target_conditions.csv',targets)]:
        with (OUT/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    fig,axes=plt.subplots(2,3,figsize=(13,8))
    for col,name in enumerate(SELECTED):
        for r in [r for r in runs if r['airfoil']==name]:
            for ax,key in zip(axes[:,col],('cl','cd')):
                ax.plot([p['alpha_deg'] for p in r['points']],[p[key] for p in r['points']],'.-',label=f"Re={r['reynolds']:,}")
                ax.set(xlabel='Angle of attack (deg)',ylabel=key.upper()); ax.grid(alpha=.2)
        axes[0,col].set_title(name+(' (NOT NACA 0018)' if name=='A18' else ''))
        axes[0,col].legend(fontsize=8)
    fig.suptitle('UIUC Low-Speed Airfoil Test program: published experimental reference data\nLow-Reynolds target context — NOT measurements from our tunnel',fontsize=13)
    fig.text(.5,.01,'Selig et al., Volume 1 (re-reduced data) | Uncertainty unavailable; lines guide the eye | GPL data',ha='center',fontsize=10)
    fig.tight_layout(rect=(0,.04,1,.92)); fig.savefig(OUT/'reference_polars.png',dpi=160); plt.close(fig)
    print(json.dumps({k:report[k] for k in ('summary','drag_mean_max_absolute_difference','sensitivity_metrics','intended_targets')},indent=2))


if __name__=='__main__': main()
