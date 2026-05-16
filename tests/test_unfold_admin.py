from __future__ import annotations

import pytest
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.test import RequestFactory
from django.urls import reverse
from unfold.admin import ModelAdmin, StackedInline

from dfir_analysis.models import AnalysisPlanProxy
from dfir_core.admin_forms import EvidenceItemAdminForm
from dfir_cases.admin import (
    EvidenceItemInline,
    PericiaCaseAdmin,
    ReportSectionInline,
    RequestedPointInline,
)
from dfir_cases.models import PericiaCaseProxy
from dfir_evidence.models import EvidenceItemProxy
from dfir_pericia.models import (
    AnalysisPlan,
    DeviceAnalysisResult,
    EvidenceFile,
    EvidenceItem,
    PericiaCase,
    PericiaExecution,
    PericiaFinding,
    PericiaPoint,
    ReportSection,
    RequestedPoint,
)
from dfir_analysis.admin import PericiaExecutionAdmin as AnalysisExecutionAdmin
from dfir_analysis.models import PericiaExecutionProxy
from dfir_reports.models import ReportSectionProxy


def test_unfold_sidebar_navigation_matches_domain_groups():
    navigation = settings.UNFOLD["SIDEBAR"]["navigation"]

    assert navigation[0]["title"] == "Flujo pericial"
    assert [item["title"] for item in navigation[0]["items"]] == [
        "Inicio",
        "Casos periciales",
        "Evidencia",
        "Analisis",
        "Informe",
    ]
    assert navigation[1]["title"] == "Administracion del sistema"


def test_domain_admin_classes_use_unfold_modeladmin():
    assert issubclass(PericiaCaseAdmin, ModelAdmin)
    assert issubclass(admin.site._registry[PericiaCaseProxy].__class__, ModelAdmin)
    assert issubclass(admin.site._registry[AnalysisPlanProxy].__class__, ModelAdmin)
    assert issubclass(admin.site._registry[EvidenceItemProxy].__class__, ModelAdmin)
    assert issubclass(admin.site._registry[ReportSectionProxy].__class__, ModelAdmin)
    assert issubclass(admin.site._registry[User].__class__, ModelAdmin)
    assert issubclass(admin.site._registry[Group].__class__, ModelAdmin)


def test_case_inlines_use_unfold_stacked_inline():
    for inline in (
        RequestedPointInline,
        EvidenceItemInline,
        ReportSectionInline,
    ):
        assert issubclass(inline, StackedInline)


@pytest.mark.django_db
def test_admin_index_shows_workflow_shortcuts(client):
    user = User.objects.create_superuser(
        username="admin",
        email="admin@example.local",
        password="secret",
    )
    client.force_login(user)

    response = client.get(reverse("admin:index"))

    body = response.content.decode()
    assert response.status_code == 200
    assert "Flujo pericial" in body
    assert "Empezar una pericia" in body
    assert "Paso 1" in body
    assert "Iniciar nueva pericia" in body
    assert "Registrar evidencia" in body
    assert "Planificar y ejecutar analisis" in body
    assert "Cerrar informe" in body
    assert "Accion principal" in body


@pytest.mark.django_db
def test_admin_index_shows_resume_guidance_for_existing_case(client):
    user = User.objects.create_superuser(
        username="admin_resume_case",
        email="admin.resume.case@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(
        case_reference="CASE-RESUME-001",
        authority_name="Fiscalia",
    )
    RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Identificar actividad del dispositivo.",
    )

    response = client.get(reverse("admin:index"))

    body = response.content.decode()
    assert response.status_code == 200
    assert "Retomar pericias" in body
    assert "CASE-RESUME-001" in body
    assert "Siguiente paso:" in body
    assert "Completado" in body or "Bloqueado" in body or "Listo" in body
    assert "Listo" in body
    assert "Crear caso" in body


@pytest.mark.django_db
def test_admin_index_keeps_start_cards_global_even_with_active_cases(client):
    user = User.objects.create_superuser(
        username="admin_stage_states",
        email="admin.stage.states@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(
        case_reference="CASE-STAGES-001",
        authority_name="Fiscalia",
    )
    RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Determinar actividad del dispositivo.",
    )
    EvidenceItem.objects.create(
        pericia_case=case,
        label="Telefono 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.RECEIVED,
    )

    response = client.get(reverse("admin:index"))

    body = response.content.decode()
    assert response.status_code == 200
    assert "Listo" in body
    assert "Crear caso" in body
    assert "Se habilita naturalmente despues de iniciar y guardar el caso." in body


@pytest.mark.django_db
def test_case_admin_add_view_renders_with_guided_inline_fields(client):
    user = User.objects.create_superuser(
        username="admin_add_case",
        email="admin.add.case@example.local",
        password="secret",
    )
    client.force_login(user)

    response = client.get(reverse("admin:dfir_cases_periciacaseproxy_add"))

    assert response.status_code == 200
    assert "Tipo de dispositivo" in response.content.decode()
    assert "cantidad inicial de dispositivos" in response.content.decode().lower()
    assert "fuente primaria de evidencia del dispositivo" in response.content.decode().lower()


@pytest.mark.django_db
def test_case_admin_change_view_shows_requested_point_case_scope_help(client):
    user = User.objects.create_superuser(
        username="admin_case_requested_point_help",
        email="admin.case.requested.point.help@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(case_reference="CASE-RP-HELP-001")
    RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        short_label="Punto 1",
        literal_text="Texto 1",
    )

    response = client.get(reverse("admin:dfir_cases_periciacaseproxy_change", args=[case.pk]))

    body = response.content.decode()
    assert response.status_code == 200
    assert "Cada punto solicitado pertenece solo a esta pericia y su orden se define dentro de este caso." in body


