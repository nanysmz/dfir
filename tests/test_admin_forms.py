from __future__ import annotations

import pytest
from django.forms.models import inlineformset_factory

from dfir_core.admin_forms import (
    AnalysisPlanAdminForm,
    EvidenceFileAdminForm,
    EvidenceItemAdminForm,
    PericiaDocumentAdminForm,
    PericiaPointAdminForm,
    PreservedArtifactAdminForm,
    ReportSectionAdminForm,
    RequestedPointAdminForm,
    RequestedPointInlineFormSet,
)
from dfir_pericia.models import (
    AnalysisPlan,
    EvidenceFile,
    EvidenceItem,
    EvidenceItemSource,
    PericiaCase,
    PericiaPoint,
    ReportSection,
    RequestedPoint,
)


def test_pericia_document_admin_form_lists_mounted_input_files(settings, tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    (input_root / "documentos").mkdir()
    (input_root / "oficio.docx").write_text("x")
    (output_root / "resultado.txt").write_text("y")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    form = PericiaDocumentAdminForm()
    rendered_choices = str(form.fields["file_path"].choices)

    assert "Entrada montada / Carpetas" in rendered_choices
    assert "[dir] documentos" in rendered_choices
    assert "Entrada montada / Archivos" in rendered_choices
    assert "Salida montada / Archivos" in rendered_choices
    assert "oficio.docx" in rendered_choices
    assert "resultado.txt" in rendered_choices


def test_evidence_item_admin_form_includes_directories(settings, tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    (input_root / "extraccion").mkdir()
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    form = EvidenceItemAdminForm()
    widget = form.fields["source_path"].widget

    assert widget.__class__.__name__ == "TextInput"
    assert (
        widget.attrs["data-mounted-path-autocomplete-url"]
        == "/admin/dfir_evidence/evidencefileproxy/mounted-path-search/"
    )
    assert widget.attrs["data-mounted-path-browser"] == "true"
    assert (
        form.fields["source_path"].label
        == "fuente primaria de evidencia del dispositivo"
    )
    assert "archivo o carpeta principal" in form.fields["source_path"].help_text
    assert "primer nivel" in form.fields["source_path"].help_text
    assert "supporting_source_paths" in form.fields
    assert "evidence_file" in form.fields


def test_evidence_item_admin_form_exposes_device_templates():
    form = EvidenceItemAdminForm()
    assert "device_template" in form.fields
    assert form.fields["device_template"].label == "Tipo de dispositivo"
    template_values = {value for value, _label in form.fields["device_template"].choices}
    assert "hdd_internal_sata" in template_values
    assert "forensic_image" in template_values


@pytest.mark.django_db
def test_evidence_item_admin_form_applies_template_defaults(settings, tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    case = PericiaCase.objects.create(case_reference="IPP-EI-TPL-001")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    form = EvidenceItemAdminForm(
        data={
            "pericia_case": str(case.pk),
            "device_template": "forensic_image",
            "label": "",
            "description": "",
            "role": "",
            "acquisition_status": "",
            "identifier": "",
            "serial_number": "",
            "source_path": "",
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
            "evidence_files": [],
        }
    )

    assert form.is_valid(), form.errors
    assert form.cleaned_data["role"] == "forensic_image"
    assert form.cleaned_data["acquisition_status"] == "acquired"
    assert form.cleaned_data["label"] == "Dispositivo 1"
    assert form.cleaned_data["metadata"]["tipo_dispositivo_clave"] == "forensic_image"
    assert form.cleaned_data["metadata"]["plantilla_dispositivo"] == "forensic_image"


@pytest.mark.django_db
def test_evidence_item_admin_form_prefills_device_type_from_saved_metadata():
    case = PericiaCase.objects.create(case_reference="IPP-EI-TPL-PREFILL-001")
    item = EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 1",
        role=EvidenceItem.Role.FORENSIC_IMAGE,
        acquisition_status=EvidenceItem.AcquisitionStatus.ACQUIRED,
        metadata={"tipo_dispositivo_clave": "forensic_image"},
    )

    form = EvidenceItemAdminForm(instance=item)

    assert form.initial["device_template"] == "forensic_image"


@pytest.mark.django_db
def test_evidence_item_admin_form_prefills_device_type_from_legacy_metadata():
    case = PericiaCase.objects.create(case_reference="IPP-EI-TPL-PREFILL-LEGACY-001")
    item = EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 1",
        role=EvidenceItem.Role.FORENSIC_IMAGE,
        acquisition_status=EvidenceItem.AcquisitionStatus.ACQUIRED,
        metadata={"plantilla_dispositivo": "forensic_image"},
    )

    form = EvidenceItemAdminForm(instance=item)

    assert form.initial["device_template"] == "forensic_image"


@pytest.mark.django_db
def test_evidence_item_admin_form_assigns_next_device_label(settings, tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    case = PericiaCase.objects.create(case_reference="IPP-EI-TPL-002")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    from dfir_pericia.models import EvidenceItem

    EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 1",
        role="original_device",
        acquisition_status="identified",
    )

    form = EvidenceItemAdminForm(
        data={
            "pericia_case": str(case.pk),
            "device_template": "hdd_internal_sata",
            "label": "",
            "description": "",
            "role": "",
            "acquisition_status": "",
            "identifier": "",
            "serial_number": "",
            "source_path": "",
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
            "evidence_files": [],
        }
    )

    assert form.is_valid(), form.errors
    assert form.cleaned_data["label"] == "Dispositivo 2"


@pytest.mark.django_db
def test_evidence_item_admin_form_accepts_file_as_primary_source(settings, tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    single_file = input_root / "archivo.txt"
    single_file.write_text("hola", encoding="utf-8")
    case = PericiaCase.objects.create(case_reference="IPP-EI-TPL-003")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    form = EvidenceItemAdminForm(
        data={
            "pericia_case": str(case.pk),
            "device_template": "hdd_internal_sata",
            "label": "",
            "description": "",
            "role": "",
            "acquisition_status": "",
            "identifier": "",
            "serial_number": "",
            "source_path": str(single_file),
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
            "evidence_files": [],
        }
    )

    assert form.is_valid(), form.errors
    item = form.save()
    assert item.evidence_file is not None
    assert item.evidence_file.source_path == str(single_file.resolve())
    primary_source = item.primary_source_record()
    assert primary_source is not None
    assert primary_source.role == EvidenceItemSource.Role.PRIMARY
    assert primary_source.source_path == str(single_file.resolve())
    linked_paths = set(item.evidence_files.values_list("source_path", flat=True))
    assert linked_paths == {str(single_file.resolve())}


@pytest.mark.django_db
def test_evidence_item_admin_form_imports_files_from_device_directory(settings, tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    device_dir = input_root / "dispositivo_1"
    nested_dir = device_dir / "nested"
    nested_dir.mkdir(parents=True)
    (device_dir / "chat.txt").write_text("chat", encoding="utf-8")
    (nested_dir / "captura.jpg").write_bytes(b"img")

    case = PericiaCase.objects.create(case_reference="IPP-EI-TPL-004")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    form = EvidenceItemAdminForm(
        data={
            "pericia_case": str(case.pk),
            "device_template": "hdd_internal_sata",
            "label": "",
            "description": "",
            "role": "",
            "acquisition_status": "",
            "identifier": "",
            "serial_number": "",
            "source_path": str(device_dir),
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
            "evidence_files": [],
        }
    )

    assert form.is_valid(), form.errors
    item = form.save()
    linked_paths = set(item.evidence_files.values_list("source_path", flat=True))
    assert str(device_dir / "chat.txt") in linked_paths
    assert str(nested_dir / "captura.jpg") in linked_paths


@pytest.mark.django_db
def test_evidence_item_admin_form_accepts_directory_as_primary_source(
    settings, tmp_path
):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    device_dir = input_root / "88-888888-26" / "Dispositivo_3"
    device_dir.mkdir(parents=True)
    case = PericiaCase.objects.create(case_reference="IPP-EI-TPL-005")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    form = EvidenceItemAdminForm(
        data={
            "pericia_case": str(case.pk),
            "device_template": "hdd_internal_sata",
            "label": "",
            "description": "",
            "role": "",
            "acquisition_status": "",
            "parent_item": "",
            "identifier": "",
            "serial_number": "",
            "source_path": str(device_dir),
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
            "evidence_files": [],
        }
    )

    assert form.is_valid(), form.errors
    item = form.save()
    assert item.evidence_file is not None
    assert item.evidence_file.source_path == str(device_dir.resolve())
    assert item.evidence_file.metadata["is_directory"] is True


@pytest.mark.django_db
def test_evidence_item_admin_form_accepts_container_style_primary_source_path(
    settings, tmp_path
):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    device_dir = input_root / "dispositivo1" / "ActividadReciente"
    device_dir.mkdir(parents=True)
    case = PericiaCase.objects.create(case_reference="IPP-EI-TPL-ALIAS-001")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    form = EvidenceItemAdminForm(
        data={
            "pericia_case": str(case.pk),
            "device_template": "hdd_internal_sata",
            "label": "",
            "description": "",
            "role": "",
            "acquisition_status": "",
            "parent_item": "",
            "identifier": "",
            "serial_number": "",
            "source_path": "/evidence/input/dispositivo1/ActividadReciente",
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
            "evidence_files": [],
        }
    )

    assert form.is_valid(), form.errors
    item = form.save()
    assert item.source_path == str(device_dir.resolve())
    assert item.evidence_file is not None
    assert item.evidence_file.source_path == str(device_dir.resolve())


@pytest.mark.django_db
def test_evidence_item_admin_form_scopes_same_mounted_path_per_case(
    settings, tmp_path
):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    repeated_path = input_root / "dispositivo1" / "ActividadReciente"
    repeated_path.mkdir(parents=True)
    evidence_file = repeated_path / "report.html"
    evidence_file.write_text("contenido", encoding="utf-8")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    first_case = PericiaCase.objects.create(case_reference="IPP-EI-SCOPE-001")
    second_case = PericiaCase.objects.create(case_reference="IPP-EI-SCOPE-002")

    first_form = EvidenceItemAdminForm(
        data={
            "pericia_case": str(first_case.pk),
            "device_template": "hdd_internal_sata",
            "label": "",
            "description": "",
            "role": "",
            "acquisition_status": "",
            "parent_item": "",
            "identifier": "",
            "serial_number": "",
            "source_path": "/evidence/input/dispositivo1/ActividadReciente",
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
            "evidence_files": [],
        }
    )
    assert first_form.is_valid(), first_form.errors
    first_item = first_form.save()

    second_form = EvidenceItemAdminForm(
        data={
            "pericia_case": str(second_case.pk),
            "device_template": "hdd_internal_sata",
            "label": "",
            "description": "",
            "role": "",
            "acquisition_status": "",
            "parent_item": "",
            "identifier": "",
            "serial_number": "",
            "source_path": "/evidence/input/dispositivo1/ActividadReciente",
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
            "evidence_files": [],
        }
    )
    assert second_form.is_valid(), second_form.errors
    second_item = second_form.save()

    repeated_source_path = str(repeated_path.resolve())
    scoped_records = list(
        EvidenceFile.objects.filter(source_path=repeated_source_path).order_by(
            "identity_scope"
        )
    )

    assert len(scoped_records) == 2
    assert scoped_records[0].identity_scope != scoped_records[1].identity_scope
    assert first_item.evidence_file.identity_scope == EvidenceFile.case_identity_scope(
        first_case.pk
    )
    assert second_item.evidence_file.identity_scope == EvidenceFile.case_identity_scope(
        second_case.pk
    )

    repeated_derived_path = str(evidence_file.resolve())
    derived_records = list(
        EvidenceFile.objects.filter(source_path=repeated_derived_path).order_by(
            "identity_scope"
        )
    )
    assert len(derived_records) == 2
    assert derived_records[0].identity_scope != derived_records[1].identity_scope


@pytest.mark.django_db
def test_evidence_item_admin_form_preserves_existing_primary_path_on_edit(settings, tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    device_dir = input_root / "dispositivo1" / "ArchivosPDF"
    device_dir.mkdir(parents=True)
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root
    case = PericiaCase.objects.create(case_reference="IPP-EI-EDIT-SOURCE-001")
    item = EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
        source_path=str(device_dir.resolve()),
    )

    form = EvidenceItemAdminForm(instance=item)

    assert form.initial["source_path"] == str(device_dir.resolve())


@pytest.mark.django_db
def test_evidence_item_admin_form_saves_supporting_sources(settings, tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    primary_dir = input_root / "dispositivo1" / "principal"
    supporting_file = input_root / "dispositivo1" / "nota.txt"
    supporting_dir = input_root / "dispositivo1" / "extra"
    primary_dir.mkdir(parents=True)
    supporting_dir.mkdir(parents=True)
    supporting_file.write_text("ok", encoding="utf-8")
    case = PericiaCase.objects.create(case_reference="IPP-EI-SOURCES-001")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    form = EvidenceItemAdminForm(
        data={
            "pericia_case": str(case.pk),
            "device_template": "hdd_internal_sata",
            "label": "",
            "description": "",
            "role": "",
            "acquisition_status": "",
            "identifier": "",
            "serial_number": "",
            "source_path": str(primary_dir),
            "supporting_source_paths": f"{supporting_file}\n{supporting_dir}",
            "device_class": "unidad de almacenamiento",
            "device_type": "HDD",
            "device_interface": "SATA",
            "device_brand": "Seagate",
            "device_model": "Barracuda",
            "device_capacity_gb": "500",
            "technical_notes": "Sin observaciones",
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
            "evidence_files": [],
        }
    )

    assert form.is_valid(), form.errors
    item = form.save()

    sources = list(item.sources.order_by("position", "id"))
    assert len(sources) == 3
    assert sources[0].role == EvidenceItemSource.Role.PRIMARY
    assert sources[1].role == EvidenceItemSource.Role.SUPPORTING
    assert sources[2].role == EvidenceItemSource.Role.SUPPORTING


@pytest.mark.django_db
def test_evidence_item_admin_form_replaces_primary_source_and_resyncs_links(
    settings, tmp_path
):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    first_dir = input_root / "dispositivo1" / "primera"
    second_dir = input_root / "dispositivo1" / "segunda"
    first_dir.mkdir(parents=True)
    second_dir.mkdir(parents=True)
    (first_dir / "old.txt").write_text("old", encoding="utf-8")
    (second_dir / "new.txt").write_text("new", encoding="utf-8")
    case = PericiaCase.objects.create(case_reference="IPP-EI-SOURCES-002")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    item = EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
        source_path=str(first_dir.resolve()),
    )
    EvidenceItemSource.objects.create(
        evidence_item=item,
        role=EvidenceItemSource.Role.PRIMARY,
        source_kind=EvidenceItemSource.SourceKind.DIRECTORY,
        source_path=str(first_dir.resolve()),
        position=0,
    )

    initial_form = EvidenceItemAdminForm(
        data={
            "pericia_case": str(case.pk),
            "device_template": "",
            "label": "Dispositivo 1",
            "description": "",
            "role": EvidenceItem.Role.ORIGINAL_DEVICE,
            "acquisition_status": EvidenceItem.AcquisitionStatus.IDENTIFIED,
            "identifier": "",
            "serial_number": "",
            "source_path": str(first_dir.resolve()),
            "supporting_source_paths": "",
            "device_class": "",
            "device_type": "",
            "device_interface": "",
            "device_brand": "",
            "device_model": "",
            "device_capacity_gb": "",
            "technical_notes": "",
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
            "evidence_files": [],
        },
        instance=item,
    )
    assert initial_form.is_valid(), initial_form.errors
    initial_form.save()

    form = EvidenceItemAdminForm(
        data={
            "pericia_case": str(case.pk),
            "device_template": "",
            "label": "Dispositivo 1",
            "description": "",
            "role": EvidenceItem.Role.ORIGINAL_DEVICE,
            "acquisition_status": EvidenceItem.AcquisitionStatus.IDENTIFIED,
            "identifier": "",
            "serial_number": "",
            "source_path": str(second_dir.resolve()),
            "supporting_source_paths": "",
            "device_class": "",
            "device_type": "",
            "device_interface": "",
            "device_brand": "",
            "device_model": "",
            "device_capacity_gb": "",
            "technical_notes": "",
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
            "evidence_files": [],
        },
        instance=item,
    )

    assert form.is_valid(), form.errors
    updated = form.save()
    updated.refresh_from_db()

    assert updated.source_path == str(second_dir.resolve())
    assert updated.primary_source_record().source_path == str(second_dir.resolve())
    linked_paths = set(updated.evidence_files.values_list("source_path", flat=True))
    assert linked_paths == {str((second_dir / "new.txt").resolve())}


@pytest.mark.django_db
def test_evidence_item_admin_form_accepts_existing_alias_source_even_if_not_mounted(
    settings, tmp_path
):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    normalized_dir = input_root / "dispositivo1" / "ArchivosPDF"
    normalized_dir.mkdir(parents=True)
    case = PericiaCase.objects.create(case_reference="IPP-EI-ALIAS-LEGACY-001")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    item = EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 2",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
        source_path=str(normalized_dir.resolve()),
    )
    EvidenceItemSource.objects.create(
        evidence_item=item,
        role=EvidenceItemSource.Role.PRIMARY,
        source_kind=EvidenceItemSource.SourceKind.DIRECTORY,
        source_path=str(normalized_dir.resolve()),
        position=0,
    )

    normalized_dir.rename(input_root / "dispositivo1" / "ArchivosPDF_moved")

    form = EvidenceItemAdminForm(
        data={
            "pericia_case": str(case.pk),
            "device_template": "",
            "label": "Dispositivo 2",
            "description": "",
            "role": EvidenceItem.Role.ORIGINAL_DEVICE,
            "acquisition_status": EvidenceItem.AcquisitionStatus.IDENTIFIED,
            "identifier": "",
            "serial_number": "",
            "source_path": "/evidence/input/dispositivo1/ArchivosPDF",
            "supporting_source_paths": "",
            "device_class": "",
            "device_type": "",
            "device_interface": "",
            "device_brand": "",
            "device_model": "",
            "device_capacity_gb": "",
            "technical_notes": "",
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
            "evidence_files": [],
        },
        instance=item,
    )

    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_evidence_item_admin_form_parent_labels_use_mounted_root(settings, tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    case_root = input_root / "88-888888-26"
    case_root.mkdir()
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    case = PericiaCase.objects.create(case_reference="88-888888-26")
    parent = EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
        source_path=str((case_root / "Dispositivo_1").resolve()),
    )

    form = EvidenceItemAdminForm(initial={"pericia_case": case.pk})
    label = form.fields["parent_item"].label_from_instance(parent)

    assert label == "88-888888-26 / Dispositivo 1"


@pytest.mark.django_db
def test_evidence_item_admin_form_prefills_primary_source_from_existing_evidence_file(
    settings, tmp_path
):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    primary_file = input_root / "dispositivo.txt"
    primary_file.write_text("ok", encoding="utf-8")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    case = PericiaCase.objects.create(case_reference="IPP-EI-FALLBACK-001")
    evidence_file = EvidenceFile.objects.create(
        source_path=str(primary_file.resolve()),
        display_name="dispositivo.txt",
        file_kind=EvidenceFile.FileKind.TEXT,
    )
    item = EvidenceItem.objects.create(
        pericia_case=case,
        evidence_file=evidence_file,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
    )

    form = EvidenceItemAdminForm(instance=item)

    assert form.initial["source_path"] == str(primary_file.resolve())


@pytest.mark.django_db
def test_evidence_item_admin_form_skips_system_files_on_directory_import(
    settings, tmp_path
):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    device_dir = input_root / "dispositivo_2"
    meta_dir = device_dir / "__MACOSX"
    device_dir.mkdir(parents=True)
    meta_dir.mkdir(parents=True)

    (device_dir / "evidencia.txt").write_text("ok", encoding="utf-8")
    (device_dir / ".DS_Store").write_text("meta", encoding="utf-8")
    (device_dir / "Thumbs.db").write_text("meta", encoding="utf-8")
    (device_dir / "desktop.ini").write_text("meta", encoding="utf-8")
    (meta_dir / "archivo.txt").write_text("meta", encoding="utf-8")

    case = PericiaCase.objects.create(case_reference="IPP-EI-TPL-005")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    form = EvidenceItemAdminForm(
        data={
            "pericia_case": str(case.pk),
            "device_template": "hdd_internal_sata",
            "label": "",
            "description": "",
            "role": "",
            "acquisition_status": "",
            "identifier": "",
            "serial_number": "",
            "source_path": str(device_dir),
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
            "evidence_files": [],
        }
    )

    assert form.is_valid(), form.errors
    item = form.save()
    linked_paths = set(item.evidence_files.values_list("source_path", flat=True))

    assert str(device_dir / "evidencia.txt") in linked_paths
    assert str(device_dir / ".DS_Store") not in linked_paths
    assert str(device_dir / "Thumbs.db") not in linked_paths
    assert str(device_dir / "desktop.ini") not in linked_paths
    assert str(meta_dir / "archivo.txt") not in linked_paths


@pytest.mark.django_db
def test_evidence_item_admin_form_parent_item_is_filtered_by_case_and_labeled():
    case_a = PericiaCase.objects.create(case_reference="IPP-PARENT-001")
    case_b = PericiaCase.objects.create(case_reference="IPP-PARENT-002")
    item_a = EvidenceItem.objects.create(
        pericia_case=case_a,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
    )
    EvidenceItem.objects.create(
        pericia_case=case_b,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
    )

    form = EvidenceItemAdminForm(initial={"pericia_case": case_a.pk})
    parent_field = form.fields["parent_item"]

    assert list(parent_field.queryset.values_list("pericia_case_id", flat=True)) == [
        case_a.pk
    ]
    assert parent_field.label_from_instance(item_a) == "IPP-PARENT-001 / Dispositivo 1"


def test_preserved_artifact_form_uses_only_output_mount(settings, tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    (input_root / "entrada.txt").write_text("x")
    (output_root / "anexo.txt").write_text("y")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    form = PreservedArtifactAdminForm()
    rendered_choices = str(form.fields["storage_path"].choices)

    assert "Salida montada / Archivos" in rendered_choices
    assert "anexo.txt" in rendered_choices
    assert "Entrada montada / Archivos" not in rendered_choices


def test_analysis_plan_form_allows_multiple_files_and_directories(settings, tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    documents = input_root / "docs"
    documents.mkdir()
    report = documents / "report.txt"
    report.write_text("contenido", encoding="utf-8")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    case = PericiaCase(case_reference="IPP-FORM-001")
    point = RequestedPoint(
        pericia_case=case,
        order=1,
        literal_text="Buscar correo",
    )
    pericia_point = PericiaPoint(
        name="Buscar correo exacto",
        point_family=PericiaPoint.PointFamily.TEXT_EMAIL_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.EXACT,
        parameters={"value": "analyst@example.com"},
    )
    plan = AnalysisPlan(
        pericia_case=case,
        requested_point=point,
        pericia_point=pericia_point,
    )

    form = AnalysisPlanAdminForm(instance=plan)
    choices = str(form.fields["analysis_targets"].choices)

    assert "Entrada montada / Carpetas" in choices
    assert "Entrada montada / Archivos" in choices
    assert "docs" in choices
    assert "report.txt" in choices


@pytest.mark.django_db
def test_analysis_plan_form_uses_spanish_labels_and_prefills_targets(
    settings, tmp_path
):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    target_dir = input_root / "caso" / "Correos"
    target_file = input_root / "caso" / "usuarios.txt"
    target_dir.mkdir(parents=True)
    target_file.write_text("contenido", encoding="utf-8")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    case = PericiaCase.objects.create(case_reference="IPP-PLAN-LABEL-001")
    requested_point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Buscar correos",
    )
    pericia_point = PericiaPoint.objects.create(
        name="Correos Electronicos",
        point_family=PericiaPoint.PointFamily.TEXT_EMAIL_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.EXACT,
        parameters={"value": "correo@ejemplo.com"},
        enabled=True,
    )
    plan = AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=requested_point,
        pericia_point=pericia_point,
        analysis_targets=[str(target_dir), str(target_file)],
    )

    form = AnalysisPlanAdminForm(instance=plan)

    assert form.fields["pericia_case"].label == "Caso pericial"
    assert form.fields["pericia_point"].label == "Punto de pericia"
    assert form.fields["label"].label == "Etiqueta del plan"
    assert form.fields["strategy_notes"].label == "Notas de estrategia"
    assert form.fields["analysis_targets"].label == "Ubicaciones objetivo del analisis"
    assert list(form.fields["analysis_targets"].initial) == [
        str(target_dir),
        str(target_file),
    ]


@pytest.mark.django_db
def test_analysis_plan_form_saves_and_reopens_analysis_targets(settings, tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    primary_dir = input_root / "caso" / "Correos"
    secondary_dir = input_root / "caso" / "Usuarios"
    primary_dir.mkdir(parents=True)
    secondary_dir.mkdir(parents=True)
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    case = PericiaCase.objects.create(case_reference="IPP-PLAN-TARGETS-001")
    requested_point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Buscar correos",
    )
    pericia_point = PericiaPoint.objects.create(
        name="Correos Electronicos",
        point_family=PericiaPoint.PointFamily.TEXT_EMAIL_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.EXACT,
        parameters={"value": "correo@ejemplo.com"},
        enabled=True,
    )

    form = AnalysisPlanAdminForm(
        data={
            "pericia_case": str(case.pk),
            "requested_point": str(requested_point.pk),
            "pericia_point": str(pericia_point.pk),
            "label": "Plan correos",
            "strategy_notes": "",
            "analysis_targets": [str(primary_dir), str(secondary_dir)],
            "scope_snapshot": "{}",
            "status": "planned",
            "search_terms": "",
            "execution_actions": "",
        }
    )

    assert form.is_valid(), form.errors
    plan = form.save()
    assert plan.analysis_targets == [str(primary_dir), str(secondary_dir)]

    reopened = AnalysisPlanAdminForm(instance=plan)
    assert list(reopened.fields["analysis_targets"].initial) == [
        str(primary_dir),
        str(secondary_dir),
    ]

    edit_form = AnalysisPlanAdminForm(
        data={
            "pericia_case": str(case.pk),
            "requested_point": str(requested_point.pk),
            "pericia_point": str(pericia_point.pk),
            "label": "Plan correos",
            "strategy_notes": "",
            "analysis_targets": [str(secondary_dir)],
            "scope_snapshot": "{}",
            "status": "planned",
            "search_terms": "",
            "execution_actions": "",
        },
        instance=plan,
    )
    assert edit_form.is_valid(), edit_form.errors
    updated_plan = edit_form.save()
    assert updated_plan.analysis_targets == [str(secondary_dir)]


@pytest.mark.django_db
def test_analysis_plan_form_compacts_descendant_targets_from_case_sources(
    settings, tmp_path
):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    primary_dir = input_root / "caso" / "Correos"
    primary_dir.mkdir(parents=True)
    nested_file_a = primary_dir / "a.txt"
    nested_file_b = primary_dir / "nested" / "b.txt"
    nested_file_a.write_text("a", encoding="utf-8")
    nested_file_b.parent.mkdir(parents=True)
    nested_file_b.write_text("b", encoding="utf-8")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    case = PericiaCase.objects.create(case_reference="IPP-PLAN-TARGETS-002")
    requested_point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Buscar correos",
    )
    pericia_point = PericiaPoint.objects.create(
        name="Correos Electronicos compact",
        point_family=PericiaPoint.PointFamily.TEXT_EMAIL_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.EXACT,
        parameters={"value": "correo@ejemplo.com"},
        enabled=True,
    )
    evidence_file = EvidenceFile.objects.create(
        identity_scope=EvidenceFile.case_identity_scope(case.pk),
        source_path=str(primary_dir.resolve()),
        display_name="Correos",
        file_kind=EvidenceFile.FileKind.UNKNOWN,
        metadata={"is_directory": True},
    )
    EvidenceItem.objects.create(
        pericia_case=case,
        evidence_file=evidence_file,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
        source_path=str(primary_dir.resolve()),
    )
    plan = AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=requested_point,
        pericia_point=pericia_point,
        analysis_targets=[
            str(primary_dir.resolve()),
            str(nested_file_a.resolve()),
            str(nested_file_b.resolve()),
        ],
    )

    form = AnalysisPlanAdminForm(instance=plan)

    assert list(form.fields["analysis_targets"].initial) == [str(primary_dir.resolve())]


