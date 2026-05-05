from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError

from dfir_pericia.models import (
    AnalysisPlan,
    DeviceAnalysisResult,
    EvidenceFile,
    EvidenceItem,
    PericiaCase,
    PericiaPoint,
    PreservedArtifact,
    ReportSection,
    RequestedPoint,
    RequestedPointResponse,
)
from dfir_pericia.services import execute_pericia_point
from dfir_pericia.workflow import build_case_workflow, build_home_stage_cards


@pytest.mark.django_db
def test_case_workflow_models_validate_case_relationships():
    case = PericiaCase.objects.create(
        case_reference="IPP-001", authority_name="Fiscalia"
    )
    point = RequestedPoint(
        pericia_case=case,
        order=1,
        literal_text="Determinar correo asociado al dispositivo.",
    )
    point.full_clean()
    point.save()

    original = EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
    )
    working_copy = EvidenceItem(
        pericia_case=case,
        parent_item=original,
        label="Imagen forense 1",
        role=EvidenceItem.Role.WORKING_COPY,
        acquisition_status=EvidenceItem.AcquisitionStatus.ACQUIRED,
    )
    working_copy.full_clean()

    invalid_working_copy = EvidenceItem(
        pericia_case=case,
        label="Copia sin origen",
        role=EvidenceItem.Role.WORKING_COPY,
        acquisition_status=EvidenceItem.AcquisitionStatus.ACQUIRED,
    )
    with pytest.raises(ValidationError, match="copias de trabajo"):
        invalid_working_copy.full_clean()

    strategy = PericiaPoint.objects.create(
        name="Buscar correo exacto",
        point_family=PericiaPoint.PointFamily.TEXT_EMAIL_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.EXACT,
        parameters={"value": "analyst@example.com"},
    )
    plan = AnalysisPlan(
        pericia_case=case,
        requested_point=point,
        pericia_point=strategy,
        analysis_targets=["SAM", "Web Accounts"],
    )
    plan.full_clean()
    assert point.metadata["taxonomy_groups"]
    assert plan.build_scope_snapshot()["analysis_playbook"]["actions"]


@pytest.mark.django_db
def test_case_response_can_link_pericia_point_execution(tmp_path):
    evidence_path = tmp_path / "browser.txt"
    evidence_path.write_text(
        "Cuenta registrada analyst@example.com en el historial.",
        encoding="utf-8",
    )
    evidence_file = EvidenceFile.objects.create(
        source_path=str(evidence_path),
        display_name="browser.txt",
        file_kind=EvidenceFile.FileKind.TEXT,
    )
    case = PericiaCase.objects.create(
        case_reference="IPP-TRACE-001",
        authority_name="Fiscalia",
    )
    point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Identificar correos ligados al dispositivo.",
    )
    evidence_item = EvidenceItem.objects.create(
        pericia_case=case,
        evidence_file=evidence_file,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.ACQUIRED,
    )
    device_result = DeviceAnalysisResult.objects.create(
        pericia_case=case,
        evidence_item=evidence_item,
        status=DeviceAnalysisResult.Status.ANALYZED,
    )
    strategy = PericiaPoint.objects.create(
        name="Buscar correo analyst",
        point_family=PericiaPoint.PointFamily.TEXT_EMAIL_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.EXACT,
        parameters={"value": "analyst@example.com"},
    )
    plan = AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=point,
        pericia_point=strategy,
        analysis_targets=["Web Accounts", "Web History"],
    )

    execution = execute_pericia_point(
        strategy,
        evidence_files=[evidence_file],
        analysis_plan=plan,
        device_analysis_result=device_result,
    )
    response = RequestedPointResponse.objects.create(
        pericia_case=case,
        requested_point=point,
        status=RequestedPointResponse.Status.ANSWERED,
        summary="Se localizo un correo asociado al dispositivo.",
        rationale="El hallazgo surge del analisis del archivo textual.",
    )
    response.device_analysis_results.add(device_result)
    response.executions.add(execution)
    response.findings.add(*execution.findings.all())

    assert execution.analysis_plan == plan
    assert execution.device_analysis_result == device_result
    finding = execution.findings.get()
    assert finding.device_analysis_result == device_result
    assert response.executions.count() == 1
    assert response.findings.count() == 1
    assert response.findings.get().matched_value == "analyst@example.com"


