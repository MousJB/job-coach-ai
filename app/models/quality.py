from pydantic import BaseModel, Field


class QualityCheck(BaseModel):

    approved: bool

    # Le score "avant" provient uniquement de l'étape de matching (Matching.ats_score) :
    # le contrôle qualité ne recalcule pas de score concurrent, il ne fait que valider.
    score_after: int | None = None

    hallucinations_detected: list[str] = Field(default_factory=list)

    inconsistencies: list[str] = Field(default_factory=list)

    improvements_made: list[str] = Field(default_factory=list)

    warnings: list[str] = Field(default_factory=list)

    final_recommendation: str | None = None