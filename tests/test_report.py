from pathlib import Path

from app.pipeline.step1_extract import ExtractStep
from app.pipeline.step2_cv_analysis import CVAnalysisStep
from app.pipeline.step3_job_analysis import JobAnalysisStep
from app.pipeline.step4_matching import MatchingStep
from app.pipeline.step5_strategy import StrategyStep
from app.pipeline.step6_cv_writer import CVWriterStep
from app.pipeline.step7_cover_letter import CoverLetterStep
from app.pipeline.step8_quality import QualityStep
from app.pipeline.step9_report import ReportStep

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

report = ReportStep().execute(cv_rewritten, letter, matching, strategy, quality)

print("\n=== RAPPORT FINAL ===")
print(f"Score avant : {report.score_before}%")
print(f"Score après : {report.score_after}%")

print(f"\n=== RÉSUMÉ ===")
print(report.summary_for_user)

print(f"\n=== COMPÉTENCES MATCHÉES ===")
for s in report.matched_skills:
    print(f"  ✓ {s}")

print(f"\n=== COMPÉTENCES MANQUANTES ===")
for s in report.missing_skills:
    print(f"  ✗ {s}")

print(f"\n=== QUALITÉ ===")
print(f"Approuvé : {report.quality.approved}")
if report.quality.hallucinations_detected:
    print("Hallucinations :")
    for h in report.quality.hallucinations_detected:
        print(f"  ⚠ {h}")

print(f"\n=== PROCHAINES ÉTAPES ===")
for step in report.next_steps:
    print(f"  → {step}")

print(f"\n=== LETTRE (aperçu) ===")
print(report.letter.body[:200] + "...")