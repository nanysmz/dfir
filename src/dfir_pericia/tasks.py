from __future__ import annotations

from celery import shared_task

from .models import EvidenceFile, PericiaPoint
from .services import execute_pericia_point


@shared_task(name="dfir_pericia.execute_pericia_point")
def execute_pericia_point_task(
    pericia_point_id: int,
    evidence_file_ids: list[int] | None = None,
    source_paths: list[str] | None = None,
) -> int:
    pericia_point = PericiaPoint.objects.get(pk=pericia_point_id)
    evidence_files = None
    if evidence_file_ids:
        evidence_files = list(EvidenceFile.objects.filter(pk__in=evidence_file_ids))
    execution = execute_pericia_point(
        pericia_point,
        evidence_files=evidence_files,
        source_paths=source_paths,
    )
    return execution.pk
