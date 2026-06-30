from pydantic import BaseModel, Field


class Job(BaseModel):

    title: str | None = None

    company: str | None = None

    location: str | None = None

    contract: str | None = None

    description: str | None = None

    required_skills: list[str] = Field(default_factory=list)

    preferred_skills: list[str] = Field(default_factory=list)

    responsibilities: list[str] = Field(default_factory=list)

    keywords: list[str] = Field(default_factory=list)