from django.contrib import admin
from django.contrib import messages
from django.core.management import call_command
from django.http import HttpResponseRedirect
from django.db import transaction
from django.db.models import Q
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, StackedInline

from dfir_core.admin_forms import (
    EvidenceItemAdminForm,
    PericiaCaseAdminForm,
    PericiaDocumentAdminForm,
    ReportSectionAdminForm,
    RequestedPointAdminForm,
    RequestedPointInlineFormSet,
)
from dfir_pericia.models import (
    AnalysisPlan,
    DeviceAnalysisResult,
    EvidenceItem,
    PericiaExecution,
    PericiaDocument,
    PreservedArtifact,
    ReportSection,
    RequestedPoint,
    RequestedPointResponse,
)
from dfir_pericia.tasks import execute_pericia_point_task
from dfir_pericia.workflow import (
    analysis_plan_operational_summary,
    analysis_plan_operator_state,
    build_case_workflow,
)

from .models import PericiaCaseProxy, PericiaDocumentProxy, RequestedPointProxy


class PericiaDocumentInline(StackedInline):
    model = PericiaDocument
    form = PericiaDocumentAdminForm
    extra = 0
    tab = True
    collapsible = True
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "document_type",
                    "file_path",
                    "extracted_text",
                    "metadata",
                )
            },
        ),
    )


class RequestedPointInline(StackedInline):
    STATUS_BADGE_STYLES = {
        "pending": ("Pendiente", "#475569", "#e2e8f0"),
        "in_progress": ("En curso", "#1d4ed8", "#dbeafe"),
        "answered": ("Respondido", "#047857", "#d1fae5"),
        "partially_answered": ("Respondido parcialmente", "#b45309", "#fef3c7"),
        "blocked": ("Bloqueado", "#b91c1c", "#fee2e2"),
    }
    model = RequestedPoint
    form = RequestedPointAdminForm
    formset = RequestedPointInlineFormSet
    extra = 0
    ordering = ("order",)
    tab = True
    collapsible = True
    readonly_fields = ("status_badge",)

    @admin.display(description=_("estado"))
    def status_badge(self, obj):
        status_value = getattr(obj, "status", RequestedPoint.Status.PENDING)
        label, text_color, background = self.STATUS_BADGE_STYLES.get(
            status_value,
            (obj.get_status_display() if obj else "Pendiente", "#334155", "#e2e8f0"),
        )

        return format_html(
            '<span style="display:inline-flex;align-items:center;padding:0.35rem 0.75rem;border-radius:9999px;font-weight:700;font-size:0.875rem;line-height:1;color:{};background:{};">{}</span>',
            text_color,
            background,
            label,
        )

    fieldsets = (
        (
            _("Punto solicitado"),
            {
                "description": _(
                    "Cada punto solicitado pertenece solo a esta pericia y su orden se define dentro de este caso."
                ),
                "fields": (
                    "order",
                    "short_label",
                    "literal_text",
                    "status_badge",
                    "notes",
                    "metadata",
                )
            },
        ),
    )


class EvidenceItemInline(StackedInline):
    model = EvidenceItem
    form = EvidenceItemAdminForm
    extra = 0
    tab = True
    collapsible = True
    readonly_fields = ("evidence_files_summary",)

    @admin.display(description=_("archivos de evidencia"))
    def evidence_files_summary(self, obj):
        if obj is None or obj.pk is None:
            return _(
                "Se resuelven automaticamente desde la fuente primaria seleccionada para este dispositivo."
            )

        count = obj.evidence_files.count()
        return format_html(
            "<strong>{}</strong><br><span style='color:#64748b;'>"
            "Resueltos automaticamente desde la fuente primaria del dispositivo."
            "</span>",
            _("{} archivo(s) vinculados").format(count),
        )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "device_template",
                    "label",
                    "role",
                    "acquisition_status",
                    "source_path",
                    "supporting_source_paths",
                    "parent_item",
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
            },
        ),
    )


class ReportSectionInline(StackedInline):
    model = ReportSection
    form = ReportSectionAdminForm
    extra = 0
    ordering = ("order",)
    tab = True
    collapsible = True
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "order",
                    "section_type",
                    "title",
                    "content",
                    "structured_data",
                )
            },
        ),
    )