@pytest.mark.django_db
def test_requested_point_admin_add_view_explains_case_local_scope(client):
    user = User.objects.create_superuser(
        username="admin_requested_point_scope",
        email="admin.requested.point.scope@example.local",
        password="secret",
    )
    client.force_login(user)

    response = client.get(reverse("admin:dfir_cases_requestedpointproxy_add"))

    body = response.content.decode()
    assert response.status_code == 200
    assert "Caso pericial" in body
    assert "Cada punto solicitado pertenece solo a esta pericia." in body
    assert "El orden es local a esta pericia" in body


@pytest.mark.django_db
def test_case_admin_creates_initial_devices_on_add(client):
    user = User.objects.create_superuser(
        username="admin_add_case_devices",
        email="admin.add.case.devices@example.local",
        password="secret",
    )
    client.force_login(user)

    payload = {
        "case_reference": "CASE-INIT-DEV-001",
        "title": "Pericia con dispositivos",
        "summary": "",
        "authority_name": "Fiscalia",
        "authority_unit": "UFI 1",
        "jurisdiction": "La Plata",
        "report_date": "",
        "analyst_name": "Perito A",
        "analyst_badge": "LEG-001",
        "metadata": "{}",
        "initial_device_count": "3",
        "requested_points-TOTAL_FORMS": "0",
        "requested_points-INITIAL_FORMS": "0",
        "requested_points-MIN_NUM_FORMS": "0",
        "requested_points-MAX_NUM_FORMS": "1000",
        "evidence_items-TOTAL_FORMS": "0",
        "evidence_items-INITIAL_FORMS": "0",
        "evidence_items-MIN_NUM_FORMS": "0",
        "evidence_items-MAX_NUM_FORMS": "1000",
        "report_sections-TOTAL_FORMS": "0",
        "report_sections-INITIAL_FORMS": "0",
        "report_sections-MIN_NUM_FORMS": "0",
        "report_sections-MAX_NUM_FORMS": "1000",
        "_save": "Guardar",
    }

    response = client.post(reverse("admin:dfir_cases_periciacaseproxy_add"), payload)
    assert response.status_code == 302

    case = PericiaCase.objects.get(case_reference="CASE-INIT-DEV-001")
    labels = list(
        EvidenceItem.objects.filter(pericia_case=case)
        .order_by("created_at", "id")
        .values_list("label", flat=True)
    )
    assert labels == ["Dispositivo 1", "Dispositivo 2", "Dispositivo 3"]
    section_titles = list(
        ReportSection.objects.filter(pericia_case=case)
        .order_by("order")
        .values_list("title", flat=True)
    )
    assert section_titles == [
        "Objeto",
        "Elementos ofrecidos",
        "Herramientas",
        "Metodología",
        "Información obtenida",
        "Conclusiones",
        "Evidencia",
        "Anexo",
    ]


@pytest.mark.django_db
def test_case_admin_addanother_redirects_to_same_case_change_view():
    case = PericiaCase.objects.create(case_reference="CASE-REDIRECT-001")
    model_admin = admin.site._registry[PericiaCaseProxy]
    request = RequestFactory().post(
        "/admin/dfir_cases/periciacaseproxy/{}/change/".format(case.pk),
        {
            "_addanother": "1",
            "_active_tab_label": "Puntos solicitados",
        },
    )

    response = model_admin.response_change(request, case)

    assert response.status_code == 302
    assert (
        response["Location"]
        == "/admin/dfir_cases/periciacaseproxy/{}/change/?_active_tab=Puntos%20solicitados".format(
            case.pk
        )
    )


@pytest.mark.django_db
def test_case_admin_status_is_rendered_as_readonly_badge():
    model_admin = admin.site._registry[PericiaCaseProxy]
    request = RequestFactory().get("/admin/dfir_cases/periciacaseproxy/add/")

    readonly_fields = model_admin.get_readonly_fields(request)

    assert "status_badge" in readonly_fields
    assert "status" not in readonly_fields

    general_fields = PericiaCaseAdmin.fieldsets[0][1]["fields"]
    assert "status_badge" in general_fields
    assert "status" not in general_fields


@pytest.mark.django_db
def test_case_admin_status_badge_uses_colored_markup():
    case = PericiaCase.objects.create(case_reference="CASE-BADGE-001")
    model_admin = admin.site._registry[PericiaCaseProxy]

    markup = str(model_admin.status_badge(case))

    assert "Ingreso" in markup
    assert "border-radius:9999px" in markup
    assert "background:#e2e8f0" in markup


@pytest.mark.django_db
def test_analysis_execution_admin_is_readonly_and_disallows_manual_add():
    model_admin = admin.site._registry[PericiaExecutionProxy]
    request = RequestFactory().get("/admin/dfir_analysis/periciaexecutionproxy/")

    assert isinstance(model_admin, AnalysisExecutionAdmin)
    assert "status" in model_admin.readonly_fields
    assert "analyzed_files_count" in model_admin.readonly_fields
    assert model_admin.has_add_permission(request) is False


