import io
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models.cv import CV
from app.models.letter import Letter

NAVY = colors.HexColor("#0f172a")
SLATE_700 = colors.HexColor("#334155")
SLATE_500 = colors.HexColor("#64748b")
SLATE_400 = colors.HexColor("#94a3b8")
SLATE_300 = colors.HexColor("#cbd5e1")
BLUE = colors.HexColor("#2563eb")
BORDER = colors.HexColor("#e2e8f0")
CAPSULE_BG = colors.HexColor("#f3f4f6")
WHITE = colors.white

_FRENCH_MONTHS = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]


def _french_date(d: date) -> str:
    return f"{d.day} {_FRENCH_MONTHS[d.month - 1]} {d.year}"


def _styles() -> dict[str, ParagraphStyle]:
    return {
        "head_name": ParagraphStyle(
            "head_name", fontName="Helvetica-Bold", fontSize=22, leading=25, textColor=WHITE
        ),
        "head_title": ParagraphStyle(
            "head_title", fontName="Helvetica", fontSize=11.5, leading=15, textColor=SLATE_400
        ),
        "head_contact": ParagraphStyle(
            "head_contact", fontName="Helvetica", fontSize=8.5, leading=13, textColor=SLATE_300
        ),
        "avatar": ParagraphStyle(
            "avatar",
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=WHITE,
            alignment=1,
        ),
        "section_head": ParagraphStyle(
            "section_head",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=NAVY,
            spaceAfter=6,
        ),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9.3, leading=13.5, textColor=SLATE_700),
        "job_title": ParagraphStyle(
            "job_title", fontName="Helvetica-Bold", fontSize=10.3, leading=13, textColor=NAVY
        ),
        "job_date": ParagraphStyle(
            "job_date", fontName="Helvetica", fontSize=8.3, leading=12, textColor=SLATE_500, alignment=2
        ),
        "job_company": ParagraphStyle(
            "job_company", fontName="Helvetica-Bold", fontSize=9.3, leading=12, textColor=BLUE, spaceAfter=3
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=SLATE_700,
            leftIndent=10,
            bulletIndent=0,
        ),
        "capsule_text": ParagraphStyle(
            "capsule_text", fontName="Helvetica", fontSize=8.8, leading=15, textColor=SLATE_700
        ),
        "edu_title": ParagraphStyle(
            "edu_title", fontName="Helvetica-Bold", fontSize=9.3, leading=12.5, textColor=NAVY
        ),
        "edu_sub": ParagraphStyle("edu_sub", fontName="Helvetica", fontSize=8.5, leading=12, textColor=SLATE_500),
        "lang_name": ParagraphStyle("lang_name", fontName="Helvetica", fontSize=9.3, leading=13, textColor=SLATE_700),
        "letter_sender_name": ParagraphStyle(
            "letter_sender_name", fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=NAVY
        ),
        "letter_sender_info": ParagraphStyle(
            "letter_sender_info", fontName="Helvetica", fontSize=8.7, leading=13, textColor=SLATE_500
        ),
        "letter_date": ParagraphStyle(
            "letter_date", fontName="Helvetica", fontSize=9, leading=13, textColor=SLATE_500, alignment=2
        ),
        "letter_subject": ParagraphStyle(
            "letter_subject", fontName="Helvetica-Bold", fontSize=9.5, leading=13, textColor=NAVY
        ),
        "letter_body": ParagraphStyle(
            "letter_body", fontName="Helvetica", fontSize=10, leading=15.5, textColor=colors.HexColor("#1f2937")
        ),
    }


def _capsules(items: list[str], style: ParagraphStyle) -> Paragraph:
    """Rend une liste de mots-clés (compétences/technos) en texte simple
    séparé par des puces : plus fiable en pagination que des badges
    multi-colonnes, et plus lisible par un parseur ATS qu'une image."""
    return Paragraph("  •  ".join(items), style)


