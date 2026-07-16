from abc import ABC, abstractmethod

from app.utils.prompt_loader import DEFAULT_LANGUAGE


class BaseStep(ABC):
    """
    Classe de base pour toutes les étapes de la pipeline.
    """

    def __init__(self, name: str, step_key: str, language: str = DEFAULT_LANGUAGE):
        self.name = name
        self.step_key = step_key
        self.language = language

    @abstractmethod
    def build_system_prompt(self) -> str:
        """Retourne le prompt système."""
        ...

    @abstractmethod
    def build_user_prompt(self, *args, **kwargs) -> str:
        """Construit le prompt utilisateur."""
        ...

    @abstractmethod
    async def execute(self, *args, **kwargs):
        """Exécute l'étape et retourne son résultat."""
        ...