@pytest.mark.django_db
def test_case_admin_guided_seed_view_creates_device_templates(client):
    user = User.objects.create_superuser(
        username="admin_seed",
        email="admin.seed@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(case_reference="CASE-GUIDED-001")

    url = reverse(
        "admin:dfir_cases_periciacaseproxy_seed_device_types",
        args=[case.pk],
    )
    response = client.get(url)

    assert response.status_code == 302
    assert "_active_tab=Elementos%20de%20evidencia" in response["Location"]
    expected_count = len(
        [key for key in EvidenceItemAdminForm.DEVICE_TEMPLATE_DATA.keys() if key]
    )
    assert EvidenceItem.objects.filter(pericia_case=case).count() == expected_count


@pytest.mark.django_db
def test_case_admin_guided_seed_view_does_not_duplicate_existing_devices(client):
    user = User.objects.create_superuser(
        username="admin_seed_existing",
        email="admin.seed.existing@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(case_reference="CASE-GUIDED-EXISTING-001")
    EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
    )
    EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 2",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
    )

    url = reverse(
        "admin:dfir_cases_periciacaseproxy_seed_device_types",
        args=[case.pk],
    )
    response = client.get(url)

    assert response.status_code == 302
    assert "_active_tab=Elementos%20de%20evidencia" in response["Location"]
    assert EvidenceItem.objects.filter(pericia_case=case).count() == 2


@pytest.mark.django_db
def test_evidence_file_admin_search_returns_directories_and_files(client, settings, tmp_path):
    user = User.objects.create_superuser(
        username="admin_evidence_file_search",
        email="admin.evidence.file.search@example.local",
        password="secret",
    )
    client.force_login(user)
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    (input_root / "extraccion").mkdir()
    (input_root / "captura.txt").write_text("ok", encoding="utf-8")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    url = reverse("admin:dfir_evidence_evidencefileproxy_mounted_path_search")
    response = client.get(url)

    assert response.status_code == 200
    results = response.json()["results"]
    assert any(item["label"] == "[dir] extraccion" for item in results)
    assert any(item["label"] == "captura.txt" for item in results)


@pytest.mark.django_db
def test_evidence_item_primary_source_browser_starts_from_first_level(client, settings, tmp_path):
    user = User.objects.create_superuser(
        username="admin_evidence_item_browser_root",
        email="admin.evidence.item.browser.root@example.local",
        password="secret",
    )
    client.force_login(user)
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    top_dir = input_root / "dispositivo1"
    top_dir.mkdir()
    (top_dir / "ArchivosPDF").mkdir()
    (top_dir / "ActividadReciente").mkdir()
    (top_dir / "nota.txt").write_text("ok", encoding="utf-8")
    (input_root / "captura.txt").write_text("ok", encoding="utf-8")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    url = reverse("admin:dfir_evidence_evidencefileproxy_mounted_path_search")
    response = client.get(url, {"browser": "1"})

    assert response.status_code == 200
    payload = response.json()
    labels = [item["label"] for item in payload["results"]]
    assert "Entrada / dispositivo1" in labels
    assert "Entrada / captura.txt" in labels
    assert not any("ArchivosPDF" in label for label in labels)
    assert payload["current_path"] == ""
    assert payload["parent_path"] == ""


@pytest.mark.django_db
def test_evidence_item_primary_source_browser_can_navigate_and_resolve_existing_path(
    client, settings, tmp_path
):
    user = User.objects.create_superuser(
        username="admin_evidence_item_browser_nested",
        email="admin.evidence.item.browser.nested@example.local",
        password="secret",
    )
    client.force_login(user)
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    target_dir = input_root / "dispositivo1" / "ArchivosPDF"
    target_dir.mkdir(parents=True)
    (target_dir / "informe.pdf").write_text("pdf", encoding="utf-8")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    url = reverse("admin:dfir_evidence_evidencefileproxy_mounted_path_search")

    nested_response = client.get(
        url,
        {"browser": "1", "current_path": str(target_dir.parent)},
    )
    assert nested_response.status_code == 200
    nested_payload = nested_response.json()
    nested_labels = [item["label"] for item in nested_payload["results"]]
    assert "Entrada / dispositivo1/ArchivosPDF" in nested_labels
    assert nested_payload["current_path"] == str(target_dir.parent.resolve())
    assert nested_payload["parent_path"] == str(input_root.resolve())

    resolved_response = client.get(
        url,
        {"browser": "1", "resolve": str(target_dir / "informe.pdf")},
    )
    assert resolved_response.status_code == 200
    resolved_payload = resolved_response.json()
    assert resolved_payload["selected_path"] == str((target_dir / "informe.pdf").resolve())
    assert resolved_payload["current_path"] == str(target_dir.resolve())
    assert any(
        item["value"] == str((target_dir / "informe.pdf").resolve())
        for item in resolved_payload["results"]
    )


@pytest.mark.django_db
def test_evidence_item_admin_add_view_uses_path_autocomplete_for_primary_evidence(client):
    user = User.objects.create_superuser(
        username="admin_evidence_item_add",
        email="admin.evidence.item.add@example.local",
        password="secret",
    )
    client.force_login(user)

    response = client.get(reverse("admin:dfir_evidence_evidenceitemproxy_add"))

    body = response.content.decode()
    assert response.status_code == 200
    assert "/admin/dfir_evidence/evidencefileproxy/mounted-path-search/" in body
    assert "data-mounted-path-browser=\"true\"" in body
    assert "Buscar archivo o carpeta primaria de evidencia" in body
    assert "Evidence file" not in body


