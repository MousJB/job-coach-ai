from types import SimpleNamespace

import httpx
import pytest
from pydantic import BaseModel

from app.exceptions import LLMResponseValidationError, LLMUpstreamError
from app.services.llm_client import LLMClient, _strip_json_fences


class _DummyModel(BaseModel):
    value: str


def _fake_response(content: str):
    message = SimpleNamespace(content=content)
    choice = SimpleNamespace(message=message)
    return SimpleNamespace(choices=[choice])


@pytest.mark.parametrize(
    "raw, expected",
    [
        ('{"a": 1}', '{"a": 1}'),
        ('```json\n{"a": 1}\n```', '{"a": 1}'),
        ('```\n{"a": 1}\n```', '{"a": 1}'),
        ('  {"a": 1}  ', '{"a": 1}'),
    ],
)
def test_strip_json_fences(raw, expected):
    assert _strip_json_fences(raw) == expected


@pytest.mark.asyncio
async def test_generate_success_on_first_try(mocker):
    client = LLMClient()
    mocker.patch.object(
        client.client.chat.completions,
        "create",
        new_callable=mocker.AsyncMock,
        return_value=_fake_response('{"value": "ok"}'),
    )

    result = await client.generate("sys", "user", _DummyModel, step="extract_cv")

    assert result.value == "ok"


@pytest.mark.asyncio
async def test_generate_repairs_invalid_json_once(mocker):
    client = LLMClient()
    create_mock = mocker.patch.object(
        client.client.chat.completions,
        "create",
        new_callable=mocker.AsyncMock,
        side_effect=[_fake_response("ceci n'est pas du JSON"), _fake_response('{"value": "fixed"}')],
    )

    result = await client.generate("sys", "user", _DummyModel, step="matching")

    assert result.value == "fixed"
    assert create_mock.call_count == 2


@pytest.mark.asyncio
async def test_generate_raises_after_failed_repair(mocker):
    client = LLMClient()
    mocker.patch.object(
        client.client.chat.completions,
        "create",
        new_callable=mocker.AsyncMock,
        side_effect=[_fake_response("pas du json"), _fake_response("toujours pas du json")],
    )

    with pytest.raises(LLMResponseValidationError):
        await client.generate("sys", "user", _DummyModel, step="matching")


@pytest.mark.asyncio
async def test_chat_wraps_upstream_connection_errors(mocker):
    from openai import APIConnectionError

    client = LLMClient()
    request = httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")
    mocker.patch.object(
        client.client.chat.completions,
        "create",
        new_callable=mocker.AsyncMock,
        side_effect=APIConnectionError(request=request),
    )

    with pytest.raises(LLMUpstreamError):
        await client.chat("sys", "user", step="extract_cv")
