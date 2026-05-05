from __future__ import annotations

from collections.abc import Iterable
import json
import os
from pathlib import Path
import re
from uuid import uuid4

from django import forms
from django.conf import settings
from django.forms.models import BaseInlineFormSet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from dfir_pericia.analysis_playbooks import (
    build_structured_actions,
    build_suggested_playbook_actions,
    normalize_structured_actions,
)
from dfir_pericia.models import (
    AnalysisPlan,
    EvidenceFile,
    EvidenceItem,
    EvidenceItemSource,
    PericiaCase,
    PericiaDocument,
    PericiaPoint,
    ReportSection,
    RequestedPoint,
    PreservedArtifact,
)


def candidate_evidence_paths(value: str | Path) -> list[Path]:
    raw_value = str(value or "").strip()
    if not raw_value:
        return []

    raw_path = Path(raw_value).expanduser()
    candidate_paths: list[Path] = []
    mounted_aliases = (
        (Path("/evidence/input"), Path(settings.EVIDENCE_INPUT_PATH).expanduser()),
        (Path("/evidence/output"), Path(settings.EVIDENCE_OUTPUT_PATH).expanduser()),
    )

    for mounted_root, configured_root in mounted_aliases:
        try:
            relative = raw_path.relative_to(mounted_root)
        except ValueError:
            continue
        candidate_paths.append(configured_root / relative)
    candidate_paths.append(raw_path)
    return candidate_paths


def resolve_existing_evidence_path(value: str | Path) -> Path | None:
    candidate_paths = candidate_evidence_paths(value)
    if not candidate_paths:
        return None

    seen: set[str] = set()
    for candidate in candidate_paths:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        try:
            resolved = candidate.resolve()
        except (OSError, RuntimeError):
            continue
        if resolved.exists() and (resolved.is_file() or resolved.is_dir()):
            return resolved

    return None


def infer_source_kind(path: Path) -> str:
    return (
        EvidenceItemSource.SourceKind.FILE
        if path.is_file()
        else EvidenceItemSource.SourceKind.DIRECTORY
    )


def parse_source_path_lines(raw_value: str) -> list[str]:
    values: list[str] = []
    for line in str(raw_value or "").splitlines():
        normalized = str(line).strip()
        if normalized:
            values.append(normalized)
    return list(dict.fromkeys(values))


class PericiaCaseAdminForm(forms.ModelForm):
    initial_device_count = forms.IntegerField(
        label=_("cantidad inicial de dispositivos"),
        min_value=1,
        required=False,
        initial=1,
        help_text=_(
            "Define cuantos dispositivos (elementos de evidencia) se crean al alta del caso."
        ),
    )

    class Meta:
        model = PericiaCase
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        is_add = not bool(getattr(self.instance, "pk", None))
        field = self.fields["initial_device_count"]
        field.required = is_add
        if not is_add:
            field.disabled = True
            field.help_text = _(
                "Solo se utiliza en el alta inicial del caso; luego se gestiona desde Elementos de evidencia."
            )


