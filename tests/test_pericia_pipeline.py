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
    email_fragment = email_findings[0]["source_locator"]["line_fragment"]
    assert email_fragment["matched_line_number"] == 1
    email_matched_line = email_fragment["lines"][email_fragment["matched_line_index"]]
    assert email_matched_line["is_match"] is True
    assert "analyst@example.com" in email_findings[0]["context"]


@pytest.mark.django_db
def test_text_findings_store_surrounding_lines_window(tmp_path):
    text_path = tmp_path / "multiline.txt"
    text_path.write_text(
        "\n".join(
            [
                "linea 1",
                "linea 2",
                "linea 3",
                "linea 4",
                "hallazgo wallet aqui",
                "linea 6",
                "linea 7",
            ]
        ),
        encoding="utf-8",
    )
    point = PericiaPoint.objects.create(
        name="Buscar wallet multilinea",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["wallet"]},
    )

    result = extract_evidence_content(ensure_evidence_file(text_path))
    findings = match_pericia_point(point, result)

    fragment = findings[0]["source_locator"]["line_fragment"]
    assert fragment["matched_line_number"] == 5
    matched_line = fragment["lines"][fragment["matched_line_index"]]
    assert matched_line["text"] == "hallazgo wallet aqui"
    assert fragment["lines"][0]["text"] == "linea 1"
    assert fragment["lines"][-1]["text"] == "linea 7"


@pytest.mark.django_db
def test_text_findings_store_correct_line_for_crlf_text(tmp_path):
    text_path = tmp_path / "windows-lines.txt"
    text_path.write_text(
        "linea previa\r\nlinea intermedia\r\nlinea wallet objetivo\r\n",
        encoding="utf-8",
    )
    point = PericiaPoint.objects.create(
        name="Buscar wallet CRLF",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["wallet"]},
    )

    result = extract_evidence_content(ensure_evidence_file(text_path))
    findings = match_pericia_point(point, result)

    fragment = findings[0]["source_locator"]["line_fragment"]
    matched_line = fragment["lines"][fragment["matched_line_index"]]
    assert fragment["matched_line_number"] == 3
    assert matched_line["text"] == "linea wallet objetivo"
    assert matched_line["is_match"] is True


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
