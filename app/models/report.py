from pydantic import BaseModel, Field

from app.models.cv import CV
from app.models.letter import Letter
from app.models.matching import Matching
from app.models.quality import QualityCheck
from app.models.strategy import Strategy


class Report(BaseModel):

    # Scores
    score_before: int | None = None
    score_after: int | None = None

    # Résumé du matching
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)

    # Documents produits
    cv_rewritten: CV | None = None
    letter: Letter | None = None

    # Stratégie appliquée
    strategy: Strategy | None = None

    # Qualité
    quality: QualityCheck | None = None

    # Résumé global pour l'utilisateur
    summary_for_user: str | None = None

    # Actions recommandées à l'utilisateur
    next_steps: list[str] = Field(default_factory=list)