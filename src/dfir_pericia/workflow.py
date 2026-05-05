from __future__ import annotations

from dataclasses import dataclass

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import (
    AnalysisPlan,
    DeviceAnalysisResult,
    PericiaCase,
    PericiaExecution,
    PericiaPoint,
    REPORT_MINIMUM_SECTION_TYPES,
    ReportSection,
    RequestedPointResponse,
    report_section_has_substantive_content,
)


@dataclass(frozen=True)
class WorkflowStageDefinition:
    key: str
    title: str
    description: str
    resume_url_name: str
    add_url_name: str | None = None


STAGE_DEFINITIONS: tuple[WorkflowStageDefinition, ...] = (
    WorkflowStageDefinition(
        key="case",
        title=_("Caso"),
        description=_("Definir la referencia, el organismo y el contexto base."),
        resume_url_name="admin:dfir_cases_periciacaseproxy_changelist",
        add_url_name="admin:dfir_cases_periciacaseproxy_add",
    ),
    WorkflowStageDefinition(
        key="documents",
        title=_("Documentos"),
        description=_("Adjuntar oficio, requerimiento y demas documentos fuente."),
        resume_url_name="admin:dfir_cases_periciacaseproxy_change",
    ),
    WorkflowStageDefinition(
        key="requested_points",
        title=_("Puntos solicitados"),
        description=_("Registrar el texto literal de cada punto requerido."),
        resume_url_name="admin:dfir_cases_periciacaseproxy_change",
    ),
    WorkflowStageDefinition(
        key="evidence",
        title=_("Evidencia"),
        description=_("Incorporar dispositivos, imagenes forenses y copias de trabajo."),
        resume_url_name="admin:dfir_cases_periciacaseproxy_change",
    ),
    WorkflowStageDefinition(
        key="analysis_plans",
        title=_("Planes de analisis"),
        description=_("Traducir cada punto solicitado a un playbook de acciones ejecutables."),
        resume_url_name="admin:dfir_analysis_analysisplanproxy_changelist",
    ),
    WorkflowStageDefinition(
        key="device_results",
        title=_("Resultados por dispositivo"),
        description=_("Documentar el estado tecnico y los hallazgos por evidencia."),
        resume_url_name="admin:dfir_analysis_deviceanalysisresultproxy_changelist",
    ),
    WorkflowStageDefinition(
        key="responses",
        title=_("Respuestas por punto"),
        description=_("Consolidar la respuesta tecnica con hallazgos y rationale."),
        resume_url_name="admin:dfir_reports_requestedpointresponseproxy_changelist",
    ),
    WorkflowStageDefinition(
        key="report",
        title=_("Informe"),
        description=_("Armar secciones, informacion obtenida y conclusiones."),
        resume_url_name="admin:dfir_reports_reportsectionproxy_changelist",
    ),
    WorkflowStageDefinition(
        key="final_review",
        title=_("Revision final"),
        description=_("Revisar consistencia del informe antes de entregarlo."),
        resume_url_name="admin:dfir_cases_periciacaseproxy_change",
    ),
)

HOME_STAGE_MAP = {
    "case_setup": {
        "step": _("Paso 1"),
        "title": _("Iniciar nueva pericia"),
        "description": _(
            "Crear el caso pericial y dejar cargado el contexto base del expediente."
        ),
        "stages": ("case", "documents", "requested_points"),
        "icon": "folder_managed",
        "url_name": "admin:dfir_cases_periciacaseproxy_add",
    },
    "evidence": {
        "step": _("Paso 2"),
        "title": _("Registrar evidencia"),
        "description": _(
            "Incorporar dispositivos, imagenes forenses, copias de trabajo y fuentes asociadas."
        ),
        "stages": ("evidence",),
        "icon": "inventory_2",
        "url_name": "admin:dfir_evidence_evidenceitemproxy_changelist",
    },
    "analysis": {
        "step": _("Paso 3"),
        "title": _("Planificar y ejecutar analisis"),
        "description": _(
            "Traducir puntos solicitados a playbooks de acciones tecnicas y documentar resultados."
        ),
        "stages": ("analysis_plans", "device_results", "responses"),
        "icon": "manage_search",
        "url_name": "admin:dfir_analysis_analysisplanproxy_changelist",
    },
    "report": {
        "step": _("Paso 4"),
        "title": _("Cerrar informe"),
        "description": _(
            "Armar secciones, consolidar conclusiones y revisar la entrega final."
        ),
        "stages": ("report", "final_review"),
        "icon": "description",
        "url_name": "admin:dfir_reports_reportsectionproxy_changelist",
    },
}


