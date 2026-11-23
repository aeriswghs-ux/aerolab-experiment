import pytest
from aerolab_experiment.comparison import compare_pair


def row(**kw):
    r=dict(airfoil='NACA0012',regime='steady',transition='80 grit',
           coefficient_definition='section',reynolds=6e6,alpha_deg=2,cl=.2,cd=.01,u_cl=.02,u_cd=.001)
    return dict(r,**kw)


def test_combined_uncertainty_and_signed_difference():
    r=compare_pair(row(cl=.24),row())
    assert r['conditions_match']
    assert r['cl']['difference']==pytest.approx(.04)
    assert r['cl']['normalized_difference']==pytest.approx(2**.5)


@pytest.mark.parametrize('key,value', [('airfoil','NACA0018'),('regime','pitching'),
    ('transition','180 grit'),('coefficient_definition','finite_span'),('reynolds',1e5),('alpha_deg',3)])
def test_mismatch_excluded(key,value):
    assert not compare_pair(row(**{key:value}),row())['conditions_match']


def test_missing_uncertainty_is_not_zero():
    r=compare_pair(row(u_cl=None),row())
    assert r['cl']['combined_standard_uncertainty'] is None
    assert r['cl']['normalized_difference'] is None


def test_unknown_metadata_fails_closed():
    assert not compare_pair(row(transition=None),row(transition=None))['conditions_match']


@pytest.mark.parametrize('key,value',[('reynolds',0),('cl',float('nan')),('u_cd',-1)])
def test_invalid_numbers(key,value):
    with pytest.raises(ValueError):
        compare_pair(row(**{key:value}),row())
