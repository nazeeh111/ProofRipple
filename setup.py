"""Bundle the same inspected LAB and frozen data into wheels and sdists."""
from pathlib import Path
from setuptools import setup

setup(data_files=[("share/proofripple/" + folder,
                   [str(p) for p in Path(folder).glob("*") if p.is_file() and p.suffix in {".html", ".js", ".css", ".svg", ".json", ".lean", ".md"}
                    and p.name not in {"certification-runs.json", "benchmark-audits.json", "Benchmark.lean"}])
                  for folder in ("lab", "examples", "artifacts", "artifacts/natural", "artifacts/mathlib", "docs")])
