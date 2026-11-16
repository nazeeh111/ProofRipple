"""Fresh, manifest-last output generations. Digests establish integrity, not authorship."""
import hashlib
import json
import os
import stat
from pathlib import Path


def _json(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def publish(directory, files, kind):
    out = Path(directory)
    if not files or any(not isinstance(name, str) or Path(name).name != name or name in ("", ".", "..", "manifest.json") for name in files):
        raise ValueError("Invalid generation filenames")
    if len(files) > 1024:
        raise ValueError("Too many generation files")
    manifest = {"schema": "proofripple-generation-v1", "kind": kind, "files": {}}
    total = 0
    for name, data in sorted(files.items()):
        if not isinstance(data, bytes):
            raise TypeError("Generation files must be bytes")
        total += len(data)
        if len(data) > 50_000_000 or total > 100_000_000:
            raise ValueError("Generation exceeds byte limit")
        manifest["files"][name] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    encoded_manifest = _json(manifest)
    if len(encoded_manifest) > 100_000:
        raise ValueError("Generation manifest exceeds byte limit")
    out.mkdir(parents=True, exist_ok=False)
    for name, data in sorted(files.items()):
        with (out / name).open("xb") as stream:
            stream.write(data)
    with (out / "manifest.json").open("xb") as stream:
        stream.write(encoded_manifest)
    return out


def _read_regular(path, limit):
    # Open nonblocking and without following a final-component symlink. The
    # descriptor is checked and consumed once, even if the path later changes.
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0)
    if not hasattr(os, "O_NOFOLLOW"):
        raise ValueError("Safe no-follow file access is unavailable")
    fd = os.open(path, flags | os.O_NOFOLLOW)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
            raise ValueError("Invalid generation file size or type")
        chunks = []
        total = 0
        while True:
            part = os.read(fd, min(65536, limit - total + 1))
            if not part:
                break
            total += len(part)
            if total > limit:
                raise ValueError("Generation file exceeds its byte limit")
            chunks.append(part)
        return b"".join(chunks)
    finally:
        os.close(fd)


def admit(directory):
    out = Path(directory)
    try:
        manifest = json.loads(_read_regular(out / "manifest.json", 100_000))
    except OSError as exc:
        raise ValueError("Missing or invalid generation manifest") from exc
    if not isinstance(manifest, dict) or set(manifest) != {"schema", "kind", "files"} or manifest["schema"] != "proofripple-generation-v1" or manifest["kind"] not in {"run", "benchmark-certification"}:
        raise ValueError("Unsupported generation manifest")
    files = manifest["files"]
    if not isinstance(files, dict) or not files or len(files) > 1024:
        raise ValueError("Invalid generation file list")
    if set(p.name for p in out.iterdir()) != set(files) | {"manifest.json"}:
        raise ValueError("Generation member set differs")
    total = 0
    for name, item in files.items():
        if not isinstance(name, str) or Path(name).name != name or name in ("", ".", "..", "manifest.json") or not isinstance(item, dict) or set(item) != {"sha256", "bytes"}:
            raise ValueError("Invalid generation member")
        size = item['bytes']
        if type(size) is not int or size < 0 or size > 50_000_000:
            raise ValueError("Invalid generation file size or type")
        total += size
        if total > 100_000_000:
            raise ValueError("Generation exceeds total byte limit")
    captured = {}
    for name, item in files.items():
        try:
            data = _read_regular(out / name, item['bytes'])
        except OSError as exc:
            raise ValueError("Invalid generation file") from exc
        if len(data) != item['bytes'] or hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError("Generation file digest or size mismatch")
        captured[name] = data
    run = None
    if manifest['kind'] == 'run':
        if set(files) not in ({'run.json'}, {'run.json', 'ProofRipple.lean'}):
            raise ValueError("Invalid run member set")
        run = json.loads(captured['run.json'])
        if not isinstance(run, dict) or ('lean_source' in run) != ('ProofRipple.lean' in files):
            raise ValueError("Run and Lean source membership differ")
        if 'lean_source' in run and (not isinstance(run['lean_source'], str) or run['lean_source'].encode('utf-8') != captured['ProofRipple.lean']):
            raise ValueError("Run and Lean source bytes differ")
    return manifest, run


def verify(directory):
    """Check an admitted generation; preserve the public manifest return value."""
    return admit(directory)[0]
