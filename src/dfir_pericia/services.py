from __future__ import annotations

from pathlib import Path

from django.db import transaction
from django.utils import timezone

from .extractors import ensure_evidence_file, extract_evidence_content
from .matchers import match_pericia_point
from .models import EvidenceFile, PericiaExecution, PericiaFinding, PericiaPoint


@transaction.atomic
def execute_pericia_point(
    pericia_point: PericiaPoint,
    *,
    evidence_files: list[EvidenceFile] | None = None,
    source_paths: list[str] | None = None,
) -> PericiaExecution:
    evidence_files = list(evidence_files or [])
    if source_paths:
        evidence_files.extend(ensure_evidence_file(path) for path in source_paths)

    execution = PericiaExecution.objects.create(
        pericia_point=pericia_point,
        scope_snapshot={
            "point_scope": pericia_point.scope,
            "evidence_files": [item.source_path for item in evidence_files],
        },
        engine_metadata={"executor": "dfir_pericia.services.execute_pericia_point"},
    )

    unsupported_files: list[dict] = []
    failed_files: list[dict] = []
    analyzed_count = 0
    matched_files = set()
    findings_count = 0

    for evidence_file in evidence_files:
        extraction = extract_evidence_content(evidence_file)
        file_entry = {
            "source_path": evidence_file.source_path,
            "file_kind": evidence_file.file_kind,
            "reason": extraction.reason,
        }
        if extraction.status == "unsupported":
            unsupported_files.append(file_entry)
            continue
        if extraction.status == "failed":
            failed_files.append(file_entry)
            continue

        analyzed_count += 1
        findings = match_pericia_point(pericia_point, extraction)
        if findings:
            matched_files.add(evidence_file.pk)

        for finding in findings:
            PericiaFinding.objects.create(
                execution=execution,
                pericia_point=pericia_point,
                evidence_file=evidence_file,
                matched_value=finding["matched_value"],
                context=finding.get("context", ""),
                confidence=finding.get("confidence"),
                extraction_metadata=finding.get("extraction_metadata", {}),
                engine_metadata=finding.get("engine_metadata", {}),
                source_locator=finding.get("source_locator", {}),
            )
            findings_count += 1

    execution.status = PericiaExecution.Status.COMPLETED
    execution.analyzed_files_count = analyzed_count
    execution.unsupported_files_count = len(unsupported_files)
    execution.failed_files_count = len(failed_files)
    execution.matched_files_count = len(matched_files)
    execution.findings_count = findings_count
    execution.unsupported_files = unsupported_files
    execution.failed_files = failed_files
    execution.finished_at = timezone.now()
    execution.save(
        update_fields=[
            "status",
            "analyzed_files_count",
            "unsupported_files_count",
            "failed_files_count",
            "matched_files_count",
            "findings_count",
            "unsupported_files",
            "failed_files",
            "finished_at",
        ]
    )
    return execution


def execute_pericia_point_from_paths(
    pericia_point: PericiaPoint,
    paths: list[str | Path],
) -> PericiaExecution:
    return execute_pericia_point(
        pericia_point,
        source_paths=[str(Path(path)) for path in paths],
    )
