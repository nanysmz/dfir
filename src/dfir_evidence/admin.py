from django.contrib import admin
from django.conf import settings
from django.http import JsonResponse
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join
from unfold.admin import ModelAdmin
import os
from pathlib import Path

from dfir_core.admin_forms import (
    EvidenceFileAdminForm,
    EvidenceItemAdminForm,
    PreservedArtifactAdminForm,
    resolve_existing_evidence_path,
)
from dfir_pericia.models import EvidenceItem
from .models import EvidenceFileProxy, EvidenceItemProxy, PreservedArtifactProxy


def _mounted_roots() -> list[tuple[str, Path]]:
    return [
        ("Entrada", Path(settings.EVIDENCE_INPUT_PATH)),
        ("Salida", Path(settings.EVIDENCE_OUTPUT_PATH)),
    ]


def _resolve_mounted_root(path: Path) -> tuple[str, Path] | None:
    for root_label, root in _mounted_roots():
        if not root.exists():
            continue
        try:
            resolved_root = root.expanduser().resolve()
            resolved_path = path.expanduser().resolve()
            resolved_path.relative_to(resolved_root)
            return root_label, resolved_root
        except (OSError, RuntimeError, ValueError):
            continue
    return None


def _entry_payload(path: Path, *, root_label: str, root: Path) -> dict[str, object]:
    relative = str(path.relative_to(root))
    kind = "directory" if path.is_dir() else "file"
    prefix = f"{root_label} / " if len(_mounted_roots()) > 1 else ""
    return {
        "value": str(path),
        "label": f"{prefix}{relative}",
        "kind": kind,
        "is_directory": path.is_dir(),
        "can_navigate": path.is_dir(),
    }


def _list_direct_children(path: Path) -> tuple[list[Path], list[Path]]:
    directories: list[Path] = []
    files: list[Path] = []
    for child in sorted(path.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower())):
        if child.name.startswith("."):
            continue
        if child.is_dir():
            directories.append(child)
        elif child.is_file():
            files.append(child)
    return directories, files