def _case_url(case: PericiaCase) -> str:
    return reverse("admin:dfir_cases_periciacaseproxy_change", args=[case.pk])


def _resolve_stage_url(definition: WorkflowStageDefinition, case: PericiaCase) -> str:
    if definition.resume_url_name == "admin:dfir_cases_periciacaseproxy_change":
        return _case_url(case)

    url = reverse(definition.resume_url_name)
    query = f"?q={case.case_reference}"
    return f"{url}{query}"


def _has_useful_documents(case: PericiaCase) -> bool:
    documents = case.documents.exclude(title="")
    return (
        documents.filter(file_path__gt="").exists()
        or documents.filter(extracted_text__gt="").exists()
        or documents.exists()
    )


def _has_requested_points(case: PericiaCase) -> bool:
    return case.requested_points.exclude(literal_text="").exists()


def _has_evidence(case: PericiaCase) -> bool:
    meaningful_statuses = {
        "received",
        "acquired",
        "partial",
        "not_acquired",
        "not_accessible",
    }
    for item in case.evidence_items.all():
        if str(item.source_path or "").strip():
            return True
        if item.evidence_file_id or item.evidence_files.exists():
            return True
        if item.acquisition_status in meaningful_statuses:
            return True
    return False


def _analysis_stage(case: PericiaCase) -> tuple[bool, list[str]]:
    blockers: list[str] = []
    if not _has_requested_points(case):
        blockers.append(_("Primero carga al menos un punto solicitado con texto util."))
    if not _has_evidence(case):
        blockers.append(_("Primero registra al menos un elemento de evidencia."))
    if not PericiaPoint.objects.filter(enabled=True).exists():
        blockers.append(
            _(
                "No hay puntos de pericia reutilizables habilitados en el catalogo para planificar."
            )
        )

    requested_ids = set(case.requested_points.values_list("pk", flat=True))
    planned_ids = set(case.analysis_plans.values_list("requested_point_id", flat=True))
    playbook_ready_ids = set()
    for plan in case.analysis_plans.select_related("requested_point", "pericia_point"):
        actions = plan.playbook_actions
        if not actions:
            continue
        if all(
            isinstance(action, dict)
            and action.get("path_scope")
            and action.get("file_kinds")
            and isinstance(action.get("search_criteria"), dict)
            for action in actions
        ):
            playbook_ready_ids.add(plan.requested_point_id)
    if planned_ids and planned_ids != playbook_ready_ids:
        blockers.append(
            _(
                "Al menos un plan todavia no explicita acciones ejecutables con carpeta, tipo de archivo y criterio."
            )
        )
    complete = bool(requested_ids) and requested_ids.issubset(playbook_ready_ids)
    return complete, blockers


def _device_results_stage(case: PericiaCase) -> tuple[bool, list[str]]:
    blockers: list[str] = []
    evidence_ids = set(case.evidence_items.values_list("pk", flat=True))
    if not evidence_ids:
        blockers.append(_("No hay evidencia registrada para documentar resultados."))
        return False, blockers

    result_map = {
        result.evidence_item_id: result.status
        for result in case.device_analysis_results.all()
    }
    if not result_map:
        return False, blockers

    pending_ids = [
        evidence_id
        for evidence_id in evidence_ids
        if result_map.get(evidence_id) in {None, DeviceAnalysisResult.Status.PENDING}
    ]
    if pending_ids:
        return False, blockers
    return not pending_ids, blockers


