from pathlib import Path

from app.pipeline.step1_extract import ExtractStep
from app.pipeline.step2_cv_analysis import CVAnalysisStep
from app.pipeline.step3_job_analysis import JobAnalysisStep
from app.pipeline.step4_matching import MatchingStep

cv_text = Path("tests/sample_cv.txt").read_text(encoding="utf-8")
job_text = Path("tests/sample_job.txt").read_text(encoding="utf-8")

cv = ExtractStep().execute(cv_text)
cv_analysis = CVAnalysisStep().execute(cv)
job = JobAnalysisStep().execute(job_text)

matching = MatchingStep().execute(cv, cv_analysis, job)

print(matching)