def _iter_mount_entries(
    root: Path,
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    if not root.exists():
        return [], []

    max_entries = int(getattr(settings, "DFIR_MOUNT_CHOICES_LIMIT", 2000))
    directories: list[tuple[str, str]] = []
    files: list[tuple[str, str]] = []
    collected = 0

    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(name for name in dirnames if not name.startswith("."))
        filenames = sorted(name for name in filenames if not name.startswith("."))
        current = Path(current_root)

        for dirname in dirnames:
            path = current / dirname
            label = f"[dir] {path.relative_to(root)}"
            directories.append((str(path), label))
            collected += 1
            if collected >= max_entries:
                return directories, files

        for filename in filenames:
            path = current / filename
            label = f"{path.relative_to(root)}"
            files.append((str(path), label))
            collected += 1
            if collected >= max_entries:
                return directories, files

    return directories, files


def _append_group(
    groups: list[tuple[str, list[tuple[str, str]]]],
    label: str,
    entries: Iterable[tuple[str, str]],
) -> None:
    normalized = list(entries)
    if normalized:
        groups.append((label, normalized))


def mounted_path_choices(
    *,
    include_input: bool = True,
    include_output: bool = True,
    include_directories: bool = False,
) -> list[tuple[str, list[tuple[str, str]]]]:
    choices: list[tuple[str, list[tuple[str, str]]]] = []

    if include_input:
        input_dirs, input_files = _iter_mount_entries(
            Path(settings.EVIDENCE_INPUT_PATH)
        )
        if include_directories:
            _append_group(choices, _("Entrada montada / Carpetas"), input_dirs)
        _append_group(choices, _("Entrada montada / Archivos"), input_files)

    if include_output:
        output_dirs, output_files = _iter_mount_entries(
            Path(settings.EVIDENCE_OUTPUT_PATH)
        )
        if include_directories:
            _append_group(choices, _("Salida montada / Carpetas"), output_dirs)
        _append_group(choices, _("Salida montada / Archivos"), output_files)

    return choices


class MountedPathChoiceMixin:
    mounted_path_field_name: str
    include_input_paths = True
    include_output_paths = True
    include_directory_paths = False
    include_file_paths = True

    def _build_choices(self) -> list[tuple[str, object]]:
        grouped_choices = mounted_path_choices(
            include_input=self.include_input_paths,
            include_output=self.include_output_paths,
            include_directories=self.include_directory_paths,
        )
        choices: list[tuple[str, object]] = [
            ("", _("Seleccionar desde volumen montado"))
        ]
        for group_label, grouped in grouped_choices:
            if self.include_file_paths:
                choices.append((group_label, grouped))
                continue

            only_directories = [
                (value, label)
                for value, label in grouped
                if str(label).strip().startswith("[dir]")
            ]
            if only_directories:
                choices.append((group_label, only_directories))
        return choices

    def _ensure_current_value(
        self, choices: list[tuple[str, object]], value: str
    ) -> None:
        if not value:
            return
        flat_values: set[str] = set()
        for _group_label, grouped in choices[1:]:
            for choice_value, _choice_label in grouped:
                flat_values.add(choice_value)
        if value not in flat_values:
            choices.append((_("Valor actual"), [(value, value)]))

    def _configure_mounted_path_field(self) -> None:
        field_name = self.mounted_path_field_name
        current_value = self.initial.get(field_name) or getattr(
            getattr(self, "instance", None), field_name, ""
        )
        choices = self._build_choices()
        self._ensure_current_value(choices, current_value)
        self.fields[field_name] = forms.ChoiceField(
            label=self.fields[field_name].label,
            required=self.fields[field_name].required,
            choices=choices,
            widget=forms.Select(
                attrs={
                    "class": "w-full min-w-0",
                    "data-placeholder": _(
                        "Seleccionar carpeta o archivo desde volumen montado"
                    ),
                }
            ),
        )
        self.fields[field_name].help_text = _(
            "Selecciona una ruta disponible dentro de los volumenes montados."
        )


class PericiaDocumentAdminForm(MountedPathChoiceMixin, forms.ModelForm):
    mounted_path_field_name = "file_path"
    include_directory_paths = True

    class Meta:
        model = PericiaDocument
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._configure_mounted_path_field()


class ReportSectionAdminForm(forms.ModelForm):
    class Meta:
        model = ReportSection
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["section_type"].help_text = _(
            "La estructura del informe sigue una plantilla estándar y este tipo identifica la sección dentro de ese orden."
        )
        self.fields["title"].help_text = _(
            "Se inicializa desde la plantilla del informe, pero puedes ajustarlo si el caso lo requiere."
        )

        instance = getattr(self, "instance", None)
        if instance is None or not getattr(instance, "pk", None):
            self.fields["content"].help_text = _(
                "Contenido editable de la sección para el caso actual."
            )
            return

        suggested_content = instance.suggested_content()
        section_type = str(instance.section_type or "")
        if not self.data and not str(instance.content or "").strip() and suggested_content:
            self.initial["content"] = suggested_content

        if section_type == ReportSection.SectionType.OFFERED_ELEMENTS:
            self.fields["content"].help_text = _(
                "Si la sección está vacía, el formulario puede sugerir contenido a partir de los elementos de evidencia del caso. Luego puedes editarlo libremente."
            )
        elif section_type == ReportSection.SectionType.OBTAINED_INFORMATION:
            self.fields["content"].help_text = _(
                "Si la sección está vacía, el formulario puede sugerir contenido a partir de los resultados por dispositivo. Luego puedes editarlo libremente."
            )
        else:
            self.fields["content"].help_text = _(
                "Contenido editable de la sección para el caso actual."
            )


class EvidenceFileAdminForm(MountedPathChoiceMixin, forms.ModelForm):
    class Meta:
        model = EvidenceFile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["source_path"].widget = forms.TextInput(
            attrs={
                "class": "w-full min-w-0",
                "autocomplete": "off",
                "data-mounted-path-autocomplete": "true",
            }
        )
        self.fields["source_path"].help_text = _(
            "Ruta del archivo o carpeta de evidencia. Puedes especificar rutas dentro de volumenes montados (con autocompletado) o cualquier otra ruta valida en el sistema de archivos."
        )

    def clean_source_path(self) -> str:
        value = str(self.cleaned_data.get("source_path") or "").strip()
        if not value:
            raise forms.ValidationError("La ruta de origen es obligatoria.")

        path = resolve_existing_evidence_path(value)
        if path is None:
            raise forms.ValidationError(
                "La ruta seleccionada no existe o no es un archivo o carpeta valido."
            )

        return str(path)


class EvidenceItemAdminForm(MountedPathChoiceMixin, forms.ModelForm):
    DEVICE_TYPE_METADATA_KEY = "tipo_dispositivo_clave"
    LEGACY_DEVICE_TYPE_METADATA_KEY = "plantilla_dispositivo"
    mounted_path_field_name = "source_path"
    include_directory_paths = True
    include_output_paths = False
    include_file_paths = False
    device_template = forms.ChoiceField(
        label=_("Tipo de dispositivo"),
        required=False,
        choices=(),
        help_text=_(
            "Opcional. Precompleta metadata tecnica y sugiere rol/estado de adquisicion segun el tipo seleccionado."
        ),
    )
    supporting_source_paths = forms.CharField(
        label=_("fuentes asociadas de evidencia del dispositivo"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "w-full min-w-0",
                "rows": 4,
                "placeholder": _(
                    "Una ruta por linea para archivos o carpetas asociados"
                ),
            }
        ),
        help_text=_(
            "Opcional. Agrega archivos o carpetas complementarios del mismo dispositivo, una ruta por linea."
        ),
    )
    device_class = forms.CharField(label=_("Clase de dispositivo"), required=False)
    device_type = forms.CharField(label=_("Tipo tecnico"), required=False)
    device_interface = forms.CharField(label=_("Interfaz / conexion"), required=False)
    device_brand = forms.CharField(label=_("Marca"), required=False)
    device_model = forms.CharField(label=_("Modelo"), required=False)
    device_capacity_gb = forms.CharField(label=_("Capacidad (GB)"), required=False)
    technical_notes = forms.CharField(
        label=_("Observaciones tecnicas"),
        required=False,
        widget=forms.Textarea(attrs={"class": "w-full min-w-0", "rows": 3}),
    )
    DEVICE_TEMPLATE_DATA = {
        "": {
            "label": _("Sin plantilla"),
            "role": None,
            "acquisition_status": None,
            "metadata": {},
        },
        "hdd_internal_sata": {
            "label": _("HDD Interno (SATA/SAS)"),
            "role": EvidenceItem.Role.ORIGINAL_DEVICE,
            "acquisition_status": EvidenceItem.AcquisitionStatus.IDENTIFIED,
            "metadata": {
                "device_class": "unidad de almacenamiento",
                "device_type": "HDD",
                "device_interface": "SATA/SAS",
                "device_brand": "",
                "device_model": "",
                "device_capacity_gb": "",
                "tipo_dispositivo": "HDD",
                "medio": "fisico",
                "interfaz": "SATA/SAS",
                "forma_factor": "3.5\" o 2.5\"",
                "observaciones_tecnicas": "Una (01) unidad de almacenamiento, disco electromecánico, tipo HDD, conexión SATA/SAS. Relevar marca, modelo, número de serie y capacidad GB.",
                "technical_notes": "Una (01) unidad de almacenamiento, disco electromecanico, tipo HDD, conexion SATA/SAS. Relevar marca, modelo, numero de serie y capacidad GB.",
            },
        },
        "hdd_external_usb": {
            "label": _("HDD Externo (USB)"),
            "role": EvidenceItem.Role.ORIGINAL_DEVICE,
            "acquisition_status": EvidenceItem.AcquisitionStatus.IDENTIFIED,
            "metadata": {
                "device_class": "unidad de almacenamiento externa",
                "device_type": "HDD externo",
                "device_interface": "USB",
                "device_brand": "",
                "device_model": "",
                "device_capacity_gb": "",
                "tipo_dispositivo": "HDD externo",
                "medio": "fisico",
                "interfaz": "USB",
                "observaciones_tecnicas": "Una (01) unidad de almacenamiento externa, conexión USB, disco electromecánico, tipo HDD. Carcasa marca/modelo con número de serie. Revisar si carcasa con controlador integrado o HDD desmontable para adquisición directa.",
                "technical_notes": "Una (01) unidad de almacenamiento externa, conexion USB, disco electromecanico, tipo HDD. Carcasa marca/modelo con numero de serie. Revisar si carcasa con controlador integrado o HDD desmontable para adquisicion directa.",
            },
        },
        "ssd_m2_nvme": {
            "label": _("SSD M.2 NVMe"),
            "role": EvidenceItem.Role.ORIGINAL_DEVICE,
            "acquisition_status": EvidenceItem.AcquisitionStatus.IDENTIFIED,
            "metadata": {
                "device_class": "unidad de almacenamiento",
                "device_type": "SSD",
                "device_interface": "PCIe/NVMe",
                "tipo_dispositivo": "SSD",
                "medio": "fisico",
                "interfaz": "PCIe/NVMe",
                "factor_forma": "M.2",
            },
        },
        "usb_flash": {
            "label": _("Pendrive USB"),
            "role": EvidenceItem.Role.ORIGINAL_DEVICE,
            "acquisition_status": EvidenceItem.AcquisitionStatus.RECEIVED,
            "metadata": {
                "device_class": "unidad de almacenamiento removible",
                "device_type": "Pendrive",
                "device_interface": "USB",
                "tipo_dispositivo": "Pendrive",
                "medio": "fisico",
                "interfaz": "USB",
            },
        },
        "memory_card": {
            "label": _("Tarjeta de memoria"),
            "role": EvidenceItem.Role.ORIGINAL_DEVICE,
            "acquisition_status": EvidenceItem.AcquisitionStatus.RECEIVED,
            "metadata": {
                "device_class": "tarjeta de memoria",
                "device_type": "Tarjeta memoria",
                "device_interface": "microSD/SD/CF/CFast",
                "tipo_dispositivo": "Tarjeta memoria",
                "medio": "fisico",
                "interfaz": "microSD/SD/CF/CFast",
            },
        },
        "notebook": {
            "label": _("Notebook/Laptop"),
            "role": EvidenceItem.Role.ORIGINAL_DEVICE,
            "acquisition_status": EvidenceItem.AcquisitionStatus.IDENTIFIED,
            "metadata": {
                "device_class": "computadora portatil",
                "device_type": "Notebook",
                "tipo_dispositivo": "Notebook",
                "medio": "fisico",
                "observaciones_tecnicas": "Relevar estado fisico, cargador y puertos",
                "technical_notes": "Relevar estado fisico, cargador y puertos",
            },
        },
        "smartphone": {
            "label": _("Smartphone"),
            "role": EvidenceItem.Role.ORIGINAL_DEVICE,
            "acquisition_status": EvidenceItem.AcquisitionStatus.IDENTIFIED,
            "metadata": {
                "device_class": "telefono movil",
                "device_type": "Smartphone",
                "device_interface": "USB/forense movil",
                "tipo_dispositivo": "Smartphone",
                "medio": "fisico",
                "interfaz": "USB/forense movil",
                "observaciones_tecnicas": "Relevar SIM/eSIM y bloqueo de pantalla",
                "technical_notes": "Relevar SIM/eSIM y bloqueo de pantalla",
            },
        },
        "forensic_image": {
            "label": _("Imagen forense (E01/dd/img)"),
            "role": EvidenceItem.Role.FORENSIC_IMAGE,
            "acquisition_status": EvidenceItem.AcquisitionStatus.ACQUIRED,
            "metadata": {
                "device_class": "imagen forense",
                "device_type": "Imagen forense",
                "tipo_dispositivo": "Imagen forense",
                "medio": "logico",
                "formato": "E01/dd/img",
                "observaciones_tecnicas": "Validar hash de adquisicion",
                "technical_notes": "Validar hash de adquisicion",
            },
        },
        "virtual_machine": {
            "label": _("Maquina virtual"),
            "role": EvidenceItem.Role.LOGICAL_EXTRACTION,
            "acquisition_status": EvidenceItem.AcquisitionStatus.ACQUIRED,
            "metadata": {
                "device_class": "maquina virtual",
                "device_type": "Maquina virtual",
                "tipo_dispositivo": "Maquina virtual",
                "medio": "logico",
                "plataforma": "VMware/VirtualBox/Hyper-V",
            },
        },
        "cloud_account": {
            "label": _("Cuenta cloud"),
            "role": EvidenceItem.Role.LOGICAL_EXTRACTION,
            "acquisition_status": EvidenceItem.AcquisitionStatus.PARTIAL,
            "metadata": {
                "device_class": "cuenta remota",
                "device_type": "Cloud",
                "tipo_dispositivo": "Cloud",
                "medio": "remoto",
                "servicio": "Drive/OneDrive/Dropbox/S3",
                "observaciones_tecnicas": "Extraccion sujeta a autorizacion",
                "technical_notes": "Extraccion sujeta a autorizacion",
            },
        },
    }

    class Meta:
        model = EvidenceItem
        fields = "__all__"

    class Media:
        js = ("dfir_evidence/mounted_path_autocomplete.js",)

    @staticmethod
    def next_device_label_for_case(pericia_case: PericiaCase | None) -> str:
        if pericia_case is None:
            return "Dispositivo 1"

        pattern = re.compile(r"^Dispositivo\s+(\d+)$", re.IGNORECASE)
        labels = EvidenceItem.objects.filter(pericia_case=pericia_case).values_list(
            "label", flat=True
        )

        max_device_number = 0
        for label in labels:
            match = pattern.match(str(label or "").strip())
            if match:
                max_device_number = max(max_device_number, int(match.group(1)))

        if max_device_number > 0:
            return f"Dispositivo {max_device_number + 1}"

        return f"Dispositivo {EvidenceItem.objects.filter(pericia_case=pericia_case).count() + 1}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["device_template"].choices = [
            (key, config["label"])
            for key, config in self.DEVICE_TEMPLATE_DATA.items()
        ]
        stored_device_type = self._stored_device_type_key()
        if stored_device_type:
            self.initial["device_template"] = stored_device_type
        structured_metadata = self._structured_device_metadata()
        for field_name, value in structured_metadata.items():
            if value:
                self.initial[field_name] = value
        self.fields["label"].required = False
        self.fields["role"].required = False
        self.fields["acquisition_status"].required = False
        instance_primary_source_path = ""
        if getattr(getattr(self, "instance", None), "pk", None):
            primary_source_record = self.instance.primary_source_record()
            if primary_source_record is not None:
                instance_primary_source_path = str(primary_source_record.source_path or "")
        current_source_path = str(
            self.initial.get("source_path")
            or getattr(getattr(self, "instance", None), "source_path", "")
            or instance_primary_source_path
            or getattr(getattr(getattr(self, "instance", None), "evidence_file", None), "source_path", "")
            or ""
        ).strip()
        self.initial["source_path"] = current_source_path
        self.fields["source_path"].widget = forms.TextInput(
            attrs={
                "class": "w-full min-w-0",
                "autocomplete": "off",
                "data-mounted-path-autocomplete": "true",
                "data-mounted-path-browser": "true",
                "data-mounted-path-autocomplete-url": reverse(
                    "admin:dfir_evidence_evidencefileproxy_mounted_path_search"
                ),
                "placeholder": _(
                    "Buscar archivo o carpeta primaria de evidencia"
                ),
            }
        )
        self.fields["source_path"].label = _(
            "fuente primaria de evidencia del dispositivo"
        )
        self.fields["source_path"].help_text = _(
            "Selecciona un archivo o carpeta principal dentro del volumen montado. Primero se muestran las entradas del primer nivel y puedes navegar dentro de carpetas si lo necesitas. Al guardar, el sistema resuelve automaticamente la referencia primaria y los archivos de evidencia derivados."
        )
        self.initial["supporting_source_paths"] = self._supporting_source_paths_initial()

        selected_case_id = self._selected_case_id()
        parent_field = self.fields.get("parent_item")
        if parent_field is not None:
            parent_queryset = EvidenceItem.objects.all().select_related("pericia_case")
            if selected_case_id is not None:
                parent_queryset = parent_queryset.filter(pericia_case_id=selected_case_id)
            if self.instance and self.instance.pk:
                parent_queryset = parent_queryset.exclude(pk=self.instance.pk)
            parent_field.queryset = parent_queryset
            parent_field.label_from_instance = self._parent_item_label

    def _stored_device_type_key(self) -> str:
        if self.data:
            return str(self.data.get("device_template") or "").strip()

        initial_value = str(self.initial.get("device_template") or "").strip()
        if initial_value:
            return initial_value

        metadata = getattr(getattr(self, "instance", None), "metadata", None)
        if isinstance(metadata, dict):
            return str(
                metadata.get(self.DEVICE_TYPE_METADATA_KEY)
                or metadata.get(self.LEGACY_DEVICE_TYPE_METADATA_KEY)
                or ""
            ).strip()

        return ""

    def _instance_metadata(self) -> dict[str, object]:
        metadata = getattr(getattr(self, "instance", None), "metadata", None)
        if isinstance(metadata, dict):
            return metadata
        return {}

    def _structured_device_metadata(self) -> dict[str, str]:
        metadata = self._instance_metadata()
        return {
            "device_class": str(metadata.get("device_class") or "").strip(),
            "device_type": str(
                metadata.get("device_type") or metadata.get("tipo_dispositivo") or ""
            ).strip(),
            "device_interface": str(
                metadata.get("device_interface") or metadata.get("interfaz") or ""
            ).strip(),
            "device_brand": str(metadata.get("device_brand") or "").strip(),
            "device_model": str(metadata.get("device_model") or "").strip(),
            "device_capacity_gb": str(
                metadata.get("device_capacity_gb")
                or metadata.get("capacity_gb")
                or ""
            ).strip(),
            "technical_notes": str(
                metadata.get("technical_notes")
                or metadata.get("observaciones_tecnicas")
                or ""
            ).strip(),
        }

    def _supporting_source_paths_initial(self) -> str:
        if self.data:
            return str(self.data.get("supporting_source_paths") or "")
        if getattr(getattr(self, "instance", None), "pk", None):
            values = [
                source.source_path
                for source in self.instance.supporting_source_records()
                if str(source.source_path).strip()
            ]
            return "\n".join(values)
        return str(self.initial.get("supporting_source_paths") or "")

    def _current_known_source_paths(self) -> set[str]:
        if getattr(getattr(self, "instance", None), "pk", None):
            return set(self.instance.known_source_paths())
        return set()

    def _resolve_or_keep_current_source(
        self,
        raw_value: str,
        *,
        field_name: str,
        known_paths: set[str],
    ) -> Path | str | None:
        source = resolve_existing_evidence_path(raw_value)
        if source is not None:
            return source
        normalized_candidates = [
            str(candidate).strip()
            for candidate in candidate_evidence_paths(raw_value)
            if str(candidate).strip()
        ]
        for normalized in normalized_candidates + [str(raw_value or "").strip()]:
            if normalized and normalized in known_paths:
                return normalized
        self.add_error(
            field_name,
            "Debes seleccionar un archivo o carpeta primaria valida.",
        )
        return None

    def _parent_item_label(self, obj: EvidenceItem) -> str:
        return f"{self._mounted_root_label(obj)} / {obj.label}"

    def _mounted_root_label(self, obj: EvidenceItem) -> str:
        source_path = str(getattr(obj, "source_path", "") or "").strip()
        if not source_path:
            linked_source = getattr(getattr(obj, "evidence_file", None), "source_path", "")
            source_path = str(linked_source or "").strip()
        if not source_path:
            return str(obj.pericia_case.case_reference)

        source = resolve_existing_evidence_path(source_path)
        candidate_sources = [source] if source is not None else candidate_evidence_paths(source_path)
        try:
            input_root = Path(settings.EVIDENCE_INPUT_PATH).expanduser().resolve()
        except (OSError, RuntimeError):
            input_root = None
        if input_root is not None:
            for candidate_source in candidate_sources:
                if candidate_source is None:
                    continue
                try:
                    relative = Path(candidate_source).expanduser().relative_to(input_root)
                    if relative.parts:
                        return relative.parts[0]
                except (OSError, RuntimeError, ValueError):
                    continue
        if source is not None:
            try:
                input_root = Path(settings.EVIDENCE_INPUT_PATH).expanduser().resolve()
                relative = source.relative_to(input_root)
                if relative.parts:
                    return relative.parts[0]
            except (OSError, RuntimeError, ValueError):
                pass

        return Path(source_path).name or str(obj.pericia_case.case_reference)

    def _selected_case_id(self) -> int | None:
        if self.instance and self.instance.pk and self.instance.pericia_case_id:
            return int(self.instance.pericia_case_id)

        raw_value = self.data.get("pericia_case") if self.data else None
        if not raw_value:
            raw_value = self.initial.get("pericia_case")
        if raw_value is None:
            return None
        try:
            return int(raw_value)
        except (TypeError, ValueError):
            return None

    def clean(self):
        cleaned_data = super().clean()
        template_key = str(cleaned_data.get("device_template") or "")
        template = self.DEVICE_TEMPLATE_DATA.get(template_key)
        metadata = cleaned_data.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}
        known_paths = self._current_known_source_paths()

        if template:
            template_metadata = dict(template.get("metadata") or {})
            template_metadata[self.DEVICE_TYPE_METADATA_KEY] = template_key
            template_metadata[self.LEGACY_DEVICE_TYPE_METADATA_KEY] = template_key
            template_metadata.update(metadata)
            cleaned_data["metadata"] = template_metadata

            pericia_case = cleaned_data.get("pericia_case")
            if not cleaned_data.get("label"):
                cleaned_data["label"] = self.next_device_label_for_case(pericia_case)

            if not cleaned_data.get("role") and template.get("role"):
                cleaned_data["role"] = template["role"]

            if (
                not cleaned_data.get("acquisition_status")
                and template.get("acquisition_status")
            ):
                cleaned_data["acquisition_status"] = template["acquisition_status"]

        if not cleaned_data.get("label"):
            self.add_error("label", "La etiqueta es obligatoria.")
        if not cleaned_data.get("role"):
            self.add_error("role", "El rol es obligatorio.")
        if not cleaned_data.get("acquisition_status"):
            self.add_error(
                "acquisition_status", "El estado de adquisicion es obligatorio."
            )

        source_path = str(cleaned_data.get("source_path") or "").strip()
        if source_path:
            source = self._resolve_or_keep_current_source(
                source_path,
                field_name="source_path",
                known_paths=known_paths,
            )
            if isinstance(source, Path):
                cleaned_data["source_path"] = str(source)
            elif isinstance(source, str):
                cleaned_data["source_path"] = source
        else:
            current_instance_path = str(
                getattr(getattr(self, "instance", None), "source_path", "")
                or getattr(getattr(getattr(self, "instance", None), "evidence_file", None), "source_path", "")
                or ""
            ).strip()
            if current_instance_path:
                cleaned_data["source_path"] = current_instance_path

        supporting_source_values = parse_source_path_lines(
            cleaned_data.get("supporting_source_paths") or ""
        )
        normalized_supporting_values: list[str] = []
        for raw_supporting_source in supporting_source_values:
            supporting_source = self._resolve_or_keep_current_source(
                raw_supporting_source,
                field_name="supporting_source_paths",
                known_paths=known_paths,
            )
            if isinstance(supporting_source, Path):
                normalized_supporting_values.append(str(supporting_source))
            elif isinstance(supporting_source, str):
                normalized_supporting_values.append(supporting_source)
        cleaned_data["supporting_source_paths"] = list(
            dict.fromkeys(normalized_supporting_values)
        )

        metadata = cleaned_data.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}
        metadata.update(
            {
                "device_class": str(
                    cleaned_data.get("device_class")
                    or metadata.get("device_class")
                    or ""
                ).strip(),
                "device_type": str(
                    cleaned_data.get("device_type")
                    or metadata.get("device_type")
                    or metadata.get("tipo_dispositivo")
                    or ""
                ).strip(),
                "device_interface": str(
                    cleaned_data.get("device_interface")
                    or metadata.get("device_interface")
                    or metadata.get("interfaz")
                    or ""
                ).strip(),
                "device_brand": str(
                    cleaned_data.get("device_brand")
                    or metadata.get("device_brand")
                    or ""
                ).strip(),
                "device_model": str(
                    cleaned_data.get("device_model")
                    or metadata.get("device_model")
                    or ""
                ).strip(),
                "device_capacity_gb": str(
                    cleaned_data.get("device_capacity_gb")
                    or metadata.get("device_capacity_gb")
                    or metadata.get("capacity_gb")
                    or ""
                ).strip(),
                "technical_notes": str(
                    cleaned_data.get("technical_notes")
                    or metadata.get("technical_notes")
                    or metadata.get("observaciones_tecnicas")
                    or ""
                ).strip(),
            }
        )
        if metadata.get("device_type"):
            metadata["tipo_dispositivo"] = metadata["device_type"]
        if metadata.get("device_interface"):
            metadata["interfaz"] = metadata["device_interface"]
        if metadata.get("device_capacity_gb"):
            metadata["capacity_gb"] = metadata["device_capacity_gb"]
        if metadata.get("technical_notes"):
            metadata["observaciones_tecnicas"] = metadata["technical_notes"]
        cleaned_data["metadata"] = metadata
        cleaned_data["evidence_file"] = None

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            self.sync_evidence_sources(instance)
            self.sync_evidence_files_from_source_path(instance)
        return instance

    def sync_evidence_sources(self, instance: EvidenceItem) -> None:
        supporting_paths = list(self.cleaned_data.get("supporting_source_paths") or [])
        desired_sources: list[tuple[str, str, int]] = []
        primary_path = str(getattr(instance, "source_path", "") or "").strip()
        if primary_path:
            desired_sources.append((primary_path, EvidenceItemSource.Role.PRIMARY, 0))
        for index, path in enumerate(supporting_paths, start=1):
            if path == primary_path:
                continue
            desired_sources.append((path, EvidenceItemSource.Role.SUPPORTING, index))

        existing_by_path = {
            source.source_path: source for source in instance.sources.all()
        }
        existing_primary = instance.sources.filter(
            role=EvidenceItemSource.Role.PRIMARY
        ).first()
        normalized_desired_paths: set[str] = set()

        for path, role, position in desired_sources:
            resolved = resolve_existing_evidence_path(path)
            normalized_path = str(resolved) if resolved is not None else path
            normalized_desired_paths.add(normalized_path)
            source_kind = (
                infer_source_kind(resolved)
                if isinstance(resolved, Path)
                else EvidenceItemSource.SourceKind.DIRECTORY
            )
            source_record = existing_by_path.get(path) or existing_by_path.get(normalized_path)
            if source_record is None and role == EvidenceItemSource.Role.PRIMARY:
                source_record = existing_primary
            if source_record is None:
                source_record = EvidenceItemSource(
                    evidence_item=instance,
                    source_path=normalized_path,
                )
            source_record.role = role
            source_record.position = position
            source_record.source_kind = source_kind
            source_record.source_path = normalized_path
            source_record.save()

        instance.sources.exclude(source_path__in=normalized_desired_paths).delete()
        primary_source = instance.primary_source_record()
        if primary_source is not None and instance.source_path != primary_source.source_path:
            instance.source_path = primary_source.source_path
            instance.save(update_fields=["source_path"])

    def sync_evidence_files_from_source_path(self, instance: EvidenceItem) -> None:
        self._sync_from_primary_source(instance)

    def _sync_from_primary_source(self, instance: EvidenceItem) -> None:
        primary_source_record = instance.primary_source_record()
        source_path = str(
            getattr(primary_source_record, "source_path", "")
            or getattr(instance, "source_path", "")
            or ""
        ).strip()
        if not source_path:
            return

        source = resolve_existing_evidence_path(source_path)
        if source is None:
            return

        identity_scope = EvidenceFile.case_identity_scope(instance.pericia_case_id)
        primary_evidence = self._get_or_create_evidence_file(
            source,
            identity_scope=identity_scope,
        )
        if instance.evidence_file_id != primary_evidence.pk:
            instance.evidence_file = primary_evidence
            instance.save(update_fields=["evidence_file"])

        linked_ids: list[int] = []
        if source.is_file():
            linked_ids.append(primary_evidence.pk)
        else:
            for file_path in sorted(path for path in source.rglob("*") if path.is_file()):
                if self._should_skip_import_file(file_path):
                    continue
                evidence_file, _created = EvidenceFile.objects.update_or_create(
                    identity_scope=identity_scope,
                    source_path=str(file_path),
                    defaults={
                        "display_name": file_path.name,
                        "file_kind": self._infer_file_kind(file_path),
                        "size_bytes": file_path.stat().st_size,
                        "metadata": {"is_directory": False},
                    },
                )
                linked_ids.append(evidence_file.pk)

        instance.evidence_files.set(linked_ids)

    @staticmethod
    def _get_or_create_evidence_file(
        path: Path,
        *,
        identity_scope: str = EvidenceFile.IDENTITY_SCOPE_GLOBAL,
    ) -> EvidenceFile:
        defaults = {
            "display_name": path.name,
            "file_kind": (
                EvidenceItemAdminForm._infer_file_kind(path)
                if path.is_file()
                else EvidenceFile.FileKind.UNKNOWN
            ),
            "size_bytes": path.stat().st_size if path.is_file() else None,
            "metadata": {"is_directory": path.is_dir()},
        }
        evidence_file, _created = EvidenceFile.objects.update_or_create(
            identity_scope=identity_scope,
            source_path=str(path),
            defaults=defaults,
        )
        return evidence_file

    @staticmethod
    def _infer_file_kind(path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix in {".txt", ".log", ".csv", ".json"}:
            return EvidenceFile.FileKind.TEXT
        if suffix in {".html", ".htm"}:
            return EvidenceFile.FileKind.HTML
        if suffix == ".pdf":
            return EvidenceFile.FileKind.PDF
        if suffix == ".doc":
            return EvidenceFile.FileKind.DOC
        if suffix == ".docx":
            return EvidenceFile.FileKind.DOCX
        if suffix in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}:
            return EvidenceFile.FileKind.IMAGE
        return EvidenceFile.FileKind.UNKNOWN

    @staticmethod
    def _should_skip_import_file(path: Path) -> bool:
        hidden_or_system_names = {
            ".ds_store",
            "thumbs.db",
            "desktop.ini",
        }

        if path.name.lower() in hidden_or_system_names:
            return True

        # Ignorar metadatos y basura de sistemas/compresiones comunes.
        lowered_parts = {part.lower() for part in path.parts}
        if "__macosx" in lowered_parts:
            return True

        # Ignorar archivos ocultos de Unix (ej.: ._foo, .gitkeep, etc.)
        if path.name.startswith("."):
            return True

        return False


