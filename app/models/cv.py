from pydantic import BaseModel, Field, field_validator


class Experience(BaseModel):
    company: str | None = None
    position: str | None = None
    start_date: str | None = None
    end_date: str | None = None

    description: str | None = None

    technologies: list[str] = Field(default_factory=list)

    achievements: list[str] = Field(default_factory=list)

    @field_validator("description", mode="before")
    @classmethod
    def join_description_if_list(cls, v):
        if isinstance(v, list):
            return ". ".join(str(item).rstrip(".") for item in v) + "."
        return v


class Education(BaseModel):
    school: str | None = None
    degree: str | None = None
    field: str | None = None
    year: str | None = None


class Language(BaseModel):
    name: str
    level: str | None = None


class Certification(BaseModel):
    name: str
    issuer: str | None = None
    year: str | None = None


class CV(BaseModel):

    first_name: str | None = None
    last_name: str | None = None

    email: str | None = None
    phone: str | None = None

    city: str | None = None

    linkedin: str | None = None
    github: str | None = None
    website: str | None = None

    summary: str | None = None

    skills: list[str] = Field(default_factory=list)

    experiences: list[Experience] = Field(default_factory=list)

    education: list[Education] = Field(default_factory=list)

    languages: list[Language] = Field(default_factory=list)

    certifications: list[Certification] = Field(default_factory=list)