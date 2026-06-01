"""POST /characters/{id}/generate — run the AI pipeline over a sheet.

Loads the character, runs the generation pipeline (locks respected), persists
the merged sheet, and writes a ``generation_runs`` row for every call (even
failed validations). Returns the updated character plus validation errors.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from ..auth import CurrentUser, get_current_user
from ..db import user_client
from ..models import sheet_from_dict
from ..pipeline import generate_character
from ..rag import retrieve_rules
from ..rate_limit import daily_generation_limit, limiter

router = APIRouter(prefix="/characters", tags=["generate"])


class GenerateRequest(BaseModel):
    user_notes: str = ""
    model: str | None = None


class GenerateResponse(BaseModel):
    character: dict[str, Any]
    validation_errors: list[dict]
    run_id: str | None = None
    version_id: str | None = None
    version_number: int | None = None


def _next_version_number(db, character_id: str) -> int:
    res = (
        db.table("character_versions")
        .select("version_number")
        .eq("character_id", character_id)
        .order("version_number", desc=True)
        .limit(1)
        .execute()
    )
    return (res.data[0]["version_number"] + 1) if res.data else 1


@router.post("/{character_id}/generate", response_model=GenerateResponse)
@limiter.limit(daily_generation_limit)
def generate(
    request: Request,
    character_id: str,
    body: GenerateRequest,
    user: CurrentUser = Depends(get_current_user),
):
    db = user_client(user.token)

    res = db.table("characters").select("*").eq("id", character_id).execute()
    if not res.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Character not found")
    character = res.data[0]

    sheet = sheet_from_dict(character["sheet"])

    # Ground generation in the SRD corpus via the user's RLS-scoped client.
    def retriever(query: str) -> list[dict]:
        return retrieve_rules(query, db, k=6)

    merged, trace = generate_character(
        sheet, body.user_notes, model=body.model, retriever=retriever
    )

    merged_dict = merged.model_dump(by_alias=True)
    # Persist the new sheet. Name field, if generated/locked, becomes the title.
    name = merged.name.value or character.get("name") or "Untitled"
    db.table("characters").update({"sheet": merged_dict, "name": name}).eq(
        "id", character_id
    ).execute()

    # Snapshot this generation as an immutable version for history + diff.
    version_id = None
    version_number = _next_version_number(db, character_id)
    ver = (
        db.table("character_versions")
        .insert(
            {
                "character_id": character_id,
                "version_number": version_number,
                "sheet": merged_dict,
            }
        )
        .execute()
    )
    if ver.data:
        version_id = ver.data[0]["id"]

    # Always record the trace, linked to the version it produced.
    run_id = None
    run = db.table("generation_runs").insert(
        trace.to_run_row(character_id, version_id)
    ).execute()
    if run.data:
        run_id = run.data[0]["id"]

    return GenerateResponse(
        character={**character, "sheet": merged_dict, "name": name},
        validation_errors=trace.validation_errors,
        run_id=run_id,
        version_id=version_id,
        version_number=version_number,
    )
