from django.contrib import admin, messages
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from dfir_core.admin_forms import AnalysisPlanAdminForm, PericiaPointAdminForm
from dfir_pericia.models import DeviceAnalysisResult, PericiaExecution, RequestedPoint
from dfir_pericia.tasks import execute_pericia_point_task
from dfir_pericia.workflow import (
    analysis_plan_operator_state,
    execution_has_observations,
    latest_analysis_execution,
)

from .models import (
    AnalysisPlanProxy,
    DeviceAnalysisResultProxy,
    PericiaExecutionProxy,
    PericiaFindingProxy,
    PericiaPointProxy,
)


@admin.register(PericiaPointProxy)
class PericiaPointAdmin(ModelAdmin):
    form = PericiaPointAdminForm
    list_display = ("name", "point_family", "matching_mode", "enabled", "updated_at")
    list_filter = ("point_family", "matching_mode", "enabled")
    search_fields = ("name", "slug")
    list_filter_submit = True
    warn_unsaved_form = True

    def get_form(self, request, obj=None, change=False, **kwargs):
        base_form = super().get_form(request, obj, change=change, **kwargs)

        class RequestAwarePericiaPointForm(base_form):
            def __init__(self, *args, **inner_kwargs):
                inner_kwargs.setdefault("request", request)
                super().__init__(*args, **inner_kwargs)

        return RequestAwarePericiaPointForm

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "name-suggestions/",
                self.admin_site.admin_view(self.name_suggestions_view),
                name="dfir_analysis_periciapointproxy_name_suggestions",
            ),
        ]
        return custom_urls + urls

    def name_suggestions_view(self, request):
        raw_case_id = request.GET.get("case_id")
        query = str(request.GET.get("q") or "").strip().lower()
        try:
            case_id = int(raw_case_id) if raw_case_id not in (None, "") else None
        except (TypeError, ValueError):
            case_id = None

        results = []
        if case_id is not None:
            values: list[str] = []
            seen: set[str] = set()

            for point in RequestedPoint.objects.filter(pericia_case_id=case_id):
                candidate = str(point.short_label or point.literal_text or "").strip()
                if not candidate:
                    continue
                if query and query not in candidate.lower():
                    continue
                key = candidate.lower()
                if key in seen:
                    continue
                seen.add(key)
                values.append(candidate)

            for plan in AnalysisPlanProxy.objects.filter(
                pericia_case_id=case_id
            ).select_related("pericia_point"):
                candidate = str(getattr(plan.pericia_point, "name", "") or "").strip()
                if not candidate:
                    continue
                if query and query not in candidate.lower():
                    continue
                key = candidate.lower()
                if key in seen:
                    continue
                seen.add(key)
                values.append(candidate)

            results = [{"value": value, "label": value} for value in values]

        return JsonResponse({"results": results})