@pytest.mark.django_db
def test_analysis_plan_form_requires_search_terms_even_with_requested_point():
    case = PericiaCase.objects.create(case_reference="IPP-PLAN-FORM-001")
    requested_point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Buscar credenciales",
    )

    form = AnalysisPlanAdminForm(
        data={
            "pericia_case": str(case.pk),
            "requested_point": str(requested_point.pk),
            "pericia_point": "",
            "label": "",
            "strategy_notes": "",
            "analysis_targets": [],
            "scope_snapshot": "{}",
            "status": "planned",
            "search_terms": "",
        }
    )

    assert not form.is_valid()
    assert "search_terms" in form.errors


@pytest.mark.django_db
def test_analysis_plan_form_creates_pericia_point_from_search_terms():
    case = PericiaCase.objects.create(case_reference="IPP-PLAN-FORM-002")
    requested_point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Buscar correos y usuarios",
    )

    form = AnalysisPlanAdminForm(
        data={
            "pericia_case": str(case.pk),
            "requested_point": str(requested_point.pk),
            "pericia_point": "",
            "label": "Plan manual",
            "strategy_notes": "",
            "analysis_targets": [],
            "scope_snapshot": "{}",
            "status": "planned",
            "search_terms": "correo@ejemplo.com, usuario123",
        }
    )

    assert form.is_valid(), form.errors
    plan = form.save()

    assert plan.pericia_point is not None
    assert plan.pericia_point.point_family == PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH
    assert "correo@ejemplo.com" in plan.pericia_point.parameters.get("terms", [])
    assert plan.scope_snapshot["structured_actions"]


