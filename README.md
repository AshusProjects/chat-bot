# CLN Chat API

FastAPI backend that forwards user questions to an n8n workflow and returns the generated answer. It acts as a thin proxy between chat clients and the n8n webhook, with API-key authentication and optional conversation memory.

## Features

- `POST /chat` endpoint that forwards questions to an n8n webhook
- API-key authentication via the `X-API-Key` header
- Conversation memory via an optional `sessionId`
- CORS enabled (allows the static HTML frontend to call the API)
- `/health` health-check endpoint

## Project Structure

```
main.py           FastAPI app: chat/health endpoints, auth, n8n forwarding
n8n.py            (placeholder)
requirements.txt  Python dependencies
.env              Configuration (API_KEY, N8N_WEBHOOK_URL)
```

## Requirements

- Python 3.10+
- Packages listed in `requirements.txt`

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   source .venv/bin/activate   # macOS/Linux
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure `.env`:

   ```env
   API_KEY=your_api_key_here
   N8N_WEBHOOK_URL=https://your-n8n-webhook-url
   ```

## Running

```bash
uvicorn main:app --reload
```

The server runs at `http://127.0.0.1:8000`.

## API Reference

### `GET /health`

Returns service health.

```bash
curl http://127.0.0.1:8000/health
```

Response: `{"status": "ok"}`

### `POST /chat`

Sends a question to the n8n chat workflow.

**Headers**

| Header      | Value              |
|-------------|--------------------|
| `X-API-Key` | Must match `API_KEY` |

**Body**

| Field       | Type   | Required | Description                                 |
|-------------|--------|----------|---------------------------------------------|
| `question`  | string | yes      | The question to ask                         |
| `sessionId` | string | no       | Optional conversation id for memory         |

**Example**

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{"question": "How many customers are in CLN?", "sessionId": "web-12345"}'
```

**Response**

```json
{"isSuccess": true, "message": "There are 1,234 customers."}
```

On failure (`isSuccess: false`) `message` contains an error description, e.g. invalid/missing API key (401) or an upstream n8n error.

## Configuration

| Variable           | Description                                  |
|--------------------|----------------------------------------------|
| `API_KEY`          | API key required for `POST /chat`            |
| `N8N_WEBHOOK_URL`  | n8n webhook URL that the chat workflow listens on |