@pytest.mark.django_db
def test_evidence_file_admin_list_shows_case_and_device_context(client):
    user = User.objects.create_superuser(
        username="admin_evidence_file_context",
        email="admin.evidence.file.context@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(case_reference="CASE-EF-CTX-001")
    evidence_file = EvidenceFile.objects.create(
        source_path="/tmp/dispositivo1.txt",
        display_name="dispositivo1.txt",
        file_kind=EvidenceFile.FileKind.UNKNOWN,
    )
    EvidenceItem.objects.create(
        pericia_case=case,
        evidence_file=evidence_file,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
    )

    response = client.get(reverse("admin:dfir_evidence_evidencefileproxy_changelist"))

    body = response.content.decode()
    assert response.status_code == 200
    assert "CASE-EF-CTX-001" in body
    assert "Dispositivo 1" in body


@pytest.mark.django_db
def test_evidence_file_admin_list_identifies_shared_and_unassociated_files(client):
    user = User.objects.create_superuser(
        username="admin_evidence_file_shared",
        email="admin.evidence.file.shared@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(case_reference="CASE-EF-CTX-002")
    shared_file = EvidenceFile.objects.create(
        source_path="/tmp/shared.txt",
        display_name="shared.txt",
        file_kind=EvidenceFile.FileKind.TEXT,
    )
    orphan_file = EvidenceFile.objects.create(
        source_path="/tmp/orphan.txt",
        display_name="orphan.txt",
        file_kind=EvidenceFile.FileKind.TEXT,
    )
    first = EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
    )
    second = EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 2",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
    )
    first.evidence_files.add(shared_file)
    second.evidence_files.add(shared_file)

    response = client.get(reverse("admin:dfir_evidence_evidencefileproxy_changelist"))

    body = response.content.decode()
    assert response.status_code == 200
    assert "shared.txt" in body
    assert "+1 asociado(s)" in body
    assert "Sin asociacion pericial visible" in body
    assert "Sin dispositivos asociados" in body


@pytest.mark.django_db
def test_evidence_file_admin_detail_explains_associations(client):
    user = User.objects.create_superuser(
        username="admin_evidence_file_detail",
        email="admin.evidence.file.detail@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(case_reference="CASE-EF-CTX-003")
    evidence_file = EvidenceFile.objects.create(
        source_path="/tmp/report.html",
        display_name="report.html",
        file_kind=EvidenceFile.FileKind.HTML,
    )
    item = EvidenceItem.objects.create(
        pericia_case=case,
        evidence_file=evidence_file,
        label="Dispositivo 9",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
    )

    response = client.get(
        reverse("admin:dfir_evidence_evidencefileproxy_change", args=[evidence_file.pk])
    )

    body = response.content.decode()
    assert response.status_code == 200
    assert "pericia asociada" in body.lower()
    assert case.case_reference in body
    assert f"{case.case_reference} / {item.label}" in body


@pytest.mark.django_db
def test_evidence_file_admin_surfaces_homonymous_records_across_cases(client):
    user = User.objects.create_superuser(
        username="admin_evidence_file_homonymous",
        email="admin.evidence.file.homonymous@example.local",
        password="secret",
    )
    client.force_login(user)
    first_case = PericiaCase.objects.create(case_reference="CASE-EF-HOM-001")
    second_case = PericiaCase.objects.create(case_reference="CASE-EF-HOM-002")
    repeated_source_path = "/evidence/input/dispositivo1/report.html"
    first_file = EvidenceFile.objects.create(
        identity_scope=EvidenceFile.case_identity_scope(first_case.pk),
        source_path=repeated_source_path,
        display_name="report.html",
        file_kind=EvidenceFile.FileKind.HTML,
    )
    second_file = EvidenceFile.objects.create(
        identity_scope=EvidenceFile.case_identity_scope(second_case.pk),
        source_path=repeated_source_path,
        display_name="report.html",
        file_kind=EvidenceFile.FileKind.HTML,
    )
    EvidenceItem.objects.create(
        pericia_case=first_case,
        evidence_file=first_file,
        label="Dispositivo A",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
    )
    EvidenceItem.objects.create(
        pericia_case=second_case,
        evidence_file=second_file,
        label="Dispositivo B",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
    )

    changelist_response = client.get(
        reverse("admin:dfir_evidence_evidencefileproxy_changelist") + "?q=report.html"
    )
    changelist_body = changelist_response.content.decode()

    assert changelist_response.status_code == 200
    assert "contexto de identidad" in changelist_body.lower()
    assert "homonimos" in changelist_body.lower()
    assert "CASE-EF-HOM-001 / scope pericial" in changelist_body
    assert "CASE-EF-HOM-002 / scope pericial" in changelist_body

    detail_response = client.get(
        reverse("admin:dfir_evidence_evidencefileproxy_change", args=[first_file.pk])
    )
    detail_body = detail_response.content.decode()

    assert detail_response.status_code == 200
    assert "homonimos en otros contextos" in detail_body.lower()
    assert "CASE-EF-HOM-002 / scope pericial / /evidence/input/dispositivo1/report.html" in detail_body


@pytest.mark.django_db
def test_pericia_finding_admin_shows_highlighted_fragment(client):
    user = User.objects.create_superuser(
        username="admin_finding_fragment",
        email="admin.finding.fragment@example.local",
        password="secret",
    )
    client.force_login(user)
    point = PericiaPoint.objects.create(
        name="Buscar wallet admin",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["wallet"]},
    )
    evidence_file = EvidenceFile.objects.create(
        source_path="/tmp/hallazgo.txt",
        display_name="hallazgo.txt",
        file_kind=EvidenceFile.FileKind.TEXT,
    )
    execution = PericiaExecution.objects.create(
        pericia_point=point,
        status=PericiaExecution.Status.COMPLETED,
    )
    finding = PericiaFinding.objects.create(
        execution=execution,
        pericia_point=point,
        evidence_file=evidence_file,
        matched_value="wallet",
        context="linea previa\nlinea wallet\nlinea posterior",
        source_locator={
            "start": 12,
            "end": 18,
            "line_fragment": {
                "matched_line_number": 2,
                "matched_line_index": 1,
                "window": 10,
                "lines": [
                    {"line_number": 1, "text": "linea previa", "is_match": False},
                    {"line_number": 2, "text": "linea wallet", "is_match": True},
                    {"line_number": 3, "text": "linea posterior", "is_match": False},
                ],
            },
        },
    )

    response = client.get(
        reverse("admin:dfir_pericia_periciafinding_change", args=[finding.pk])
    )

    body = response.content.decode()
    assert response.status_code == 200
    assert "fragmento contextual" in body.lower()
    assert "linea previa" in body
    assert "linea wallet" in body
    assert "linea posterior" in body


