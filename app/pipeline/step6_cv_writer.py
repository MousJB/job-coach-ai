from app.models.cv import CV
from app.models.job import Job
from app.models.strategy import Strategy
from app.pipeline.base_step import BaseStep
from app.services.llm_client import llm
from app.utils.prompt_loader import prompt_loader

import json


class CVWriterStep(BaseStep):

    def __init__(self, language: str = "fr"):
        super().__init__("Réécriture CV", "cv_rewrite", language)

    def build_system_prompt(self):
        return prompt_loader.load("rewrite.md", self.language)

    def build_user_prompt(self, cv: CV, strategy: Strategy, job: Job):
        if self.language == "en":
            return f"""
Here is the candidate's original resume:

{json.dumps(cv.model_dump(), indent=2, ensure_ascii=False)}

Here is the optimization strategy to apply:

{json.dumps(strategy.model_dump(), indent=2, ensure_ascii=False)}

Here is the targeted job posting (for context):

{json.dumps(job.model_dump(), indent=2, ensure_ascii=False)}
"""
        return f"""
Voici le CV original du candidat :

{json.dumps(cv.model_dump(), indent=2, ensure_ascii=False)}

Voici la stratégie d'optimisation à appliquer :

{json.dumps(strategy.model_dump(), indent=2, ensure_ascii=False)}

Voici l'offre d'emploi ciblée (pour contexte) :

{json.dumps(job.model_dump(), indent=2, ensure_ascii=False)}
"""

    async def execute(self, cv: CV, strategy: Strategy, job: Job):

        return await llm.generate(
            system_prompt=self.build_system_prompt(),
            user_prompt=self.build_user_prompt(cv, strategy, job),
            response_model=CV,
            step=self.step_key,
        )