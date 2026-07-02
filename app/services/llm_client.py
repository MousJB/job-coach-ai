import json

from openai import OpenAI
from pydantic import BaseModel

from app.config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from app.settings import TEMPERATURE, MAX_TOKENS


class LLMClient:

    def __init__(self):
        self.client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:

        response = self.client.chat.completions.create(
            model=OPENROUTER_MODEL,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        return response.choices[0].message.content

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
    ):

        response = self.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    

        data = json.loads(response)

        return response_model.model_validate(data)


llm = LLMClient()