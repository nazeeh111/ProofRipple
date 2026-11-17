"""Read recorded case integrity. No theorem execution or external dependencies."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent
for line in (D/'SHA256SUMS').read_text().splitlines():
 digest,name=line.split('  ',1);assert hashlib.sha256((D/name).read_bytes()).hexdigest()==digest,name
for name in ['selected','without','negative','edited']:
 p=D/name;m=json.loads((p/'manifest.json').read_text());assert set(x.name for x in p.iterdir())==set(m['files'])|{'manifest.json'}
 for f,v in m['files'].items():
  b=(p/f).read_bytes();assert len(b)==v['bytes'] and hashlib.sha256(b).hexdigest()==v['sha256'],f
 r=json.loads((p/'run.json').read_text());print(name, r['metrics']['baseline_solved'], '->', r['metrics']['augmented_solved'], '/',r['metrics']['goal_count'],r['verification']['status'],'(recorded)')
print('Integrity only; hashes are not authentication. Use proofripple verify-run selected --recheck for fresh Lean.')
