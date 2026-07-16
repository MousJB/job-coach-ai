from functools import lru_cache
from pathlib import Path

SUPPORTED_LANGUAGES = ("fr", "en")
DEFAULT_LANGUAGE = "fr"


class PromptLoader:
    """
    Charge les prompts Markdown depuis app/prompts/<langue>/, avec cache
    mémoire (les fichiers de prompt ne changent jamais en cours d'exécution).
    """

    def __init__(self):
        self.prompt_dir = Path(__file__).parent.parent / "prompts"

    @lru_cache(maxsize=64)
    def load(self, filename: str, language: str = DEFAULT_LANGUAGE) -> str:
        if language not in SUPPORTED_LANGUAGES:
            language = DEFAULT_LANGUAGE

        path = self.prompt_dir / language / filename

        if not path.exists():
            raise FileNotFoundError(f"Prompt introuvable : {language}/{filename}")

        return path.read_text(encoding="utf-8")


prompt_loader = PromptLoader()
