from pathlib import Path

from app.pipeline.step1_extract import ExtractStep
from app.pipeline.step2_cv_analysis import CVAnalysisStep
from app.pipeline.step3_job_analysis import JobAnalysisStep
from app.pipeline.step4_matching import MatchingStep
from app.pipeline.step5_strategy import StrategyStep
from app.pipeline.step6_cv_writer import CVWriterStep
from app.pipeline.step7_cover_letter import CoverLetterStep
from app.pipeline.step8_quality import QualityStep

cv_text = Path("tests/sample_cv.txt").read_text(encoding="utf-8")
job_text = Path("tests/sample_job_dev.txt").read_text(encoding="utf-8")

cv = ExtractStep().execute(cv_text)
cv_analysis = CVAnalysisStep().execute(cv)
job = JobAnalysisStep().execute(job_text)
matching = MatchingStep().execute(cv, cv_analysis, job)
strategy = StrategyStep().execute(cv_analysis, job, matching)
cv_rewritten = CVWriterStep().execute(cv, strategy, job)
letter = CoverLetterStep().execute(cv, cv_rewritten, strategy, job)

quality = QualityStep().execute(cv, cv_rewritten, letter, matching, job)

print("\n=== CONTRÔLE QUALITÉ ===")
print(f"Approuvé : {quality.approved}")
print(f"Score avant : {quality.score_before}")
print(f"Score après : {quality.score_after}")

print("\n=== HALLUCINATIONS DÉTECTÉES ===")
for h in quality.hallucinations_detected:
    print(f"  ⚠ {h}")

print("\n=== INCOHÉRENCES ===")
for i in quality.inconsistencies:
    print(f"  ✗ {i}")

print("\n=== AMÉLIORATIONS LÉGITIMES ===")
for a in quality.improvements_made:
    print(f"  ✓ {a}")

print("\n=== AVERTISSEMENTS ===")
for w in quality.warnings:
    print(f"  ! {w}")

print(f"\n=== RECOMMANDATION FINALE ===")
print(quality.final_recommendation)