@pytest.mark.django_db
def test_case_admin_guided_seed_analysis_view_creates_plans(client):
    user = User.objects.create_superuser(
        username="admin_plan_seed",
        email="admin.plan.seed@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(case_reference="CASE-GUIDED-PLAN-001")
    RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Identificar actividad de navegacion.",
    )

    url = reverse(
        "admin:dfir_cases_periciacaseproxy_seed_analysis_plans",
        args=[case.pk],
    )
    response = client.get(url)

    assert response.status_code == 302
    assert "admin/dfir_analysis/analysisplanproxy/" in response["Location"]
    assert AnalysisPlan.objects.filter(pericia_case=case).count() == 1


@pytest.mark.django_db
def test_analysis_plan_change_view_shows_execute_button(client):
    user = User.objects.create_superuser(
        username="admin_plan_execute",
        email="admin.plan.execute@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(case_reference="CASE-PLAN-EXEC-001")
    requested_point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Buscar wallet en la evidencia.",
    )
    pericia_point = PericiaPoint.objects.create(
        name="Buscar wallet",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["wallet"]},
    )
    plan = AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=requested_point,
        pericia_point=pericia_point,
        analysis_targets=["/evidence/input/caso/dispositivo"],
    )

    response = client.get(
        reverse("admin:dfir_analysis_analysisplanproxy_change", args=[plan.pk])
    )

    body = response.content.decode()
    assert response.status_code == 200
    assert "Ejecutar este plan" in body
    assert "run-point" in body
    assert "Orden recomendado en Administracion de Analisis" in body
    assert "Puntos de pericia reutilizables" in body
    assert "Planes de analisis por caso" in body
    assert "Familias operativas" in body
    assert "Acciones ejecutables derivadas" in body
    assert "carpetas:" in body
    assert "tipos:" in body
    assert "criterio:" in body


@pytest.mark.django_db
def test_analysis_plan_changelist_shows_operator_states_and_row_actions(client):
    user = User.objects.create_superuser(
        username="admin_plan_list_actions",
        email="admin.plan.list.actions@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(case_reference="CASE-PLAN-LIST-001")
    requested_point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Buscar correos en la evidencia.",
    )
    pericia_point = PericiaPoint.objects.create(
        name="Buscar correos list",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["correo"]},
    )
    ready_plan = AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=requested_point,
        pericia_point=pericia_point,
        label="Correos listos",
        analysis_targets=["/evidence/input/caso/dispositivo"],
    )
    failed_plan = AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=requested_point,
        pericia_point=pericia_point,
        label="Correos fallidos",
        analysis_targets=["/evidence/input/caso/dispositivo-2"],
    )
    completed_obs_plan = AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=requested_point,
        pericia_point=pericia_point,
        label="Correos observados",
        analysis_targets=["/evidence/input/caso/dispositivo-3"],
    )
    PericiaExecution.objects.create(
        pericia_point=pericia_point,
        analysis_plan=failed_plan,
        status=PericiaExecution.Status.FAILED,
        engine_metadata={"error": "fallo de lectura"},
    )
    PericiaExecution.objects.create(
        pericia_point=pericia_point,
        analysis_plan=completed_obs_plan,
        status=PericiaExecution.Status.COMPLETED,
        analyzed_files_count=5,
        unsupported_files_count=1,
        failed_files_count=1,
    )

    response = client.get(
        reverse("admin:dfir_analysis_analysisplanproxy_changelist") + f"?q={case.case_reference}"
    )

    body = response.content.decode()
    assert response.status_code == 200
    assert "Listo" in body
    assert "Fallido" in body
    assert "Completado con observaciones" in body
    assert "Ejecutar este plan" in body
    assert "Reintentar" in body
    assert "Reejecutar" in body


