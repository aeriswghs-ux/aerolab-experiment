from pathlib import Path
import runpy
import hashlib

ROOT=Path(__file__).resolve().parents[1]


def test_reference_integrity_and_parser():
    module=runpy.run_path(str(ROOT/'scripts/validate.py'))
    assert len(module['reference_rows']()) == 53
    assert hashlib.sha256(module['DATA'].read_bytes()).hexdigest() == '78cd2f6aa4968e80f44cbf6c96f699bd9c6e45681d958ec528a10cf72ed23357'


def test_independent_formulas_all_input_derivatives_and_monte_carlo():
    module=runpy.run_path(str(ROOT/'scripts/validate.py'))
    assert len(module['numerical_verification']()) == 4
