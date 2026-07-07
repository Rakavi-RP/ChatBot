import json
import os
import urllib.error
import urllib.request
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_DIR = BASE_DIR / "frontend"
ENV_PATH = BASE_DIR / ".env"


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

app = FastAPI()


@app.post("/api/chat")
async def chat(request: Request):
    if not API_KEY:
        return JSONResponse(
            {"error": "Server is missing GEMINI_API_KEY. Add it to .env and restart."}, status_code=500
        )

    try:
        payload = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    message = (payload.get("message") or "").strip()
    history = payload.get("history") or []
    if not message:
        return JSONResponse({"error": "message is required"}, status_code=400)

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
        return JSONResponse({"error": message_text}, status_code=e.code)
    except urllib.error.URLError as e:
        return JSONResponse({"error": f"Could not reach Gemini API: {e.reason}"}, status_code=502)

    candidates = data.get("candidates") or []
    reply = ""
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        reply = "".join(p.get("text", "") for p in parts)
    reply = reply or "(empty response)"

    contents.append({"role": "model", "parts": [{"text": reply}]})
    return JSONResponse({"reply": reply, "history": contents})


app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="frontend")


def main():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")


if __name__ == "__main__":
    main()
