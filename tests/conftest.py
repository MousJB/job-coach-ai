import pytest

from app.models.cv import CV, Experience
from app.models.cv_analysis import CVAnalysis
from app.models.job import Job
from app.models.letter import Letter
from app.models.matching import Matching
from app.models.quality import QualityCheck
from app.models.strategy import Strategy


@pytest.fixture
def sample_cv() -> CV:
    return CV(
        first_name="Jean",
        last_name="Dupont",
        email="jean.dupont@email.com",
        phone="0612345678",
        city="Lyon",
        summary="Développeur full stack avec 5 ans d'expérience.",
        skills=["React", "Node.js"],
        experiences=[
            Experience(
                company="TechNova",
                position="Développeur",
                start_date="2021-01",
                end_date=None,
                description="Développement d'une plateforme SaaS.",
                technologies=["React", "Node.js"],
                achievements=["Livraison de la v2 en avance"],
            )
        ],
    )


@pytest.fixture
def sample_job() -> Job:
    return Job(
        title="Développeur Full Stack",
        company="Acme",
        required_skills=["React", "Node.js"],
        preferred_skills=["Docker"],
    )


@pytest.fixture
def sample_cv_analysis() -> CVAnalysis:
    return CVAnalysis(overall_seniority="mid", years_of_experience=4, top_skills=["React"])


@pytest.fixture
def sample_matching() -> Matching:
    return Matching(ats_score=80, matched_skills=["React", "Node.js"], missing_skills=["Docker"])


@pytest.fixture
def sample_strategy() -> Strategy:
    return Strategy(
        skills_to_highlight=["React"],
        experiences_to_highlight=[0],
        writing_style="dynamique_startup",
    )


@pytest.fixture
def sample_letter() -> Letter:
    return Letter(
        subject="Candidature au poste de Développeur Full Stack",
        body="Madame, Monsieur,\n\nContenu de la lettre.\n\nCordialement,\nJean Dupont",
        word_count=10,
    )


@pytest.fixture
def sample_quality() -> QualityCheck:
    return QualityCheck(approved=True, score_after=90, hallucinations_detected=[], final_recommendation="OK")


@pytest.fixture
def mock_llm_responses(
    sample_cv,
    sample_job,
    sample_cv_analysis,
    sample_matching,
    sample_strategy,
    sample_letter,
    sample_quality,
) -> dict:
    """Table de correspondance step_key -> résultat mocké du pipeline."""
    return {
        "extract_cv": sample_cv,
        "analyze_job": sample_job,
        "cv_analysis": sample_cv_analysis,
        "matching": sample_matching,
        "strategy": sample_strategy,
        "cv_rewrite": sample_cv,
        "cover_letter": sample_letter,
        "quality_check": sample_quality,
    }