@pytest.mark.django_db
def test_technical_limitation_and_preserved_artifact_traceability(tmp_path):
    evidence_path = tmp_path / "artifact.txt"
    evidence_path.write_text("telefono 1164849848", encoding="utf-8")
    evidence_file = EvidenceFile.objects.create(
        source_path=str(evidence_path),
        display_name="artifact.txt",
        file_kind=EvidenceFile.FileKind.TEXT,
    )
    case = PericiaCase.objects.create(
        case_reference="IPP-LIMIT-001",
        authority_name="Fiscalia",
    )
    point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text=(
            "Informar si se puede acceder a la evidencia y si existe " "contenido util."
        ),
    )
    evidence_item = EvidenceItem.objects.create(
        pericia_case=case,
        evidence_file=evidence_file,
        label="Dispositivo no accesible",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.NOT_ACCESSIBLE,
    )
    device_result = DeviceAnalysisResult(
        pericia_case=case,
        evidence_item=evidence_item,
        status=DeviceAnalysisResult.Status.FOLLOW_UP_REQUIRED,
        technical_reason="No se conto con cargador compatible.",
        follow_up_recommendation=(
            "Aportar cargador o evaluar adquisicion especializada."
        ),
    )
    device_result.full_clean()
    device_result.save()

    strategy = PericiaPoint.objects.create(
        name="Buscar telefono",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["1164849848"]},
    )
    execution = execute_pericia_point(
        strategy,
        evidence_files=[evidence_file],
        device_analysis_result=device_result,
    )
    artifact = PreservedArtifact(
        pericia_case=case,
        evidence_item=evidence_item,
        source_finding=execution.findings.get(),
        artifact_kind=PreservedArtifact.ArtifactKind.REPORT_SAMPLE,
        display_name="Muestra para informe",
        storage_path="/evidence/output/case-1/muestra.txt",
    )
    artifact.full_clean()
    artifact.save()

    response = RequestedPointResponse.objects.create(
        pericia_case=case,
        requested_point=point,
        status=RequestedPointResponse.Status.PARTIALLY_ANSWERED,
        summary="Se preservo una muestra y se consigno limitacion tecnica.",
        technical_observations=(
            "El dispositivo requiere insumo adicional para analisis completo."
        ),
    )
    response.device_analysis_results.add(device_result)
    response.findings.add(*execution.findings.all())
    response.preserved_artifacts.add(artifact)

    section = case.report_sections.get(
        section_type=ReportSection.SectionType.OBTAINED_INFORMATION
    )
    section.content = "Detalle de analisis por dispositivo."
    section.save(update_fields=["content"])
    section.responses.add(response)
    section.device_analysis_results.add(device_result)
    section.preserved_artifacts.add(artifact)

    assert device_result.technical_reason == "No se conto con cargador compatible."
    assert "cargador" in device_result.follow_up_recommendation.lower()
    assert response.preserved_artifacts.get() == artifact
    assert section.device_analysis_results.get() == device_result


@pytest.mark.django_db
def test_evidence_item_offered_item_description_uses_structured_metadata():
    case = PericiaCase.objects.create(case_reference="IPP-OFFERED-001")
    evidence_item = EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
        serial_number="SN123",
        metadata={
            "device_class": "unidad de almacenamiento",
            "device_type": "HDD",
            "device_interface": "SATA",
            "device_brand": "Seagate",
            "device_model": "Barracuda",
            "device_capacity_gb": "500",
            "technical_notes": "Sin novedades",
        },
    )

    description = evidence_item.offered_item_description

    assert "unidad de almacenamiento" in description
    assert "tipo HDD" in description
    assert "conexion SATA" in description
    assert "marca Seagate" in description
    assert "modelo Barracuda" in description
    assert "SN123" in description
    assert "500 GB" in description


