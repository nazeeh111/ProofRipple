#!/usr/bin/env python3
"""Check installed documentation links and the bundled frozen evidence, offline."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sysconfig
from urllib.parse import unquote, urlsplit


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        self.refs.extend(value for key, value in attrs if key in {'href', 'src'} and value)


def check(root):
    root = Path(root).resolve()
    checked = 0
    missing = []
    for document in [root/'lab/index.html', *sorted((root/'docs').glob('*.md'))]:
        text = document.read_text()
        if document.suffix == '.html':
            parser = References(); parser.feed(text); refs = parser.refs
        else:
            refs = re.findall(r'\]\(([^)]+)\)', text)
        for ref in refs:
            url = urlsplit(ref)
            if url.scheme or url.netloc or not url.path:
                continue
            target = (document.parent/unquote(url.path)).resolve()
            if not target.is_relative_to(root) or not target.exists():
                missing.append({'document':str(document.relative_to(root)), 'target':ref})
            checked += 1
    if missing:
        raise ValueError('Missing installed links: '+json.dumps(missing))
    folder = root/'artifacts/mathlib'
    freeze = json.loads((folder/'source-freeze.json').read_text())
    for name, digest in freeze['corpus_sha256'].items():
        assert hashlib.sha256((folder/name).read_bytes()).hexdigest() == digest, name
    for name, digest in freeze['source_sha256'].items():
        assert hashlib.sha256((folder/'experiment-source'/name).read_bytes()).hexdigest() == digest, name
    report = json.loads((folder/'benchmark.json').read_text())
    formal = report['formal_verification']
    assert formal['status'] == 'kernel_verified' and formal['audits_received'] == formal['declarations']
    for row in formal['contexts']:
        assert hashlib.sha256((folder/row['source']).read_bytes()).hexdigest() == row['source_sha256']
    assert hashlib.sha256((folder/'benchmark-audits.json.gz').read_bytes()).hexdigest() == formal['audits_sha256']
    assert hashlib.sha256((folder/'model.json').read_bytes()).hexdigest() == report['model_sha256']
    repair = json.loads((folder/'control-repair/summary.json').read_text())
    assert repair['status'] == 'kernel_verified' and repair['solved'] == repair['total'] == 254
    assert repair['provenance']['data_sha256'] == freeze['data_sha256']
    return {'status':'passed', 'root':str(root), 'local_links_checked':checked,
            'frozen_scientific_sources':len(freeze['source_sha256']),
            'declaration_audits':formal['audits_received'],
            'repaired_control_goals':repair['solved'], 'outcomes_sha256':report['outcomes_sha256']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(sysconfig.get_path('data'))/'share/proofripple')
    args = parser.parse_args()
    print(json.dumps(check(args.root), indent=2))
