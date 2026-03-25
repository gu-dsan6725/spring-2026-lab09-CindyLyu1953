"""
FastAPI wrapper around the memory-enabled Agent from agent.py.

Provides multi-tenant isolation via user_id and session continuity via run_id,
with one Agent instance cached per (user_id, run_id) pair.
"""

from __future__ import annotations

import os
import uuid
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agent import Agent

load_dotenv()

app = FastAPI(
    title="Memory Agent API",
    description="Multi-tenant conversational agent with semantic memory",
    version="1.0.0",
)

# One Agent per user/session; key avoids collisions if two users reuse the same run_id string.
_session_cache: Dict[str, Agent] = {}


def _cache_key(user_id: str, run_id: str) -> str:
    return f"{user_id}::{run_id}"


def _get_or_create_agent(user_id: str, run_id: str) -> Agent:
    key = _cache_key(user_id, run_id)
    if key in _session_cache:
        return _session_cache[key]
    agent = Agent(user_id=user_id, run_id=run_id)
    _session_cache[key] = agent
    return agent


class InvocationRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="User identifier for memory isolation")
    run_id: Optional[str] = Field(
        default=None,
        description="Session id; auto-generated if omitted",
    )
    query: str = Field(..., min_length=1, description="User message")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional tags/context (accepted for API compatibility)",
    )


class InvocationResponse(BaseModel):
    response: str
    run_id: str


class PingResponse(BaseModel):
    status: str
    message: str


@app.get("/ping", response_model=PingResponse)
def ping() -> PingResponse:
    return PingResponse(status="ok", message="Memory Agent API is running")


@app.post("/invocation", response_model=InvocationResponse)
def invocation(body: InvocationRequest) -> InvocationResponse:
    run_id = body.run_id or str(uuid.uuid4())[:8]
    try:
        agent = _get_or_create_agent(body.user_id, run_id)
        text = agent.chat(body.query.strip())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return InvocationResponse(response=text, run_id=run_id)