def _responses_stage(case: PericiaCase) -> tuple[bool, list[str]]:
    blockers: list[str] = []
    point_ids = set(case.requested_points.values_list("pk", flat=True))
    if not point_ids:
        blockers.append(_("No hay puntos solicitados cargados para responder."))
        return False, blockers

    response_map = {
        response.requested_point_id: response
        for response in case.requested_point_responses.all()
    }
    missing = [point_id for point_id in point_ids if point_id not in response_map]

    incomplete = []
    for point_id, response in response_map.items():
        if point_id not in point_ids:
            continue
        if response.status == RequestedPointResponse.Status.BLOCKED:
            blockers.append(
                _("Existe al menos una respuesta bloqueada que requiere seguimiento.")
            )
            continue
        has_meaningful_text = bool(
            response.summary.strip()
            and (response.rationale.strip() or response.technical_observations.strip())
        )
        if response.status not in {
            RequestedPointResponse.Status.ANSWERED,
            RequestedPointResponse.Status.PARTIALLY_ANSWERED,
        } or not has_meaningful_text:
            incomplete.append(point_id)
    if incomplete:
        return False, blockers

    return not missing and not incomplete and not any(
        "bloqueada" in str(message).lower() for message in blockers
    ), blockers


def _analysis_execution_summary(case: PericiaCase) -> dict:
    executions = list(
        PericiaExecution.objects.filter(analysis_plan__pericia_case=case)
        .select_related("analysis_plan")
        .order_by("-started_at", "-id")
    )
    summary = {
        "total": len(executions),
        "pending": 0,
        "running": 0,
        "completed": 0,
        "failed": 0,
        "active": False,
        "latest": None,
    }
    for execution in executions:
        if execution.status == PericiaExecution.Status.PENDING:
            summary["pending"] += 1
        elif execution.status == PericiaExecution.Status.RUNNING:
            summary["running"] += 1
        elif execution.status == PericiaExecution.Status.COMPLETED:
            summary["completed"] += 1
        elif execution.status == PericiaExecution.Status.FAILED:
            summary["failed"] += 1

    summary["active"] = summary["pending"] > 0 or summary["running"] > 0
    if executions:
        latest = executions[0]
        progress = dict((latest.engine_metadata or {}).get("progress") or {})
        summary["latest"] = {
            "id": latest.pk,
            "status": latest.get_status_display(),
            "processed_files": int(progress.get("processed_files") or 0),
            "total_files": int(progress.get("total_files") or 0),
            "findings_count": latest.findings_count,
        }
    return summary


def latest_analysis_execution(plan: AnalysisPlan) -> PericiaExecution | None:
    return (
        PericiaExecution.objects.filter(analysis_plan=plan)
        .order_by("-started_at", "-id")
        .first()
    )


def execution_has_observations(execution: PericiaExecution | None) -> bool:
    if execution is None or execution.status != PericiaExecution.Status.COMPLETED:
        return False

    if execution.unsupported_files_count > 0 or execution.failed_files_count > 0:
        return True

    metadata = execution.engine_metadata if isinstance(execution.engine_metadata, dict) else {}
    warnings = metadata.get("warnings") or metadata.get("warning")
    if isinstance(warnings, (list, tuple, set)):
        return bool(warnings)
    return bool(str(warnings or "").strip())


