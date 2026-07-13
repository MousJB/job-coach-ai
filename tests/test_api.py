import pytest
from fastapi.testclient import TestClient

from app.exceptions import LLMUpstreamError
from app.main import app
from app.models.report import Report


@pytest.fixture
def client():
    return TestClient(app)


async def _fake_run(self, cv_text, job_text):
    yield {"step": "extract_cv", "label": "Analyse du CV", "status": "done"}
    yield {
        "step": "complete",
        "label": "Finalisation",
        "status": "done",
        "cached": False,
        "report": Report(score_before=80, score_after=90, summary_for_user="ok"),
    }


async def _raising_run(self, cv_text, job_text):
    if False:  # garde la fonction en générateur asynchrone sans jamais yield
        yield {}
    raise LLMUpstreamError("boom")


def test_optimize_returns_report(client, mocker):
    mocker.patch("app.pipeline.pipeline.Pipeline.run", _fake_run)

    response = client.post("/optimize", json={"cv_text": "x" * 60, "job_text": "y" * 60})

    assert response.status_code == 200
    assert response.json()["score_before"] == 80


def test_optimize_rejects_input_below_min_length(client):
    response = client.post("/optimize", json={"cv_text": "trop court", "job_text": "trop court"})

    assert response.status_code == 422


def test_optimize_maps_llm_upstream_error_to_502(client, mocker):
    mocker.patch("app.pipeline.pipeline.Pipeline.run", _raising_run)

    response = client.post("/optimize", json={"cv_text": "x" * 60, "job_text": "y" * 60})

    assert response.status_code == 502
    assert response.json()["error_code"] == "llm_upstream_error"


def test_health_check_never_calls_the_llm(client, mocker):
    generate_mock = mocker.patch("app.services.llm_client.llm.generate")

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    generate_mock.assert_not_called()
