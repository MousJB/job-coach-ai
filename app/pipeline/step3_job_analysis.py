from app.models.job import Job
from app.pipeline.base_step import BaseStep
from app.services.llm_client import llm
from app.utils.prompt_loader import prompt_loader


class JobAnalysisStep(BaseStep):

    def __init__(self):
        super().__init__("Analyse Offre", "analyze_job")

    def build_system_prompt(self):
        return prompt_loader.load("job_analysis.md")

    def build_user_prompt(self, job_text):
        return f"""
Analyse l'offre d'emploi suivante :

{job_text}
"""

    async def execute(self, job_text):

        return await llm.generate(
            system_prompt=self.build_system_prompt(),
            user_prompt=self.build_user_prompt(job_text),
            response_model=Job,
            step=self.step_key,
        )