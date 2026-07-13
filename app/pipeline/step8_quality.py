from app.models.cv import CV
from app.models.job import Job
from app.models.letter import Letter
from app.models.matching import Matching
from app.models.quality import QualityCheck
from app.pipeline.base_step import BaseStep
from app.services.llm_client import llm
from app.utils.prompt_loader import prompt_loader

import json


class QualityStep(BaseStep):

    def __init__(self):
        super().__init__("Contrôle Qualité", "quality_check")

    def build_system_prompt(self):
        return prompt_loader.load("quality.md")

    def build_user_prompt(
        self,
        cv: CV,
        cv_rewritten: CV,
        letter: Letter,
        matching: Matching,
        job: Job,
    ):
        return f"""
Voici le CV original du candidat (source de vérité) :

{json.dumps(cv.model_dump(), indent=2, ensure_ascii=False)}

Voici le CV réécrit et optimisé :

{json.dumps(cv_rewritten.model_dump(), indent=2, ensure_ascii=False)}

Voici la lettre de motivation générée :

{json.dumps(letter.model_dump(), indent=2, ensure_ascii=False)}

Voici le résultat du matching (score ATS avant optimisation) :

{json.dumps(matching.model_dump(), indent=2, ensure_ascii=False)}

Voici l'offre d'emploi ciblée :

{json.dumps(job.model_dump(), indent=2, ensure_ascii=False)}
"""

    async def execute(
        self,
        cv: CV,
        cv_rewritten: CV,
        letter: Letter,
        matching: Matching,
        job: Job,
    ):
        return await llm.generate(
            system_prompt=self.build_system_prompt(),
            user_prompt=self.build_user_prompt(cv, cv_rewritten, letter, matching, job),
            response_model=QualityCheck,
            step=self.step_key,
        )