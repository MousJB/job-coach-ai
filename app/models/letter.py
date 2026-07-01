from pydantic import BaseModel


class Letter(BaseModel):

    subject: str | None = None  # objet du mail / titre

    body: str  # corps de la lettre complète

    word_count: int | None = None