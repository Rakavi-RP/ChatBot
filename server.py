import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"
ENV_PATH = BASE_DIR / ".env"

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
}


def load_env(path):
    env = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip('"').strip("'")
    return env


ENV = load_env(ENV_PATH)
API_KEY = ENV.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
MODEL_NAME = ENV.get("GEMINI_MODEL") or os.environ.get("GEMINI_MODEL") or "gemini-2.5-flash"
SYSTEM_PROMPT = ENV.get("SYSTEM_PROMPT") or os.environ.get("SYSTEM_PROMPT") or ""

if not API_KEY:
    print("WARNING: GEMINI_API_KEY is not set. Add it to .env and restart the server.")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = "/index.html" if self.path == "/" else self.path.split("?", 1)[0]
        safe_path = os.path.normpath(path).lstrip("/\\")
        file_path = (PUBLIC_DIR / safe_path).resolve()

        if file_path != PUBLIC_DIR and PUBLIC_DIR not in file_path.parents:
            self.send_error(403)
            return
        if not file_path.is_file():
            self.send_error(404)
            return

        content_type = CONTENT_TYPES.get(file_path.suffix, "application/octet-stream")
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_error(404)
            return

        if not API_KEY:
            self._send_json(500, {"error": "Server is missing GEMINI_API_KEY. Add it to .env and restart."})
            return

        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON body"})
            return

        message = (payload.get("message") or "").strip()
        history = payload.get("history") or []
        if not message:
            self._send_json(400, {"error": "message is required"})
            return

        contents = history + [{"role": "user", "parts": [{"text": message}]}]
        body = {"contents": contents}
        if SYSTEM_PROMPT:
            body["systemInstruction"] = {"parts": [{"text": SYSTEM_PROMPT}]}

        req = urllib.request.Request(
            f"{GEMINI_URL}?key={API_KEY}",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore")
            try:
                message_text = json.loads(error_body).get("error", {}).get("message", error_body)
            except json.JSONDecodeError:
                message_text = error_body
            self._send_json(e.code, {"error": message_text})
            return
        except urllib.error.URLError as e:
            self._send_json(502, {"error": f"Could not reach Gemini API: {e.reason}"})
            return

        candidates = data.get("candidates") or []
        reply = ""
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            reply = "".join(p.get("text", "") for p in parts)
        reply = reply or "(empty response)"

        contents.append({"role": "model", "parts": [{"text": reply}]})
        self._send_json(200, {"reply": reply, "history": contents})

    def log_message(self, format, *args):
        pass


def main():
    port = int(os.environ.get("PORT", 8000))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Serving on http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
