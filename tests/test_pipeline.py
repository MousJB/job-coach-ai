import pytest

from app.pipeline.pipeline import Pipeline
from app.services.cache import pipeline_cache


@pytest.fixture(autouse=True)
def clear_pipeline_cache():
    pipeline_cache._store.clear()
    yield
    pipeline_cache._store.clear()


@pytest.mark.asyncio
async def test_pipeline_runs_all_steps_in_dependency_order(mocker, mock_llm_responses):
    async def fake_generate(system_prompt, user_prompt, response_model, step=None):
        return mock_llm_responses[step]

    mocker.patch("app.services.llm_client.llm.generate", side_effect=fake_generate)

    events = [event async for event in Pipeline().run("cv text " * 20, "job text " * 20)]

    step_keys = [event["step"] for event in events]
    assert step_keys == [
        "extract_cv",
        "cv_analysis",
        "analyze_job",
        "matching",
        "strategy",
        "cv_rewrite",
        "cover_letter",
        "quality_check",
        "complete",
    ]

    final_report = events[-1]["report"]
    assert final_report.cv_rewritten is not None
    assert final_report.letter is not None
    assert final_report.score_before == mock_llm_responses["matching"].ats_score


@pytest.mark.asyncio
async def test_pipeline_caches_identical_requests(mocker, mock_llm_responses):
    call_count = 0

    async def fake_generate(system_prompt, user_prompt, response_model, step=None):
        nonlocal call_count
        call_count += 1
        return mock_llm_responses[step]

    mocker.patch("app.services.llm_client.llm.generate", side_effect=fake_generate)

    cv_text = "cv text " * 20
    job_text = "job text " * 20

    async for _ in Pipeline().run(cv_text, job_text):
        pass
    calls_after_first_run = call_count

    events = [event async for event in Pipeline().run(cv_text, job_text)]

    assert call_count == calls_after_first_run, "le deuxième run ne doit déclencher aucun appel LLM"
    assert len(events) == 1
    assert events[0]["step"] == "complete"
    assert events[0]["cached"] is True
