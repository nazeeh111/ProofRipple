"""Exercise actual static evidence routes without running Lean or remote calls."""
import gzip
from http.client import HTTPConnection
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from proofripple.server import create_server


class EvidenceRoutesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root/'artifacts/natural/proofs').mkdir(parents=True)
        (self.root/'scripts').mkdir()
        (self.root/'lab').mkdir()
        (self.root/'lab/index.html').write_text('laboratory')
        (self.root/'artifacts/natural/proofs/checked.lean').write_text('theorem checked : True := True.intro\n')
        (self.root/'artifacts/natural/proofs/<name>.lean').write_text('public fixture')
        (self.root/'scripts/reproduce.py').write_text('raise RuntimeError("must only be served as text")\n')
        (self.root/'private.json').write_text('{"private":true}')
        (self.root/'artifacts/.env').write_text('not an allowed asset')
        self.audit = gzip.compress(b'[{"name":"checked"}]', mtime=0)
        (self.root/'artifacts/audits.json.gz').write_bytes(self.audit)
        self.server = create_server(self.root, port=0)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join()
        self.temp.cleanup()

    def request(self, path, headers=None, method='GET', body=None):
        conn = HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        try:
            conn.request(method, path, body=body, headers=headers or {})
            response = conn.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            conn.close()

    def test_directory_links_resolve_and_escape_filenames(self):
        status, headers, _ = self.request('/artifacts/natural/proofs')
        self.assertEqual(status, 301)
        self.assertEqual(headers['Location'], '/artifacts/natural/proofs/')
        status, _, body = self.request(headers['Location'])
        self.assertEqual(status, 200)
        self.assertIn(b'checked.lean', body)
        self.assertIn(b'&lt;name&gt;.lean', body)
        self.assertNotIn(b'<name>.lean', body)
        self.assertEqual(self.request('/artifacts/natural/proofs/%3Cname%3E.lean')[0], 200)

    def test_compressed_audits_are_downloaded_without_corruption(self):
        status, headers, body = self.request('/artifacts/audits.json.gz')
        self.assertEqual(status, 200)
        self.assertEqual(headers['Content-Type'], 'application/gzip')
        self.assertEqual(body, self.audit)
        self.assertEqual(gzip.decompress(body), b'[{"name":"checked"}]')

    def test_reproduction_scripts_are_read_only_text(self):
        status, headers, body = self.request('/scripts/reproduce.py')
        self.assertEqual(status, 200)
        self.assertIn('text/plain', headers['Content-Type'])
        self.assertIn(b'must only be served as text', body)

    def test_root_and_suffix_boundaries_remain_enforced(self):
        for path in ['/private.json', '/artifacts/../private.json', '/artifacts/%2e%2e/private.json', '/artifacts/.env', '/artifacts/%00']:
            with self.subTest(path=path):
                self.assertEqual(self.request(path)[0], 404)
        self.assertEqual(self.request('/lab/', headers={'Host':'untrusted.example'})[0], 403)
        self.assertEqual(self.request('/api/run', method='POST', body='{}', headers={'Origin':'https://untrusted.example'})[0], 403)
        # A same-origin request on an OS-assigned port reaches input validation.
        origin = f'http://127.0.0.1:{self.server.server_port}'
        self.assertEqual(self.request('/api/run', method='POST', body='{}', headers={'Origin':origin})[0], 400)


if __name__ == '__main__':
    unittest.main()
