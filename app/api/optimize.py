from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.pipeline.step1_extract import ExtractStep
from app.pipeline.step2_cv_analysis import CVAnalysisStep
from app.pipeline.step3_job_analysis import JobAnalysisStep
from app.pipeline.step4_matching import MatchingStep
from app.pipeline.step5_strategy import StrategyStep
from app.pipeline.step6_cv_writer import CVWriterStep
from app.pipeline.step7_cover_letter import CoverLetterStep
from app.pipeline.step8_quality import QualityStep
from app.pipeline.step9_report import ReportStep
from app.models.report import Report

router = APIRouter()

class OptimizeRequest(BaseModel):
    cv_text: str
    job_text: str

@router.post("/optimize", response_model=Report)
def optimize_candidacy(request: OptimizeRequest):
    """
    Point d'entrée principal de la pipeline.
    Reçoit le texte du CV et de l'offre, retourne le rapport complet.
    """
    try:
        # 1. Extraction & Analyse
        cv = ExtractStep().execute(request.cv_text)
        cv_analysis = CVAnalysisStep().execute(cv)
        job = JobAnalysisStep().execute(request.job_text)

        # 2. Matching & Stratégie
        matching = MatchingStep().execute(cv, cv_analysis, job)
        strategy = StrategyStep().execute(cv_analysis, job, matching)

        # 3. Génération
        cv_rewritten = CVWriterStep().execute(cv, strategy, job)
        letter = CoverLetterStep().execute(cv, cv_rewritten, strategy, job)

        # 4. Qualité & Rapport
        quality = QualityStep().execute(cv, cv_rewritten, letter, matching, job)
        report = ReportStep().execute(cv_rewritten, letter, matching, strategy, quality)

        return report

    except Exception as e:
        # En cas d'erreur dans la pipeline (ex: IA qui renvoie un mauvais JSON)
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'optimisation: {str(e)}")