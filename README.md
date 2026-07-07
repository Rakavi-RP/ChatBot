# Chatbot

A minimal single-page chat UI backed by the Google Gemini API. No frameworks, no build step, no dependencies — pure Python 3 stdlib server and vanilla HTML/CSS/JS frontend.

## Setup

1. Create a `.env` file in the repo root:

   ```
   GEMINI_API_KEY=your-key-here
   GEMINI_MODEL=gemini-2.5-flash   # optional, this is the default
   SYSTEM_PROMPT=...               # optional
   ```

2. Run the server:

   To run the application
   ```
   python backend/server.py
   ```

3. Open `http://localhost:8000` in your browser.

The port can be overridden with the `PORT` environment variable. There is no package manager, build tool, linter, or test suite — nothing to install.

## Architecture

- **`backend/server.py`** — a single `ThreadingHTTPServer` handler doing two jobs:
  - `do_GET`: serves static files from `frontend/` (path-traversal-checked).
  - `do_POST` on `/api/chat`: proxies chat requests to the Gemini `generateContent` REST endpoint using only `urllib` (no SDK). It reads `.env` itself via a hand-rolled parser rather than a library like `python-dotenv`.
- **`frontend/app.js`** — frontend chat logic. Conversation history is kept client-side as a plain array of Gemini-format `{role, parts}` turns and round-tripped on every request: the client sends the full `history` plus the new message, and the server echoes back the updated `history` (including the model's reply). The server itself is stateless between requests — no session or database.
- **`frontend/index.html`** / **`frontend/style.css`** — static shell, no templating.

## API

`POST /api/chat`

Request:
```json
{ "message": "hello", "history": [] }
```

Response:
```json
{ "reply": "...", "history": [ { "role": "user", "parts": [{ "text": "hello" }] }, { "role": "model", "parts": [{ "text": "..." }] } ] }
```

On failure, returns `{ "error": "..." }` with an appropriate status code.
