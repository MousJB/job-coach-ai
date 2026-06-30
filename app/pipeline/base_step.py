from abc import ABC, abstractmethod

from app.services.llm_client import llm


class BaseStep(ABC):
    """
    Classe de base pour toutes les étapes de la pipeline.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def build_system_prompt(self) -> str:
        """Retourne le prompt système."""
        pass

    @abstractmethod
    def build_user_prompt(self, data) -> str:
        """Construit le prompt utilisateur."""
        pass

    def execute(self, data):

        system_prompt = self.build_system_prompt()
        user_prompt = self.build_user_prompt(data)

        return llm.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )