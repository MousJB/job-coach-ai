from pydantic import BaseModel, Field


class CVAnalysis(BaseModel):

    overall_seniority: str | None = None  # "junior", "mid", "senior", "lead"

    years_of_experience: float | None = None

    career_consistency: str | None = None  # "linéaire", "diversifié", "reconversion"

    main_domain: str | None = None  # ex: "développement web", "data science"

    top_skills: list[str] = Field(default_factory=list)

    strengths: list[str] = Field(default_factory=list)

    weaknesses: list[str] = Field(default_factory=list)

    career_progression_summary: str | None = None

    red_flags: list[str] = Field(default_factory=list)  # usage interne uniquement, jamais affiché à l'utilisateur