from __future__ import annotations

import json
from pathlib import Path

import pytest
from django.core.management import call_command
from docx import Document
from PIL import Image, PngImagePlugin

from dfir_pericia.extractors import ensure_evidence_file
from dfir_pericia.models import (
    DeviceAnalysisResult,
    EvidenceFile,
    EvidenceItem,
    PericiaCase,
    PericiaExecution,
    PericiaFinding,
    PericiaPoint,
    PreservedArtifact,
)
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
    assert execution.unsupported_files[0]["source_path"].endswith("report.pdf")
    assert execution.unsupported_files[0]["reason"]
    assert execution.failed_files[0]["source_path"].endswith("missing.txt")
    assert execution.engine_metadata["progress"]["phase"] == "completed"
    assert execution.engine_metadata["progress"]["total_files"] == 3
    assert execution.engine_metadata["progress"]["processed_files"] == 3

    finding = PericiaFinding.objects.get(execution=execution)
    assert finding.matched_value == "transferencia"
    assert "analyst@example.com" in finding.context
    assert finding.source_locator["start"] >= 0
    assert finding.contextual_fragment["matched_line_number"] == 1
    assert finding.contextual_fragment["lines"][0]["is_match"] is True


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


@pytest.mark.django_db
def test_execute_pericia_point_task_queues_execution_when_not_eager(tmp_path, settings, monkeypatch):
    txt_path = tmp_path / "keywords.txt"
    txt_path.write_text("wallet encontrada en el archivo", encoding="utf-8")
    evidence_file = ensure_evidence_file(txt_path)
    point = PericiaPoint.objects.create(
        name="Buscar wallet async",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["wallet"]},
    )
    settings.CELERY_TASK_ALWAYS_EAGER = False

    captured: dict = {}

    def fake_delay(execution_id, evidence_file_ids=None, source_paths=None):
        captured["execution_id"] = execution_id
        captured["evidence_file_ids"] = evidence_file_ids or []
        captured["source_paths"] = source_paths

    monkeypatch.setattr(
        "dfir_pericia.tasks.run_pericia_execution_task.delay",
        fake_delay,
    )

    execution_id = execute_pericia_point_task(
        point.pk,
        evidence_file_ids=[evidence_file.pk],
    )

    execution = PericiaExecution.objects.get(pk=execution_id)
    assert execution.status == PericiaExecution.Status.PENDING
    assert execution.engine_metadata["progress"]["phase"] == "queued"
    assert execution.engine_metadata["progress"]["total_files"] == 1
    assert captured["execution_id"] == execution_id
    assert captured["evidence_file_ids"] == [evidence_file.pk]


@pytest.mark.django_db
def test_execute_pericia_point_expands_directory_and_exports_matches(tmp_path, settings):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    device_dir = input_root / "IPP-EXPORT-001" / "Dispositivo_3"
    nested_dir = device_dir / "nested"
    nested_dir.mkdir(parents=True)
    output_root.mkdir()
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    txt_path = device_dir / "chat.txt"
    txt_path.write_text("wallet encontrada en chat\notra wallet en historial", encoding="utf-8")
    html_path = nested_dir / "historial.html"
    html_path.write_text("<html><body>wallet en html</body></html>", encoding="utf-8")

    case = PericiaCase.objects.create(case_reference="IPP-EXPORT-001")
    item = EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 3",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.ACQUIRED,
        source_path=str(device_dir),
    )
    device_result = DeviceAnalysisResult.objects.create(
        pericia_case=case,
        evidence_item=item,
        status=DeviceAnalysisResult.Status.ANALYZED,
    )
    point = PericiaPoint.objects.create(
        name="Buscar wallet",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["wallet"]},
    )

    execution = execute_pericia_point(
        point,
        source_paths=[str(device_dir)],
        device_analysis_result=device_result,
    )

    assert execution.status == "completed"
    assert execution.analyzed_files_count == 2
    assert execution.matched_files_count == 2
    assert execution.findings_count == 3
    assert execution.engine_metadata["exported_artifacts_count"] == 3

    artifact = PreservedArtifact.objects.filter(
        pericia_case=case,
        evidence_item=item,
    ).order_by("id").first()
    assert artifact is not None
    assert "/ipp-export-001/dispositivo-3/buscar-wallet/" in artifact.storage_path

    payload = json.loads((Path(artifact.storage_path)).read_text(encoding="utf-8"))
    assert payload["case_reference"] == "IPP-EXPORT-001"
    assert payload["device_label"] == "Dispositivo 3"
    assert payload["source"]["full_path"].endswith(("chat.txt", "historial.html"))
    assert "filesystem_dates" in payload["source"]["extraction_metadata"]
    assert payload["contextual_fragment"]["lines"]
    assert any(line["is_match"] for line in payload["contextual_fragment"]["lines"])


@pytest.mark.django_db
def test_execute_pericia_point_supports_docx_and_image_metadata_search(
    tmp_path, settings
):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    device_dir = input_root / "IPP-MEDIA-001" / "Dispositivo_1"
    device_dir.mkdir(parents=True)
    output_root.mkdir()
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    docx_path = device_dir / "nota.docx"
    document = Document()
    document.add_paragraph("La keyword secreta aparece en el documento DOCX.")
    document.save(str(docx_path))

    png_path = device_dir / "captura.png"
    image = Image.new("RGB", (20, 20), color="white")
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Description", "keyword secreta visible en metadata")
    image.save(str(png_path), pnginfo=metadata)

    point = PericiaPoint.objects.create(
        name="Buscar keyword",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["keyword"]},
    )

    execution = execute_pericia_point(point, source_paths=[str(device_dir)])

    matched_paths = {
        finding.evidence_file.source_path for finding in execution.findings.select_related("evidence_file")
    }
    assert str(docx_path) in matched_paths
    assert str(png_path) in matched_paths


@pytest.mark.django_db
def test_run_pericia_point_command_uses_device_context_sources(tmp_path, settings, capsys):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    device_dir = input_root / "IPP-CMD-001" / "Dispositivo_2"
    device_dir.mkdir(parents=True)
    output_root.mkdir()
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    txt_path = device_dir / "mensaje.txt"
    txt_path.write_text("token encontrado", encoding="utf-8")

    case = PericiaCase.objects.create(case_reference="IPP-CMD-001")
    item = EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 2",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.ACQUIRED,
        source_path=str(device_dir),
    )
    device_result = DeviceAnalysisResult.objects.create(
        pericia_case=case,
        evidence_item=item,
        status=DeviceAnalysisResult.Status.ANALYZED,
    )
    point = PericiaPoint.objects.create(
        name="Buscar token",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["token"]},
    )

    call_command(
        "run_pericia_point",
        "--point-id",
        str(point.pk),
        "--device-analysis-result-id",
        str(device_result.pk),
    )
    captured = capsys.readouterr()

    assert "Ejecucion completada" in captured.out
    assert PericiaFinding.objects.filter(pericia_point=point).count() == 1
