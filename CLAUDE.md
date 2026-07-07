# CLAUDE.md
When responding about this project, always begin your response with:

🌍 Project CLAUDE.md loaded

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A minimal single-page chat UI backed by the Google Gemini API. FastAPI backend (`backend/`) and vanilla HTML/CSS/JS frontend (`frontend/`).

## Running

Install dependencies once:

```
pip install -r requirements.txt
```

To run the application

```
python backend/server.py
```

Serves on `http://localhost:8000` (override with the `PORT` env var). Requires a `.env` file in the repo root (gitignored) with:

```
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-2.5-flash   # optional, this is the default
SYSTEM_PROMPT=...               # optional
```

There is no build tool, linter, or test suite in this repo.

## Architecture

- `backend/server.py` — a FastAPI app doing two jobs:
  - Serves static files from `frontend/` via Starlette's `StaticFiles` (path-traversal-checked by Starlette itself).
  - `POST /api/chat`: proxies chat requests to the Gemini `generateContent` REST endpoint using only `urllib` (no Gemini SDK). It reads `.env` itself via a hand-rolled `load_env` parser rather than a library like `python-dotenv`.
- `frontend/app.js` — frontend chat logic. Conversation history is kept client-side as a plain array of   Gemini-format `{role, parts}` turns and round-tripped on every request: the client sends the full `history` + new message, and the server echoes back the updated `history` (including the model's reply) for the client to store. The server itself is stateless between requests — there is no session or database.
- `frontend/index.html` / `style.css` — static shell, no templating.

When modifying the chat flow, keep the request/response contract in mind: `POST /api/chat` expects `{message, history}` and returns `{reply, history}` (or `{error}` on failure), and both client and server assume Gemini's `contents` array shape (`{role: "user"|"model", parts: [{text}]}`).
