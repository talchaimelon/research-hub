import hashlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
password = os.environ.get('SITE_PASSWORD')
if not password:
    raise SystemExit('SITE_PASSWORD is required')
salt = os.environ.get('SITE_SALT', 'research-hub-salt')
hash_value = hashlib.sha256(f'{salt}:{password}'.encode()).hexdigest()
path = ROOT / 'src' / 'assets' / 'gate.js'
text = path.read_text()
text = text.replace('__SITE_PASSWORD_HASH__', hash_value).replace('__SITE_SALT__', salt)
path.write_text(text)
print('Gate prepared.')
