from pathlib import Path

from app.pipeline.step1_extract import ExtractStep

cv_text = Path("tests/sample_cv.txt").read_text(
    encoding="utf-8"
)

step = ExtractStep()

result = step.execute(cv_text)

print(result)