@admin.register(EvidenceFileProxy)
class EvidenceFileAdmin(ModelAdmin):
    form = EvidenceFileAdminForm
    list_display = (
        "display_name",
        "pericia_context",
        "associated_devices",
        "identity_context",
        "homonymous_contexts",
        "file_kind",
        "source_path",
        "updated_at",
    )
    search_fields = ("display_name", "source_path", "sha256")
    list_filter = ("file_kind",)
    list_filter_submit = True
    readonly_fields = (
        "pericia_context_detail",
        "associated_devices_detail",
        "identity_context_detail",
        "homonymous_contexts_detail",
    )
    fields = (
        "display_name",
        "pericia_context_detail",
        "associated_devices_detail",
        "identity_context_detail",
        "homonymous_contexts_detail",
        "file_kind",
        "source_path",
        "sha256",
        "size_bytes",
        "metadata",
    )

    class Media:
        js = ("dfir_evidence/mounted_path_autocomplete.js",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related(
            "case_evidence_items__pericia_case",
            "linked_evidence_items__pericia_case",
        )

    @admin.display(description="contexto de identidad")
    def identity_context(self, obj):
        return obj.identity_scope_label()

    @admin.display(description="homonimos")
    def homonymous_contexts(self, obj):
        homonymous_records = list(obj.homonymous_records()[:3])
        if not homonymous_records:
            return format_html(
                "<span style='color:#64748b;'>{}</span>",
                "Sin homonimos visibles",
            )
        first = homonymous_records[0].identity_scope_label()
        if len(homonymous_records) == 1:
            return first
        return format_html(
            "<strong>{}</strong><br><span style='color:#64748b;font-size:0.84rem;'>{}</span>",
            first,
            f"+{len(homonymous_records) - 1} contexto(s)",
        )

    @admin.display(description="pericia")
    def pericia_context(self, obj):
        case_refs = [case.case_reference for case in obj.associated_pericia_cases()]
        if not case_refs:
            return format_html(
                "<span style='color:#b45309;'>{}</span>",
                "Sin asociacion pericial visible",
            )
        if len(case_refs) == 1:
            return case_refs[0]
        return format_html(
            "<strong>{}</strong><br><span style='color:#64748b;font-size:0.84rem;'>{}</span>",
            case_refs[0],
            f"+{len(case_refs) - 1} pericia(s)",
        )

    @admin.display(description="dispositivos asociados")
    def associated_devices(self, obj):
        labels = [item.label for item in obj.associated_evidence_items()]
        if not labels:
            return format_html(
                "<span style='color:#b45309;'>{}</span>",
                "Sin dispositivos asociados",
            )
        if len(labels) == 1:
            return labels[0]
        return format_html(
            "<strong>{}</strong><br><span style='color:#64748b;font-size:0.84rem;'>{}</span>",
            labels[0],
            f"+{len(labels) - 1} asociado(s)",
        )

    @admin.display(description="pericia asociada")
    def pericia_context_detail(self, obj):
        if obj is None or obj.pk is None:
            return "Se completa automaticamente cuando el archivo queda vinculado a uno o mas elementos de evidencia."
        cases = list(obj.associated_pericia_cases())
        if not cases:
            return format_html(
                "<span style='color:#b45309;'>{}</span>",
                "Archivo sin asociacion pericial visible.",
            )
        return format_html_join(
            "<br>",
            "{}",
            ((case.case_reference,) for case in cases),
        )

    @admin.display(description="dispositivos asociados")
    def associated_devices_detail(self, obj):
        if obj is None or obj.pk is None:
            return "Se completa automaticamente cuando el archivo queda vinculado a uno o mas dispositivos."
        items = list(obj.associated_evidence_items())
        if not items:
            return format_html(
                "<span style='color:#b45309;'>{}</span>",
                "Archivo sin dispositivos asociados visibles.",
            )
        return format_html_join(
            "<br>",
            "{}",
            (
                (
                    f"{item.pericia_case.case_reference} / {item.label}",
                )
                for item in items
            ),
        )

    @admin.display(description="scope de identidad")
    def identity_context_detail(self, obj):
        if obj is None or obj.pk is None:
            return "Por defecto los archivos manuales usan scope global; los derivados desde dispositivos quedan scopeados a su pericia."
        return obj.identity_scope_label()

    @admin.display(description="homonimos en otros contextos")
    def homonymous_contexts_detail(self, obj):
        if obj is None or obj.pk is None:
            return "Se completa cuando existan archivos o carpetas con el mismo nombre en otros contextos."
        homonymous_records = list(obj.homonymous_records())
        if not homonymous_records:
            return format_html(
                "<span style='color:#64748b;'>{}</span>",
                "No hay homonimos registrados en otros contextos.",
            )
        return format_html_join(
            "<br>",
            "{}",
            (
                (
                    f"{record.identity_scope_label()} / {record.source_path}",
                )
                for record in homonymous_records
            ),
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj=obj, **kwargs)
        source_path_field = form.base_fields.get("source_path")
        if source_path_field is not None:
            source_path_field.widget.attrs[
                "data-mounted-path-autocomplete-url"
            ] = reverse("admin:dfir_evidence_evidencefileproxy_mounted_path_search")
            source_path_field.widget.attrs["data-mounted-path-autocomplete"] = "true"
        return form

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "mounted-path-search/",
                self.admin_site.admin_view(self.mounted_path_search_view),
                name="dfir_evidence_evidencefileproxy_mounted_path_search",
            )
        ]
        return custom_urls + urls

    def mounted_path_search_view(self, request):
        query = str(request.GET.get("q") or "").strip().lower()
        browser_mode = str(request.GET.get("browser") or "").strip().lower() in {
            "1",
            "true",
            "yes",
        }
        current_path_value = str(request.GET.get("current_path") or "").strip()
        resolve_value = str(request.GET.get("resolve") or "").strip()
        max_results = 60
        max_scanned = 12000
        scanned = 0
        results = []
        roots = [root for _label, root in _mounted_roots()]

        if browser_mode:
            browse_target = resolve_existing_evidence_path(
                current_path_value or resolve_value
            )
            selected_path = ""
            if browse_target is not None:
                selected_path = str(browse_target)
                if browse_target.is_file():
                    browse_target = browse_target.parent
            payload: dict[str, object] = {
                "results": [],
                "current_path": "",
                "current_label": "Raices montadas",
                "parent_path": "",
                "selected_path": selected_path,
            }

            if browse_target is None:
                for root_label, root in _mounted_roots():
                    if not root.exists():
                        continue
                    directories, files = _list_direct_children(root)
                    for path in directories + files:
                        if query and query not in str(path.name).lower():
                            continue
                        payload["results"].append(
                            _entry_payload(path, root_label=root_label, root=root)
                        )
                return JsonResponse(payload)

            resolved_root_info = _resolve_mounted_root(browse_target)
            if resolved_root_info is None or not browse_target.is_dir():
                return JsonResponse(payload)

            root_label, root = resolved_root_info
            payload["current_path"] = str(browse_target)
            try:
                relative = browse_target.relative_to(root)
                payload["current_label"] = (
                    f"{root_label} / {relative}" if relative.parts else root_label
                )
            except ValueError:
                payload["current_label"] = root_label
            if browse_target != root:
                payload["parent_path"] = str(browse_target.parent)

            directories, files = _list_direct_children(browse_target)
            for path in directories + files:
                if query and query not in str(path.name).lower():
                    continue
                payload["results"].append(
                    _entry_payload(path, root_label=root_label, root=root)
                )
            return JsonResponse(payload)

        for root in roots:
            if not root.exists():
                continue

            for current_root, dirnames, filenames in os.walk(root):
                dirnames[:] = sorted(
                    name for name in dirnames if not name.startswith(".")
                )
                filenames = sorted(
                    name for name in filenames if not name.startswith(".")
                )

                for dirname in dirnames:
                    scanned += 1
                    if scanned > max_scanned or len(results) >= max_results:
                        return JsonResponse({"results": results})

                    full_path = Path(current_root) / dirname
                    full_path_str = str(full_path)
                    if query and query not in full_path_str.lower():
                        continue
                    results.append(
                        {
                            "value": full_path_str,
                            "label": f"[dir] {full_path.relative_to(root)}",
                        }
                    )

                for filename in filenames:
                    scanned += 1
                    if scanned > max_scanned or len(results) >= max_results:
                        return JsonResponse({"results": results})

                    full_path = Path(current_root) / filename
                    full_path_str = str(full_path)
                    if query and query not in full_path_str.lower():
                        continue
                    results.append(
                        {
                            "value": full_path_str,
                            "label": str(full_path.relative_to(root)),
                        }
                    )

        return JsonResponse({"results": results})