@pytest.mark.django_db
def test_analysis_plan_form_accepts_existing_pericia_point_without_search_terms():
    case = PericiaCase.objects.create(case_reference="IPP-PLAN-FORM-002B")
    requested_point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Buscar correos",
    )
    pericia_point = PericiaPoint.objects.create(
        name="Correos Electronicos",
        point_family=PericiaPoint.PointFamily.TEXT_EMAIL_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.EXACT,
        parameters={"value": "correo@ejemplo.com"},
        enabled=True,
    )

    form = AnalysisPlanAdminForm(
        data={
            "pericia_case": str(case.pk),
            "requested_point": str(requested_point.pk),
            "pericia_point": str(pericia_point.pk),
            "label": "Plan desde punto existente",
            "strategy_notes": "",
            "analysis_targets": [],
            "scope_snapshot": "{}",
            "status": "planned",
            "search_terms": "",
            "execution_actions": "",
        }
    )

    assert form.is_valid(), form.errors
    plan = form.save()

    assert plan.pericia_point_id == pericia_point.pk
    assert plan.scope_snapshot.get("search_terms") == []
    assert plan.scope_snapshot["analysis_playbook"]["primary_technique"]["id"] == pericia_point.pk
    assert plan.scope_snapshot["analysis_playbook"]["actions"]


