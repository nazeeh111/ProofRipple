"""Loopback-only workbench server. No arbitrary filesystem or Lean execution API."""
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import mimetypes
from pathlib import Path
from urllib.parse import quote, unquote, urlparse


STATIC_FOLDERS = ("lab", "examples", "artifacts", "docs", "scripts")
STATIC_SUFFIXES = {".html", ".js", ".css", ".svg", ".json", ".lean", ".png", ".mp4", ".webm", ".md", ".gz", ".log", ".txt", ".py", ".cjs"}


def create_server(root, port=8765):
    root = Path(root).resolve()
    class Handler(BaseHTTPRequestHandler):
        def allowed(self):
            bound_port = self.server.server_port
            return self.headers.get("Host") in {f"127.0.0.1:{bound_port}", f"localhost:{bound_port}"}

        def send(self, status, data, content_type="application/json"):
            body = json.dumps(data).encode() if isinstance(data, (dict, list)) else data
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if not self.allowed():
                return self.send(403, {"error": "Use the loopback URL printed by the server"})
            path = unquote(urlparse(self.path).path)
            if "\0" in path:
                return self.send(404, {"error": "No such workbench asset"})
            if path in ("/", "/lab", "/lab/"):
                path = "/lab/index.html"
            file = (root / path.lstrip("/")).resolve()
            if not any(file.is_relative_to(root / folder) for folder in STATIC_FOLDERS):
                return self.send(404, {"error": "No such workbench asset"})
            if file.is_dir():
                if not path.endswith("/"):
                    self.send_response(301)
                    self.send_header("Location", quote(path, safe="/") + "/")
                    self.end_headers()
                    return
                links = []
                for child in sorted(file.iterdir(), key=lambda item: item.name):
                    if child.name.startswith(".") or not (child.is_dir() or child.suffix in STATIC_SUFFIXES):
                        continue
                    name = child.name + ("/" if child.is_dir() else "")
                    links.append(f'<li><a href="{quote(name)}">{escape(name)}</a></li>')
                title = escape(file.relative_to(root).as_posix())
                body = ('<!doctype html><html lang="en"><meta charset="utf-8">'
                        '<meta name="viewport" content="width=device-width, initial-scale=1">'
                        f'<title>{title} · ProofRipple evidence</title>'
                        '<style>body{background:#111412;color:#e3e8e2;font:16px system-ui;'
                        'max-width:960px;margin:48px auto;padding:0 24px}a{color:#b0cdb4}'
                        'h1{font-size:24px;overflow-wrap:anywhere}li{margin:12px 0}</style>'
                        f'<a href="/lab/">← ProofRipple LAB</a><h1>{title}</h1><ul>'
                        + ''.join(links) + '</ul></html>')
                return self.send(200, body.encode(), "text/html; charset=utf-8")
            if not file.is_file() or file.suffix not in STATIC_SUFFIXES:
                return self.send(404, {"error": "No such workbench asset"})
            content_type = ("application/gzip" if file.suffix == ".gz" else
                            "text/plain; charset=utf-8" if file.suffix in {".py", ".cjs", ".log", ".txt"} else
                            mimetypes.guess_type(file.name)[0] or "application/octet-stream")
            self.send(200, file.read_bytes(), content_type)

        def do_POST(self):
            origin = self.headers.get("Origin")
            bound_port = self.server.server_port
            if not self.allowed() or (origin and origin not in {f"http://127.0.0.1:{bound_port}", f"http://localhost:{bound_port}"}):
                return self.send(403, {"error": "Cross-origin requests are disabled"})
            if self.path not in {"/api/run", "/api/import-declaration"}:
                return self.send(404, {"error": "Unknown endpoint"})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 1_000_000:
                    return self.send(413, {"error": "Request must be 1..1000000 bytes"})
                payload = json.loads(self.rfile.read(size))
                if not isinstance(payload, dict):
                    raise ValueError("Request must be a JSON object")
                from .cli import run_context
                if self.path == "/api/import-declaration":
                    if payload.get("name") == "inf_sup_left":
                        from .mathlib_benchmark import make_example
                    elif payload.get("name") == "List.length_filter_le":
                        from .natural import make_example
                    else:
                        raise ValueError("Supported declarations: inf_sup_left, List.length_filter_le")
                    payload["context"] = make_example()
                run = run_context(payload["context"], payload.get("budget", 8), payload.get("select"), method=payload.get("method"))
                self.send(200, run)
            except (ValueError, KeyError, TypeError) as exc:
                self.send(400, {"error": str(exc)})

    return HTTPServer(("127.0.0.1", port), Handler)


def serve(root, port=8765):
    server = create_server(root, port)
    print(f"PROOFRIPPLE LAB http://127.0.0.1:{server.server_port}/lab/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
