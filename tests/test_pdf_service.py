from app.api.export import LetterSender
from app.models.cv import CV
from app.services.pdf_service import render_cv_pdf, render_letter_pdf


def test_render_cv_pdf_produces_valid_pdf_bytes(sample_cv):
    pdf_bytes = render_cv_pdf(sample_cv)

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 500


def test_render_cv_pdf_handles_minimal_cv_without_optional_fields():
    minimal_cv = CV(first_name="Jean", last_name="Dupont")

    pdf_bytes = render_cv_pdf(minimal_cv)

    assert pdf_bytes.startswith(b"%PDF")


def test_render_letter_pdf_produces_valid_pdf_bytes(sample_letter):
    sender = LetterSender(first_name="Jean", last_name="Dupont", email="jean.dupont@email.com")

    pdf_bytes = render_letter_pdf(sample_letter, sender)

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 300
