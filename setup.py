"""Bundle the LAB and the evidence referenced by its installed documentation."""
from pathlib import Path
from setuptools import setup

SUFFIXES = {".html", ".js", ".css", ".svg", ".json", ".lean", ".md", ".gz", ".py", ".cjs", ".log", ".txt", ".png"}
EXCLUDED = {"certification-runs.json", "benchmark-audits.json", "Benchmark.lean"}
folders = {Path(name) for name in ("lab", "examples", "docs", "scripts", "artifacts")}
folders.update(path.parent for base in ("artifacts", "docs") for path in Path(base).rglob("*")
               if path.is_file() and path.suffix in SUFFIXES and "__pycache__" not in path.parts)
setup(data_files=[("share/proofripple/" + folder.as_posix(),
                   [str(path) for path in sorted(folder.iterdir())
                    if path.is_file() and path.suffix in SUFFIXES and path.name not in EXCLUDED
                    and not (folder == Path("artifacts/natural/proofs") and path.suffix == ".log")])
                  for folder in sorted(folders)])