@admin.register(AnalysisPlanProxy)
class AnalysisPlanAdmin(ModelAdmin):
    form = AnalysisPlanAdminForm
    list_display = (
        "pericia_case",
        "requested_point",
        "pericia_point",
        "operator_state_badge",
        "playbook_taxonomy",
        "row_execution_action",
    )
    readonly_fields = (
        "analysis_workflow_order",
        "playbook_summary",
        "execution_actions",
        "latest_execution_summary",
    )
    fields = (
        "pericia_case",
        "requested_point",
        "pericia_point",
        "analysis_workflow_order",
        "label",
        "strategy_notes",
        "analysis_targets",
        "search_terms",
        "execution_actions",
        "structured_actions_json",
        "scope_snapshot",
        "status",
        "playbook_summary",
        "latest_execution_summary",
    )
    list_filter = ("status", "pericia_point__point_family")
    search_fields = (
        "label",
        "pericia_case__case_reference",
        "requested_point__literal_text",
    )
    list_filter_submit = True
    warn_unsaved_form = True

    @admin.display(description=_("orden recomendado del modulo"))
    def analysis_workflow_order(self, obj):
        return format_html(
            "<div style='display:flex;flex-direction:column;gap:0.4rem;'>"
            "<strong>{}</strong>"
            "<ol style='margin:0 0 0 1.1rem;'>"
            "<li>{}</li>"
            "<li>{}</li>"
            "<li>{}</li>"
            "<li>{}</li>"
            "</ol>"
            "<span style='color:#64748b;'>{}</span>"
            "</div>",
            _("Orden recomendado en Administracion de Analisis"),
            _("1. Definir o revisar Puntos de pericia reutilizables."),
            _("2. Crear Planes de analisis por caso y por punto solicitado."),
            _("3. Ejecutar el plan sobre las ubicaciones objetivo definidas."),
            _("4. Revisar Ejecuciones y Resultados por dispositivo."),
            _(
                "Este orden acompaña el workflow del caso: evidencia cargada, planificacion, ejecucion y revision tecnica antes del informe."
            ),
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "requested-points/",
                self.admin_site.admin_view(self.requested_points_view),
                name="dfir_analysis_analysisplanproxy_requested_points",
            ),
            path(
                "<path:object_id>/run-point/",
                self.admin_site.admin_view(self.run_point_view),
                name="dfir_analysis_analysisplanproxy_run_point",
            ),
        ]
        return custom_urls + urls

    OPERATOR_STATE_STYLES = {
        "incomplete": ("#92400e", "#fef3c7"),
        "ready": ("#0f766e", "#ccfbf1"),
        "queued": ("#92400e", "#fef3c7"),
        "running": ("#1d4ed8", "#dbeafe"),
        "completed": ("#047857", "#d1fae5"),
        "completed_with_observations": ("#b45309", "#fef3c7"),
        "failed": ("#b91c1c", "#fee2e2"),
        "omitted": ("#475569", "#e2e8f0"),
    }

    def requested_points_view(self, request):
        raw_case_id = request.GET.get("case_id")
        try:
            case_id = int(raw_case_id) if raw_case_id not in (None, "") else None
        except (TypeError, ValueError):
            case_id = None

        results = []
        if case_id is not None:
            queryset = RequestedPoint.objects.filter(pericia_case_id=case_id)
            results = [
                {
                    "id": point.pk,
                    "label": str(point),
                }
                for point in queryset
            ]
        return JsonResponse({"results": results})

    @admin.display(description=_("taxonomia"))
    def playbook_taxonomy(self, obj):
        labels = [str(item.get("label") or "").strip() for item in obj.taxonomy_groups]
        labels = [label for label in labels if label]
        if not labels:
            return _("Sin clasificar")
        return ", ".join(labels[:2])

    @admin.display(description=_("playbook del plan"))
    def playbook_summary(self, obj):
        if obj is None or obj.pk is None:
            return _(
                "Guarda el plan para ver la taxonomia y las acciones ejecutables derivadas del punto solicitado."
            )

        taxonomy = obj.taxonomy_groups
        actions = obj.playbook_actions
        if taxonomy:
            taxonomy_markup = format_html_join(
                "",
                (
                    "<span style='display:inline-flex;align-items:center;padding:0.25rem 0.55rem;"
                    "border-radius:9999px;background:#e2e8f0;color:#0f172a;font-weight:700;"
                    "font-size:0.72rem;line-height:1;margin:0 0.35rem 0.35rem 0;'>{}</span>"
                ),
                ((item.get("label", ""),) for item in taxonomy),
            )
        else:
            taxonomy_markup = format_html(
                "<span style='color:#64748b;'>{}</span>",
                _("Sin taxonomia derivada todavia."),
            )
        if actions:
            actions_markup = format_html_join(
                "",
                (
                    "<li><strong>{}</strong><br>"
                    "<span style='color:#475569;'>carpetas: {}</span><br>"
                    "<span style='color:#475569;'>tipos: {}</span><br>"
                    "<span style='color:#475569;'>criterio: {} {}</span>"
                    "</li>"
                ),
                (
                    (
                        action.get("label", ""),
                        ", ".join(action.get("path_scope", []) or ["(sin definir)"]),
                        ", ".join(action.get("file_kinds", []) or ["*"]),
                        str((action.get("search_criteria") or {}).get("mode") or "any"),
                        ", ".join((action.get("search_criteria") or {}).get("terms", []) or ["(sin terminos)"]),
                    )
                    for action in actions
                ),
            )
        else:
            actions_markup = format_html(
                "<li>{}</li>",
                _("Todavia no hay acciones definidas para este plan."),
            )

        return format_html(
            "<div style='display:flex;flex-direction:column;gap:0.65rem;'>"
            "<div><strong>{}</strong><div style='margin-top:0.35rem;'>{}</div></div>"
            "<div><strong>{}</strong><ol style='margin:0.35rem 0 0 1.2rem;'>{}</ol></div>"
            "<div style='color:#64748b;'>{}</div>"
            "</div>",
            _("Familias operativas"),
            taxonomy_markup,
            _("Acciones ejecutables derivadas"),
            actions_markup,
            _(
                "Este plan traduce el punto solicitado del caso a un playbook de acciones reutilizables y ejecutables."
            ),
        )

    @admin.display(description=_("ejecucion guiada"))
    def execution_actions(self, obj):
        if obj is None or obj.pk is None:
            return _("Guarda el plan para habilitar la ejecucion guiada.")

        state = analysis_plan_operator_state(obj)
        if state["key"] == "incomplete":
            return format_html(
                "<div style='display:flex;flex-direction:column;gap:0.45rem;'>"
                "<span style='color:#b45309;font-weight:600;'>{}</span>"
                "<span style='color:#64748b;'>{}</span>"
                "</div>",
                _("Plan incompleto"),
                _(
                    "Carga al menos una carpeta o archivo de analisis y un punto de pericia para habilitar la ejecucion."
                ),
            )

        action = self._row_action_data(obj)
        return format_html(
            "<div style='display:flex;flex-direction:column;gap:0.55rem;'>"
            "{}"
            "<span style='color:#64748b;'>{}</span>"
            "</div>",
            self._row_action_link(action),
            action["help_text"],
        )

    @admin.display(description=_("ultima ejecucion"))
    def latest_execution_summary(self, obj):
        if obj is None or obj.pk is None:
            return _("Todavia no hay ejecuciones asociadas.")

        execution = self._latest_execution(obj)
        if execution is None:
            return _("Todavia no hay ejecuciones asociadas.")

        execution_url = reverse(
            "admin:dfir_analysis_periciaexecutionproxy_change",
            args=[execution.pk],
            current_app=self.admin_site.name,
        )
        visible_state = analysis_plan_operator_state(obj, latest_execution=execution)
        state_color = self.OPERATOR_STATE_STYLES.get(visible_state["key"], ("#334155", "#e2e8f0"))
        return format_html(
            "<div style='display:flex;flex-direction:column;gap:0.35rem;'>"
            "<span style='display:inline-flex;align-items:center;padding:0.2rem 0.55rem;border-radius:9999px;font-weight:700;font-size:0.72rem;line-height:1;color:{};background:{};width:max-content;'>{}</span>"
            "<a href='{}' style='font-weight:700;color:#1d4ed8;text-decoration:none;'>{}</a>"
            "<span style='color:#64748b;'>{}</span>"
            "</div>",
            state_color[0],
            state_color[1],
            visible_state["label"],
            execution_url,
            _("Ver ejecucion #{}").format(execution.pk),
            self._execution_progress_text(execution),
        )

    @admin.display(description=_("estado operativo"))
    def operator_state_badge(self, obj):
        state = analysis_plan_operator_state(obj)
        colors = self.OPERATOR_STATE_STYLES.get(state["key"], ("#334155", "#e2e8f0"))
        return format_html(
            "<span style='display:inline-flex;align-items:center;padding:0.25rem 0.65rem;"
            "border-radius:9999px;font-weight:700;font-size:0.8rem;line-height:1;color:{};"
            "background:{};'>{}</span>",
            colors[0],
            colors[1],
            state["label"],
        )

    @admin.display(description=_("accion"))
    def row_execution_action(self, obj):
        return self._row_action_link(self._row_action_data(obj))

    def run_point_view(self, request, object_id):
        plan = self.get_object(request, object_id)
        if plan is None:
            messages.error(request, "No se encontro el plan de analisis solicitado.")
            changelist_url = reverse(
                "admin:dfir_analysis_analysisplanproxy_changelist",
                current_app=self.admin_site.name,
            )
            return HttpResponseRedirect(changelist_url)

        targets = [str(target).strip() for target in (plan.analysis_targets or []) if str(target).strip()]
        if not targets:
            messages.warning(
                request,
                "Este plan no tiene targets configurados para ejecutar el analisis.",
            )
            change_url = reverse(
                "admin:dfir_analysis_analysisplanproxy_change",
                args=[plan.pk],
                current_app=self.admin_site.name,
            )
            return HttpResponseRedirect(change_url)

        device_result = self._resolve_device_analysis_result(plan, targets)
        plan.status = AnalysisPlanProxy.Status.RUNNING
        plan.save(update_fields=["status"])
        try:
            execution_id = execute_pericia_point_task(
                plan.pericia_point_id,
                source_paths=targets,
                analysis_plan_id=plan.pk,
                device_analysis_result_id=device_result.pk if device_result else None,
            )
        except Exception as exc:
            plan.status = AnalysisPlanProxy.Status.PLANNED
            plan.save(update_fields=["status"])
            messages.error(
                request,
                f"No se pudo ejecutar el punto de pericia: {exc}",
            )
            change_url = reverse(
                "admin:dfir_analysis_analysisplanproxy_change",
                args=[plan.pk],
                current_app=self.admin_site.name,
            )
            return HttpResponseRedirect(change_url)

        execution = PericiaExecution.objects.get(pk=execution_id)
        if execution.status == PericiaExecution.Status.COMPLETED:
            plan.status = AnalysisPlanProxy.Status.COMPLETED
            plan.save(update_fields=["status"])
            messages.success(
                request,
                "Ejecucion completada: "
                f"{execution.analyzed_files_count} archivo(s) analizados, "
                f"{execution.findings_count} hallazgo(s).",
            )
            execution_url = reverse(
                "admin:dfir_analysis_periciaexecutionproxy_change",
                args=[execution.pk],
                current_app=self.admin_site.name,
            )
            return HttpResponseRedirect(execution_url)

        messages.info(
            request,
            "Analisis encolado. El plan ya muestra el estado y el avance de la ejecucion.",
        )
        change_url = reverse(
            "admin:dfir_analysis_analysisplanproxy_change",
            args=[plan.pk],
            current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(change_url)

    def _latest_execution(self, obj):
        return latest_analysis_execution(obj)

    def _execution_progress_text(self, execution):
        progress = dict((execution.engine_metadata or {}).get("progress") or {})
        processed = int(progress.get("processed_files") or 0)
        total = int(progress.get("total_files") or 0)
        if execution.status == PericiaExecution.Status.PENDING:
            return _("En cola: {} archivo(s) preparados para analizar.").format(total)
        if execution.status == PericiaExecution.Status.RUNNING:
            if total:
                return _(
                    "En curso: {} de {} archivo(s) procesados, {} hallazgo(s)."
                ).format(processed, total, execution.findings_count)
            return _("En curso: la ejecucion ya fue iniciada.")
        if execution.status == PericiaExecution.Status.FAILED:
            error = str((execution.engine_metadata or {}).get("error") or "").strip()
            if error:
                return _("Fallo: {}").format(error)
            return _("La ejecucion fallo antes de completarse.")
        if execution_has_observations(execution):
            return _(
                "{} archivo(s) analizados, {} hallazgo(s), {} no soportado(s), {} fallido(s)."
            ).format(
                execution.analyzed_files_count,
                execution.findings_count,
                execution.unsupported_files_count,
                execution.failed_files_count,
            )
        return _(
            "{} archivo(s) analizados, {} hallazgo(s), {} no soportado(s), {} fallido(s)."
        ).format(
            execution.analyzed_files_count,
            execution.findings_count,
            execution.unsupported_files_count,
            execution.failed_files_count,
        )

    def _row_action_data(self, obj):
        state = analysis_plan_operator_state(obj)
        latest_execution = self._latest_execution(obj)
        run_url = reverse(
            "admin:dfir_analysis_analysisplanproxy_run_point",
            args=[obj.pk],
            current_app=self.admin_site.name,
        )
        if state["key"] == "incomplete":
            return {
                "label": _("Completar plan"),
                "url": reverse(
                    "admin:dfir_analysis_analysisplanproxy_change",
                    args=[obj.pk],
                    current_app=self.admin_site.name,
                ),
                "background": "#e2e8f0",
                "color": "#334155",
                "help_text": _("Este plan aun no tiene el alcance minimo para ejecutarse."),
            }
        if state["key"] in {"queued", "running"} and latest_execution is not None:
            return {
                "label": _("Ver ejecucion"),
                "url": reverse(
                    "admin:dfir_analysis_periciaexecutionproxy_change",
                    args=[latest_execution.pk],
                    current_app=self.admin_site.name,
                ),
                "background": "#e2e8f0",
                "color": "#0f172a",
                "help_text": self._execution_progress_text(latest_execution),
            }
        if state["key"] == "failed":
            return {
                "label": _("Reintentar"),
                "url": run_url,
                "background": "#b91c1c",
                "color": "#fff",
                "help_text": _("La ultima ejecucion fallo. Puedes relanzar este plan manualmente."),
            }
        if state["key"] in {"completed", "completed_with_observations"}:
            return {
                "label": _("Reejecutar"),
                "url": run_url,
                "background": "#0f766e",
                "color": "#fff",
                "help_text": _("Relanza este plan sobre los mismos targets configurados."),
            }
        return {
            "label": _("Ejecutar este plan"),
            "url": run_url,
            "background": "#0f766e",
            "color": "#fff",
            "help_text": _("Usa los targets del plan para ejecutar las acciones del playbook y generar hallazgos."),
        }

    @staticmethod
    def _row_action_link(action):
        return format_html(
            "<a href='{}' style='display:inline-flex;align-items:center;justify-content:center;"
            "padding:0.55rem 0.8rem;border-radius:0.75rem;background:{};color:{};"
            "font-weight:700;text-decoration:none;width:max-content;'>{}</a>",
            action["url"],
            action["background"],
            action["color"],
            action["label"],
        )

    def _resolve_device_analysis_result(self, plan, targets):
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


@admin.register(DeviceAnalysisResultProxy)
class DeviceAnalysisResultAdmin(ModelAdmin):
    list_display = ("evidence_item", "pericia_case", "status", "finished_at")
    list_filter = ("status",)
    search_fields = ("evidence_item__label", "pericia_case__case_reference")
    list_filter_submit = True
    warn_unsaved_form = True


@admin.register(PericiaExecutionProxy)
class PericiaExecutionAdmin(ModelAdmin):
    list_display = (
        "pericia_point",
        "analysis_plan",
        "device_analysis_result",
        "status",
        "analyzed_files_count",
        "findings_count",
        "started_at",
    )
    readonly_fields = (
        "pericia_point",
        "analysis_plan",
        "device_analysis_result",
        "status",
        "scope_snapshot",
        "engine_metadata",
        "analyzed_files_count",
        "unsupported_files_count",
        "failed_files_count",
        "matched_files_count",
        "findings_count",
        "unsupported_files",
        "failed_files",
        "started_at",
        "finished_at",
    )
    fields = readonly_fields
    list_filter = ("status", "pericia_point__point_family")
    list_filter_submit = True
    search_fields = (
        "pericia_point__name",
        "analysis_plan__label",
        "analysis_plan__pericia_case__case_reference",
        "device_analysis_result__evidence_item__label",
    )
    warn_unsaved_form = True

    def has_add_permission(self, request):
        return False


@admin.register(PericiaFindingProxy)
class PericiaFindingAdmin(ModelAdmin):
    list_display = (
        "pericia_point",
        "device_analysis_result",
        "evidence_file",
        "matched_value",
        "confidence",
    )
    search_fields = ("matched_value", "context", "evidence_file__source_path")
    warn_unsaved_form = True
