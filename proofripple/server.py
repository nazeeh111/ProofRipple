"""Loopback-only workbench server. No arbitrary filesystem or Lean execution API."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import mimetypes
from pathlib import Path
from urllib.parse import urlparse


def serve(root, port=8765):
    root = Path(root).resolve()
    class Handler(BaseHTTPRequestHandler):
        def allowed(self):
            return self.headers.get("Host") in {f"127.0.0.1:{port}", f"localhost:{port}"}

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
            path = urlparse(self.path).path
            if path in ("/", "/lab", "/lab/"):
                path = "/lab/index.html"
            file = (root / path.lstrip("/")).resolve()
            if not any(file.is_relative_to(root / folder) for folder in ("lab", "examples", "artifacts", "docs")) or not file.is_file():
                return self.send(404, {"error": "No such workbench asset"})
            if file.suffix not in {".html", ".js", ".css", ".svg", ".json", ".lean", ".png", ".mp4", ".md"}:
                return self.send(404, {"error": "Unsupported asset type"})
            self.send(200, file.read_bytes(), mimetypes.guess_type(file.name)[0] or "text/plain")

        def do_POST(self):
            origin = self.headers.get("Origin")
            if not self.allowed() or (origin and origin not in {f"http://127.0.0.1:{port}", f"http://localhost:{port}"}):
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
                    if payload.get("name") != "List.length_filter_le":
                        raise ValueError("Supported declaration: List.length_filter_le")
                    from .natural import make_example
                    payload["context"] = make_example()
                run = run_context(payload["context"], payload.get("budget", 8), payload.get("select"), method=payload.get("method"))
                self.send(200, run)
            except (ValueError, KeyError, TypeError) as exc:
                self.send(400, {"error": str(exc)})

    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"PROOFRIPPLE LAB http://127.0.0.1:{port}/lab/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
