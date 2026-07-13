import re

from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel

from app.models.cv import CV
from app.models.letter import Letter
from app.services.pdf_service import render_cv_pdf, render_letter_pdf

router = APIRouter(prefix="/export", tags=["export"])

_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9_-]+")


class LetterSender(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    city: str | None = None
    linkedin: str | None = None


class LetterExportRequest(BaseModel):
    letter: Letter
    sender: LetterSender = LetterSender()


def _filename(*parts: str | None, fallback: str) -> str:
    name = "_".join(p for p in parts if p) or fallback
    safe = _UNSAFE_FILENAME_CHARS.sub("_", name).strip("_") or fallback
    return f"{safe}.pdf"


def _pdf_response(pdf_bytes: bytes, filename: str) -> Response:
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/cv-pdf")
def export_cv_pdf(cv: CV):
    pdf_bytes = render_cv_pdf(cv)
    filename = _filename("CV", cv.first_name, cv.last_name, fallback="CV")
    return _pdf_response(pdf_bytes, filename)


@router.post("/letter-pdf")
def export_letter_pdf(request: LetterExportRequest):
    pdf_bytes = render_letter_pdf(request.letter, request.sender)
    filename = _filename(
        "Lettre_motivation", request.sender.first_name, request.sender.last_name,
        fallback="Lettre_motivation",
    )
    return _pdf_response(pdf_bytes, filename)
