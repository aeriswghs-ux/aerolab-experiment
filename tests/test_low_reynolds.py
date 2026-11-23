from pathlib import Path
import runpy
import pytest

ROOT=Path(__file__).resolve().parents[1]
M=runpy.run_path(str(ROOT/'scripts/low_reynolds.py'))


def test_uiuc_provenance():
    assert len(M['verify_sources']()['files'])==6


def test_real_low_re_reference_and_airfoil_identity():
    runs=M['parse_drag']((M['DATA']/'DRAG01.TXT').read_text())
    selected=[r for r in runs if r['airfoil'] in M['SELECTED'] and 30000<=r['reynolds']<=110000]
    assert len(selected)==7
    assert sum(len(r['points']) for r in selected)==67
    a=next(r for r in selected if r['reynolds']==40000)
    assert a['airfoil']=='A18'  # This is not NACA 0018.
    assert a['points'][0]['cd']==.0244
    assert a['points'][0]['spanwise_cd']==[.0247,.0203,.029,.0236]


def test_parser_rejects_truncated_run():
    text=(M['DATA']/'DRAG01.TXT').read_text()
    text=text.replace(' -1.16   0.117   0.0244   0.0247   0.0203   0.0290   0.0236','',1)
    with pytest.raises(ValueError,match='point count'):
        M['parse_drag'](text)
