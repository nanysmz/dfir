from __future__ import annotations

import pytest

from dfir_pericia.extractors import ensure_evidence_file, extract_evidence_content
from dfir_pericia.matchers import match_pericia_point
from dfir_pericia.models import EvidenceFile, PericiaPoint


@pytest.mark.django_db
def test_text_and_html_files_are_normalized_before_matching(tmp_path):
    txt_path = tmp_path / "note.txt"
    txt_path.write_text(
        "Contacto analyst@example.com en la evidencia", encoding="utf-8"
    )
    html_path = tmp_path / "report.html"
    html_path.write_text(
        "<html><body><h1>Hallazgo</h1><p>transferencia sospechosa</p></body></html>",
        encoding="utf-8",
    )

    email_point = PericiaPoint.objects.create(
        name="Buscar email analyst",
        point_family=PericiaPoint.PointFamily.TEXT_EMAIL_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.EXACT,
        parameters={"value": "analyst@example.com"},
    )
    keyword_point = PericiaPoint.objects.create(
        name="Buscar transferencia",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.PHRASE,
        parameters={"terms": ["transferencia sospechosa"]},
    )

    text_result = extract_evidence_content(ensure_evidence_file(txt_path))
    html_result = extract_evidence_content(ensure_evidence_file(html_path))

    assert text_result.status == "supported"
    assert html_result.status == "supported"
    assert "Hallazgo" in html_result.content.text
    assert "<h1>" not in html_result.content.text

    email_findings = match_pericia_point(email_point, text_result)
    keyword_findings = match_pericia_point(keyword_point, html_result)

    assert [finding["matched_value"] for finding in email_findings] == [
        "analyst@example.com"
    ]
    assert [finding["matched_value"] for finding in keyword_findings] == [
        "transferencia sospechosa"
    ]


@pytest.mark.django_db
def test_image_matching_uses_normalized_labels(tmp_path):
    image_path = tmp_path / "frame.jpg"
    image_path.write_bytes(b"fake-image")
    evidence_file = EvidenceFile.objects.create(
        source_path=str(image_path),
        display_name="frame.jpg",
        file_kind=EvidenceFile.FileKind.IMAGE,
        metadata={
            "image_labels": [
                {"label": "person", "confidence": 0.93},
                {"label": "vehicle", "confidence": 0.41},
            ]
        },
    )
    point = PericiaPoint.objects.create(
        name="Buscar personas",
        point_family=PericiaPoint.PointFamily.IMAGE_CHARACTERISTIC_DETECTION,
        matching_mode=PericiaPoint.MatchingMode.LABEL,
        parameters={"target_labels": ["person"], "min_confidence": 0.8},
    )

    result = extract_evidence_content(evidence_file)
    findings = match_pericia_point(point, result)

    assert result.status == "supported"
    assert findings[0]["matched_value"] == "person"
    assert findings[0]["confidence"] == pytest.approx(0.93)
