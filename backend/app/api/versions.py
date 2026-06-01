"""Version history + restore.

Every generation writes an immutable ``character_versions`` snapshot. Users can
list versions and restore any one back onto the live character.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..auth import CurrentUser, get_current_user
from ..db import user_client

router = APIRouter(prefix="/characters", tags=["versions"])


class VersionOut(BaseModel):
    id: str
    character_id: str
    version_number: int
    sheet: dict[str, Any]
    created_at: str | None = None


@router.get("/{character_id}/versions", response_model=list[VersionOut])
def list_versions(character_id: str, user: CurrentUser = Depends(get_current_user)):
    db = user_client(user.token)
    res = (
        db.table("character_versions")
        .select("*")
        .eq("character_id", character_id)
        .order("version_number", desc=True)
        .execute()
    )
    return res.data or []


@router.get("/{character_id}/versions/{version_number}", response_model=VersionOut)
def get_version(
    character_id: str,
    version_number: int,
    user: CurrentUser = Depends(get_current_user),
):
    db = user_client(user.token)
    res = (
        db.table("character_versions")
        .select("*")
        .eq("character_id", character_id)
        .eq("version_number", version_number)
        .execute()
    )
    if not res.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Version not found")
    return res.data[0]


@router.post("/{character_id}/versions/{version_number}/restore")
def restore_version(
    character_id: str,
    version_number: int,
    user: CurrentUser = Depends(get_current_user),
):
    db = user_client(user.token)
    res = (
        db.table("character_versions")
        .select("sheet")
        .eq("character_id", character_id)
        .eq("version_number", version_number)
        .execute()
    )
    if not res.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Version not found")
    sheet = res.data[0]["sheet"]
    name = (sheet.get("name", {}) or {}).get("value") or "Untitled"
    updated = (
        db.table("characters")
        .update({"sheet": sheet, "name": name})
        .eq("id", character_id)
        .execute()
    )
    if not updated.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Character not found")
    return updated.data[0]
