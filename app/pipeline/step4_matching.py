from app.models.cv import CV
from app.models.cv_analysis import CVAnalysis
from app.models.job import Job
from app.models.matching import Matching
from app.pipeline.base_step import BaseStep
from app.services.llm_client import llm
from app.utils.prompt_loader import prompt_loader

import json


class MatchingStep(BaseStep):

    def __init__(self):
        super().__init__("Matching")

    def build_system_prompt(self):
        return prompt_loader.load("matching.md")

    def build_user_prompt(self, cv: CV, cv_analysis: CVAnalysis, job: Job):
        return f"""
Voici le CV structuré du candidat :

{json.dumps(cv.model_dump(), indent=2, ensure_ascii=False)}

Voici l'analyse qualitative du candidat :

{json.dumps(cv_analysis.model_dump(), indent=2, ensure_ascii=False)}

Voici l'offre d'emploi structurée :

{json.dumps(job.model_dump(), indent=2, ensure_ascii=False)}
"""

    def execute(self, cv: CV, cv_analysis: CVAnalysis, job: Job):

        return llm.generate(
            system_prompt=self.build_system_prompt(),
            user_prompt=self.build_user_prompt(cv, cv_analysis, job),
            response_model=Matching,
        )