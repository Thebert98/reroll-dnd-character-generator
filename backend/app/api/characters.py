"""Character CRUD. Persistence goes through a JWT-scoped Supabase client so
Postgres RLS guarantees a user only ever touches their own rows.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..auth import CurrentUser, get_current_user
from ..db import user_client
from ..models import CharacterSheet, empty_sheet, sheet_from_dict

router = APIRouter(prefix="/characters", tags=["characters"])


class CharacterCreate(BaseModel):
    name: str = "Untitled"


class CharacterUpdate(BaseModel):
    name: str | None = None
    sheet: dict[str, Any] | None = None


class CharacterOut(BaseModel):
    id: str
    name: str
    sheet: dict[str, Any]
    created_at: str | None = None
    updated_at: str | None = None


@router.get("", response_model=list[CharacterOut])
def list_characters(user: CurrentUser = Depends(get_current_user)):
    db = user_client(user.token)
    res = (
        db.table("characters")
        .select("*")
        .eq("user_id", user.id)
        .order("updated_at", desc=True)
        .execute()
    )
    return res.data or []


@router.post("", response_model=CharacterOut, status_code=status.HTTP_201_CREATED)
def create_character(
    body: CharacterCreate, user: CurrentUser = Depends(get_current_user)
):
    db = user_client(user.token)
    sheet = empty_sheet().model_dump(by_alias=True)
    res = (
        db.table("characters")
        .insert({"user_id": user.id, "name": body.name, "sheet": sheet})
        .execute()
    )
    if not res.data:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Insert failed")
    return res.data[0]


@router.get("/{character_id}", response_model=CharacterOut)
def get_character(character_id: str, user: CurrentUser = Depends(get_current_user)):
    db = user_client(user.token)
    res = db.table("characters").select("*").eq("id", character_id).execute()
    if not res.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Character not found")
    return res.data[0]


@router.put("/{character_id}", response_model=CharacterOut)
def update_character(
    character_id: str,
    body: CharacterUpdate,
    user: CurrentUser = Depends(get_current_user),
):
    db = user_client(user.token)
    patch: dict[str, Any] = {}
    if body.name is not None:
        patch["name"] = body.name
    if body.sheet is not None:
        # Normalize through the schema so stored shape is always consistent.
        sheet: CharacterSheet = sheet_from_dict(body.sheet)
        patch["sheet"] = sheet.model_dump(by_alias=True)
    if not patch:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No fields to update")

    res = (
        db.table("characters")
        .update(patch)
        .eq("id", character_id)
        .execute()
    )
    if not res.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Character not found")
    return res.data[0]


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(character_id: str, user: CurrentUser = Depends(get_current_user)):
    db = user_client(user.token)
    res = db.table("characters").delete().eq("id", character_id).execute()
    if not res.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Character not found")
    return None
