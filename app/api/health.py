from fastapi import APIRouter

from app.config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from app.services.llm_client import llm

router = APIRouter()


@router.get("/health")
def health():
    """
    Health check léger : vérifie que la configuration est chargée,
    sans appel réseau. À utiliser pour le monitoring d'uptime.
    """
    return {
        "status": "ok",
        "model_configured": bool(OPENROUTER_MODEL),
        "api_key_configured": bool(OPENROUTER_API_KEY),
    }


@router.get("/ping-openrouter")
async def ping():
    """
    Health check coûteux : effectue un vrai appel au LLM.
    À utiliser ponctuellement pour vérifier la connectivité OpenRouter,
    jamais comme cible d'un monitoring d'uptime automatique (coût récurrent).
    """
    response = await llm.chat(
        system_prompt="Tu es un assistant.",
        user_prompt="Réponds uniquement : Bonjour Job Coach 🚀",
    )

    return {
        "response": response
    }