@admin.register(EvidenceItemProxy)
class EvidenceItemAdmin(ModelAdmin):
    form = EvidenceItemAdminForm
    list_display = (
        "label",
        "pericia_case",
        "role",
    )
    list_filter = ("role",)
    search_fields = (
        "label",
        "identifier",
        "serial_number",
        "pericia_case__case_reference",
    )
    readonly_fields = ("evidence_files_summary",)
    fields = (
        "pericia_case",
        "parent_item",
        "device_template",
        "label",
        "role",
        "acquisition_status",
        "source_path",
        "supporting_source_paths",
        "evidence_files_summary",
        "device_class",
        "device_type",
        "device_interface",
        "device_brand",
        "device_model",
        "identifier",
        "serial_number",
        "device_capacity_gb",
        "sha256",
        "size_bytes",
        "technical_notes",
        "description",
        "metadata",
    )
    list_filter_submit = True
    warn_unsaved_form = True
    actions = ["duplicate_evidence_item"]

    @admin.display(description="archivos de evidencia")
    def evidence_files_summary(self, obj):
        if obj is None or obj.pk is None:
            return "Se resuelven automaticamente desde la fuente primaria seleccionada para este dispositivo."

        count = obj.evidence_files.count()
        return format_html(
            "<strong>{}</strong><br><span style='color:#64748b;'>"
            "Resueltos automaticamente desde la fuente primaria del dispositivo."
            "</span>",
            f"{count} archivo(s) vinculados",
        )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if isinstance(form, EvidenceItemAdminForm):
            form.sync_evidence_files_from_source_path(form.instance)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "mounted-directory-search/",
                self.admin_site.admin_view(self.mounted_directory_search_view),
                name="dfir_evidence_evidenceitemproxy_mounted_directory_search",
            )
        ]
        return custom_urls + urls

    def mounted_directory_search_view(self, request):
        query = str(request.GET.get("q") or "").strip().lower()
        input_root = Path(settings.EVIDENCE_INPUT_PATH)
        if not input_root.exists():
            return JsonResponse({"results": []})

        max_results = 60
        results: list[dict[str, str]] = []
        seen: set[str] = set()

        def add_result(path: Path) -> None:
            value = str(path)
            if value in seen or len(results) >= max_results:
                return
            seen.add(value)
            results.append(
                {
                    "value": value,
                    "label": str(path.relative_to(input_root)),
                }
            )

        if not query:
            for child in sorted(input_root.iterdir()):
                if child.name.startswith(".") or not child.is_dir():
                    continue
                add_result(child)
            return JsonResponse({"results": results})

        max_scanned = 12000
        scanned = 0
        for current_root, dirnames, _filenames in os.walk(input_root):
            dirnames[:] = sorted(name for name in dirnames if not name.startswith("."))
            current = Path(current_root)
            for dirname in dirnames:
                scanned += 1
                if scanned > max_scanned or len(results) >= max_results:
                    return JsonResponse({"results": results})
                path = current / dirname
                relative = str(path.relative_to(input_root)).lower()
                if query not in relative:
                    continue
                add_result(path)

        return JsonResponse({"results": results})

    def duplicate_evidence_item(self, request, queryset):
        """Duplica elementos de evidencia seleccionados."""
        for item in queryset:
            # Crear copia con los mismos datos
            new_item = EvidenceItem.objects.create(
                pericia_case=item.pericia_case,
                parent_item=item.parent_item,
                evidence_file=item.evidence_file,
                label=EvidenceItemAdminForm.next_device_label_for_case(item.pericia_case),
                description=item.description,
                role=item.role,
                acquisition_status=item.acquisition_status,
                identifier=item.identifier,
                serial_number=item.serial_number,
                source_path=item.source_path,
                sha256=item.sha256,
                size_bytes=item.size_bytes,
                metadata=dict(item.metadata) if item.metadata else {},
            )
            # Copiar relaciones M2M
            new_item.evidence_files.set(item.evidence_files.all())
            for source in item.sources.all():
                source.__class__.objects.create(
                    evidence_item=new_item,
                    role=source.role,
                    source_kind=source.source_kind,
                    source_path=source.source_path,
                    position=source.position,
                    metadata=dict(source.metadata) if source.metadata else {},
                )
        
        count = queryset.count()
        self.message_user(
            request,
            f"{count} elemento(s) de evidencia duplicado(s) exitosamente.",
        )

    duplicate_evidence_item.short_description = "Duplicar elemento(s) de evidencia"


@admin.register(PreservedArtifactProxy)
class PreservedArtifactAdmin(ModelAdmin):
    form = PreservedArtifactAdminForm
    list_display = ("display_name", "pericia_case", "artifact_kind", "storage_path")
    list_filter = ("artifact_kind",)
    search_fields = ("display_name", "storage_path", "pericia_case__case_reference")
    list_filter_submit = True
