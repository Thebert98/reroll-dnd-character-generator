"""Export a character as JSON or a PDF that looks like a real sheet."""
from __future__ import annotations

import io
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, StreamingResponse

from ..auth import CurrentUser, get_current_user
from ..db import user_client
from ..models import SHEET_FIELDS, sheet_from_dict

router = APIRouter(prefix="/characters", tags=["export"])

_LABELS = {
    "name": "Name", "race": "Race", "char_class": "Class",
    "background": "Background", "alignment": "Alignment", "level": "Level",
    "stats": "Ability Scores", "proficiencies": "Proficiencies",
    "spells": "Spells", "equipment": "Equipment", "backstory": "Backstory",
    "personality": "Personality",
}


def _load(character_id: str, user: CurrentUser):
    db = user_client(user.token)
    res = db.table("characters").select("*").eq("id", character_id).execute()
    if not res.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Character not found")
    return res.data[0]


@router.get("/{character_id}/export.json")
def export_json(character_id: str, user: CurrentUser = Depends(get_current_user)):
    character = _load(character_id, user)
    body = json.dumps(character, indent=2, default=str)
    return Response(
        content=body,
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="{character["name"]}.json"'
        },
    )


def _fmt(value) -> str:
    if isinstance(value, dict):
        return ", ".join(f"{k.upper()} {v}" for k, v in value.items())
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else "—"
    return str(value) if value not in (None, "") else "—"


@router.get("/{character_id}/export.pdf")
def export_pdf(character_id: str, user: CurrentUser = Depends(get_current_user)):
    # Imported lazily so the rest of the app doesn't hard-depend on reportlab.
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    )

    character = _load(character_id, user)
    sheet = sheet_from_dict(character["sheet"])

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "title", parent=styles["Title"], textColor=colors.HexColor("#6d4aff")
    )
    story = [
        Paragraph(character["name"] or "Untitled", title_style),
        Paragraph(
            f"{_fmt(sheet.race.value)} {_fmt(sheet.char_class.value)} · "
            f"Level {_fmt(sheet.level.value)} · {_fmt(sheet.alignment.value)}",
            styles["Normal"],
        ),
        Spacer(1, 0.25 * inch),
    ]

    rows = [[_LABELS[f], _fmt(getattr(sheet, f).value)] for f in SHEET_FIELDS]
    table = Table(rows, colWidths=[1.6 * inch, 5.0 * inch])
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#6d4aff")),
                ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.3 * inch))
    story.append(
        Paragraph(
            "Generated with Re:Roll — Character Builder. Rules from SRD 5.1 (CC-BY-4.0).",
            ParagraphStyle("foot", parent=styles["Italic"], fontSize=8,
                           textColor=colors.grey),
        )
    )
    doc.build(story)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{character["name"]}.pdf"'
        },
    )
