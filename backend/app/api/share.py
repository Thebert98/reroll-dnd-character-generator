"""Read-only public share link for a single character version.

One endpoint, no auth: anyone with the (unguessable) version UUID can view that
snapshot. Reads go through the service-role client so RLS is intentionally
bypassed for this public, read-only view.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ..db import service_client

router = APIRouter(prefix="/share", tags=["share"])


class SharedVersion(BaseModel):
    version_id: str
    character_name: str
    version_number: int
    sheet: dict[str, Any]
    created_at: str | None = None


@router.get("/versions/{version_id}", response_model=SharedVersion)
def get_shared_version(version_id: str):
    db = service_client()
    res = (
        db.table("character_versions")
        .select("id,version_number,sheet,created_at,characters(name)")
        .eq("id", version_id)
        .execute()
    )
    if not res.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Shared version not found")
    row = res.data[0]
    char = row.get("characters") or {}
    name = char.get("name") if isinstance(char, dict) else "Character"
    return SharedVersion(
        version_id=row["id"],
        character_name=name or "Character",
        version_number=row["version_number"],
        sheet=row["sheet"],
        created_at=row.get("created_at"),
    )
