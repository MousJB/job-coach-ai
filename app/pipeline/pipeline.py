import asyncio
import hashlib
import logging
import time
from collections.abc import AsyncIterator

from app.models.report import Report
from app.pipeline.step1_extract import ExtractStep
from app.pipeline.step2_cv_analysis import CVAnalysisStep
from app.pipeline.step3_job_analysis import JobAnalysisStep
from app.pipeline.step4_matching import MatchingStep
from app.pipeline.step5_strategy import StrategyStep
from app.pipeline.step6_cv_writer import CVWriterStep
from app.pipeline.step7_cover_letter import CoverLetterStep
from app.pipeline.step8_quality import QualityStep
from app.pipeline.step9_report import ReportStep
from app.services.cache import pipeline_cache

logger = logging.getLogger(__name__)

STEP_LABELS: dict[str, str] = {
    "extract_cv": "Analyse du CV",
    "analyze_job": "Analyse de l'offre d'emploi",
    "cv_analysis": "Évaluation du profil",
    "matching": "Calcul du score de compatibilité",
    "strategy": "Définition de la stratégie",
    "cv_rewrite": "Réécriture du CV",
    "cover_letter": "Rédaction de la lettre de motivation",
    "quality_check": "Contrôle qualité",
    "report": "Finalisation du rapport",
}


def _cache_key(cv_text: str, job_text: str) -> str:
    digest = hashlib.sha256()
    digest.update(cv_text.encode("utf-8"))
    digest.update(b"\x00")
    digest.update(job_text.encode("utf-8"))
    return digest.hexdigest()


class Pipeline:
    """
    Orchestrateur du pipeline d'optimisation de candidature.

    Exécute les 9 étapes en respectant leurs vraies dépendances plutôt qu'une
    chaîne strictement séquentielle : l'extraction du CV et l'analyse de
    l'offre n'ont aucune dépendance croisée et tournent en parallèle, tout
    comme l'analyse qualitative du CV (qui ne dépend que de l'extraction).
    """

    async def run(self, cv_text: str, job_text: str) -> AsyncIterator[dict]:
        cache_key = _cache_key(cv_text, job_text)
        cached_report = pipeline_cache.get(cache_key)
        if cached_report is not None:
            logger.info("pipeline cache hit")
            yield {
                "step": "complete",
                "label": STEP_LABELS["report"],
                "status": "done",
                "cached": True,
                "report": cached_report,
            }
            return

        start = time.perf_counter()

        async def run_step(coro, step_key: str):
            step_start = time.perf_counter()
            result = await coro
            logger.info(
                "step=%s duration_ms=%d",
                step_key,
                int((time.perf_counter() - step_start) * 1000),
            )
            return result

        def event(step_key: str) -> dict:
            return {"step": step_key, "label": STEP_LABELS[step_key], "status": "done"}

        # Round A : extraction CV et analyse de l'offre n'ont aucune dépendance
        # croisée, elles démarrent donc en même temps.
        extract_task = asyncio.create_task(run_step(ExtractStep().execute(cv_text), "extract_cv"))
        job_task = asyncio.create_task(run_step(JobAnalysisStep().execute(job_text), "analyze_job"))

        cv = await extract_task
        yield event("extract_cv")

        # L'analyse qualitative du CV ne dépend que de l'extraction, pas de
        # l'offre : elle continue de tourner pendant que job_task termine.
        cv_analysis = await run_step(CVAnalysisStep().execute(cv), "cv_analysis")
        yield event("cv_analysis")

        job = await job_task
        yield event("analyze_job")

        matching = await run_step(MatchingStep().execute(cv, cv_analysis, job), "matching")
        yield event("matching")

        strategy = await run_step(StrategyStep().execute(cv_analysis, job, matching), "strategy")
        yield event("strategy")

        cv_rewritten = await run_step(CVWriterStep().execute(cv, strategy, job), "cv_rewrite")
        yield event("cv_rewrite")

        letter = await run_step(
            CoverLetterStep().execute(cv, cv_rewritten, strategy, job), "cover_letter"
        )
        yield event("cover_letter")

        quality = await run_step(
            QualityStep().execute(cv, cv_rewritten, letter, matching, job), "quality_check"
        )
        yield event("quality_check")

        report: Report = await ReportStep().execute(cv_rewritten, letter, matching, strategy, quality)

        logger.info("pipeline total duration_ms=%d", int((time.perf_counter() - start) * 1000))

        pipeline_cache.set(cache_key, report)

        yield {
            "step": "complete",
            "label": STEP_LABELS["report"],
            "status": "done",
            "cached": False,
            "report": report,
        }


pipeline = Pipeline()
