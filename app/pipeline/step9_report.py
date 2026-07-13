from app.models.cv import CV
from app.models.letter import Letter
from app.models.matching import Matching
from app.models.quality import QualityCheck
from app.models.report import Report
from app.models.strategy import Strategy
from app.pipeline.base_step import BaseStep


class ReportStep(BaseStep):

    def __init__(self):
        super().__init__("Rapport Final", "report")

    def build_system_prompt(self):
        return ""

    def build_user_prompt(self, *args, **kwargs):
        return ""

    async def execute(
        self,
        cv_rewritten: CV,
        letter: Letter,
        matching: Matching,
        strategy: Strategy,
        quality: QualityCheck,
    ) -> Report:

        if quality.approved:
            summary = (
                f"Votre candidature est prête. "
                f"Score de compatibilité : {matching.ats_score}%. "
                f"{len(matching.matched_skills)} compétences clés correspondent à l'offre."
            )
        else:
            summary = (
                f"Votre candidature a été optimisée mais nécessite une vérification. "
                f"Score de compatibilité : {matching.ats_score}%. "
                f"{len(quality.hallucinations_detected)} point(s) à revoir avant envoi."
            )

        next_steps = []

        if not quality.approved:
            next_steps.append(
                f"Vérifiez les {len(quality.hallucinations_detected)} point(s) signalés avant d'envoyer votre candidature."
            )

        if matching.missing_skills:
            missing = ", ".join(matching.missing_skills[:3])
            next_steps.append(
                f"Compétences manquantes à développer si possible : {missing}."
            )

        if quality.warnings:
            next_steps.append(
                "Relisez la lettre de motivation pour vérifier les formulations signalées en avertissement."
            )

        next_steps.append(
            "Téléchargez votre CV optimisé et votre lettre de motivation."
        )

        return Report(
            score_before=matching.ats_score,
            score_after=quality.score_after,
            matched_skills=matching.matched_skills,
            missing_skills=matching.missing_skills,
            cv_rewritten=cv_rewritten,
            letter=letter,
            strategy=strategy,
            quality=quality,
            summary_for_user=summary,
            next_steps=next_steps,
        )