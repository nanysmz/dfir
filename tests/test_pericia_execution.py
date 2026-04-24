from __future__ import annotations

import pytest

from dfir_pericia.extractors import ensure_evidence_file
from dfir_pericia.models import EvidenceFile, PericiaFinding, PericiaPoint
from dfir_pericia.services import execute_pericia_point
from dfir_pericia.tasks import execute_pericia_point_task


@pytest.mark.django_db
def test_execution_records_success_unsupported_and_failed_files(tmp_path):
    txt_path = tmp_path / "message.txt"
    txt_path.write_text(
        "transferencia confirmada para analyst@example.com",
        encoding="utf-8",
    )
    pdf_path = tmp_path / "report.pdf"
    pdf_path.write_bytes(b"%PDF-1.4")

    supported_file = ensure_evidence_file(txt_path)
    unsupported_file = ensure_evidence_file(pdf_path)
    failed_file = EvidenceFile.objects.create(
        source_path=str(tmp_path / "missing.txt"),
        display_name="missing.txt",
        file_kind=EvidenceFile.FileKind.TEXT,
    )

    point = PericiaPoint.objects.create(
        name="Buscar transferencia",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["transferencia"]},
    )

    execution = execute_pericia_point(
        point,
        evidence_files=[supported_file, unsupported_file, failed_file],
    )

    assert execution.status == "completed"
    assert execution.analyzed_files_count == 1
    assert execution.unsupported_files_count == 1
    assert execution.failed_files_count == 1
    assert execution.matched_files_count == 1
    assert execution.findings_count == 1
    assert (
        "Extractor adapter not implemented yet"
        in execution.unsupported_files[0]["reason"]
    )
    assert execution.failed_files[0]["source_path"].endswith("missing.txt")

    finding = PericiaFinding.objects.get(execution=execution)
    assert finding.matched_value == "transferencia"
    assert "analyst@example.com" in finding.context
    assert finding.source_locator["start"] >= 0


@pytest.mark.django_db
def test_execute_pericia_point_task_creates_execution_from_file_ids(tmp_path):
    txt_path = tmp_path / "keywords.txt"
    txt_path.write_text("wallet encontrada en el archivo", encoding="utf-8")
    evidence_file = ensure_evidence_file(txt_path)
    point = PericiaPoint.objects.create(
        name="Buscar wallet",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["wallet"]},
    )

    execution_id = execute_pericia_point_task(
        point.pk,
        evidence_file_ids=[evidence_file.pk],
    )

    assert PericiaFinding.objects.filter(execution_id=execution_id).count() == 1
