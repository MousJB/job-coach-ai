from app.models.cv import CV
from app.pipeline.base_step import BaseStep
from app.services.llm_client import llm
from app.utils.prompt_loader import prompt_loader


class ExtractStep(BaseStep):

    def __init__(self):
        super().__init__("Extraction")

    def build_system_prompt(self):
        return prompt_loader.load("extract.md")

    def build_user_prompt(self, cv_text):
        return f"""
Analyse le CV suivant :

{cv_text}
"""

    def execute(self, cv_text):

        return llm.generate(
            system_prompt=self.build_system_prompt(),
            user_prompt=self.build_user_prompt(cv_text),
            response_model=CV,
        )