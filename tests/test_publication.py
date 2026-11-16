import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from proofripple.cli import save_run
from proofripple.publication import verify
from proofripple.certification import certify_benchmark

class PublicationTests(unittest.TestCase):
    def test_no_overwrite_and_proof_absence(self):
        with tempfile.TemporaryDirectory() as d:
            old = Path(d) / 'old'
            save_run({'lean_source': '-- old\n'}, old)
            before = {p.name: p.read_bytes() for p in old.iterdir()}
            with self.assertRaises(FileExistsError): save_run({'verification': {'status': 'proposed'}}, old)
            self.assertEqual(before, {p.name: p.read_bytes() for p in old.iterdir()})
            fresh = Path(d) / 'fresh'
            save_run({'verification': {'status': 'proposed'}}, fresh)
            self.assertNotIn('ProofRipple.lean', verify(fresh)['files'])
            self.assertFalse((fresh / 'ProofRipple.lean').exists())

    def test_tampered_or_incomplete_refused(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'out'; save_run({'lean_source': '-- proof\n'}, out)
            (out / 'ProofRipple.lean').write_text('-- changed\n')
            with self.assertRaises(ValueError): verify(out)
            (out / 'manifest.json').unlink()
            with self.assertRaises(ValueError): verify(out)

    def test_failed_write_does_not_create_complete_generation(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'partial'
            original = Path.open
            def fail(path, *args, **kwargs):
                if path.name == 'manifest.json': raise OSError('injected write failure')
                return original(path, *args, **kwargs)
            with patch.object(Path, 'open', fail):
                with self.assertRaises(OSError): save_run({'x': 1}, out)
            with self.assertRaises(ValueError): verify(out)
            retry = Path(d) / 'retry'; save_run({'x': 1}, retry); verify(retry)

    def test_batch_publishes_separate_generation_and_preserves_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d); report = b'{"summary": {}}\n'; runs = b'[]\n'
            (out/'benchmark.json').write_bytes(report); (out/'certification-runs.json').write_bytes(runs)
            result = certify_benchmark(out)
            self.assertEqual(result['formal_verification']['status'], 'failed')
            self.assertEqual((out/'benchmark.json').read_bytes(), report)
            self.assertEqual((out/'certification-runs.json').read_bytes(), runs)
            self.assertEqual(verify(out/'certification')['kind'], 'benchmark-certification')
            with self.assertRaises(FileExistsError): certify_benchmark(out)

class SnapshotTests(unittest.TestCase):
    def test_cli_recheck_consumes_admitted_snapshot_after_replacement(self):
        from proofripple import cli, publication
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'run'; save_run({'marker': 'original'}, out)
            real = publication._read_regular
            def swap(path, bound):
                data = real(path, bound)
                if path.name == 'run.json': path.write_bytes(b'{"marker":"changed"}\n')
                return data
            with patch.object(publication, '_read_regular', side_effect=swap), patch.object(cli, 'certify_run', return_value={'verification': {'status': 'kernel_verified'}}) as certify:
                self.assertEqual(cli.main(['verify-run',str(out),'--recheck']),0)
            self.assertEqual(certify.call_args.args[0]['marker'],'original')
            with self.assertRaises(ValueError): verify(out)

    def test_symlink_fifo_oversize_and_aggregate_bound_refuse(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            out=root/'run';save_run({'x':1},out)
            (out/'run.json').unlink();(out/'run.json').symlink_to(root/'outside')
            with self.assertRaises(ValueError):verify(out)
            (out/'run.json').unlink();os.mkfifo(out/'run.json')
            with self.assertRaises(ValueError):verify(out)
            (out/'run.json').unlink()
            with (out/'run.json').open('wb') as f:f.truncate(50_000_001)
            with self.assertRaises(ValueError):verify(out)
            m={'schema':'proofripple-generation-v1','kind':'benchmark-certification','files':{str(i):{'bytes':50_000_000,'sha256':'x'} for i in range(3)}}
            group=root/'group';group.mkdir();(group/'manifest.json').write_text(json.dumps(m))
            for n in m['files']:(group/n).touch()
            with self.assertRaisesRegex(ValueError,'total byte limit'):verify(group)
