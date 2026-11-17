"""Behavior and adapter independence of the shared context workflow."""
import copy
from http.client import HTTPConnection
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch

from proofripple import cli, workflow
from proofripple.mathlib_benchmark import make_example as mathlib_example
from proofripple.server import create_server


ROOT = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def test_legacy_entrypoint_is_the_same_callable(self):
        self.assertIs(cli.run_context, workflow.run_context)
        self.assertEqual(str(inspect.signature(cli.run_context)),
                         '(context, budget=8, select=None, verify=True, method=None)')

    def test_server_runs_a_real_request_without_importing_the_cli(self):
        script = '''
import importlib.abc, json, sys
from http.client import HTTPConnection
from pathlib import Path
from threading import Thread
class NoCLI(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname == "proofripple.cli":
            raise ImportError("CLI must not be required by the server")
sys.meta_path.insert(0, NoCLI())
from proofripple.server import create_server
root = Path(sys.argv[1])
context = json.loads((root / "examples/invariants.json").read_text())
server = create_server(root, 0)
thread = Thread(target=server.serve_forever)
thread.start()
connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
try:
    connection.request("POST", "/api/run", json.dumps({"context": context}),
                       {"Content-Type": "application/json"})
    response = connection.getresponse()
    result = json.loads(response.read())
    assert response.status == 200, result
    assert result["verification"]["status"] == "unavailable", result
    assert "proofripple.cli" not in sys.modules
finally:
    connection.close()
    server.shutdown()
    server.server_close()
    thread.join()
'''
        env = {**os.environ, 'PYTHONPATH': str(ROOT), 'PATH': '',
               'PYTHONDONTWRITEBYTECODE': '1'}
        result = subprocess.run([sys.executable, '-B', '-c', script, str(ROOT)],
                                env=env, cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_domain_defaults_match_explicit_policies(self):
        examples = [
            ('invariants.json', 'learned', 3),
            ('list_capacity.json', 'graph', 1),
        ]
        for filename, method, count in examples:
            context = json.loads((ROOT / 'examples' / filename).read_text())
            default = workflow.run_context(context, verify=False)
            explicit = workflow.run_context(context, select=count, method=method, verify=False)
            self.assertEqual(default, explicit)
        with patch.object(workflow, 'load_model', side_effect=AssertionError('heuristic loaded a model')):
            context = mathlib_example()
            default = workflow.run_context(context, verify=False)
            explicit = workflow.run_context(context, select=3, method='greedy_coverage', verify=False)
        # Preprocessing cache work and elapsed time depend on prior calls;
        # policy defaults must preserve the complete mathematical result.
        default.pop('selection_cost')
        explicit.pop('selection_cost')
        self.assertEqual(default, explicit)

    def test_missing_mathlib_learned_model_refuses_but_heuristic_still_runs(self):
        context = mathlib_example()
        with tempfile.TemporaryDirectory() as folder, patch.object(workflow, 'data_root', return_value=Path(folder)):
            for method in ('learned', 'learned_no_bonus', 'learned_singleton', 'structure_only'):
                with self.subTest(method=method), self.assertRaisesRegex(ValueError, 'frozen Mathlib usefulness model is missing'):
                    workflow.run_context(context, method=method, verify=False)
            self.assertTrue(workflow.run_context(context, method='graph', verify=False)['candidates'])

    def test_invalid_budgets_fail_before_model_or_certification(self):
        context = json.loads((ROOT / 'examples/invariants.json').read_text())
        with patch.object(workflow, 'load_model', side_effect=AssertionError('model touched')), \
             patch.object(workflow, 'certify_run', side_effect=AssertionError('certifier touched')):
            for arguments, message in [({'budget': True}, 'Search expansion'),
                                       ({'budget': 0}, 'Search expansion'),
                                       ({'budget': 129}, 'Search expansion'),
                                       ({'select': True}, 'Selected consequence'),
                                       ({'select': -1}, 'Selected consequence'),
                                       ({'select': 17}, 'Selected consequence')]:
                with self.subTest(arguments=arguments), self.assertRaisesRegex(ValueError, message):
                    workflow.run_context(context, **arguments)

    def test_direct_cli_and_http_agree_and_outputs_remain_admitted(self):
        context = json.loads((ROOT / 'examples/invariants.json').read_text())
        arguments = {'budget': 4, 'select': 0, 'method': 'graph'}
        with patch('proofripple.lean.shutil.which', return_value=None):
            expected = workflow.run_context(copy.deepcopy(context), **arguments)
            server = create_server(ROOT, 0)
            thread = Thread(target=server.serve_forever)
            thread.start()
            connection = HTTPConnection('127.0.0.1', server.server_port, timeout=5)
            try:
                connection.request('POST', '/api/run', json.dumps({'context': context, **arguments}))
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                self.assertEqual(json.loads(response.read()), expected)
            finally:
                connection.close(); server.shutdown(); server.server_close(); thread.join()
        self.assertEqual(expected['verification']['status'], 'unavailable')
        self.assertTrue(all(item['status'] != 'kernel_verified' for item in expected['candidates']))
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / 'run'
            environment = {**os.environ, 'PYTHONPATH': str(ROOT), 'PATH': '', 'PYTHONDONTWRITEBYTECODE': '1'}
            command = [sys.executable, '-B', '-m', 'proofripple.cli', 'discover',
                       str(ROOT / 'examples/invariants.json'), '--out', str(out),
                       '--budget', '4', '--select', '0', '--method', 'graph']
            result = subprocess.run(command, env=environment, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(json.loads((out / 'run.json').read_text()), expected)
            from proofripple.publication import admit
            self.assertEqual(admit(out)[1], expected)
            before = {p.name: p.read_bytes() for p in out.iterdir()}
            again = subprocess.run(command, env=environment, capture_output=True, text=True, timeout=10)
            self.assertEqual(again.returncode, 2)
            self.assertIn(str(out), again.stderr)
            self.assertEqual({p.name: p.read_bytes() for p in out.iterdir()}, before)


if __name__ == '__main__':
    unittest.main()