@admin.register(PericiaCaseProxy)
class PericiaCaseAdmin(ModelAdmin):
    form = PericiaCaseAdminForm
    STATUS_BADGE_STYLES = {
        "intake": ("Ingreso", "#475569", "#e2e8f0"),
        "evidence_registered": ("Evidencia registrada", "#1d4ed8", "#dbeafe"),
        "analysis_in_progress": ("Analisis en curso", "#7c3aed", "#ede9fe"),
        "report_in_progress": ("Informe en curso", "#b45309", "#fef3c7"),
        "completed": ("Completado", "#047857", "#d1fae5"),
        "blocked": ("Bloqueado", "#b91c1c", "#fee2e2"),
    }
    list_display = (
        "case_reference",
        "authority_name",
        "jurisdiction",
        "status",
        "report_date",
    )
    list_filter = ("status", "jurisdiction")
    search_fields = ("case_reference", "title", "authority_name", "authority_unit")
    inlines = [
        RequestedPointInline,
        EvidenceItemInline,
        ReportSectionInline,
    ]
    list_filter_submit = True
    warn_unsaved_form = True

    class Media:
        js = (
            "dfir_cases/inline_auto_expand.js",
            "dfir_cases/evidence_item_inline.js",
            "dfir_evidence/mounted_path_autocomplete.js",
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/seed-device-types/",
                self.admin_site.admin_view(self.seed_device_types_view),
                name="dfir_cases_periciacaseproxy_seed_device_types",
            ),
            path(
                "<path:object_id>/seed-analysis-plans/",
                self.admin_site.admin_view(self.seed_analysis_plans_view),
                name="dfir_cases_periciacaseproxy_seed_analysis_plans",
            ),
            path(
                "<path:object_id>/run-ready-analysis-plans/",
                self.admin_site.admin_view(self.run_ready_analysis_plans_view),
                name="dfir_cases_periciacaseproxy_run_ready_analysis_plans",
            ),
        ]
        return custom_urls + urls

    def seed_device_types_view(self, request, object_id):
        case = self.get_object(request, object_id)
        if case is None:
            messages.error(request, "No se encontro el caso pericial solicitado.")
            changelist_url = reverse(
                "admin:dfir_cases_periciacaseproxy_changelist",
                current_app=self.admin_site.name,
            )
            return HttpResponseRedirect(changelist_url)

        if case.evidence_items.exists():
            messages.warning(
                request,
                "Este caso ya tiene elementos de evidencia cargados. Usa las plantillas dentro de cada dispositivo existente en lugar de generar un lote nuevo.",
            )
            change_url = reverse(
                "admin:dfir_cases_periciacaseproxy_change",
                args=[case.pk],
                current_app=self.admin_site.name,
            )
            return HttpResponseRedirect(
                f"{change_url}?_active_tab=Elementos de evidencia"
            )

        call_command("seed_device_types", "--case-id", str(case.pk))
        messages.success(
            request,
            "Se aplico la carga guiada de tipos de dispositivo para este caso.",
        )
        change_url = reverse(
            "admin:dfir_cases_periciacaseproxy_change",
            args=[case.pk],
            current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(f"{change_url}?_active_tab=Elementos de evidencia")

    def seed_analysis_plans_view(self, request, object_id):
        case = self.get_object(request, object_id)
        if case is None:
            messages.error(request, "No se encontro el caso pericial solicitado.")
            changelist_url = reverse(
                "admin:dfir_cases_periciacaseproxy_changelist",
                current_app=self.admin_site.name,
            )
            return HttpResponseRedirect(changelist_url)

        call_command("seed_analysis_plans", "--case-id", str(case.pk))
        messages.success(
            request,
            "Se genero un plan inicial por cada punto solicitado sin plan asociado.",
        )
        analysis_url = reverse(
            "admin:dfir_analysis_analysisplanproxy_changelist",
            current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(f"{analysis_url}?q={case.case_reference}")

    def run_ready_analysis_plans_view(self, request, object_id):
        case = self.get_object(request, object_id)
        if case is None:
            messages.error(request, "No se encontro el caso pericial solicitado.")
            changelist_url = reverse(
                "admin:dfir_cases_periciacaseproxy_changelist",
                current_app=self.admin_site.name,
            )
            return HttpResponseRedirect(changelist_url)

        plans = list(
            case.analysis_plans.select_related("requested_point", "pericia_point").order_by(
                "requested_point__order",
                "id",
            )
        )
        launched = 0
        completed_now = 0
        queued_now = 0
        omitted_incomplete = 0
        omitted_active = 0
        omitted_completed = 0
        omitted_failed = 0
        omitted_skipped = 0

        for plan in plans:
            state = analysis_plan_operator_state(plan)
            key = state["key"]
            if key == "ready":
                try:
                    execution = self._launch_analysis_plan(plan)
                except Exception as exc:
                    messages.error(
                        request,
                        f"No se pudo ejecutar el plan '{plan}': {exc}",
                    )
                    continue
                launched += 1
                if execution.status == PericiaExecution.Status.COMPLETED:
                    completed_now += 1
                else:
                    queued_now += 1
                continue
            if key in {"queued", "running"}:
                omitted_active += 1
            elif key == "completed":
                omitted_completed += 1
            elif key == "completed_with_observations":
                omitted_completed += 1
            elif key == "failed":
                omitted_failed += 1
            elif key == "omitted":
                omitted_skipped += 1
            else:
                omitted_incomplete += 1

        if launched:
            messages.success(
                request,
                "Se lanzaron {} plan(es): {} completado(s) en el momento y {} encolado(s).".format(
                    launched,
                    completed_now,
                    queued_now,
                ),
            )
        else:
            messages.info(
                request,
                "No habia planes listos para ejecutar en este caso.",
            )

        messages.info(
            request,
            "Omitidos: incompletos={} · activos={} · completados={} · fallidos={} · omitidos={}".format(
                omitted_incomplete,
                omitted_active,
                omitted_completed,
                omitted_failed,
                omitted_skipped,
            ),
        )
        change_url = reverse(
            "admin:dfir_cases_periciacaseproxy_change",
            args=[case.pk],
            current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(change_url)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if "status_badge" not in readonly_fields:
            readonly_fields.append("status_badge")
        if "guided_actions" not in readonly_fields:
            readonly_fields.append("guided_actions")
        return readonly_fields

    @admin.display(description=_("estado"))
    def status_badge(self, obj):
        if obj is None:
            label, text_color, background = self.STATUS_BADGE_STYLES["intake"]
        else:
            status_value = obj.status or "intake"
            label, text_color, background = self.STATUS_BADGE_STYLES.get(
                status_value,
                (obj.get_status_display(), "#334155", "#e2e8f0"),
            )

        return format_html(
            '<span style="display:inline-flex;align-items:center;padding:0.35rem 0.75rem;border-radius:9999px;font-weight:700;font-size:0.875rem;line-height:1;color:{};background:{};">{}</span>',
            text_color,
            background,
            label,
        )

    @admin.display(description=_("acciones guiadas"))
    def guided_actions(self, obj):
        if obj is None:
            return _("Guarda el caso para habilitar la carga guiada de tipos de dispositivo.")

        workflow = build_case_workflow(obj)
        seed_url = reverse(
            "admin:dfir_cases_periciacaseproxy_seed_device_types",
            args=[obj.pk],
            current_app=self.admin_site.name,
        )
        seed_analysis_url = reverse(
            "admin:dfir_cases_periciacaseproxy_seed_analysis_plans",
            args=[obj.pk],
            current_app=self.admin_site.name,
        )
        run_ready_url = reverse(
            "admin:dfir_cases_periciacaseproxy_run_ready_analysis_plans",
            args=[obj.pk],
            current_app=self.admin_site.name,
        )
        current_stage = workflow["current_stage"]
        next_stage = workflow["next_stage"]
        stage_markup = []
        execution_summary = workflow["analysis_execution_summary"]
        plan_summary = analysis_plan_operational_summary(obj)
        for stage in workflow["stages"]:
            if stage["complete"]:
                stage_color = "#047857"
                stage_background = "#d1fae5"
                prefix = "Completado"
            elif stage["blocked"]:
                stage_color = "#b91c1c"
                stage_background = "#fee2e2"
                prefix = "Bloqueado"
            else:
                stage_color = "#1d4ed8"
                stage_background = "#dbeafe"
                prefix = "Siguiente"
            blocker_text = stage["blockers"][0] if stage["blockers"] else stage["description"]
            stage_markup.append(
                format_html(
                    "<div style='display:flex;flex-direction:column;gap:0.2rem;padding:0.75rem 0.9rem;border:1px solid #e2e8f0;border-radius:0.85rem;background:#fff;'>"
                    "<span style='font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.04em;color:{};background:{};display:inline-flex;align-self:flex-start;padding:0.2rem 0.55rem;border-radius:9999px;'>{}</span>"
                    "<strong style='font-size:0.92rem;color:#0f172a;'>{}</strong>"
                    "<span style='font-size:0.82rem;color:#64748b;'>{}</span>"
                    "</div>",
                    stage_color,
                    stage_background,
                    prefix,
                    stage["title"],
                    blocker_text,
                )
            )
        execution_markup = ""
        if execution_summary["total"]:
            latest = execution_summary["latest"]
            latest_text = ""
            if latest is not None:
                if latest["total_files"]:
                    latest_text = (
                        f"Ultima ejecucion: {latest['status']} · "
                        f"{latest['processed_files']}/{latest['total_files']} archivo(s) · "
                        f"{latest['findings_count']} hallazgo(s)."
                    )
                else:
                    latest_text = (
                        f"Ultima ejecucion: {latest['status']} · "
                        f"{latest['findings_count']} hallazgo(s)."
                    )
            execution_markup = format_html(
                "<div style='padding:0.9rem 1rem;border-radius:0.9rem;background:#eff6ff;border:1px solid #bfdbfe;'>"
                "<strong style='display:block;font-size:0.9rem;color:#1e3a8a;'>Ejecuciones de analisis</strong>"
                "<span style='display:block;margin-top:0.25rem;font-size:0.84rem;color:#1e40af;'>Pendientes: {} · En curso: {} · Completadas: {} · Fallidas: {}</span>"
                "<span style='display:block;margin-top:0.35rem;font-size:0.82rem;color:#475569;'>{}</span>"
                "</div>",
                execution_summary["pending"],
                execution_summary["running"],
                execution_summary["completed"],
                execution_summary["failed"],
                latest_text or "Todavia no hay detalle adicional para mostrar.",
            )
        analysis_controls_markup = format_html(
            "<div style='padding:0.9rem 1rem;border-radius:0.9rem;background:#f0fdf4;border:1px solid #bbf7d0;'>"
            "<strong style='display:block;font-size:0.9rem;color:#166534;'>Analisis listo para iniciar</strong>"
            "<span style='display:block;margin-top:0.25rem;font-size:0.84rem;color:#166534;'>Planes listos: {} · Activos: {} · Fallidos: {} · Completados: {} · Completados con observaciones: {}</span>"
            "<div style='display:flex;flex-wrap:wrap;gap:0.6rem;margin-top:0.65rem;'>"
            "<a href='{}' style='display:inline-flex;align-items:center;padding:0.45rem 0.8rem;border-radius:0.65rem;font-weight:700;font-size:0.85rem;line-height:1;color:#ffffff;background:#0f766e;'>Ejecutar planes listos</a>"
            "<a href='{}' style='display:inline-flex;align-items:center;padding:0.45rem 0.8rem;border-radius:0.65rem;font-weight:700;font-size:0.85rem;line-height:1;color:#0f172a;background:#e2e8f0;'>Ver planes de analisis</a>"
            "<a href='{}' style='display:inline-flex;align-items:center;padding:0.45rem 0.8rem;border-radius:0.65rem;font-weight:700;font-size:0.85rem;line-height:1;color:#0f172a;background:#e2e8f0;'>Ver ejecuciones</a>"
            "</div>"
            "</div>",
            plan_summary["ready"],
            plan_summary["active"],
            plan_summary["failed"],
            plan_summary["completed"],
            plan_summary["completed_with_observations"],
            run_ready_url,
            f"{reverse('admin:dfir_analysis_analysisplanproxy_changelist', current_app=self.admin_site.name)}?q={obj.case_reference}",
            f"{reverse('admin:dfir_analysis_periciaexecutionproxy_changelist', current_app=self.admin_site.name)}?q={obj.case_reference}",
        )
        return format_html(
            "<div style='display:flex;flex-direction:column;gap:1rem;'>"
            "<div style='padding:1rem 1.05rem;border-radius:1rem;background:#f8fafc;border:1px solid #e2e8f0;'>"
            "<div style='display:flex;flex-wrap:wrap;gap:0.75rem;align-items:center;justify-content:space-between;'>"
            "<div style='display:flex;flex-direction:column;gap:0.25rem;'>"
            "<span style='font-size:0.74rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;color:#475569;'>Progreso guiado</span>"
            "<strong style='font-size:1rem;color:#0f172a;'>Etapa actual: {}</strong>"
            "<span style='font-size:0.84rem;color:#475569;'>Siguiente etapa recomendada: {}</span>"
            "</div>"
            "<div style='display:flex;flex-direction:column;align-items:flex-end;gap:0.25rem;'>"
            "<strong style='font-size:1.1rem;color:#0f172a;'>{}/{} etapas</strong>"
            "<span style='font-size:0.84rem;color:#475569;'>{}% completo</span>"
            "</div>"
            "</div>"
            "</div>"
            "<div style='display:flex;flex-wrap:wrap;gap:0.6rem;'>"
            "<a href='{}' style='display:inline-flex;align-items:center;padding:0.45rem 0.8rem;border-radius:0.65rem;font-weight:700;font-size:0.85rem;line-height:1;color:#ffffff;background:#2563eb;'>Cargar tipos de dispositivo</a>"
            "<a href='{}' style='display:inline-flex;align-items:center;padding:0.45rem 0.8rem;border-radius:0.65rem;font-weight:700;font-size:0.85rem;line-height:1;color:#ffffff;background:#0f766e;'>Crear planes iniciales</a>"
            "<a href='{}' style='display:inline-flex;align-items:center;padding:0.45rem 0.8rem;border-radius:0.65rem;font-weight:700;font-size:0.85rem;line-height:1;color:#0f172a;background:#e2e8f0;'>Abrir siguiente etapa</a>"
            "</div>"
            "{}"
            "{}"
            "<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:0.65rem;'>{}</div>"
            "<span style='display:block;color:#64748b;font-size:0.82rem;'>1) Tipos de dispositivo: crea un lote base (HDD, SSD, USB, smartphone, imagen forense, VM, cloud). 2) Planes iniciales: crea un plan por punto solicitado que todavia no lo tenga.</span>"
            "</div>",
            current_stage["title"],
            next_stage["title"],
            workflow["completed_count"],
            workflow["total_count"],
            workflow["completion_ratio"],
            seed_url,
            seed_analysis_url,
            next_stage["resume_url"],
            analysis_controls_markup,
            execution_markup,
            format_html_join("", "{}", ((item,) for item in stage_markup)),
        )

    def _launch_analysis_plan(self, plan):
        targets = [str(target).strip() for target in (plan.analysis_targets or []) if str(target).strip()]
        if not targets:
            raise ValueError("El plan no tiene targets configurados.")

        device_result = self._resolve_device_analysis_result(plan, targets)
        plan.status = AnalysisPlan.Status.RUNNING
        plan.save(update_fields=["status"])
        try:
            execution_id = execute_pericia_point_task(
                plan.pericia_point_id,
                source_paths=targets,
                analysis_plan_id=plan.pk,
                device_analysis_result_id=device_result.pk if device_result else None,
            )
        except Exception:
            plan.status = AnalysisPlan.Status.PLANNED
            plan.save(update_fields=["status"])
            raise

        execution = PericiaExecution.objects.get(pk=execution_id)
        if execution.status == PericiaExecution.Status.COMPLETED:
            plan.status = AnalysisPlan.Status.COMPLETED
            plan.save(update_fields=["status"])
        return execution

    @staticmethod
    def _resolve_device_analysis_result(plan, targets):
        matched_items = []
        normalized_targets = {str(target).strip() for target in targets if str(target).strip()}
        for evidence_item in plan.pericia_case.evidence_items.all():
            source_path = str(evidence_item.source_path or "").strip()
            linked_paths = set(
                evidence_item.associated_evidence_files().values_list("source_path", flat=True)
            )
            if source_path and source_path in normalized_targets:
                matched_items.append(evidence_item)
                continue
            if linked_paths.intersection(normalized_targets):
                matched_items.append(evidence_item)

        unique_ids = list(dict.fromkeys(item.pk for item in matched_items))
        if len(unique_ids) != 1:
            return None

        evidence_item = matched_items[0]
        device_result, _created = DeviceAnalysisResult.objects.get_or_create(
            pericia_case=plan.pericia_case,
            evidence_item=evidence_item,
        )
        return device_result

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        case = self.get_object(request, object_id)
        if case is not None:
            extra_context["guided_workflow"] = build_case_workflow(case)
        return super().change_view(request, object_id, form_url, extra_context)

    def response_change(self, request, obj):
        active_tab_label = str(request.POST.get("_active_tab_label") or "").strip()
        if "_addanother" in request.POST:
            url = reverse(
                "admin:dfir_cases_periciacaseproxy_change",
                args=[obj.pk],
                current_app=self.admin_site.name,
            )
            if active_tab_label:
                return HttpResponseRedirect(f"{url}?_active_tab={active_tab_label}")
            return HttpResponseRedirect(url)

        return super().response_change(request, obj)

    @staticmethod
    def _delete_case_graph(case):
        # 1) Remover respuestas y artefactos vinculados al caso
        RequestedPointResponse.objects.filter(pericia_case=case).delete()
        PreservedArtifact.objects.filter(pericia_case=case).delete()

        # 2) Remover ejecuciones asociadas a planes/resultados del caso
        PericiaExecution.objects.filter(
            Q(analysis_plan__pericia_case=case)
            | Q(device_analysis_result__pericia_case=case)
        ).delete()

        # 3) Remover planes/resultados del caso
        AnalysisPlan.objects.filter(pericia_case=case).delete()
        DeviceAnalysisResult.objects.filter(pericia_case=case).delete()

        # 4) Evitar bloqueo por parent_item=PROTECT dentro del mismo caso
        EvidenceItem.objects.filter(pericia_case=case).update(parent_item=None)
        EvidenceItem.objects.filter(pericia_case=case).delete()

        # 5) Eliminar puntos solicitados y finalmente el caso
        RequestedPoint.objects.filter(pericia_case=case).delete()
        case.delete()

    def delete_model(self, request, obj):
        with transaction.atomic():
            self._delete_case_graph(obj)

    def delete_queryset(self, request, queryset):
        with transaction.atomic():
            for case in queryset:
                self._delete_case_graph(case)

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        if obj is None:
            title, config = fieldsets[0]
            fields = list(config.get("fields", ()))
            if "initial_device_count" not in fields:
                fields.append("initial_device_count")
            fieldsets[0] = (title, {**config, "fields": tuple(fields)})
        return tuple(fieldsets)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        if change:
            return

        case = form.instance
        requested_count = int(form.cleaned_data.get("initial_device_count") or 0)
        if requested_count <= 0:
            return

        current_count = EvidenceItem.objects.filter(pericia_case=case).count()
        missing = max(0, requested_count - current_count)
        for _ in range(missing):
            EvidenceItem.objects.create(
                pericia_case=case,
                label=EvidenceItemAdminForm.next_device_label_for_case(case),
                role=EvidenceItem.Role.ORIGINAL_DEVICE,
                acquisition_status=EvidenceItem.AcquisitionStatus.IDENTIFIED,
            )

    fieldsets = (
        (
            _("Datos del caso"),
            {
                "fields": (
                    "case_reference",
                    "title",
                    "status_badge",
                    "guided_actions",
                    "summary",
                )
            },
        ),
        (
            _("Contexto judicial"),
            {
                "classes": ("tab",),
                "fields": (
                    "authority_name",
                    "authority_unit",
                    "jurisdiction",
                    "report_date",
                ),
            },
        ),
        (
            _("Perito"),
            {
                "classes": ("tab",),
                "fields": (
                    "analyst_name",
                    "analyst_badge",
                ),
            },
        ),
        (
            _("Metadata"),
            {
                "classes": ("tab",),
                "fields": ("metadata",),
            },
        ),
    )


@admin.register(PericiaDocumentProxy)
class PericiaDocumentAdmin(ModelAdmin):
    form = PericiaDocumentAdminForm
    list_display = ("title", "pericia_case", "document_type", "updated_at")
    list_filter = ("document_type",)
    search_fields = ("title", "file_path", "pericia_case__case_reference")
    list_filter_submit = True
    warn_unsaved_form = True


@admin.register(RequestedPointProxy)
class RequestedPointAdmin(ModelAdmin):
    STATUS_BADGE_STYLES = RequestedPointInline.STATUS_BADGE_STYLES
    form = RequestedPointAdminForm
    list_display = ("pericia_case", "order", "short_label", "status_badge")
    list_filter = ("status",)
    search_fields = ("short_label", "literal_text", "pericia_case__case_reference")
    ordering = ("pericia_case", "order")
    list_filter_submit = True
    warn_unsaved_form = True
    readonly_fields = ("status_badge",)
    fields = (
        "pericia_case",
        "order",
        "short_label",
        "literal_text",
        "status_badge",
        "notes",
        "metadata",
    )
    exclude = ("status",)

    @admin.display(description=_("estado"))
    def status_badge(self, obj):
        status_value = getattr(obj, "status", RequestedPoint.Status.PENDING)
        label, text_color, background = self.STATUS_BADGE_STYLES.get(
            status_value,
            (obj.get_status_display() if obj else "Pendiente", "#334155", "#e2e8f0"),
        )
        return format_html(
            '<span style="display:inline-flex;align-items:center;padding:0.25rem 0.65rem;border-radius:9999px;font-weight:700;font-size:0.8rem;line-height:1;color:{};background:{};">{}</span>',
            text_color,
            background,
            label,
        )
