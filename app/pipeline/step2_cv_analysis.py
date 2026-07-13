from app.models.cv import CV
from app.models.cv_analysis import CVAnalysis
from app.pipeline.base_step import BaseStep
from app.services.llm_client import llm
from app.utils.prompt_loader import prompt_loader

import json


class CVAnalysisStep(BaseStep):

    def __init__(self):
        super().__init__("Analyse CV", "cv_analysis")

    def build_system_prompt(self):
        return prompt_loader.load("cv_analysis.md")

    def build_user_prompt(self, cv: CV):
        return f"""
Voici le CV structuré à analyser :

{json.dumps(cv.model_dump(), indent=2, ensure_ascii=False)}
"""

    async def execute(self, cv: CV):

        return await llm.generate(
            system_prompt=self.build_system_prompt(),
            user_prompt=self.build_user_prompt(cv),
            response_model=CVAnalysis,
            step=self.step_key,
        )