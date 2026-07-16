from app.models.cv import CV
from app.models.letter import Letter
from app.models.matching import Matching
from app.models.quality import QualityCheck
from app.models.report import Report
from app.models.strategy import Strategy
from app.pipeline.base_step import BaseStep


class ReportStep(BaseStep):

    def __init__(self, language: str = "fr"):
        super().__init__("Rapport Final", "report", language)

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

        is_en = self.language == "en"

        if quality.approved:
            summary = (
                (
                    f"Your application is ready. "
                    f"Compatibility score: {matching.ats_score}%. "
                    f"{len(matching.matched_skills)} key skills match the job posting."
                )
                if is_en
                else (
                    f"Votre candidature est prête. "
                    f"Score de compatibilité : {matching.ats_score}%. "
                    f"{len(matching.matched_skills)} compétences clés correspondent à l'offre."
                )
            )
        else:
            summary = (
                (
                    f"Your application has been optimized but needs a quick check. "
                    f"Compatibility score: {matching.ats_score}%. "
                    f"{len(quality.hallucinations_detected)} point(s) to review before sending."
                )
                if is_en
                else (
                    f"Votre candidature a été optimisée mais nécessite une vérification. "
                    f"Score de compatibilité : {matching.ats_score}%. "
                    f"{len(quality.hallucinations_detected)} point(s) à revoir avant envoi."
                )
            )

        next_steps = []

        if not quality.approved:
            next_steps.append(
                (
                    f"Review the {len(quality.hallucinations_detected)} flagged point(s) before sending your application."
                    if is_en
                    else f"Vérifiez les {len(quality.hallucinations_detected)} point(s) signalés avant d'envoyer votre candidature."
                )
            )

        if matching.missing_skills:
            missing = ", ".join(matching.missing_skills[:3])
            next_steps.append(
                (
                    f"Missing skills you could develop if relevant: {missing}."
                    if is_en
                    else f"Compétences manquantes à développer si possible : {missing}."
                )
            )

        if quality.warnings:
            next_steps.append(
                "Re-read the cover letter to check the wording flagged as a warning."
                if is_en
                else "Relisez la lettre de motivation pour vérifier les formulations signalées en avertissement."
            )

        next_steps.append(
            "Download your optimized resume and cover letter."
            if is_en
            else "Téléchargez votre CV optimisé et votre lettre de motivation."
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