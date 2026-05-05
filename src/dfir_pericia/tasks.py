from __future__ import annotations

from celery import shared_task
from django.conf import settings

from .models import DeviceAnalysisResult, AnalysisPlan, EvidenceFile, PericiaPoint
from .services import (
    fail_pericia_execution,
    prepare_pericia_execution,
    process_pericia_execution,
)

def execute_pericia_point_task(
    pericia_point_id: int,
    evidence_file_ids: list[int] | None = None,
    source_paths: list[str] | None = None,
    analysis_plan_id: int | None = None,
    device_analysis_result_id: int | None = None,
) -> int:
    pericia_point = PericiaPoint.objects.get(pk=pericia_point_id)
    evidence_files = None
    if evidence_file_ids:
        evidence_files = list(EvidenceFile.objects.filter(pk__in=evidence_file_ids))
    analysis_plan = None
    if analysis_plan_id:
        analysis_plan = AnalysisPlan.objects.get(pk=analysis_plan_id)
    device_analysis_result = None
    if device_analysis_result_id:
        device_analysis_result = DeviceAnalysisResult.objects.get(
            pk=device_analysis_result_id
        )
    execution, prepared_files = prepare_pericia_execution(
        pericia_point,
        evidence_files=evidence_files,
        source_paths=source_paths,
        analysis_plan=analysis_plan,
        device_analysis_result=device_analysis_result,
    )

    prepared_file_ids = [item.pk for item in prepared_files]
    if settings.CELERY_TASK_ALWAYS_EAGER:
        run_pericia_execution_task(
            execution.pk,
            evidence_file_ids=prepared_file_ids,
            source_paths=None,
        )
    else:
        run_pericia_execution_task.delay(
            execution.pk,
            evidence_file_ids=prepared_file_ids,
            source_paths=None,
        )
    return execution.pk


@shared_task(name="dfir_pericia.run_pericia_execution")
def run_pericia_execution_task(
    execution_id: int,
    evidence_file_ids: list[int] | None = None,
    source_paths: list[str] | None = None,
) -> int:
    from .models import PericiaExecution

    execution = PericiaExecution.objects.get(pk=execution_id)
    evidence_files = None
    if evidence_file_ids:
        evidence_files = list(EvidenceFile.objects.filter(pk__in=evidence_file_ids))
    try:
        process_pericia_execution(
            execution,
            evidence_files=evidence_files,
            source_paths=source_paths,
        )
    except Exception as exc:
        fail_pericia_execution(execution, str(exc))
        raise
    return execution.pk