@pytest.mark.django_db
def test_analysis_plan_change_view_shows_running_execution_progress(client):
    user = User.objects.create_superuser(
        username="admin_plan_progress",
        email="admin.plan.progress@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(case_reference="CASE-PLAN-PROGRESS-001")
    requested_point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Buscar wallet en la evidencia.",
    )
    pericia_point = PericiaPoint.objects.create(
        name="Buscar wallet progreso",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["wallet"]},
    )
    plan = AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=requested_point,
        pericia_point=pericia_point,
        analysis_targets=["/evidence/input/caso/dispositivo"],
        status=AnalysisPlan.Status.RUNNING,
    )
    PericiaExecution.objects.create(
        pericia_point=pericia_point,
        analysis_plan=plan,
        status=PericiaExecution.Status.RUNNING,
        engine_metadata={
            "progress": {
                "phase": "running",
                "processed_files": 3,
                "total_files": 10,
                "findings_count": 2,
            }
        },
    )

    response = client.get(
        reverse("admin:dfir_analysis_analysisplanproxy_change", args=[plan.pk])
    )

    body = response.content.decode()
    assert response.status_code == 200
    assert "En ejecucion" in body or "En ejecución" in body
    assert "3 de 10 archivo(s) procesados" in body
    assert "Ver ejecucion" in body


@pytest.mark.django_db
def test_analysis_plan_add_view_limits_requested_points_to_selected_case(client):
    user = User.objects.create_superuser(
        username="admin_plan_filter",
        email="admin.plan.filter@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(case_reference="CASE-PLAN-FILTER-001")
    other_case = PericiaCase.objects.create(case_reference="CASE-PLAN-FILTER-002")
    RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        short_label="Punto visible",
        literal_text="Punto visible del caso",
    )
    RequestedPoint.objects.create(
        pericia_case=other_case,
        order=1,
        short_label="Punto oculto",
        literal_text="Punto oculto de otro caso",
    )

    response = client.get(
        reverse("admin:dfir_analysis_analysisplanproxy_add") + f"?pericia_case={case.pk}"
    )

    body = response.content.decode()
    assert response.status_code == 200
    assert "Punto visible" in body
    assert "Punto oculto" not in body
    assert "requested_point_filter.js" in body
    assert "Caso pericial" in body
    assert "Punto de pericia" in body
    assert "Etiqueta del plan" in body
    assert "Ubicaciones objetivo del analisis" in body


@pytest.mark.django_db
def test_analysis_plan_requested_points_endpoint_filters_by_case(client):
    user = User.objects.create_superuser(
        username="admin_plan_points_api",
        email="admin.plan.points.api@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(case_reference="CASE-PLAN-FILTER-API-001")
    other_case = PericiaCase.objects.create(case_reference="CASE-PLAN-FILTER-API-002")
    visible = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        short_label="Visible API",
        literal_text="Visible API",
    )
    RequestedPoint.objects.create(
        pericia_case=other_case,
        order=1,
        short_label="Oculto API",
        literal_text="Oculto API",
    )

    response = client.get(
        reverse("admin:dfir_analysis_analysisplanproxy_requested_points"),
        {"case_id": case.pk},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["results"] == [{"id": visible.pk, "label": "Visible API"}]


@pytest.mark.django_db
def test_pericia_point_add_view_preloads_case_aware_name_suggestions(client):
    user = User.objects.create_superuser(
        username="admin_pericia_point_form",
        email="admin.pericia.point.form@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(case_reference="CASE-POINT-FILTER-001")

    response = client.get(
        reverse("admin:dfir_analysis_periciapointproxy_add") + f"?pericia_case={case.pk}"
    )

    body = response.content.decode()
    assert response.status_code == 200
    assert "name-suggestions/" in body
    assert "Caso pericial" in body


@pytest.mark.django_db
def test_pericia_point_name_suggestions_endpoint_filters_by_case(client):
    user = User.objects.create_superuser(
        username="admin_pericia_point_names_api",
        email="admin.pericia.point.names.api@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(case_reference="CASE-POINT-FILTER-API-001")
    other_case = PericiaCase.objects.create(case_reference="CASE-POINT-FILTER-API-002")
    RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        short_label="Correos Electrónicos",
        literal_text="Buscar correos",
    )
    RequestedPoint.objects.create(
        pericia_case=other_case,
        order=1,
        short_label="Usuarios",
        literal_text="Buscar usuarios",
    )

    response = client.get(
        reverse("admin:dfir_analysis_periciapointproxy_name_suggestions"),
        {"case_id": case.pk},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["results"] == [
        {"value": "Correos Electrónicos", "label": "Correos Electrónicos"}
    ]


@pytest.mark.django_db
def test_analysis_plan_run_view_executes_and_redirects_to_execution(
    client, settings, tmp_path
):
    user = User.objects.create_superuser(
        username="admin_plan_run",
        email="admin.plan.run@example.local",
        password="secret",
    )
    client.force_login(user)
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    device_dir = input_root / "CASE-PLAN-RUN-001" / "Dispositivo_1"
    device_dir.mkdir(parents=True)
    output_root.mkdir()
    (device_dir / "mensaje.txt").write_text("wallet encontrada", encoding="utf-8")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root
    settings.CELERY_TASK_ALWAYS_EAGER = True

    case = PericiaCase.objects.create(case_reference="CASE-PLAN-RUN-001")
    requested_point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Buscar wallet en archivos del dispositivo.",
    )
    pericia_point = PericiaPoint.objects.create(
        name="Buscar wallet plan",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["wallet"]},
    )
    evidence_item = EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.ACQUIRED,
        source_path=str(device_dir),
    )
    plan = AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=requested_point,
        pericia_point=pericia_point,
        analysis_targets=[str(device_dir)],
    )

    response = client.get(
        reverse("admin:dfir_analysis_analysisplanproxy_run_point", args=[plan.pk])
    )

    plan.refresh_from_db()
    execution = PericiaExecution.objects.get(analysis_plan=plan)
    device_result = DeviceAnalysisResult.objects.get(
        pericia_case=case,
        evidence_item=evidence_item,
    )
    assert response.status_code == 302
    assert f"/admin/dfir_analysis/periciaexecutionproxy/{execution.pk}/change/" in response["Location"]
    assert execution.findings_count == 1
    assert execution.device_analysis_result == device_result
    assert plan.status == AnalysisPlan.Status.COMPLETED