def render_cv_pdf(cv: CV) -> bytes:
    styles = _styles()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=0,
        rightMargin=0,
        topMargin=0,
        bottomMargin=0,
    )

    page_width = A4[0]
    content_margin = 12 * mm

    initials = f"{(cv.first_name or '')[:1]}{(cv.last_name or '')[:1]}".upper() or "?"
    title = cv.experiences[0].position if cv.experiences and cv.experiences[0].position else "Profil professionnel"

    contact_parts = [p for p in [cv.email, cv.phone, cv.city, cv.linkedin] if p]
    contact_line = "   •   ".join(contact_parts)

    header_inner = Table(
        [
            [
                Paragraph(initials, styles["avatar"]),
                [
                    Paragraph(f"{cv.first_name or ''} {cv.last_name or ''}".strip(), styles["head_name"]),
                    Spacer(1, 2),
                    Paragraph(title, styles["head_title"]),
                    Spacer(1, 6),
                    Paragraph(contact_line, styles["head_contact"]),
                ],
            ]
        ],
        colWidths=[22 * mm, page_width - 22 * mm - 2 * content_margin],
    )
    header_inner.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#1e293b")),
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ("BOX", (0, 0), (0, 0), 0, colors.HexColor("#1e293b")),
                ("TOPPADDING", (0, 0), (0, 0), 14),
                ("BOTTOMPADDING", (0, 0), (0, 0), 14),
                ("LEFTPADDING", (1, 0), (1, 0), 16),
            ]
        )
    )

    header = Table(
        [[header_inner]],
        colWidths=[page_width],
    )
    header.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), NAVY),
                ("LEFTPADDING", (0, 0), (-1, -1), content_margin),
                ("RIGHTPADDING", (0, 0), (-1, -1), content_margin),
                ("TOPPADDING", (0, 0), (-1, -1), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
            ]
        )
    )

    content_width = page_width - 2 * content_margin
    main_col_width = content_width * 0.63

    # --- Colonne principale : profil + expériences ---
    main_flow = []

    if cv.summary:
        main_flow.append(Paragraph("PROFIL", styles["section_head"]))
        main_flow.append(Paragraph(cv.summary, styles["body"]))
        main_flow.append(Spacer(1, 14))

    if cv.experiences:
        main_flow.append(Paragraph("EXPÉRIENCES PROFESSIONNELLES", styles["section_head"]))
        for exp in cv.experiences:
            row = Table(
                [
                    [
                        Paragraph(exp.position or "", styles["job_title"]),
                        Paragraph(f"{exp.start_date or ''} — {exp.end_date or 'Présent'}", styles["job_date"]),
                    ]
                ],
                colWidths=[main_col_width * 0.7, main_col_width * 0.3],
            )
            row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM"), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
            main_flow.append(row)
            if exp.company:
                main_flow.append(Paragraph(exp.company, styles["job_company"]))
            if exp.description:
                main_flow.append(Paragraph(exp.description, styles["body"]))
            if exp.achievements:
                for achievement in exp.achievements:
                    main_flow.append(Paragraph(f"•  {achievement}", styles["bullet"]))
            if exp.technologies:
                main_flow.append(Spacer(1, 3))
                main_flow.append(_capsules(exp.technologies, styles["capsule_text"]))
            main_flow.append(Spacer(1, 12))

    # --- Colonne latérale : compétences, langues, formation, certifications ---
    side_flow = []

    if cv.skills:
        side_flow.append(Paragraph("COMPÉTENCES", styles["section_head"]))
        side_flow.append(_capsules(cv.skills, styles["capsule_text"]))
        side_flow.append(Spacer(1, 14))

    if cv.languages:
        side_flow.append(Paragraph("LANGUES", styles["section_head"]))
        for lang in cv.languages:
            level = f" — {lang.level}" if lang.level else ""
            side_flow.append(Paragraph(f"{lang.name}{level}", styles["lang_name"]))
        side_flow.append(Spacer(1, 14))

    if cv.education:
        side_flow.append(Paragraph("FORMATION", styles["section_head"]))
        for edu in cv.education:
            degree = " — ".join(p for p in [edu.degree, edu.field] if p)
            side_flow.append(Paragraph(degree or "", styles["edu_title"]))
            sub = " · ".join(p for p in [edu.school, edu.year] if p)
            if sub:
                side_flow.append(Paragraph(sub, styles["edu_sub"]))
            side_flow.append(Spacer(1, 8))
        side_flow.append(Spacer(1, 6))

    if cv.certifications:
        side_flow.append(Paragraph("CERTIFICATIONS", styles["section_head"]))
        for cert in cv.certifications:
            side_flow.append(Paragraph(cert.name, styles["edu_title"]))
            sub = " · ".join(p for p in [cert.issuer, cert.year] if p)
            if sub:
                side_flow.append(Paragraph(sub, styles["edu_sub"]))
            side_flow.append(Spacer(1, 8))

    body_table = Table(
        [[main_flow, side_flow]],
        colWidths=[main_col_width, content_width - main_col_width],
    )
    body_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (0, 0), 0),
                ("RIGHTPADDING", (0, 0), (0, 0), 14),
                ("LEFTPADDING", (1, 0), (1, 0), 14),
                ("RIGHTPADDING", (1, 0), (1, 0), 0),
                ("LINEBEFORE", (1, 0), (1, 0), 0.5, BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 16),
            ]
        )
    )

    wrapped_body = Table([[body_table]], colWidths=[page_width])
    wrapped_body.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), content_margin),
                ("RIGHTPADDING", (0, 0), (-1, -1), content_margin),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    doc.build([header, wrapped_body])
    return buffer.getvalue()


def render_letter_pdf(letter: Letter, sender) -> bytes:
    styles = _styles()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=25 * mm,
        rightMargin=25 * mm,
        topMargin=25 * mm,
        bottomMargin=25 * mm,
    )

    contact_lines = [p for p in [sender.email, sender.phone, sender.city, sender.linkedin] if p]
    contact_html = "<br/>".join(contact_lines)

    header = Table(
        [
            [
                [
                    Paragraph(f"{sender.first_name or ''} {sender.last_name or ''}".strip(), styles["letter_sender_name"]),
                    Spacer(1, 4),
                    Paragraph(contact_html, styles["letter_sender_info"]),
                ],
                Paragraph(_french_date(date.today()), styles["letter_date"]),
            ]
        ],
        colWidths=[110 * mm, 45 * mm],
    )
    header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))

    flow = [header, Spacer(1, 20)]

    if letter.subject:
        flow.append(Paragraph(f"Objet : {letter.subject}", styles["letter_subject"]))
        flow.append(Spacer(1, 6))
        flow.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
        flow.append(Spacer(1, 18))

    for paragraph in letter.body.split("\n\n"):
        cleaned = paragraph.strip().replace("\n", "<br/>")
        if cleaned:
            flow.append(Paragraph(cleaned, styles["letter_body"]))
            flow.append(Spacer(1, 10))

    doc.build(flow)
    return buffer.getvalue()