@pytest.mark.django_db
def test_case_status_is_automatic_from_workflow_progress():
    case = PericiaCase.objects.create(
        case_reference="IPP-STATUS-001",
        authority_name="Fiscalia",
        status=PericiaCase.Status.COMPLETED,
    )

    case.refresh_from_db()
    assert case.status == PericiaCase.Status.INTAKE

    point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Determinar informacion relevante.",
    )
    point.refresh_from_db()
    assert point.status == RequestedPoint.Status.PENDING
    EvidenceItem.objects.create(
        pericia_case=case,
        label="Telefono 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.RECEIVED,
    )

    case.refresh_from_db()
    assert case.status == PericiaCase.Status.EVIDENCE_REGISTERED


@pytest.mark.django_db
def test_new_case_seeds_standard_report_sections_in_expected_order():
    case = PericiaCase.objects.create(case_reference="IPP-REPORT-TPL-001")

    sections = list(
        case.report_sections.order_by("order").values_list("section_type", "title", "order")
    )

    assert sections == [
        (ReportSection.SectionType.OBJECT, "Objeto", 1),
        (ReportSection.SectionType.OFFERED_ELEMENTS, "Elementos ofrecidos", 2),
        (ReportSection.SectionType.TOOLS, "Herramientas", 3),
        (ReportSection.SectionType.METHODOLOGY, "Metodología", 4),
        (ReportSection.SectionType.OBTAINED_INFORMATION, "Información obtenida", 5),
        (ReportSection.SectionType.CONCLUSIONS, "Conclusiones", 6),
        (ReportSection.SectionType.EVIDENCE, "Evidencia", 7),
        (ReportSection.SectionType.ANNEX, "Anexo", 8),
    ]
    case.refresh_from_db()
    assert case.status == PericiaCase.Status.INTAKE


@pytest.mark.django_db
def test_standard_report_section_seed_is_idempotent():
    case = PericiaCase.objects.create(case_reference="IPP-REPORT-TPL-002")

    case.ensure_standard_report_sections()
    case.ensure_standard_report_sections()

    assert case.report_sections.count() == 8


@pytest.mark.django_db
def test_report_section_suggested_content_uses_case_data():
    case = PericiaCase.objects.create(case_reference="IPP-REPORT-TPL-003")
    evidence_item = EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
        metadata={
            "device_class": "unidad de almacenamiento",
            "device_type": "HDD",
            "device_interface": "SATA",
            "device_brand": "WD",
            "device_model": "Blue",
            "serial_number": "SN-1",
            "device_capacity_gb": "500",
        },
    )
    device_result = DeviceAnalysisResult.objects.create(
        pericia_case=case,
        evidence_item=evidence_item,
        status=DeviceAnalysisResult.Status.ANALYZED,
        overview="Se identificó documentación operativa relevante.",
    )

    offered_section = case.report_sections.get(
        section_type=ReportSection.SectionType.OFFERED_ELEMENTS
    )
    obtained_section = case.report_sections.get(
        section_type=ReportSection.SectionType.OBTAINED_INFORMATION
    )

    assert "unidad de almacenamiento" in offered_section.suggested_content()
    assert "500 GB" in offered_section.suggested_content()
    obtained_content = obtained_section.suggested_content()
    assert device_result.evidence_item.label in obtained_content
    assert "documentación operativa relevante" in obtained_content