@pytest.mark.django_db
def test_evidence_item_directory_search_prefers_top_level_and_matches_nested(
    client, settings, tmp_path
):
    user = User.objects.create_superuser(
        username="admin_dir_search",
        email="admin.dir.search@example.local",
        password="secret",
    )
    client.force_login(user)
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    top_level = input_root / "dispositivo_a"
    nested = input_root / "caso_1" / "extracciones" / "smartphone"
    top_level.mkdir()
    nested.mkdir(parents=True)
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    base_url = reverse(
        "admin:dfir_evidence_evidenceitemproxy_mounted_directory_search"
    )
    response = client.get(base_url)

    assert response.status_code == 200
    payload = response.json()
    assert any(item["label"] == "dispositivo_a" for item in payload["results"])
    assert not any("smartphone" in item["label"] for item in payload["results"])

    search_response = client.get(base_url, {"q": "smart"})
    assert search_response.status_code == 200
    search_payload = search_response.json()
    assert any(
        item["label"] == "caso_1/extracciones/smartphone"
        for item in search_payload["results"]
    )


@pytest.mark.django_db
def test_case_admin_change_view_shows_guided_progress(client):
    user = User.objects.create_superuser(
        username="admin_guided_progress",
        email="admin.guided.progress@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(
        case_reference="CASE-GUIDED-PROGRESS-001",
        authority_name="Fiscalia",
    )
    RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Revisar informacion del equipo.",
    )

    response = client.get(
        reverse("admin:dfir_cases_periciacaseproxy_change", args=[case.pk])
    )

    body = response.content.decode()
    assert response.status_code == 200
    assert "Progreso guiado" in body
    assert "Etapa actual" in body
    assert "Abrir siguiente etapa" in body
    assert "Puntos solicitados" in body


@pytest.mark.django_db
def test_case_admin_change_view_shows_execute_ready_plans_button(client):
    user = User.objects.create_superuser(
        username="admin_case_run_ready",
        email="admin.case.run.ready@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(case_reference="CASE-RUN-READY-001")
    requested = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Buscar correos del dispositivo.",
    )
    point = PericiaPoint.objects.create(
        name="Correos ready case",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["correo"]},
    )
    AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=requested,
        pericia_point=point,
        analysis_targets=["/evidence/input/caso/dispositivo"],
    )

    response = client.get(
        reverse("admin:dfir_cases_periciacaseproxy_change", args=[case.pk])
    )

    body = response.content.decode()
    assert response.status_code == 200
    assert "Ejecutar planes listos" in body
    assert "Planes listos: 1" in body
    assert "Ver planes de analisis" in body
    assert "Ver ejecuciones" in body


@pytest.mark.django_db
def test_case_admin_change_view_shows_analysis_execution_activity(client):
    user = User.objects.create_superuser(
        username="admin_guided_exec_activity",
        email="admin.guided.exec.activity@example.local",
        password="secret",
    )
    client.force_login(user)
    case = PericiaCase.objects.create(case_reference="CASE-GUIDED-EXEC-001")
    requested = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Buscar correos",
    )
    pericia_point = PericiaPoint.objects.create(
        name="Buscar correo guiado",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["correo"]},
    )
    plan = AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=requested,
        pericia_point=pericia_point,
        analysis_targets=["/evidence/input/caso/dispositivo"],
        status=AnalysisPlan.Status.RUNNING,
    )
    PericiaExecution.objects.create(
        pericia_point=pericia_point,
        analysis_plan=plan,
        status=PericiaExecution.Status.PENDING,
        engine_metadata={
            "progress": {"phase": "queued", "processed_files": 0, "total_files": 5}
        },
    )

    response = client.get(
        reverse("admin:dfir_cases_periciacaseproxy_change", args=[case.pk])
    )

    body = response.content.decode()
    assert response.status_code == 200
    assert "Ejecuciones de analisis" in body
    assert "Pendientes: 1" in body
    assert "Completadas: 0" in body


