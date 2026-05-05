from __future__ import annotations

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from dfir_core.admin_forms import EvidenceItemAdminForm
from dfir_pericia.models import EvidenceItem, PericiaCase


@pytest.mark.django_db
def test_seed_device_types_creates_template_items_for_case_reference():
    case = PericiaCase.objects.create(case_reference="IPP-SEED-001")

    call_command("seed_device_types", "--case-reference", case.case_reference)

    expected_count = len(
        [key for key in EvidenceItemAdminForm.DEVICE_TEMPLATE_DATA.keys() if key]
    )
    case_items = EvidenceItem.objects.filter(pericia_case=case).order_by("id")
    assert case_items.count() == expected_count
    labels = set(case_items.values_list("label", flat=True))
    assert "Dispositivo 1" in labels
    assert f"Dispositivo {expected_count}" in labels


@pytest.mark.django_db
def test_seed_device_types_is_idempotent_for_existing_labels():
    case = PericiaCase.objects.create(case_reference="IPP-SEED-002")

    call_command("seed_device_types", "--case-id", str(case.pk))
    first_count = EvidenceItem.objects.filter(pericia_case=case).count()

    call_command("seed_device_types", "--case-id", str(case.pk))
    second_count = EvidenceItem.objects.filter(pericia_case=case).count()

    assert second_count == first_count


@pytest.mark.django_db
def test_seed_device_types_does_not_create_templates_when_case_has_items():
    case = PericiaCase.objects.create(case_reference="IPP-SEED-003")
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

    call_command("seed_device_types", "--case-id", str(case.pk))

    assert EvidenceItem.objects.filter(pericia_case=case).count() == 2


@pytest.mark.django_db
def test_seed_device_types_requires_case_selector():
    with pytest.raises(CommandError, match="Debes indicar --case-id o --case-reference"):
        call_command("seed_device_types")
