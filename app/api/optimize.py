import json
from collections.abc import AsyncIterator
from typing import Literal

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.exceptions import LLMResponseValidationError, LLMUpstreamError
from app.models.report import Report
from app.pipeline.pipeline import Pipeline

router = APIRouter()

_ERROR_LABELS = {
    "fr": {
        "llm_upstream_error": "Erreur du fournisseur IA",
        "llm_invalid_response": "Réponse IA invalide",
    },
    "en": {
        "llm_upstream_error": "AI provider error",
        "llm_invalid_response": "Invalid AI response",
    },
}


class OptimizeRequest(BaseModel):
    cv_text: str = Field(min_length=50, max_length=20000)
    job_text: str = Field(min_length=50, max_length=20000)
    language: Literal["fr", "en"] = "fr"


@router.post("/optimize", response_model=Report)
async def optimize_candidacy(request: OptimizeRequest):
    """
    Point d'entrée principal de la pipeline.
    Reçoit le texte du CV et de l'offre, retourne le rapport complet.

    Les erreurs LLM (upstream ou réponse invalide) sont gérées par les
    handlers d'exceptions globaux définis dans app.main.
    """
    report: Report | None = None

    async for event in Pipeline().run(request.cv_text, request.job_text, request.language):
        if event["step"] == "complete":
            report = event["report"]

    return report


def _sse_pack(event: dict) -> str:
    payload = dict(event)
    report = payload.get("report")
    if report is not None:
        payload["report"] = report.model_dump() if hasattr(report, "model_dump") else report
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/optimize/stream")
async def optimize_candidacy_stream(request: OptimizeRequest):
    """
    Variante streamée de /optimize : envoie un événement Server-Sent Events
    (SSE) à chaque étape terminée du pipeline, pour afficher une progression
    en direct côté client plutôt qu'un simple spinner. Le dernier événement
    ("complete") contient le rapport final.
    """
    labels = _ERROR_LABELS.get(request.language, _ERROR_LABELS["fr"])

    async def event_stream() -> AsyncIterator[str]:
        try:
            async for event in Pipeline().run(request.cv_text, request.job_text, request.language):
                yield _sse_pack(event)
        except LLMUpstreamError as exc:
            yield _sse_pack(
                {
                    "step": "error",
                    "status": "error",
                    "label": labels["llm_upstream_error"],
                    "detail": str(exc),
                    "error_code": "llm_upstream_error",
                }
            )
        except LLMResponseValidationError as exc:
            yield _sse_pack(
                {
                    "step": "error",
                    "status": "error",
                    "label": labels["llm_invalid_response"],
                    "detail": str(exc),
                    "error_code": "llm_invalid_response",
                }
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