@pytest.mark.django_db
def test_case_admin_run_ready_analysis_plans_executes_only_eligible_plans(
    client, settings, tmp_path
):
    user = User.objects.create_superuser(
        username="admin_case_batch_run",
        email="admin.case.batch.run@example.local",
        password="secret",
    )
    client.force_login(user)
    settings.CELERY_TASK_ALWAYS_EAGER = True
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    device_dir = input_root / "CASE-BATCH-RUN-001" / "Dispositivo_1"
    device_dir.mkdir(parents=True)
    output_root.mkdir()
    (device_dir / "mail.txt").write_text("correo relevante", encoding="utf-8")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    case = PericiaCase.objects.create(case_reference="CASE-BATCH-RUN-001")
    requested = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Buscar correos",
    )
    point = PericiaPoint.objects.create(
        name="Correos batch",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["correo"]},
    )
    EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.ACQUIRED,
        source_path=str(device_dir),
    )
    ready_plan = AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=requested,
        pericia_point=point,
        label="Plan listo",
        analysis_targets=[str(device_dir)],
    )
    completed_plan = AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=requested,
        pericia_point=point,
        label="Plan ya completo",
        analysis_targets=["/evidence/input/caso/otro"],
    )
    failed_plan = AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=requested,
        pericia_point=point,
        label="Plan fallido",
        analysis_targets=["/evidence/input/caso/fallido"],
    )
    PericiaExecution.objects.create(
        pericia_point=point,
        analysis_plan=completed_plan,
        status=PericiaExecution.Status.COMPLETED,
    )
    PericiaExecution.objects.create(
        pericia_point=point,
        analysis_plan=failed_plan,
        status=PericiaExecution.Status.FAILED,
        engine_metadata={"error": "fallo previo"},
    )

    response = client.get(
        reverse("admin:dfir_cases_periciacaseproxy_run_ready_analysis_plans", args=[case.pk]),
        follow=True,
    )

    body = response.content.decode()
    ready_plan.refresh_from_db()
    completed_plan.refresh_from_db()
    failed_plan.refresh_from_db()
    assert response.status_code == 200
    assert "Se lanzaron 1 plan(es)" in body
    assert "Omitidos: incompletos=0" in body
    assert "completados=1" in body
    assert "fallidos=1" in body
    assert PericiaExecution.objects.filter(analysis_plan=ready_plan).count() == 1
    assert ready_plan.status == AnalysisPlan.Status.COMPLETED
    assert PericiaExecution.objects.filter(analysis_plan=completed_plan).count() == 1
    assert PericiaExecution.objects.filter(analysis_plan=failed_plan).count() == 1


@pytest.mark.django_db
def test_case_admin_delete_model_removes_evidence_items_with_analysis_dependencies():
    case = PericiaCase.objects.create(case_reference="CASE-DELETE-001")
    requested = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Buscar correo",
    )
    pericia_point = PericiaPoint.objects.create(
        name="Eliminar caso - keyword",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["correo"]},
    )
    evidence = EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
    )
    AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=requested,
        pericia_point=pericia_point,
    )
    DeviceAnalysisResult.objects.create(
        pericia_case=case,
        evidence_item=evidence,
    )

    model_admin = admin.site._registry[PericiaCaseProxy]
    request = RequestFactory().post(
        "/admin/dfir_cases/periciacaseproxy/{}/delete/".format(case.pk)
    )

    model_admin.delete_model(request, PericiaCaseProxy.objects.get(pk=case.pk))

    assert not PericiaCase.objects.filter(pk=case.pk).exists()
    assert not EvidenceItem.objects.filter(pericia_case_id=case.pk).exists()


@pytest.mark.django_db
def test_case_admin_delete_queryset_removes_related_evidence_items():
    case1 = PericiaCase.objects.create(case_reference="CASE-DELETE-BULK-001")
    case2 = PericiaCase.objects.create(case_reference="CASE-DELETE-BULK-002")
    EvidenceItem.objects.create(
        pericia_case=case1,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
    )
    EvidenceItem.objects.create(
        pericia_case=case2,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
    )

    model_admin = admin.site._registry[PericiaCaseProxy]
    request = RequestFactory().post("/admin/dfir_cases/periciacaseproxy/")
    queryset = PericiaCaseProxy.objects.filter(pk__in=[case1.pk, case2.pk])

    model_admin.delete_queryset(request, queryset)

    assert not PericiaCase.objects.filter(
        pk__in=[case1.pk, case2.pk]
    ).exists()
    assert not EvidenceItem.objects.filter(
        pericia_case_id__in=[case1.pk, case2.pk]
    ).exists()


@pytest.mark.django_db
def test_evidence_item_admin_save_related_imports_all_files_from_source_directory(
    settings, tmp_path
):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    device_dir = input_root / "dispositivo1"
    (device_dir / "CuentaGmail").mkdir(parents=True)
    (device_dir / "ArchivosPDF").mkdir(parents=True)
    (device_dir / "CuentaGmail" / "mail1.txt").write_text("x", encoding="utf-8")
    (device_dir / "ArchivosPDF" / "doc1.pdf").write_bytes(b"pdf")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    case = PericiaCase.objects.create(case_reference="CASE-EVIDENCE-DIR-001")
    item = EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
    )

    form = EvidenceItemAdminForm(
        data={
            "pericia_case": str(case.pk),
            "parent_item": "",
            "evidence_file": "",
            "evidence_files": [],
            "label": "Dispositivo 1",
            "description": "",
            "role": EvidenceItem.Role.ORIGINAL_DEVICE,
            "acquisition_status": EvidenceItem.AcquisitionStatus.IDENTIFIED,
            "identifier": "",
            "serial_number": "",
            "source_path": str(device_dir),
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
        },
        instance=item,
    )
    assert form.is_valid(), form.errors

    model_admin = admin.site._registry[EvidenceItemProxy]
    request = RequestFactory().post("/admin/dfir_evidence/evidenceitemproxy/1/change/")
    obj = form.save(commit=False)
    model_admin.save_model(request, obj, form, change=True)
    model_admin.save_related(request, form, [], change=True)

    linked_paths = set(obj.evidence_files.values_list("source_path", flat=True))
    assert str(device_dir / "CuentaGmail" / "mail1.txt") in linked_paths
    assert str(device_dir / "ArchivosPDF" / "doc1.pdf") in linked_paths