@pytest.mark.django_db
def test_analysis_plan_form_accepts_execution_actions_without_explicit_search_terms():
    case = PericiaCase.objects.create(case_reference="IPP-PLAN-FORM-003")
    requested_point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Detallar usuarios de redes sociales",
    )

    form = AnalysisPlanAdminForm(
        data={
            "pericia_case": str(case.pk),
            "requested_point": str(requested_point.pk),
            "pericia_point": "",
            "label": "Plan redes",
            "strategy_notes": "",
            "analysis_targets": [],
            "scope_snapshot": "{}",
            "status": "planned",
            "search_terms": "",
            "execution_actions": (
                "Buscar correos electronicos dados\n"
                "Buscar nombres de usuarios dados"
            ),
        }
    )

    assert not form.is_valid()
    assert "search_terms" in form.errors


@pytest.mark.django_db
def test_analysis_plan_form_saves_search_terms_in_scope_snapshot():
    case = PericiaCase.objects.create(case_reference="IPP-PLAN-FORM-003B")
    requested_point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Detallar usuarios de redes sociales",
    )

    form = AnalysisPlanAdminForm(
        data={
            "pericia_case": str(case.pk),
            "requested_point": str(requested_point.pk),
            "pericia_point": "",
            "label": "Plan redes",
            "strategy_notes": "",
            "analysis_targets": [],
            "scope_snapshot": "{}",
            "status": "planned",
            "search_terms": "correo@ejemplo.com, usuario123",
            "execution_actions": (
                "Buscar correos electronicos dados\n"
                "Buscar nombres de usuarios dados"
            ),
        }
    )

    assert form.is_valid(), form.errors
    plan = form.save()

    assert plan.scope_snapshot.get("search_terms") == [
        "correo@ejemplo.com",
        "usuario123",
    ]
    assert plan.scope_snapshot.get("execution_actions") == [
        "Buscar correos electronicos dados",
        "Buscar nombres de usuarios dados",
    ]
    assert plan.scope_snapshot["analysis_playbook"]["requested_point_summary"] == str(
        requested_point
    )
    assert [group["code"] for group in plan.scope_snapshot["analysis_playbook"]["taxonomy_groups"]]
    assert plan.scope_snapshot["analysis_playbook"]["actions"][0]["targets"] == []