def analysis_plan_operator_state(
    plan: AnalysisPlan,
    *,
    latest_execution: PericiaExecution | None = None,
) -> dict[str, str]:
    execution = latest_execution if latest_execution is not None else latest_analysis_execution(plan)
    has_targets = any(str(target).strip() for target in (plan.analysis_targets or []))
    has_point = bool(plan.pericia_point_id)

    if plan.status == AnalysisPlan.Status.SKIPPED:
        return {"key": "omitted", "label": str(_("Omitido"))}
    if not has_point or not has_targets:
        return {"key": "incomplete", "label": str(_("Incompleto"))}
    if execution is None:
        return {"key": "ready", "label": str(_("Listo"))}
    if execution.status == PericiaExecution.Status.PENDING:
        return {"key": "queued", "label": str(_("En cola"))}
    if execution.status == PericiaExecution.Status.RUNNING:
        return {"key": "running", "label": str(_("En ejecucion"))}
    if execution.status == PericiaExecution.Status.FAILED:
        return {"key": "failed", "label": str(_("Fallido"))}
    if execution_has_observations(execution):
        return {"key": "completed_with_observations", "label": str(_("Completado con observaciones"))}
    return {"key": "completed", "label": str(_("Completado"))}


def ready_analysis_plans(case: PericiaCase) -> list[AnalysisPlan]:
    plans = list(
        case.analysis_plans.select_related("requested_point", "pericia_point").order_by(
            "requested_point__order",
            "id",
        )
    )
    ready: list[AnalysisPlan] = []
    for plan in plans:
        state = analysis_plan_operator_state(plan)
        if state["key"] == "ready":
            ready.append(plan)
    return ready


def analysis_plan_operational_summary(case: PericiaCase) -> dict[str, int]:
    plans = list(
        case.analysis_plans.select_related("requested_point", "pericia_point").order_by(
            "requested_point__order",
            "id",
        )
    )
    summary = {
        "total": len(plans),
        "ready": 0,
        "active": 0,
        "failed": 0,
        "completed": 0,
        "completed_with_observations": 0,
        "incomplete": 0,
        "omitted": 0,
    }
    for plan in plans:
        state = analysis_plan_operator_state(plan)
        key = state["key"]
        if key in {"queued", "running"}:
            summary["active"] += 1
        elif key in summary:
            summary[key] += 1
    return summary


def _report_stage(case: PericiaCase) -> tuple[bool, list[str]]:
    blockers: list[str] = []
    sections = list(case.report_sections.all())
    if not sections:
        return False, blockers

    types_with_content = {
        section.section_type
        for section in sections
        if section.title.strip() and report_section_has_substantive_content(section)
    }
    missing_types = sorted(REPORT_MINIMUM_SECTION_TYPES.difference(types_with_content))
    if missing_types:
        return False, blockers
    return not missing_types, blockers


