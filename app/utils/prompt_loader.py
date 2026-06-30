from pathlib import Path


class PromptLoader:
    """
    Charge les prompts Markdown depuis app/prompts/.
    """

    def __init__(self):
        self.prompt_dir = Path(__file__).parent.parent / "prompts"

    def load(self, filename: str) -> str:
        path = self.prompt_dir / filename

        if not path.exists():
            raise FileNotFoundError(f"Prompt introuvable : {filename}")

        return path.read_text(encoding="utf-8")


prompt_loader = PromptLoader()