"""Regression ISSUE-002: invalid LAB ports refuse before socket creation.

Found by /qa on 2026-11-16.
Report: research/proofripple-product/qa-report-proofripple-2026-11-16.md
Native unittest naming keeps this regression in the existing discovery command.
No Lean, model training, network listener or successful proof is simulated here.
"""
import contextlib
import io
import unittest
from unittest.mock import patch
from proofripple.cli import main


class LabPortContractTests(unittest.TestCase):
    def test_invalid_ports_fail_cleanly_before_server_dispatch(self):
        for port in ("-1", "65536", "1.5", "abc"):
            with self.subTest(port=port), patch("proofripple.server.serve") as serve:
                error = io.StringIO()
                with contextlib.redirect_stderr(error), self.assertRaises(SystemExit) as stopped:
                    main(["lab", "--port", port])
                self.assertEqual(stopped.exception.code, 2)
                self.assertIn("--port", error.getvalue())
                self.assertNotIn("Traceback", error.getvalue())
                serve.assert_not_called()

    def test_zero_and_largest_port_reach_the_existing_server(self):
        for port in (0, 65535):
            with self.subTest(port=port), patch("proofripple.server.serve") as serve:
                self.assertEqual(main(["lab", "--port", str(port)]), 0)
                self.assertEqual(serve.call_args.args[1], port)


if __name__ == "__main__":
    unittest.main()