@pytest.mark.django_db
def test_requested_point_derives_operational_taxonomy_metadata():
    case = PericiaCase.objects.create(case_reference="IPP-TAXONOMY-001")

    point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Identificación de correos electrónicos, credenciales almacenadas y formularios de autocompletado.",
    )

    taxonomy_codes = [group["code"] for group in point.metadata["taxonomy_groups"]]
    assert "credentials_access" in taxonomy_codes

    strategy = PericiaPoint.objects.create(
        name="Buscar termino estado automatico",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["relevante"]},
    )
    AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=point,
        pericia_point=strategy,
    )

    point.refresh_from_db()
    assert point.status == RequestedPoint.Status.IN_PROGRESS

    case.refresh_from_db()
    assert case.status == PericiaCase.Status.ANALYSIS_IN_PROGRESS

    RequestedPointResponse.objects.create(
        pericia_case=case,
        requested_point=point,
        status=RequestedPointResponse.Status.ANSWERED,
        summary="Respuesta preliminar.",
    )

    point.refresh_from_db()
    assert point.status == RequestedPoint.Status.ANSWERED

    case.refresh_from_db()
    assert case.status == PericiaCase.Status.REPORT_IN_PROGRESS

    object_section = case.report_sections.get(
        section_type=ReportSection.SectionType.OBJECT
    )
    object_section.content = "Objeto pericial."
    object_section.save(update_fields=["content"])
    obtained_section = case.report_sections.get(
        section_type=ReportSection.SectionType.OBTAINED_INFORMATION
    )
    obtained_section.content = "Información obtenida."
    obtained_section.save(update_fields=["content"])
    conclusions_section = case.report_sections.get(
        section_type=ReportSection.SectionType.CONCLUSIONS
    )
    conclusions_section.content = "Contenido final."
    conclusions_section.save(update_fields=["content"])

    case.refresh_from_db()
    assert case.status == PericiaCase.Status.COMPLETED

    response = RequestedPointResponse.objects.get(
        pericia_case=case,
        requested_point=point,
    )
    response.status = RequestedPointResponse.Status.BLOCKED
    response.save()

    point.refresh_from_db()
    assert point.status == RequestedPoint.Status.BLOCKED

    case.refresh_from_db()
    assert case.status == PericiaCase.Status.BLOCKED


@pytest.mark.django_db
def test_placeholder_evidence_item_does_not_mark_case_as_evidence_registered():
    case = PericiaCase.objects.create(case_reference="IPP-PLACEHOLDER-001")

    EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
    )

    case.refresh_from_db()
    assert case.status == PericiaCase.Status.INTAKE

    workflow = build_case_workflow(case)
    evidence_stage = next(
        stage for stage in workflow["stages"] if stage["key"] == "evidence"
    )
    assert evidence_stage["complete"] is False

    item = case.evidence_items.get()
    item.acquisition_status = EvidenceItem.AcquisitionStatus.RECEIVED
    item.save()

    case.refresh_from_db()
    assert case.status == PericiaCase.Status.EVIDENCE_REGISTERED


@pytest.mark.django_db
def test_requested_point_status_manual_assignment_is_ignored():
    case = PericiaCase.objects.create(case_reference="IPP-RP-STATUS-001")
    point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Punto de control.",
        status=RequestedPoint.Status.ANSWERED,
    )

    point.refresh_from_db()
    assert point.status == RequestedPoint.Status.PENDING


@pytest.mark.django_db
def test_preserved_artifact_accepts_findings_from_any_associated_file(tmp_path):
    first_path = tmp_path / "evidence-a.txt"
    second_path = tmp_path / "evidence-b.txt"
    first_path.write_text("sin dato", encoding="utf-8")
    second_path.write_text("mail analyst@example.com", encoding="utf-8")

    first_file = EvidenceFile.objects.create(
        source_path=str(first_path),
        display_name="evidence-a.txt",
        file_kind=EvidenceFile.FileKind.TEXT,
    )
    second_file = EvidenceFile.objects.create(
        source_path=str(second_path),
        display_name="evidence-b.txt",
        file_kind=EvidenceFile.FileKind.TEXT,
    )

    case = PericiaCase.objects.create(
        case_reference="IPP-ART-001",
        authority_name="Fiscalia",
    )
    evidence_item = EvidenceItem.objects.create(
        pericia_case=case,
        label="Notebook",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.ACQUIRED,
    )
    evidence_item.evidence_files.set([first_file, second_file])

    point = PericiaPoint.objects.create(
        name="Buscar correo",
        point_family=PericiaPoint.PointFamily.TEXT_EMAIL_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.EXACT,
        parameters={"value": "analyst@example.com"},
    )
    execution = execute_pericia_point(point, evidence_files=[second_file])
    finding = execution.findings.get()

    artifact = PreservedArtifact(
        pericia_case=case,
        evidence_item=evidence_item,
        source_finding=finding,
        artifact_kind=PreservedArtifact.ArtifactKind.REPORT_SAMPLE,
        display_name="Muestra correo",
        storage_path="/evidence/output/muestra.txt",
    )

    artifact.full_clean()


