import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

API_KEY = os.getenv("API_KEY", "")
N8N_WEBHOOK_URL = os.getenv(
    "N8N_WEBHOOK_URL",
    "https://colt-flavoring-avenge.ngrok-free.dev/webhook/a6f8a4b8-2d53-4bcf-b3e7-75137a5a1f2f",
)

N8N_TIMEOUT_SECONDS = 60.0

app = FastAPI(title="CLN Chat API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The question to ask")
    sessionId: str | None = Field(default=None, description="Optional conversation id for memory")


def _check_api_key(x_api_key: str | None) -> None:
    if not API_KEY or not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat")
async def chat(payload: ChatRequest, x_api_key: str | None = Header(default=None)) -> dict:
    _check_api_key(x_api_key)

    forward_body: dict = {"question": payload.question}
    if payload.sessionId:
        forward_body["sessionId"] = payload.sessionId

    try:
        async with httpx.AsyncClient(timeout=N8N_TIMEOUT_SECONDS) as client:
            resp = await client.post(N8N_WEBHOOK_URL, json=forward_body)
    except httpx.HTTPError:
        return {"isSuccess": False, "message": "Upstream chat service unavailable"}

    if resp.status_code != 200:
        return {"isSuccess": False, "message": f"Upstream chat service returned status {resp.status_code}"}

    try:
        data = resp.json()
    except ValueError:
        return {"isSuccess": False, "message": "Upstream chat service returned invalid JSON"}

    return {"isSuccess": True, "message": data.get("answer")}