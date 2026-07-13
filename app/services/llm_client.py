import json
import logging

from openai import APIConnectionError, APIError, APITimeoutError, AsyncOpenAI
from pydantic import BaseModel, ValidationError

from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    OPENROUTER_MODEL_FAST,
    OPENROUTER_MODEL_QUALITY,
)
from app.exceptions import LLMResponseValidationError, LLMUpstreamError
from app.settings import DEFAULT_STEP_CONFIG, STEP_CONFIG, STEP_MODEL_TIER

logger = logging.getLogger(__name__)


def _strip_json_fences(text: str) -> str:
    """Retire un éventuel bloc ```json ... ``` autour de la réponse, au cas où
    le modèle ignorerait la consigne de ne jamais en utiliser."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else ""
        if cleaned.rstrip().endswith("```"):
            cleaned = cleaned.rstrip()[:-3]
    return cleaned.strip()


class LLMClient:

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            timeout=60.0,
            max_retries=2,
        )

    def _model_for(self, step: str | None) -> str:
        tier = STEP_MODEL_TIER.get(step or "", "quality")
        if tier == "fast" and OPENROUTER_MODEL_FAST:
            return OPENROUTER_MODEL_FAST
        if tier == "quality" and OPENROUTER_MODEL_QUALITY:
            return OPENROUTER_MODEL_QUALITY
        return OPENROUTER_MODEL

    async def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        step: str | None = None,
    ) -> str:
        config = STEP_CONFIG.get(step or "", DEFAULT_STEP_CONFIG)

        try:
            response = await self.client.chat.completions.create(
                model=self._model_for(step),
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except (APIError, APIConnectionError, APITimeoutError) as exc:
            raise LLMUpstreamError(
                f"Échec de l'appel au fournisseur IA (étape : {step or 'inconnue'}) : {exc}"
            ) from exc

        content = response.choices[0].message.content
        if not content:
            raise LLMUpstreamError(f"Réponse vide du fournisseur IA (étape : {step or 'inconnue'})")

        return content

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
        step: str | None = None,
    ):
        raw = await self.chat(system_prompt, user_prompt, step=step)

        try:
            return response_model.model_validate(json.loads(_strip_json_fences(raw)))
        except (json.JSONDecodeError, ValidationError) as first_error:
            logger.warning(
                "Réponse JSON invalide à l'étape %s, tentative de correction (%s)",
                step,
                first_error,
            )

            repair_prompt = (
                "Ta réponse précédente n'était pas un JSON valide ou ne respectait pas le "
                f"schéma attendu (erreur : {first_error}). Voici ta réponse précédente :\n\n"
                f"{raw}\n\n"
                "Corrige-la et retourne UNIQUEMENT le JSON valide correspondant au format demandé, "
                "sans aucune explication ni balise ```json."
            )

            raw_repair = await self.chat(system_prompt, repair_prompt, step=step)

            try:
                return response_model.model_validate(json.loads(_strip_json_fences(raw_repair)))
            except (json.JSONDecodeError, ValidationError) as second_error:
                raise LLMResponseValidationError(
                    f"Réponse IA invalide à l'étape {step or 'inconnue'} après tentative de correction : "
                    f"{second_error}"
                ) from second_error


llm = LLMClient()
