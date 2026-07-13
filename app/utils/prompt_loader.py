from functools import lru_cache
from pathlib import Path


class PromptLoader:
    """
    Charge les prompts Markdown depuis app/prompts/, avec cache mémoire
    (les fichiers de prompt ne changent jamais en cours d'exécution).
    """

    def __init__(self):
        self.prompt_dir = Path(__file__).parent.parent / "prompts"

    @lru_cache(maxsize=32)
    def load(self, filename: str) -> str:
        path = self.prompt_dir / filename

        if not path.exists():
            raise FileNotFoundError(f"Prompt introuvable : {filename}")

        return path.read_text(encoding="utf-8")


prompt_loader = PromptLoader()
