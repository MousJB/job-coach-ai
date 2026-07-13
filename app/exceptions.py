class PipelineError(Exception):
    """Classe de base pour les erreurs du pipeline d'optimisation."""


class LLMUpstreamError(PipelineError):
    """Le fournisseur LLM (OpenRouter) a échoué (réseau, timeout, erreur API)."""


class LLMResponseValidationError(PipelineError):
    """La réponse du LLM n'a pas pu être validée face au schéma attendu, même après correction."""
