from pydantic import BaseModel, Field


class Strategy(BaseModel):

    skills_to_highlight: list[str] = Field(default_factory=list)

    experiences_to_highlight: list[int] = Field(default_factory=list)

    keywords_to_add: list[str] = Field(default_factory=list)

    projects_to_mention: list[str] = Field(default_factory=list)

    writing_style: str | None = None