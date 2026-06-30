from fastapi import APIRouter

from app.services.llm_client import llm

router = APIRouter()


@router.get("/ping-openrouter")
def ping():

    response = llm.chat(
        system_prompt="Tu es un assistant.",
        user_prompt="Réponds uniquement : Bonjour Job Coach 🚀",
    )

    return {
        "response": response
    }