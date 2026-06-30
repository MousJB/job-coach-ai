from pathlib import Path

from app.pipeline.step1_extract import ExtractStep
from app.pipeline.step2_cv_analysis import CVAnalysisStep

cv_text = Path("tests/sample_cv.txt").read_text(
    encoding="utf-8"
)

extract_step = ExtractStep()
cv = extract_step.execute(cv_text)

analysis_step = CVAnalysisStep()
result = analysis_step.execute(cv)

print(result)