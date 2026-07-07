# CLAUDE.md
When responding about this project, always begin your response with:

🌍 Project CLAUDE.md loaded

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A minimal single-page chat UI backed by the Google Gemini API. No frameworks, no build step, no dependencies — pure Python 3 stdlib server and vanilla HTML/CSS/JS frontend.

## Running

```
python server.py
```

Serves on `http://localhost:8000` (override with the `PORT` env var). Requires a `.env` file in the repo root (gitignored) with:

```
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-2.5-flash   # optional, this is the default
SYSTEM_PROMPT=...               # optional
```

There is no package manager, build tool, linter, or test suite in this repo — nothing to install.

## Architecture

- `server.py` — a single `ThreadingHTTPServer` handler doing two jobs:
  - `do_GET`: serves static files from `public/` (path-traversal-checked against `PUBLIC_DIR`).
  - `do_POST` on `/api/chat`: proxies chat requests to the Gemini `generateContent` REST endpoint using only `urllib` (no SDK). It reads `.env` itself via a hand-rolled `load_env` parser rather than a library like `python-dotenv`.
- `public/app.js` — frontend chat logic. Conversation history is kept client-side as a plain array of   Gemini-format `{role, parts}` turns and round-tripped on every request: the client sends the full `history` + new message, and the server echoes back the updated `history` (including the model's reply) for the client to store. The server itself is stateless between requests — there is no session or database.
- `public/index.html` / `style.css` — static shell, no templating.

When modifying the chat flow, keep the request/response contract in mind: `POST /api/chat` expects `{message, history}` and returns `{reply, history}` (or `{error}` on failure), and both client and server assume Gemini's `contents` array shape (`{role: "user"|"model", parts: [{text}]}`).
