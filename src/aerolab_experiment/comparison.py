"""Explicit pair comparison; matching is necessary, never proof of validation."""
from math import isfinite, sqrt


def compare_pair(observed, reference, *, re_rtol=0.01, alpha_atol=0.1):
    """No interpolation. Uncertainties are k=1 and independent between sources.

    Required metadata: airfoil, regime, transition, coefficient_definition,
    reynolds, alpha_deg, cl, cd. Missing metadata fails closed.
    """
    if not isfinite(re_rtol) or not isfinite(alpha_atol) or min(re_rtol, alpha_atol) < 0:
        raise ValueError("matching tolerances must be finite and nonnegative")
    flags = []
    for key in ('airfoil', 'regime', 'transition', 'coefficient_definition'):
        if not observed.get(key) or not reference.get(key):
            flags.append(key + '_unknown')
        elif observed[key] != reference[key]:
            flags.append(key + '_mismatch')
    for row in (observed, reference):
        for key in ('reynolds', 'alpha_deg', 'cl', 'cd'):
            if not isfinite(row[key]):
                raise ValueError(key + ' must be finite')
        if row['reynolds'] <= 0:
            raise ValueError('Reynolds must be positive')
    re_delta = abs(observed['reynolds'] / reference['reynolds'] - 1)
    aoa_delta = abs(observed['alpha_deg'] - reference['alpha_deg'])
    if re_delta > re_rtol:
        flags.append('reynolds_mismatch')
    if aoa_delta > alpha_atol:
        flags.append('alpha_mismatch')
    result = dict(flags=flags, conditions_match=not flags,
                  relative_re_difference=re_delta, alpha_difference_deg=aoa_delta)
    for key in ('cl', 'cd'):
        delta = observed[key] - reference[key]
        uncertainties = [row.get('u_' + key) for row in (observed, reference)]
        for u in uncertainties:
            if u is not None and (not isfinite(u) or u < 0):
                raise ValueError('standard uncertainties must be finite and nonnegative')
        combined = None if None in uncertainties else sqrt(sum(u*u for u in uncertainties))
        result[key] = dict(difference=delta, combined_standard_uncertainty=combined,
                           normalized_difference=delta/combined if combined else None)
    return result