def build_case_workflow(case: PericiaCase) -> dict:
    analysis_complete, analysis_blockers = _analysis_stage(case)
    device_complete, device_blockers = _device_results_stage(case)
    responses_complete, responses_blockers = _responses_stage(case)
    report_complete, report_blockers = _report_stage(case)
    execution_summary = _analysis_execution_summary(case)

    stage_states = {
        "case": {"complete": True, "blocked": False, "blockers": []},
        "documents": {
            "complete": _has_useful_documents(case),
            "blocked": False,
            "blockers": []
            if _has_useful_documents(case)
            else [_("Carga al menos un documento fuente para contextualizar la pericia.")],
        },
        "requested_points": {
            "complete": _has_requested_points(case),
            "blocked": False,
            "blockers": []
            if _has_requested_points(case)
            else [_("Registra al menos un punto solicitado literal.")],
        },
        "evidence": {
            "complete": _has_evidence(case),
            "blocked": False,
            "blockers": []
            if _has_evidence(case)
            else [_("Registra al menos un dispositivo, imagen o copia de trabajo.")],
        },
        "analysis_plans": {
            "complete": analysis_complete,
            "blocked": bool(analysis_blockers),
            "blockers": analysis_blockers,
        },
        "device_results": {
            "complete": device_complete,
            "blocked": bool(device_blockers),
            "blockers": device_blockers,
        },
        "responses": {
            "complete": responses_complete,
            "blocked": bool(responses_blockers),
            "blockers": responses_blockers,
        },
        "report": {
            "complete": report_complete,
            "blocked": bool(report_blockers),
            "blockers": report_blockers,
        },
        "final_review": {
            "complete": report_complete and responses_complete,
            "blocked": not report_complete or not responses_complete,
            "blockers": []
            if report_complete and responses_complete
            else [
                _(
                    "La revision final se habilita cuando las respuestas y el informe minimo ya estan completos."
                )
            ],
        },
    }

    stages = []
    current_stage_key = "final_review"
    next_stage_key = None
    for definition in STAGE_DEFINITIONS:
        state = stage_states[definition.key]
        if not state["complete"] and next_stage_key is None:
            next_stage_key = definition.key
            current_stage_key = definition.key

        stages.append(
            {
                "key": definition.key,
                "title": str(definition.title),
                "description": str(definition.description),
                "complete": state["complete"],
                "blocked": state["blocked"],
                "blockers": [str(item) for item in state["blockers"]],
                "resume_url": _resolve_stage_url(definition, case),
            }
        )

    if next_stage_key is None:
        next_stage_key = "final_review"

    current_stage = next(stage for stage in stages if stage["key"] == current_stage_key)
    next_stage = next(stage for stage in stages if stage["key"] == next_stage_key)
    completed_count = sum(1 for stage in stages if stage["complete"])
    completion_ratio = int((completed_count / len(stages)) * 100)

    action_items = []
    for stage in stages:
        if stage["complete"]:
            continue
        if stage["blocked"]:
            action_items.append(
                {
                    "title": stage["title"],
                    "kind": "blocked",
                    "message": stage["blockers"][0] if stage["blockers"] else "",
                    "url": stage["resume_url"],
                }
            )
        else:
            action_items.append(
                {
                    "title": stage["title"],
                    "kind": "next",
                    "message": stage["description"],
                    "url": stage["resume_url"],
                }
            )

    return {
        "case_id": case.pk,
        "case_reference": case.case_reference,
        "case_title": case.title or case.case_reference,
        "case_url": _case_url(case),
        "status_label": case.get_status_display(),
        "current_stage": current_stage,
        "next_stage": next_stage,
        "stages": stages,
        "completed_count": completed_count,
        "total_count": len(stages),
        "completion_ratio": completion_ratio,
        "is_complete": completed_count == len(stages),
        "action_items": action_items,
        "analysis_execution_summary": execution_summary,
    }


def build_dashboard_workflow_context(limit: int = 5) -> dict:
    case_summaries = [
        build_case_workflow(case)
        for case in PericiaCase.objects.order_by("-updated_at")[:limit]
    ]
    focus_case = next((case for case in case_summaries if not case["is_complete"]), None)
    stage_cards = build_home_stage_cards()
    return {
        "workflow_resume_cases": case_summaries,
        "workflow_has_cases": bool(case_summaries),
        "workflow_stage_cards": stage_cards,
        "workflow_focus_case": focus_case,
    }


def build_home_stage_cards() -> list[dict]:
    cards = []
    for key, config in HOME_STAGE_MAP.items():
        if key == "case_setup":
            state = "ready"
            state_label = _("Empezar aqui")
            helper = _("Primer paso recomendado para abrir una pericia nueva.")
            cta_label = _("Crear caso")
        else:
            state = "upcoming"
            state_label = _("Siguiente")
            helper = _("Se habilita naturalmente despues de iniciar y guardar el caso.")
            cta_label = _("Ver etapa")

        cards.append(
            {
                "key": key,
                "step": str(config["step"]),
                "title": str(config["title"]),
                "description": str(config["description"]),
                "icon": config["icon"],
                "state": state,
                "state_label": str(state_label),
                "helper": str(helper),
                "cta_label": str(cta_label),
                "link": reverse(config["url_name"]),
                "is_featured": state in {"ready", "in_progress"},
            }
        )
    return cards