@pytest.mark.django_db
def test_analysis_plan_form_loads_execution_actions_initial_from_scope_snapshot():
    case = PericiaCase.objects.create(case_reference="IPP-PLAN-FORM-004")
    requested_point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Buscar datos",
    )
    pericia_point = PericiaPoint.objects.create(
        name="Punto preexistente",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["correo"]},
        enabled=True,
    )
    plan = AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=requested_point,
        pericia_point=pericia_point,
        scope_snapshot={"execution_actions": ["Buscar correos", "Buscar usuarios"]},
    )

    form = AnalysisPlanAdminForm(instance=plan)
    assert "Buscar correos" in str(form.fields["execution_actions"].initial)
    assert "Buscar usuarios" in str(form.fields["execution_actions"].initial)


@pytest.mark.django_db
def test_analysis_plan_form_accepts_structured_actions_json():
    case = PericiaCase.objects.create(case_reference="IPP-PLAN-STRUCT-001")
    requested_point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Identificación de programas P2P instalados.",
    )
    pericia_point = PericiaPoint.objects.create(
        name="Busqueda de palabras en texto/html",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["torrent", "p2p"]},
        enabled=True,
    )

    form = AnalysisPlanAdminForm(
        data={
            "pericia_case": str(case.pk),
            "requested_point": str(requested_point.pk),
            "pericia_point": str(pericia_point.pk),
            "label": "Plan P2P",
            "strategy_notes": "",
            "analysis_targets": [],
            "scope_snapshot": "{}",
            "status": "planned",
            "search_terms": "torrent, p2p",
            "execution_actions": "Buscar indicadores P2P",
            "structured_actions_json": '[{"label":"Buscar indicadores de software P2P en ActividadReciente","action_family":"keyword_search","path_scope":["ActividadReciente"],"file_kinds":["html"],"search_criteria":{"mode":"any","terms":["torrent","p2p"]}}]',
        }
    )

    assert form.is_valid(), form.errors
    plan = form.save()

    structured_action = plan.scope_snapshot["structured_actions"][0]
    assert structured_action["path_scope"] == ["ActividadReciente"]
    assert structured_action["file_kinds"] == ["html"]
    assert structured_action["search_criteria"]["terms"] == ["torrent", "p2p"]


