"""Re-fetch original archive; extract only approved, hash-verified files."""
from pathlib import Path
from urllib.request import urlopen
from hashlib import sha256
from io import BytesIO
import json
import zipfile

if __name__=='__main__':
    dest=Path(__file__).resolve().parents[1]/'data/reference/uiuc'
    p=json.loads((dest/'provenance.json').read_text())
    data=urlopen(p['source'],timeout=30).read()
    if sha256(data).hexdigest()!=p['archive_sha256']:
        raise ValueError('Upstream archive changed; review before accepting')
    z=zipfile.ZipFile(BytesIO(data))
    verified={}
    for entry in p['files']:
        name=entry['file']
        if Path(name).name!=name: raise ValueError('invalid filename')
        value=z.read('volume01/'+name)
        if sha256(value).hexdigest()!=entry['sha256']: raise ValueError('file hash mismatch')
        verified[name]=value
    for name,value in verified.items(): (dest/name).write_bytes(value)
    print('Verified',len(verified),'original files')
