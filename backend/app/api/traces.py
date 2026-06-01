"""Trace viewer data: read ``generation_runs`` rows.

The trace viewer is the project's highest-leverage "wow" feature — it exposes
the locked constraints, retrieved chunks, the assembled prompt, raw model
output, validation results, and token/cost/latency for any generation.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..auth import CurrentUser, get_current_user
from ..db import user_client

router = APIRouter(tags=["traces"])


class RunSummary(BaseModel):
    id: str
    character_id: str
    version_id: str | None = None
    model: str
    locked_fields: list[str]
    validation_errors: list[dict] | None = None
    latency_ms: int | None = None
    cost_usd: float | None = None
    created_at: str | None = None


@router.get("/characters/{character_id}/runs", response_model=list[RunSummary])
def list_runs(character_id: str, user: CurrentUser = Depends(get_current_user)):
    db = user_client(user.token)
    res = (
        db.table("generation_runs")
        .select(
            "id,character_id,version_id,model,locked_fields,"
            "validation_errors,latency_ms,cost_usd,created_at"
        )
        .eq("character_id", character_id)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


@router.get("/runs/{run_id}")
def get_run(run_id: str, user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    """Full trace for one run. RLS ensures the caller owns the parent character."""
    db = user_client(user.token)
    res = db.table("generation_runs").select("*").eq("id", run_id).execute()
    if not res.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Run not found")
    return res.data[0]
