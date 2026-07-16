from app.models.cv_analysis import CVAnalysis
from app.models.job import Job
from app.models.matching import Matching
from app.models.strategy import Strategy
from app.pipeline.base_step import BaseStep
from app.services.llm_client import llm
from app.utils.prompt_loader import prompt_loader

import json


class StrategyStep(BaseStep):

    def __init__(self, language: str = "fr"):
        super().__init__("Stratégie", "strategy", language)

    def build_system_prompt(self):
        return prompt_loader.load("strategy.md", self.language)

    def build_user_prompt(self, cv_analysis: CVAnalysis, job: Job, matching: Matching):
        if self.language == "en":
            return f"""
Here is the qualitative analysis of the candidate:

{json.dumps(cv_analysis.model_dump(), indent=2, ensure_ascii=False)}

Here is the structured job posting:

{json.dumps(job.model_dump(), indent=2, ensure_ascii=False)}

Here is the matching result:

{json.dumps(matching.model_dump(), indent=2, ensure_ascii=False)}
"""
        return f"""
Voici l'analyse qualitative du candidat :

{json.dumps(cv_analysis.model_dump(), indent=2, ensure_ascii=False)}

Voici l'offre d'emploi structurée :

{json.dumps(job.model_dump(), indent=2, ensure_ascii=False)}

Voici le résultat du matching :

{json.dumps(matching.model_dump(), indent=2, ensure_ascii=False)}
"""

    async def execute(self, cv_analysis: CVAnalysis, job: Job, matching: Matching):

        return await llm.generate(
            system_prompt=self.build_system_prompt(),
            user_prompt=self.build_user_prompt(cv_analysis, job, matching),
            response_model=Strategy,
            step=self.step_key,
        )