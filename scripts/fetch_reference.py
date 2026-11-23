"""Fetch a pinned public reference, verifying bytes before replacing local data."""
from pathlib import Path
from hashlib import sha256
from urllib.request import urlopen

URL = 'https://raw.githubusercontent.com/TMBWG/turbmodels/20a39f549dbff988a6accc421ac84dafc4487695/NACA0012_validation/CLCD_Ladson_expdata.dat'
EXPECTED = '78cd2f6aa4968e80f44cbf6c96f699bd9c6e45681d958ec528a10cf72ed23357'

if __name__ == '__main__':
    data = urlopen(URL, timeout=30).read()
    if sha256(data).hexdigest() != EXPECTED:
        raise RuntimeError('Source hash differs; inspect upstream provenance before accepting')
    target = Path(__file__).resolve().parents[1]/'data/reference/CLCD_Ladson_expdata.dat'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    print(EXPECTED)
