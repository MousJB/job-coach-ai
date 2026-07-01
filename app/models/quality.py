from pydantic import BaseModel, Field


class QualityCheck(BaseModel):

    approved: bool

    score_before: int | None = None
    score_after: int | None = None

    hallucinations_detected: list[str] = Field(default_factory=list)

    inconsistencies: list[str] = Field(default_factory=list)

    improvements_made: list[str] = Field(default_factory=list)

    warnings: list[str] = Field(default_factory=list)

    final_recommendation: str | None = None