@pytest.mark.django_db
def test_guided_workflow_derives_next_stage_and_blockers():
    case = PericiaCase.objects.create(
        case_reference="IPP-GUIDED-001",
        authority_name="Fiscalia",
    )

    workflow = build_case_workflow(case)

    assert workflow["current_stage"]["key"] == "documents"
    assert workflow["next_stage"]["key"] == "documents"
    assert workflow["completion_ratio"] > 0
    assert workflow["action_items"][0]["title"] == "Documentos"

    RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Determinar si hubo actividad relevante.",
    )
    EvidenceItem.objects.create(
        pericia_case=case,
        label="Telefono 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.RECEIVED,
    )

    workflow = build_case_workflow(case)

    assert workflow["current_stage"]["key"] == "documents"
    analysis_stage = next(
        stage for stage in workflow["stages"] if stage["key"] == "analysis_plans"
    )
    assert analysis_stage["blocked"] is True
    assert "catalogo" in analysis_stage["blockers"][0].lower()


@pytest.mark.django_db
def test_guided_workflow_advances_through_case_stages():
    case = PericiaCase.objects.create(
        case_reference="IPP-GUIDED-002",
        authority_name="Fiscalia",
    )
    case.documents.create(
        title="Oficio judicial",
        document_type="judicial_request",
        extracted_text="Texto util del requerimiento.",
    )
    point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Identificar correos asociados.",
    )
    evidence = EvidenceItem.objects.create(
        pericia_case=case,
        label="Notebook",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.ACQUIRED,
    )
    strategy = PericiaPoint.objects.create(
        name="Workflow guided exact email",
        point_family=PericiaPoint.PointFamily.TEXT_EMAIL_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.EXACT,
        parameters={"value": "analyst@example.com"},
    )

    workflow = build_case_workflow(case)
    assert workflow["current_stage"]["key"] == "analysis_plans"

    AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=point,
        pericia_point=strategy,
    )
    workflow = build_case_workflow(case)
    assert workflow["current_stage"]["key"] == "device_results"

    DeviceAnalysisResult.objects.create(
        pericia_case=case,
        evidence_item=evidence,
        status=DeviceAnalysisResult.Status.ANALYZED,
        overview="Equipo revisado.",
    )
    workflow = build_case_workflow(case)
    assert workflow["current_stage"]["key"] == "responses"

    RequestedPointResponse.objects.create(
        pericia_case=case,
        requested_point=point,
        status=RequestedPointResponse.Status.ANSWERED,
        summary="Se detecto una cuenta relevante.",
        rationale="La respuesta surge del analisis tecnico del equipo.",
    )
    workflow = build_case_workflow(case)
    assert workflow["current_stage"]["key"] == "report"

    object_section = case.report_sections.get(
        section_type=ReportSection.SectionType.OBJECT
    )
    object_section.content = "Objeto pericial."
    object_section.save(update_fields=["content"])
    obtained_section = case.report_sections.get(
        section_type=ReportSection.SectionType.OBTAINED_INFORMATION
    )
    obtained_section.content = "Hallazgos por dispositivo."
    obtained_section.save(update_fields=["content"])
    conclusions_section = case.report_sections.get(
        section_type=ReportSection.SectionType.CONCLUSIONS
    )
    conclusions_section.content = "Conclusiones finales."
    conclusions_section.save(update_fields=["content"])

    workflow = build_case_workflow(case)
    assert workflow["current_stage"]["key"] == "final_review"
    assert workflow["is_complete"] is True


def test_home_stage_cards_stay_global_for_new_case_entry():
    cards = build_home_stage_cards()
    start_card = next(card for card in cards if card["key"] == "case_setup")
    evidence_card = next(card for card in cards if card["key"] == "evidence")

    assert start_card["state"] == "ready"
    assert start_card["cta_label"] == "Crear caso"
    assert evidence_card["state"] == "upcoming"
