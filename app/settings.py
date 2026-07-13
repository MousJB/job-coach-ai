from dataclasses import dataclass

DEBUG = True


@dataclass(frozen=True)
class StepConfig:
    temperature: float
    max_tokens: int


# Config LLM par étape : les étapes d'extraction/scoring sont courtes et factuelles
# (température basse, peu de tokens) ; les étapes de rédaction ont besoin de plus
# de latitude et de place pour produire un texte long et naturel.
STEP_CONFIG: dict[str, StepConfig] = {
    "extract_cv": StepConfig(temperature=0.1, max_tokens=1500),
    "analyze_job": StepConfig(temperature=0.1, max_tokens=1200),
    "cv_analysis": StepConfig(temperature=0.2, max_tokens=800),
    "matching": StepConfig(temperature=0.1, max_tokens=900),
    "strategy": StepConfig(temperature=0.2, max_tokens=1000),
    "cv_rewrite": StepConfig(temperature=0.35, max_tokens=2500),
    # Température un peu plus haute pour la lettre : encourage des formulations moins
    # interchangeables d'une candidature à l'autre (cf. consignes anti-cliché du prompt).
    "cover_letter": StepConfig(temperature=0.5, max_tokens=1200),
    "quality_check": StepConfig(temperature=0.1, max_tokens=1200),
}

DEFAULT_STEP_CONFIG = StepConfig(temperature=0.2, max_tokens=1500)

# Étapes d'extraction/scoring factuelles -> modèle rapide.
# Étapes de rédaction/jugement -> modèle le plus capable.
STEP_MODEL_TIER: dict[str, str] = {
    "extract_cv": "fast",
    "analyze_job": "fast",
    "cv_analysis": "fast",
    "matching": "fast",
    "strategy": "quality",
    "cv_rewrite": "quality",
    "cover_letter": "quality",
    "quality_check": "quality",
}