class PreservedArtifactAdminForm(MountedPathChoiceMixin, forms.ModelForm):
    mounted_path_field_name = "storage_path"
    include_input_paths = False

    class Meta:
        model = PreservedArtifact
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._configure_mounted_path_field()


class AnalysisPlanAdminForm(forms.ModelForm):
    search_terms = forms.CharField(
        label=_("informacion a buscar"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 2,
                "class": "w-full min-w-0",
                "placeholder": _("Ej.: correo@dominio.com, usuario123, telefono"),
            }
        ),
        help_text=_(
            "Ingresa una o mas palabras clave para este punto (usuario, correo, telefono, etc.). "
            "Es obligatorio solo cuando no seleccionas un punto de pericia existente."
        ),
    )
    execution_actions = forms.CharField(
        label=_("playbook de acciones ejecutables"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "class": "w-full min-w-0",
                "placeholder": _(
                    "Ej.: Buscar correos electrónicos dados\nBuscar nombres de usuario dados"
                ),
            }
        ),
        help_text=_(
            "Describe las acciones concretas del playbook que se ejecutaran para responder este punto."
        ),
    )
    structured_actions_json = forms.CharField(
        label=_("acciones estructuradas del playbook"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 12,
                "class": "w-full min-w-0 font-mono",
                "placeholder": _(
                    '[{"label":"Buscar indicadores P2P","path_scope":["ActividadReciente"],"file_kinds":["html"],"search_criteria":{"mode":"any","terms":["torrent","p2p"]}}]'
                ),
            }
        ),
        help_text=_(
            "JSON opcional para definir acciones estructuradas con carpeta, tipos de archivo y criterio de busqueda."
        ),
    )

    STOPWORDS = {
        "para",
        "como",
        "sobre",
        "entre",
        "desde",
        "hasta",
        "luego",
        "este",
        "esta",
        "estos",
        "estas",
        "donde",
        "cuando",
        "datos",
        "archivo",
        "archivos",
        "dispositivo",
        "dispositivos",
        "informacion",
        "investigacion",
        "analisis",
        "pericia",
        "punto",
        "solicitado",
        "texto",
    }

    class Meta:
        model = AnalysisPlan
        fields = "__all__"

    class Media:
        js = ("dfir_analysis/requested_point_filter.js",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pericia_case"].label = _("Caso pericial")
        self.fields["requested_point"].label = _("Punto solicitado")
        self.fields["pericia_point"].label = _("Punto de pericia")
        self.fields["label"].label = _("Etiqueta del plan")
        self.fields["strategy_notes"].label = _("Notas de estrategia")
        self.fields["status"].label = _("Estado del plan")
        self.fields["scope_snapshot"].label = _("datos internos del playbook")
        self.fields["strategy_notes"].help_text = _(
            "Opcional. Documenta decisiones del analisis, limites del alcance o criterios del plan."
        )
        case_id = self._resolve_selected_case_id(args, kwargs)
        requested_point_field = self.fields["requested_point"]
        requested_point_field.queryset = self._build_requested_point_queryset(case_id)
        requested_point_field.widget.attrs[
            "data-requested-point-filter-url"
        ] = reverse("admin:dfir_analysis_analysisplanproxy_requested_points")

        self.fields["pericia_point"].queryset = PericiaPoint.objects.filter(
            enabled=True
        )
        self.fields["pericia_point"].required = False
        self.fields["pericia_point"].help_text = _(
            "Opcional: selecciona una tecnica reusable existente o completa 'informacion a buscar' para crearla automaticamente."
        )

        if self.instance and self.instance.pk:
            scope_terms = self._extract_search_terms_from_scope(self.instance.scope_snapshot)
            if scope_terms:
                self.fields["search_terms"].initial = ", ".join(scope_terms)
            terms = self._extract_terms_from_point(self.instance.pericia_point)
            if terms and not self.fields["search_terms"].initial:
                self.fields["search_terms"].initial = ", ".join(terms)
            actions = self._extract_actions_from_scope(self.instance.scope_snapshot)
            if actions and "execution_actions" in self.fields:
                self.fields["execution_actions"].initial = "\n".join(actions)
            structured_actions = self._extract_structured_actions_from_scope(
                self.instance.scope_snapshot
            )
            if structured_actions:
                self.fields["structured_actions_json"].initial = json.dumps(
                    structured_actions,
                    ensure_ascii=True,
                    indent=2,
                )
        elif case_id is not None:
            requested_point_id = self._resolve_requested_point_id(args, kwargs)
            if requested_point_id is not None:
                try:
                    requested_point = RequestedPoint.objects.get(
                        pk=requested_point_id,
                        pericia_case_id=case_id,
                    )
                except RequestedPoint.DoesNotExist:
                    requested_point = None
                if requested_point is not None:
                    suggested_actions = build_suggested_playbook_actions(
                        self._requested_point_text(requested_point)
                    )
                    if suggested_actions and "execution_actions" in self.fields:
                        self.fields["execution_actions"].initial = "\n".join(
                            suggested_actions
                        )
                    structured_actions = build_structured_actions(
                        self._requested_point_text(requested_point)
                    )
                    if structured_actions:
                        self.fields["structured_actions_json"].initial = json.dumps(
                            structured_actions,
                            ensure_ascii=True,
                            indent=2,
                        )

        grouped_choices = mounted_path_choices(
            include_input=True,
            include_output=False,
            include_directories=True,
        )

        current_values = (
            self.initial.get("analysis_targets")
            or getattr(getattr(self, "instance", None), "analysis_targets", [])
            or []
        )
        current_values = self._normalize_analysis_target_values(
            current_values,
            case_id=case_id,
        )
        flat_values = {
            choice_value
            for _group_label, grouped in grouped_choices
            for choice_value, _choice_label in grouped
        }
        extra_values = [value for value in current_values if value not in flat_values]
        if extra_values:
            grouped_choices.append(
                (_("Valor actual"), [(value, value) for value in extra_values])
            )

        grouped_choices = self._append_case_evidence_target_choices(
            grouped_choices,
            case_id=case_id,
        )

        self.fields["analysis_targets"] = forms.MultipleChoiceField(
            label=_("Ubicaciones objetivo del analisis"),
            required=False,
            choices=grouped_choices,
            initial=current_values,
            widget=forms.SelectMultiple(
                attrs={
                    "class": "w-full min-w-0",
                    "size": 12,
                    "data-placeholder": _(
                        "Seleccionar una o mas carpetas o archivos desde volumen montado"
                    ),
                }
            ),
            help_text=_(
                "Selecciona una o mas carpetas o archivos donde correra este plan. El alcance elegido se conserva al guardar y puede editarse despues."
            ),
        )

    def _case_analysis_target_values(self, case_id: int | None) -> list[str]:
        if case_id is None:
            return []

        values: list[str] = []
        seen: set[str] = set()
        queryset = EvidenceItem.objects.filter(pericia_case_id=case_id).select_related(
            "evidence_file"
        )
        for evidence_item in queryset:
            for source_path in evidence_item.known_source_paths():
                normalized = str(source_path or "").strip()
                if not normalized or normalized in seen:
                    continue
                seen.add(normalized)
                values.append(normalized)
        return values

    def _normalize_analysis_target_values(
        self,
        values,
        *,
        case_id: int | None,
    ) -> list[str]:
        unique_values: list[str] = []
        seen: set[str] = set()
        for value in values or []:
            normalized = str(value or "").strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            unique_values.append(normalized)

        preferred_roots = self._case_analysis_target_values(case_id)
        if preferred_roots:
            compacted: list[str] = []
            for value in unique_values:
                if value in preferred_roots:
                    compacted.append(value)
                    continue
                if self._is_covered_by_directory_target(value, preferred_roots):
                    continue
                compacted.append(value)
            unique_values = compacted

        compacted_unique: list[str] = []
        for value in unique_values:
            other_values = [candidate for candidate in unique_values if candidate != value]
            if self._is_covered_by_directory_target(value, other_values):
                continue
            compacted_unique.append(value)
        return compacted_unique

    @staticmethod
    def _is_covered_by_directory_target(value: str, candidates: list[str]) -> bool:
        resolved_value = resolve_existing_evidence_path(value)
        for candidate in candidates:
            if candidate == value:
                continue
            resolved_candidate = resolve_existing_evidence_path(candidate)
            if resolved_candidate is None or not resolved_candidate.is_dir():
                continue
            if resolved_value is not None:
                try:
                    resolved_value.relative_to(resolved_candidate)
                    return True
                except ValueError:
                    continue
            candidate_prefix = f"{str(resolved_candidate).rstrip('/')}/"
            if str(value).startswith(candidate_prefix):
                return True
        return False

    def _append_case_evidence_target_choices(
        self,
        grouped_choices: list[tuple[str, list[tuple[str, str]]]],
        *,
        case_id: int | None,
    ) -> list[tuple[str, list[tuple[str, str]]]]:
        if case_id is None:
            return grouped_choices

        existing_values = {
            choice_value
            for _group_label, grouped in grouped_choices
            for choice_value, _choice_label in grouped
        }
        case_entries: list[tuple[str, str]] = []
        queryset = EvidenceItem.objects.filter(pericia_case_id=case_id).select_related(
            "evidence_file"
        )
        for evidence_item in queryset:
            for source_path in evidence_item.known_source_paths():
                normalized = str(source_path or "").strip()
                if not normalized or normalized in existing_values:
                    continue
                existing_values.add(normalized)
                case_entries.append(
                    (
                        normalized,
                        f"{evidence_item.label} -> {self._analysis_target_label(normalized)}",
                    )
                )

        if case_entries:
            grouped_choices.append((_("Fuentes del caso actual"), case_entries))
        return grouped_choices

    @staticmethod
    def _analysis_target_label(source_path: str) -> str:
        resolved = resolve_existing_evidence_path(source_path)
        if resolved is not None:
            try:
                input_root = Path(settings.EVIDENCE_INPUT_PATH).expanduser().resolve()
                return str(resolved.relative_to(input_root))
            except (OSError, RuntimeError, ValueError):
                return str(resolved)
        return str(source_path)

    def _resolve_selected_case_id(self, args, kwargs) -> int | None:
        if self.instance and self.instance.pk and self.instance.pericia_case_id:
            return int(self.instance.pericia_case_id)

        data = args[0] if args else kwargs.get("data")
        raw_value = data.get("pericia_case") if data else None
        if not raw_value:
            raw_value = self.initial.get("pericia_case")

        try:
            return int(raw_value) if raw_value not in (None, "") else None
        except (TypeError, ValueError):
            return None

    def _resolve_requested_point_id(self, args, kwargs) -> int | None:
        if self.instance and self.instance.pk and self.instance.requested_point_id:
            return int(self.instance.requested_point_id)

        data = args[0] if args else kwargs.get("data")
        raw_value = data.get("requested_point") if data else None
        if not raw_value:
            raw_value = self.initial.get("requested_point")

        try:
            return int(raw_value) if raw_value not in (None, "") else None
        except (TypeError, ValueError):
            return None

    def _build_requested_point_queryset(self, case_id: int | None):
        queryset = RequestedPoint.objects.none()
        if case_id is not None:
            queryset = RequestedPoint.objects.filter(pericia_case_id=case_id)

        current_requested_point_id = getattr(self.instance, "requested_point_id", None)
        if current_requested_point_id and not queryset.filter(pk=current_requested_point_id).exists():
            queryset = RequestedPoint.objects.filter(pk=current_requested_point_id) | queryset

        return queryset

    def clean_analysis_targets(self) -> list[str]:
        values = self.cleaned_data.get("analysis_targets") or []
        case_id = None
        raw_case = self.cleaned_data.get("pericia_case")
        if raw_case is not None:
            case_id = getattr(raw_case, "pk", raw_case)
        try:
            normalized_case_id = int(case_id) if case_id not in (None, "") else None
        except (TypeError, ValueError):
            normalized_case_id = None
        return self._normalize_analysis_target_values(
            values,
            case_id=normalized_case_id,
        )

    def clean(self):
        cleaned_data = super().clean()
        pericia_point = cleaned_data.get("pericia_point")
        raw_terms = str(cleaned_data.get("search_terms") or "").strip()
        raw_actions = str(cleaned_data.get("execution_actions") or "").strip()
        raw_structured_actions = str(cleaned_data.get("structured_actions_json") or "").strip()

        if pericia_point is None and not raw_terms:
            self.add_error(
                "search_terms",
                "Debes indicar al menos una palabra clave para este punto.",
            )

        if pericia_point is None and not raw_terms and not raw_actions:
            self.add_error(
                "execution_actions",
                "Completa las acciones o selecciona un punto de pericia existente.",
            )

        if raw_structured_actions:
            try:
                parsed_structured = json.loads(raw_structured_actions)
            except json.JSONDecodeError:
                self.add_error(
                    "structured_actions_json",
                    "Debes ingresar un JSON valido para las acciones estructuradas.",
                )
            else:
                if not isinstance(parsed_structured, list):
                    self.add_error(
                        "structured_actions_json",
                        "Las acciones estructuradas deben enviarse como una lista JSON.",
                    )
                else:
                    cleaned_data["structured_actions_json"] = parsed_structured

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        actions = self._parse_actions(self.cleaned_data.get("execution_actions") or "")
        raw_search_terms = str(self.cleaned_data.get("search_terms") or "").strip()
        if raw_search_terms:
            search_terms = self._extract_terms(raw_search_terms)
        else:
            search_terms = self._extract_terms_from_point(instance.pericia_point)

        pericia_point = self._safe_pericia_point(instance)
        if not actions:
            actions = build_suggested_playbook_actions(
                self._requested_point_text(instance.requested_point),
                pericia_point_name=getattr(pericia_point, "name", ""),
                point_family=getattr(pericia_point, "point_family", ""),
            )
        structured_actions = self.cleaned_data.get("structured_actions_json")
        if isinstance(structured_actions, list):
            structured_actions = normalize_structured_actions(
                structured_actions,
                pericia_point_id=getattr(pericia_point, "pk", None),
                pericia_point_name=getattr(pericia_point, "name", ""),
                point_family=getattr(pericia_point, "point_family", ""),
                analysis_targets=list(self.cleaned_data.get("analysis_targets") or []),
            )
        else:
            structured_actions = build_structured_actions(
                self._requested_point_text(instance.requested_point),
                pericia_point_id=getattr(pericia_point, "pk", None),
                pericia_point_name=getattr(pericia_point, "name", ""),
                point_family=getattr(pericia_point, "point_family", ""),
                search_terms=search_terms,
                analysis_targets=list(self.cleaned_data.get("analysis_targets") or []),
                raw_actions=actions,
            )

        scope_snapshot = instance.scope_snapshot
        if not isinstance(scope_snapshot, dict):
            scope_snapshot = {}
        scope_snapshot["search_terms"] = search_terms
        if actions:
            scope_snapshot["execution_actions"] = actions
        else:
            scope_snapshot.pop("execution_actions", None)
        scope_snapshot["structured_actions"] = structured_actions
        instance.scope_snapshot = scope_snapshot

        if instance.pericia_point_id is None:
            terms = search_terms
            requested_point = instance.requested_point
            case = instance.pericia_case
            point_name = (
                f"Manual {case.case_reference} - punto {requested_point.order} - {uuid4().hex[:6]}"
            )
            instance.pericia_point = PericiaPoint.objects.create(
                name=point_name,
                point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
                matching_mode=PericiaPoint.MatchingMode.ANY,
                parameters={"terms": terms},
                enabled=True,
            )

        if commit:
            instance.save()
            self.save_m2m()

        return instance

    @classmethod
    def _extract_terms(cls, text: str) -> list[str]:
        tokens = re.findall(r"[a-zA-Z0-9_@.\\-]{3,}", str(text).lower())
        terms: list[str] = []
        seen: set[str] = set()
        for token in tokens:
            if token in cls.STOPWORDS or token in seen:
                continue
            seen.add(token)
            terms.append(token)
            if len(terms) >= 12:
                break
        if not terms:
            return ["relevante"]
        return terms

    @staticmethod
    def _extract_terms_from_point(pericia_point: PericiaPoint | None) -> list[str]:
        if pericia_point is None:
            return []
        params = pericia_point.parameters if isinstance(pericia_point.parameters, dict) else {}
        terms = params.get("terms")
        if isinstance(terms, list):
            return [str(term).strip() for term in terms if str(term).strip()]
        return []

    @staticmethod
    def _parse_actions(raw_text: str) -> list[str]:
        actions: list[str] = []
        seen: set[str] = set()
        for line in str(raw_text).splitlines():
            normalized = line.strip().lstrip("-*").strip()
            if not normalized:
                continue
            key = normalized.lower()
            if key in seen:
                continue
            seen.add(key)
            actions.append(normalized)
        return actions

    @staticmethod
    def _extract_actions_from_scope(scope_snapshot: object) -> list[str]:
        if not isinstance(scope_snapshot, dict):
            return []
        actions = scope_snapshot.get("execution_actions")
        if not isinstance(actions, list):
            return []
        return [str(action).strip() for action in actions if str(action).strip()]

    @staticmethod
    def _extract_search_terms_from_scope(scope_snapshot: object) -> list[str]:
        if not isinstance(scope_snapshot, dict):
            return []
        terms = scope_snapshot.get("search_terms")
        if not isinstance(terms, list):
            return []
        return [str(term).strip() for term in terms if str(term).strip()]

    @staticmethod
    def _extract_structured_actions_from_scope(scope_snapshot: object) -> list[dict]:
        if not isinstance(scope_snapshot, dict):
            return []
        structured_actions = scope_snapshot.get("structured_actions")
        if not isinstance(structured_actions, list):
            playbook = scope_snapshot.get("analysis_playbook")
            if not isinstance(playbook, dict):
                return []
            structured_actions = playbook.get("actions")
        if not isinstance(structured_actions, list):
            return []
        return [action for action in structured_actions if isinstance(action, dict)]

    @staticmethod
    def _requested_point_text(requested_point: RequestedPoint | None) -> str:
        if requested_point is None:
            return ""
        return " ".join(
            part
            for part in [
                str(getattr(requested_point, "short_label", "") or "").strip(),
                str(getattr(requested_point, "literal_text", "") or "").strip(),
            ]
            if part
        )

    @staticmethod
    def _safe_pericia_point(instance: AnalysisPlan) -> PericiaPoint | None:
        if not getattr(instance, "pericia_point_id", None):
            return None
        try:
            return instance.pericia_point
        except PericiaPoint.DoesNotExist:
            return None


class RequestedPointAdminForm(forms.ModelForm):
    class Meta:
        model = RequestedPoint
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        status_field = self.fields.get("status")
        if status_field is not None:
            status_field.required = False

        case_field = self.fields.get("pericia_case")
        if case_field is not None:
            case_field.label = _("Caso pericial")
            case_field.help_text = _(
                "Cada punto solicitado pertenece solo a esta pericia."
            )

        order_field = self.fields.get("order")
        if order_field is not None:
            order_field.help_text = _(
                "El orden es local a esta pericia y no se comparte con otros casos."
            )
            if not self.is_bound:
                next_order = self._suggested_order()
                if next_order is not None:
                    self.initial.setdefault("order", next_order)

    def clean(self):
        cleaned_data = super().clean()
        pericia_case = cleaned_data.get("pericia_case")
        order = cleaned_data.get("order")
        if pericia_case is None or order in (None, ""):
            return cleaned_data

        duplicate_exists = RequestedPoint.objects.filter(
            pericia_case=pericia_case,
            order=order,
        ).exclude(pk=getattr(self.instance, "pk", None)).exists()
        if duplicate_exists:
            self.add_error(
                "order",
                _("Ya existe un punto solicitado con ese orden dentro de esta pericia."),
            )
        return cleaned_data

    def _suggested_order(self) -> int | None:
        if getattr(self.instance, "pk", None):
            return int(self.instance.order)

        raw_case = self.data.get("pericia_case") if self.is_bound else self.initial.get("pericia_case")
        if raw_case in (None, ""):
            return 1
        try:
            case_id = int(raw_case)
        except (TypeError, ValueError):
            return 1
        current_max = (
            RequestedPoint.objects.filter(pericia_case_id=case_id)
            .order_by("-order")
            .values_list("order", flat=True)
            .first()
        )
        return int(current_max or 0) + 1


class RequestedPointInlineFormSet(BaseInlineFormSet):
    duplicate_order_message = _(
        "Ya existe un punto solicitado con ese orden dentro de esta pericia."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.is_bound:
            return

        next_order = self._next_order()
        for form in self.extra_forms:
            if not form.instance.pk:
                form.initial["order"] = next_order
                form.fields["order"].initial = next_order
                next_order += 1

        try:
            empty_form = self.empty_form
        except Exception:
            empty_form = None
        if empty_form is not None:
            empty_form.initial["order"] = next_order
            empty_form.fields["order"].initial = next_order

    def clean(self):
        seen_orders: dict[int, forms.Form] = {}
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if form.cleaned_data.get("DELETE"):
                continue
            order = form.cleaned_data.get("order")
            if order in (None, ""):
                continue
            if order in seen_orders:
                seen_orders[order].add_error("order", self.duplicate_order_message)
                form.add_error("order", self.duplicate_order_message)
            else:
                seen_orders[order] = form

    def _next_order(self) -> int:
        if getattr(self.instance, "pk", None):
            current_max = (
                RequestedPoint.objects.filter(pericia_case=self.instance)
                .order_by("-order")
                .values_list("order", flat=True)
                .first()
            )
            return int(current_max or 0) + 1
        return 1

    @property
    def empty_form(self):
        form = super().empty_form
        next_order = self._next_order() + len(self.extra_forms)
        form.initial["order"] = next_order
        form.fields["order"].initial = next_order
        return form


# ---------------------------------------------------------------------------
# PericiaPoint admin form — parámetros + alcance amigables
# ---------------------------------------------------------------------------

_PATTERN_CHOICES = [
    ("", _("Seleccionar patrón predefinido (opcional)")),
    ("email", _("Correo electrónico")),
    ("phone", _("Número de teléfono")),
    ("dni", _("Número de documento (DNI/CUIL/CUIT)")),
    ("cbu", _("Número de CBU (22 dígitos)")),
    ("ip", _("Dirección IP")),
    ("url", _("URL / Enlace web")),
]

_BUILTIN_PATTERNS: dict[str, str] = {
    "email": r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    "phone": r"(?:\+?54)?[\s\-]?(?:9[\s\-]?)?(?:11|[2-9]\d)[\s\-]?\d{4}[\s\-]?\d{4}",
    "dni": r"\b(?:DNI|CUIL|CUIT)?[\s:\-]?\d{1,2}[\.\-]?\d{3}[\.\-]?\d{3}[\.\-]?\d{0,4}\b",
    "cbu": r"\b\d{22}\b",
    "ip": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "url": r"https?://[^\s\"'<>]+",
}


class PericiaPointAdminForm(MountedPathChoiceMixin, forms.ModelForm):
    """Formulario amigable para PericiaPoint.

    - ``search_keywords``: palabras/frases a buscar (reemplaza ``parameters.terms``).
    - ``pattern_preset``: selector de patrón predefinido (email, teléfono, etc.)
      que se almacena como ``parameters.pattern``.
    - ``scope_path``: selector de ruta montada para el alcance de búsqueda,
      almacenado en ``scope.path``.
    """

    mounted_path_field_name = "scope_path"
    include_directory_paths = True
    include_input_paths = True
    include_output_paths = True
    include_file_paths = True
    pericia_case = forms.ModelChoiceField(
        label=_("Caso pericial"),
        queryset=PericiaCase.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "w-full min-w-0"}),
        help_text=_(
            "Opcional. Selecciona una pericia para sugerir nombres relevantes desde sus puntos solicitados."
        ),
    )

    search_keywords = forms.CharField(
        label=_("palabras / frases a buscar"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "class": "w-full min-w-0",
                "placeholder": _(
                    "Ej.: usuario@ejemplo.com, juan perez, caso2024 (separadas por coma o una por línea)"
                ),
            }
        ),
        help_text=_(
            "Ingresa una o más palabras clave separadas por coma o salto de línea. "
            "Se almacenan en parameters.terms del punto."
        ),
    )

    pattern_preset = forms.ChoiceField(
        label=_("patrón predefinido"),
        required=False,
        choices=_PATTERN_CHOICES,
        widget=forms.Select(attrs={"class": "w-full min-w-0"}),
        help_text=_(
            "Selecciona un patrón conocido para búsqueda por expresión regular. "
            "Se almacena en parameters.pattern. Puedes combinar con palabras clave."
        ),
    )

    scope_path = forms.ChoiceField(
        label=_("alcance (carpeta o archivo)"),
        required=False,
        choices=[],
        widget=forms.Select(
            attrs={
                "class": "w-full min-w-0",
                "data-placeholder": _(
                    "Seleccionar carpeta o archivo desde volumen montado"
                ),
            }
        ),
        help_text=_(
            "Opcional. Define la carpeta o archivo donde se realizará la búsqueda. "
            "Se almacena en scope.path del punto."
        ),
    )

    class Meta:
        model = PericiaPoint
        fields = "__all__"
        exclude = ["parameters", "scope"]

    class Media:
        js = (
            "dfir_evidence/mounted_path_autocomplete.js",
            "dfir_analysis/pericia_point_name_suggestions.js",
        )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self._configure_mounted_path_field()
        # Remove parameters/scope from the form fields if somehow present
        self.fields.pop("parameters", None)
        self.fields.pop("scope", None)
        self.fields["pericia_case"].queryset = PericiaCase.objects.all().order_by(
            "-created_at"
        )

        selected_case_id = self._resolve_selected_case_id(args, kwargs)
        if selected_case_id is not None:
            self.fields["pericia_case"].initial = selected_case_id

        self.fields["name"].label = _("Nombre del punto de pericia")
        self.fields["name"].widget = forms.TextInput(
            attrs={
                "class": "w-full min-w-0",
                "autocomplete": "off",
                "data-pericia-point-name-suggestions-url": reverse(
                    "admin:dfir_analysis_periciapointproxy_name_suggestions"
                ),
            }
        )
        if selected_case_id is not None:
            self.fields["name"].widget.attrs["data-selected-case-id"] = str(
                selected_case_id
            )
        self.fields["name"].help_text = _(
            "Puedes escribir manualmente o seleccionar un nombre sugerido desde la pericia elegida."
        )

        # Pre-popular desde la instancia existente
        instance = getattr(self, "instance", None)
        if instance and instance.pk:
            params = instance.parameters if isinstance(instance.parameters, dict) else {}
            terms = params.get("terms")
            if isinstance(terms, list) and terms:
                self.fields["search_keywords"].initial = ", ".join(
                    str(t) for t in terms
                )
            pattern = params.get("pattern")
            if pattern:
                # Intentar identificar si coincide con un preset o dejar regex crudo
                reverse_map = {v: k for k, v in _BUILTIN_PATTERNS.items()}
                preset_key = reverse_map.get(pattern)
                if preset_key:
                    self.fields["pattern_preset"].initial = preset_key
            scope = instance.scope if isinstance(instance.scope, dict) else {}
            scope_path_value = scope.get("path", "")
            if scope_path_value:
                self.fields["scope_path"].initial = scope_path_value
                self._ensure_current_value(
                    self.fields["scope_path"].choices
                    if isinstance(self.fields["scope_path"].choices, list)
                    else [],
                    scope_path_value,
                )

    def _resolve_selected_case_id(self, args, kwargs) -> int | None:
        data = args[0] if args else kwargs.get("data")
        raw_value = data.get("pericia_case") if data else None
        if not raw_value:
            raw_value = self.initial.get("pericia_case")
        if not raw_value and self.request is not None:
            raw_value = self.request.GET.get("pericia_case")
        try:
            return int(raw_value) if raw_value not in (None, "") else None
        except (TypeError, ValueError):
            return None

    def _parse_keywords(self, raw: str) -> list[str]:
        """Tokeniza el texto de búsqueda separado por coma o salto de línea."""
        terms: list[str] = []
        seen: set[str] = set()
        for token in re.split(r"[,\n]+", raw):
            normalized = token.strip()
            if not normalized:
                continue
            key = normalized.lower()
            if key in seen:
                continue
            seen.add(key)
            terms.append(normalized)
        return terms

    def _post_clean(self):
        # Compute and set parameters/scope on the instance BEFORE super()._post_clean()
        # calls model.full_clean(). Since these fields are excluded from the form,
        # super() will not overwrite them.
        if hasattr(self, "cleaned_data"):
            raw_keywords = str(self.cleaned_data.get("search_keywords") or "").strip()
            pattern_preset = str(self.cleaned_data.get("pattern_preset") or "").strip()
            scope_path_value = str(self.cleaned_data.get("scope_path") or "").strip()

            parameters: dict = {}
            if raw_keywords:
                parameters["terms"] = self._parse_keywords(raw_keywords)
            if pattern_preset and pattern_preset in _BUILTIN_PATTERNS:
                parameters["pattern"] = _BUILTIN_PATTERNS[pattern_preset]
                parameters["pattern_label"] = pattern_preset

            # Provide minimal placeholders so model-level clean() passes even when
            # the user only provided a pattern preset (no keywords).
            point_family = str(self.cleaned_data.get("point_family") or "")
            if not parameters.get("terms") and point_family == PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH:
                parameters.setdefault("terms", [parameters.get("pattern_label", "_pattern")])
            if not parameters.get("value") and point_family == PericiaPoint.PointFamily.TEXT_EMAIL_SEARCH:
                parameters.setdefault("value", "_placeholder")
            if not parameters.get("target_labels") and point_family == PericiaPoint.PointFamily.IMAGE_CHARACTERISTIC_DETECTION:
                parameters.setdefault("target_labels", ["_placeholder"])
                parameters.setdefault("min_confidence", 0.5)

            self.instance.parameters = parameters
            self.instance.scope = {"path": scope_path_value} if scope_path_value else {}

        super()._post_clean()

    def _update_errors(self, errors):
        """Remap errors on model-only fields (parameters, scope) to NON_FIELD_ERRORS."""
        from django.core.exceptions import ValidationError

        if hasattr(errors, "error_dict"):
            remapped: dict = {}
            non_field: list = []
            for field_name, error_list in errors.error_dict.items():
                if field_name not in self.fields and field_name != "__all__":
                    non_field.extend(error_list)
                else:
                    remapped[field_name] = error_list
            if non_field:
                remapped.setdefault("__all__", []).extend(non_field)
            if remapped:
                super()._update_errors(ValidationError(remapped))
        else:
            super()._update_errors(errors)


    def clean(self):
        cleaned_data = super().clean()
        raw_keywords = str(cleaned_data.get("search_keywords") or "").strip()
        pattern_preset = str(cleaned_data.get("pattern_preset") or "").strip()
        scope_path_value = str(cleaned_data.get("scope_path") or "").strip()

        if not raw_keywords and not pattern_preset:
            self.add_error(
                "search_keywords",
                _(
                    "Debes ingresar al menos una palabra clave o seleccionar un patrón predefinido."
                ),
            )

        # Construir parameters
        parameters: dict = {}
        if raw_keywords:
            parameters["terms"] = self._parse_keywords(raw_keywords)
        if pattern_preset and pattern_preset in _BUILTIN_PATTERNS:
            parameters["pattern"] = _BUILTIN_PATTERNS[pattern_preset]
            parameters["pattern_label"] = pattern_preset

        cleaned_data["_computed_parameters"] = parameters

        # Construir scope
        scope: dict = {}
        if scope_path_value:
            scope["path"] = scope_path_value
        cleaned_data["_computed_scope"] = scope

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        computed = dict(self.cleaned_data.get("_computed_parameters") or {})

        # Ensure model validation passes: add minimal terms if only pattern was set.
        point_family = str(instance.point_family or "")
        if not computed.get("terms") and point_family == PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH:
            computed.setdefault("terms", [computed.get("pattern_label", "busqueda")])
        if not computed.get("value") and point_family == PericiaPoint.PointFamily.TEXT_EMAIL_SEARCH:
            computed.setdefault("value", computed.get("pattern_label", "email"))
        if not computed.get("target_labels") and point_family == PericiaPoint.PointFamily.IMAGE_CHARACTERISTIC_DETECTION:
            computed.setdefault("target_labels", [computed.get("pattern_label", "objeto")])
            computed.setdefault("min_confidence", 0.5)

        instance.parameters = computed
        instance.scope = self.cleaned_data.get("_computed_scope") or {}
        if commit:
            instance.save()
        return instance
