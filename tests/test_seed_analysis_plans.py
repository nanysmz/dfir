from __future__ import annotations

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from dfir_pericia.models import AnalysisPlan, EvidenceFile, EvidenceItem, PericiaCase, RequestedPoint


@pytest.mark.django_db
def test_seed_analysis_plans_creates_one_plan_per_requested_point():
    case = PericiaCase.objects.create(case_reference="IPP-SEED-PLAN-001")
    RequestedPoint.objects.create(pericia_case=case, order=1, literal_text="Buscar correo")
    RequestedPoint.objects.create(pericia_case=case, order=2, literal_text="Buscar p2p")

    call_command("seed_analysis_plans", "--case-reference", case.case_reference)

    plans = AnalysisPlan.objects.filter(pericia_case=case)
    assert plans.count() == 2
    assert plans.filter(label__icontains="Plan inicial").count() == 2


@pytest.mark.django_db
def test_seed_analysis_plans_is_idempotent_when_plans_exist():
    case = PericiaCase.objects.create(case_reference="IPP-SEED-PLAN-002")
    RequestedPoint.objects.create(pericia_case=case, order=1, literal_text="Actividad web")

    call_command("seed_analysis_plans", "--case-id", str(case.pk))
    first_count = AnalysisPlan.objects.filter(pericia_case=case).count()
    call_command("seed_analysis_plans", "--case-id", str(case.pk))
    second_count = AnalysisPlan.objects.filter(pericia_case=case).count()

    assert first_count == 1
    assert second_count == 1


@pytest.mark.django_db
def test_seed_analysis_plans_requires_case_selector():
    with pytest.raises(CommandError, match="Debes indicar --case-id o --case-reference"):
        call_command("seed_analysis_plans")


@pytest.mark.django_db
def test_seed_analysis_plans_prefills_targets_from_case_evidence(tmp_path):
    case = PericiaCase.objects.create(case_reference="IPP-SEED-PLAN-003")
    RequestedPoint.objects.create(pericia_case=case, order=1, literal_text="Buscar evidencia")

    first_path = str(tmp_path / "disk1.E01")
    second_path = str(tmp_path / "extraction" / "chat.db")
    shared_source_path = str(tmp_path / "mounted" / "device")

    first_file = EvidenceFile.objects.create(
        source_path=first_path,
        display_name="disk1.E01",
        file_kind=EvidenceFile.FileKind.UNKNOWN,
    )
    second_file = EvidenceFile.objects.create(
        source_path=second_path,
        display_name="chat.db",
        file_kind=EvidenceFile.FileKind.UNKNOWN,
    )

    item_a = EvidenceItem.objects.create(
        pericia_case=case,
        label="Equipo A",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
        source_path=shared_source_path,
        evidence_file=first_file,
    )
    item_b = EvidenceItem.objects.create(
        pericia_case=case,
        label="Equipo B",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
        source_path=shared_source_path,
    )
    item_b.evidence_files.add(second_file)
    item_a.evidence_files.add(first_file)

    call_command("seed_analysis_plans", "--case-reference", case.case_reference)

    plan = AnalysisPlan.objects.get(pericia_case=case)
    assert plan.analysis_targets == [
        shared_source_path,
        first_path,
    ]
    assert plan.scope_snapshot["execution_actions"]
    assert plan.scope_snapshot["analysis_playbook"]["actions"]
    assert plan.scope_snapshot["analysis_playbook"]["taxonomy_groups"]


@pytest.mark.django_db
def test_seed_analysis_plans_generates_structured_catalog_actions_for_p2p():
    case = PericiaCase.objects.create(case_reference="IPP-SEED-PLAN-004")
    RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Identificación de programas P2P instalados.",
    )

    call_command("seed_analysis_plans", "--case-reference", case.case_reference)

    plan = AnalysisPlan.objects.get(pericia_case=case)
    action = plan.scope_snapshot["analysis_playbook"]["actions"][0]
    assert action["path_scope"] == ["ActividadReciente"]
    assert action["file_kinds"] == ["html"]
    assert "torrent" in action["search_criteria"]["terms"]