@pytest.mark.django_db
def test_analysis_plan_form_derives_taxonomy_groups_from_requested_point():
    case = PericiaCase.objects.create(case_reference="IPP-PLAN-TAX-001")
    requested_point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Determinación de accesos y logs de cuentas (IP, fechas, horarios).",
    )
    pericia_point = PericiaPoint.objects.create(
        name="Buscar correos y accesos",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["correo", "ip"]},
        enabled=True,
    )

    form = AnalysisPlanAdminForm(
        data={
            "pericia_case": str(case.pk),
            "requested_point": str(requested_point.pk),
            "pericia_point": str(pericia_point.pk),
            "label": "Plan accesos",
            "strategy_notes": "",
            "analysis_targets": [],
            "scope_snapshot": "{}",
            "status": "planned",
            "search_terms": "",
            "execution_actions": "",
        }
    )

    assert form.is_valid(), form.errors
    plan = form.save()

    taxonomy_codes = [group["code"] for group in plan.scope_snapshot["analysis_playbook"]["taxonomy_groups"]]
    assert "activity_timeline" in taxonomy_codes
    assert "credentials_access" in taxonomy_codes


@pytest.mark.django_db
def test_analysis_plan_form_filters_requested_points_by_selected_case():
    case_a = PericiaCase.objects.create(case_reference="IPP-PLAN-FILTER-001")
    case_b = PericiaCase.objects.create(case_reference="IPP-PLAN-FILTER-002")
    point_a = RequestedPoint.objects.create(
        pericia_case=case_a,
        order=1,
        literal_text="Punto del caso A",
    )
    RequestedPoint.objects.create(
        pericia_case=case_b,
        order=1,
        literal_text="Punto del caso B",
    )

    form = AnalysisPlanAdminForm(initial={"pericia_case": case_a.pk})

    assert list(form.fields["requested_point"].queryset.values_list("pk", flat=True)) == [
        point_a.pk
    ]


@pytest.mark.django_db
def test_analysis_plan_form_filters_requested_points_for_existing_plan():
    case = PericiaCase.objects.create(case_reference="IPP-PLAN-FILTER-003")
    other_case = PericiaCase.objects.create(case_reference="IPP-PLAN-FILTER-004")
    point = RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        literal_text="Punto del caso",
    )
    RequestedPoint.objects.create(
        pericia_case=other_case,
        order=1,
        literal_text="Punto ajeno",
    )
    pericia_point = PericiaPoint.objects.create(
        name="Punto de plan",
        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
        matching_mode=PericiaPoint.MatchingMode.ANY,
        parameters={"terms": ["dato"]},
        enabled=True,
    )
    plan = AnalysisPlan.objects.create(
        pericia_case=case,
        requested_point=point,
        pericia_point=pericia_point,
    )

    form = AnalysisPlanAdminForm(instance=plan)

    assert list(form.fields["requested_point"].queryset.values_list("pk", flat=True)) == [
        point.pk
    ]


