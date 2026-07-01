from app.models.cv import CV
from app.models.job import Job
from app.models.letter import Letter
from app.models.strategy import Strategy
from app.pipeline.base_step import BaseStep
from app.services.llm_client import llm
from app.utils.prompt_loader import prompt_loader

import json


class CoverLetterStep(BaseStep):

    def __init__(self):
        super().__init__("Lettre de motivation")

    def build_system_prompt(self):
        return prompt_loader.load("letter.md")

    def build_user_prompt(self, cv: CV, cv_rewritten: CV, strategy: Strategy, job: Job):
        return f"""
Voici le CV original du candidat :

{json.dumps(cv.model_dump(), indent=2, ensure_ascii=False)}

Voici le CV réécrit et optimisé :

{json.dumps(cv_rewritten.model_dump(), indent=2, ensure_ascii=False)}

Voici la stratégie à appliquer :

{json.dumps(strategy.model_dump(), indent=2, ensure_ascii=False)}

Voici l'offre d'emploi ciblée :

{json.dumps(job.model_dump(), indent=2, ensure_ascii=False)}
"""

    def execute(self, cv: CV, cv_rewritten: CV, strategy: Strategy, job: Job):

        return llm.generate(
            system_prompt=self.build_system_prompt(),
            user_prompt=self.build_user_prompt(cv, cv_rewritten, strategy, job),
            response_model=Letter,
        )