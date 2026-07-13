import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.export import router as export_router
from app.api.health import router as health_router
from app.api.optimize import router as optimize_router
from app.config import ALLOWED_ORIGINS
from app.exceptions import LLMResponseValidationError, LLMUpstreamError
from app.utils.logger import configure_logging

configure_logging()

logger = logging.getLogger(__name__)

app = FastAPI(title="Job Coach API")

# Origines autorisées via la variable d'env ALLOWED_ORIGINS (liste séparée par
# des virgules) ; repli sur les origines par défaut (Vercel + dev local) si absente.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrement des routes
app.include_router(health_router)
app.include_router(optimize_router)
app.include_router(export_router)


@app.exception_handler(LLMUpstreamError)
async def llm_upstream_error_handler(request: Request, exc: LLMUpstreamError):
    logger.error("LLM upstream error: %s", exc)
    return JSONResponse(
        status_code=502,
        content={"detail": str(exc), "error_code": "llm_upstream_error"},
    )


@app.exception_handler(LLMResponseValidationError)
async def llm_validation_error_handler(request: Request, exc: LLMResponseValidationError):
    logger.error("LLM response validation error: %s", exc)
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc), "error_code": "llm_invalid_response"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur.", "error_code": "internal_error"},
    )


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Job Coach API is running 🚀"
    }