@pytest.mark.django_db
def test_evidence_file_form_accepts_file_from_mounted_root(settings, tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    candidate = input_root / "captura.txt"
    candidate.write_text("ok", encoding="utf-8")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    form = EvidenceFileAdminForm(
        data={
            "identity_scope": EvidenceFile.IDENTITY_SCOPE_GLOBAL,
            "source_path": str(candidate),
            "display_name": "captura.txt",
            "file_kind": "text",
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
        }
    )

    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_evidence_file_form_accepts_directory_from_mounted_root(settings, tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    candidate = input_root / "extraccion_dispositivo"
    candidate.mkdir()
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    form = EvidenceFileAdminForm(
        data={
            "identity_scope": EvidenceFile.IDENTITY_SCOPE_GLOBAL,
            "source_path": str(candidate),
            "display_name": "extraccion_dispositivo",
            "file_kind": "unknown",
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
        }
    )

    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_evidence_file_form_accepts_file_outside_mounted_roots(settings, tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("x", encoding="utf-8")
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    form = EvidenceFileAdminForm(
        data={
            "identity_scope": EvidenceFile.IDENTITY_SCOPE_GLOBAL,
            "source_path": str(outside),
            "display_name": "outside.txt",
            "file_kind": "text",
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
        }
    )

    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_evidence_file_form_accepts_directory_outside_mounted_roots(settings, tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    outside = tmp_path / "outside_dir"
    outside.mkdir()
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    form = EvidenceFileAdminForm(
        data={
            "identity_scope": EvidenceFile.IDENTITY_SCOPE_GLOBAL,
            "source_path": str(outside),
            "display_name": "outside_dir",
            "file_kind": "unknown",
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
        }
    )

    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_evidence_file_form_accepts_container_style_mounted_path(settings, tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    candidate = input_root / "dispositivo1" / "ActividadReciente"
    candidate.mkdir(parents=True)
    settings.EVIDENCE_INPUT_PATH = input_root
    settings.EVIDENCE_OUTPUT_PATH = output_root

    form = EvidenceFileAdminForm(
        data={
            "identity_scope": EvidenceFile.IDENTITY_SCOPE_GLOBAL,
            "source_path": "/evidence/input/dispositivo1/ActividadReciente",
            "display_name": "ActividadReciente",
            "file_kind": "unknown",
            "sha256": "",
            "size_bytes": "",
            "metadata": "{}",
        }
    )

    assert form.is_valid(), form.errors
    assert form.cleaned_data["source_path"] == str(candidate.resolve())


@pytest.mark.django_db
def test_requested_point_form_hides_source_document_field():
    case = PericiaCase.objects.create(case_reference="IPP-RP-FORM-001")

    form = RequestedPointAdminForm(
        data={
            "pericia_case": str(case.pk),
            "order": "1",
            "short_label": "Punto 1",
            "literal_text": "Texto del punto",
            "notes": "",
            "metadata": "{}",
        }
    )

    assert "source_document" not in form.fields
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_requested_point_form_suggests_next_order_for_case():
    case = PericiaCase.objects.create(case_reference="IPP-RP-FORM-ORDER-001")
    RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        short_label="Punto 1",
        literal_text="Texto 1",
    )
    RequestedPoint.objects.create(
        pericia_case=case,
        order=2,
        short_label="Punto 2",
        literal_text="Texto 2",
    )

    form = RequestedPointAdminForm(initial={"pericia_case": case.pk})

    assert form.initial["order"] == 3
    assert "Cada punto solicitado pertenece solo a esta pericia." in form.fields["pericia_case"].help_text


@pytest.mark.django_db
def test_report_section_admin_form_prefills_suggested_content_for_offered_elements():
    case = PericiaCase.objects.create(case_reference="IPP-REPORT-FORM-001")
    EvidenceItem.objects.create(
        pericia_case=case,
        label="Dispositivo 1",
        role=EvidenceItem.Role.ORIGINAL_DEVICE,
        acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
        metadata={
            "device_class": "unidad de almacenamiento",
            "device_type": "SSD",
            "device_interface": "SATA",
            "device_brand": "Kingston",
            "device_model": "SA400",
            "device_capacity_gb": "240",
        },
    )
    section = case.report_sections.get(
        section_type=ReportSection.SectionType.OFFERED_ELEMENTS
    )

    form = ReportSectionAdminForm(instance=section)

    assert "elementos de evidencia del caso" in form.fields["content"].help_text
    assert "unidad de almacenamiento" in form.initial["content"]


@pytest.mark.django_db
def test_requested_point_form_reuses_same_order_in_different_case():
    case_a = PericiaCase.objects.create(case_reference="IPP-RP-FORM-CASE-A")
    case_b = PericiaCase.objects.create(case_reference="IPP-RP-FORM-CASE-B")
    RequestedPoint.objects.create(
        pericia_case=case_a,
        order=1,
        short_label="Punto A",
        literal_text="Texto A",
    )

    form = RequestedPointAdminForm(
        data={
            "pericia_case": str(case_b.pk),
            "order": "1",
            "short_label": "Punto B",
            "literal_text": "Texto B",
            "notes": "",
            "metadata": "{}",
        }
    )

    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_requested_point_form_uses_friendly_duplicate_order_message():
    case = PericiaCase.objects.create(case_reference="IPP-RP-FORM-DUP-001")
    RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        short_label="Punto 1",
        literal_text="Texto 1",
    )

    form = RequestedPointAdminForm(
        data={
            "pericia_case": str(case.pk),
            "order": "1",
            "short_label": "Punto duplicado",
            "literal_text": "Texto duplicado",
            "notes": "",
            "metadata": "{}",
        }
    )

    assert not form.is_valid()
    assert "Ya existe un punto solicitado con ese orden dentro de esta pericia." in form.errors["order"]


@pytest.mark.django_db
def test_requested_point_inline_formset_suggests_case_local_next_order():
    case = PericiaCase.objects.create(case_reference="IPP-RP-INLINE-001")
    RequestedPoint.objects.create(
        pericia_case=case,
        order=1,
        short_label="Punto 1",
        literal_text="Texto 1",
    )
    RequestedPoint.objects.create(
        pericia_case=case,
        order=2,
        short_label="Punto 2",
        literal_text="Texto 2",
    )

    FormSet = inlineformset_factory(
        PericiaCase,
        RequestedPoint,
        form=RequestedPointAdminForm,
        formset=RequestedPointInlineFormSet,
        fields=("order", "short_label", "literal_text", "notes", "metadata"),
        extra=1,
    )
    formset = FormSet(instance=case)

    assert formset.extra_forms[0].initial["order"] == 3
    assert formset.empty_form.initial["order"] == 4


@pytest.mark.django_db
def test_requested_point_inline_formset_flags_duplicate_orders_in_same_submission():
    case = PericiaCase.objects.create(case_reference="IPP-RP-INLINE-DUP-001")
    FormSet = inlineformset_factory(
        PericiaCase,
        RequestedPoint,
        form=RequestedPointAdminForm,
        formset=RequestedPointInlineFormSet,
        fields=("order", "short_label", "literal_text", "notes", "metadata"),
        extra=2,
    )
    formset = FormSet(
        data={
            "requested_points-TOTAL_FORMS": "2",
            "requested_points-INITIAL_FORMS": "0",
            "requested_points-MIN_NUM_FORMS": "0",
            "requested_points-MAX_NUM_FORMS": "1000",
            "requested_points-0-order": "1",
            "requested_points-0-short_label": "Punto 1",
            "requested_points-0-literal_text": "Texto 1",
            "requested_points-0-notes": "",
            "requested_points-0-metadata": "{}",
            "requested_points-1-order": "1",
            "requested_points-1-short_label": "Punto 2",
            "requested_points-1-literal_text": "Texto 2",
            "requested_points-1-notes": "",
            "requested_points-1-metadata": "{}",
        },
        instance=case,
        prefix="requested_points",
    )

    assert not formset.is_valid()
    assert "Ya existe un punto solicitado con ese orden dentro de esta pericia." in formset.forms[0].errors["order"]
    assert "Ya existe un punto solicitado con ese orden dentro de esta pericia." in formset.forms[1].errors["order"]


# ---------------------------------------------------------------------------
# PericiaPointAdminForm
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_pericia_point_form_saves_keywords_as_parameters_terms(settings, tmp_path):
    settings.EVIDENCE_INPUT_PATH = str(tmp_path / "input")
    settings.EVIDENCE_OUTPUT_PATH = str(tmp_path / "output")
    (tmp_path / "input").mkdir()
    (tmp_path / "output").mkdir()

    form = PericiaPointAdminForm(
        data={
            "name": "Buscar usuario",
            "slug": "",
            "point_family": "text_keyword_search",
            "matching_mode": "any",
            "enabled": "1",
            "search_keywords": "usuario123, juan perez",
            "pattern_preset": "",
            "scope_path": "",
        }
    )
    assert form.is_valid(), form.errors
    instance = form.save(commit=True)
    assert instance.parameters.get("terms") == ["usuario123", "juan perez"]


@pytest.mark.django_db
def test_pericia_point_form_accepts_case_context_from_initial(settings, tmp_path):
    settings.EVIDENCE_INPUT_PATH = str(tmp_path / "input")
    settings.EVIDENCE_OUTPUT_PATH = str(tmp_path / "output")
    (tmp_path / "input").mkdir()
    (tmp_path / "output").mkdir()
    case = PericiaCase.objects.create(case_reference="IPP-PP-FORM-001")

    form = PericiaPointAdminForm(initial={"pericia_case": case.pk})

    assert "pericia_case" in form.fields
    assert form.fields["pericia_case"].initial == case.pk
    assert (
        form.fields["name"].widget.attrs["data-pericia-point-name-suggestions-url"]
        == "/admin/dfir_analysis/periciapointproxy/name-suggestions/"
    )


@pytest.mark.django_db
def test_pericia_point_form_saves_pattern_preset_as_parameters_pattern(settings, tmp_path):
    settings.EVIDENCE_INPUT_PATH = str(tmp_path / "input")
    settings.EVIDENCE_OUTPUT_PATH = str(tmp_path / "output")
    (tmp_path / "input").mkdir()
    (tmp_path / "output").mkdir()

    form = PericiaPointAdminForm(
        data={
            "name": "Buscar correos",
            "slug": "",
            "point_family": "text_keyword_search",
            "matching_mode": "regex",
            "enabled": "1",
            "search_keywords": "",
            "pattern_preset": "email",
            "scope_path": "",
        }
    )
    assert form.is_valid(), form.errors
    instance = form.save(commit=True)
    assert "pattern" in instance.parameters
    assert instance.parameters.get("pattern_label") == "email"


@pytest.mark.django_db
def test_pericia_point_form_resolves_case_context_from_request(settings, tmp_path):
    from django.test import RequestFactory

    settings.EVIDENCE_INPUT_PATH = str(tmp_path / "input")
    settings.EVIDENCE_OUTPUT_PATH = str(tmp_path / "output")
    (tmp_path / "input").mkdir()
    (tmp_path / "output").mkdir()
    case = PericiaCase.objects.create(case_reference="IPP-PP-FORM-002")
    request = RequestFactory().get(
        "/admin/dfir_analysis/periciapointproxy/add/",
        {"pericia_case": case.pk},
    )

    form = PericiaPointAdminForm(request=request)

    assert form.fields["pericia_case"].initial == case.pk


@pytest.mark.django_db
def test_pericia_point_form_requires_keyword_or_pattern(settings, tmp_path):
    settings.EVIDENCE_INPUT_PATH = str(tmp_path / "input")
    settings.EVIDENCE_OUTPUT_PATH = str(tmp_path / "output")
    (tmp_path / "input").mkdir()
    (tmp_path / "output").mkdir()

    form = PericiaPointAdminForm(
        data={
            "name": "Sin datos",
            "slug": "",
            "point_family": "text_keyword_search",
            "matching_mode": "any",
            "enabled": "1",
            "search_keywords": "",
            "pattern_preset": "",
            "scope_path": "",
        }
    )
    assert not form.is_valid()
    assert "search_keywords" in form.errors


@pytest.mark.django_db
def test_pericia_point_form_saves_scope_path(settings, tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    input_root.mkdir()
    output_root.mkdir()
    target_dir = input_root / "caso2024"
    target_dir.mkdir()
    settings.EVIDENCE_INPUT_PATH = str(input_root)
    settings.EVIDENCE_OUTPUT_PATH = str(output_root)

    form = PericiaPointAdminForm(
        data={
            "name": "Buscar con alcance",
            "slug": "",
            "point_family": "text_keyword_search",
            "matching_mode": "any",
            "enabled": "1",
            "search_keywords": "evidencia",
            "pattern_preset": "",
            "scope_path": str(target_dir),
        }
    )
    assert form.is_valid(), form.errors
    instance = form.save(commit=True)
    assert instance.scope.get("path") == str(target_dir)


@pytest.mark.django_db
def test_pericia_point_form_keeps_manual_name_without_case_context(settings, tmp_path):
    settings.EVIDENCE_INPUT_PATH = str(tmp_path / "input")
    settings.EVIDENCE_OUTPUT_PATH = str(tmp_path / "output")
    (tmp_path / "input").mkdir()
    (tmp_path / "output").mkdir()

    form = PericiaPointAdminForm(
        data={
            "pericia_case": "",
            "name": "Nombre manual global",
            "slug": "",
            "point_family": "text_keyword_search",
            "matching_mode": "any",
            "enabled": "1",
            "search_keywords": "usuario123",
            "pattern_preset": "",
            "scope_path": "",
        }
    )
    assert form.is_valid(), form.errors
    instance = form.save(commit=True)
    assert instance.name == "Nombre manual global"
