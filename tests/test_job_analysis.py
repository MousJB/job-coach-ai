from pathlib import Path

from app.pipeline.step3_job_analysis import JobAnalysisStep

job_text = Path("tests/sample_job.txt").read_text(
    encoding="utf-8"
)

step = JobAnalysisStep()

result = step.execute(job_text)

print(result)