from __future__ import annotations

import hashlib
import json
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.utils.text import slugify
from django.utils import timezone

from .extractors import ensure_evidence_file, extract_evidence_content
from .matchers import match_pericia_point
from .models import (
    EvidenceFile,
    PericiaExecution,
    PericiaFinding,
    PericiaPoint,
    PreservedArtifact,
)


@transaction.atomic
def prepare_pericia_execution(
    pericia_point: PericiaPoint,
    *,
    evidence_files: list[EvidenceFile] | None = None,
    source_paths: list[str] | None = None,
    analysis_plan=None,
    device_analysis_result=None,
) -> tuple[PericiaExecution, list[EvidenceFile]]:
    evidence_files = _collect_evidence_files(
        evidence_files=evidence_files,
        source_paths=source_paths,
    )

    execution = PericiaExecution.objects.create(
        pericia_point=pericia_point,
        analysis_plan=analysis_plan,
        device_analysis_result=device_analysis_result,
        scope_snapshot={
            "point_scope": pericia_point.scope,
            "evidence_files": [item.source_path for item in evidence_files],
            "source_paths": [str(path) for path in source_paths or []],
        },
        engine_metadata={
            "executor": "dfir_pericia.services.execute_pericia_point",
            "progress": {
                "phase": "queued",
                "processed_files": 0,
                "total_files": len(evidence_files),
                "matched_files": 0,
                "findings_count": 0,
            },
        },
    )
    if analysis_plan is not None and analysis_plan.status != analysis_plan.Status.RUNNING:
        analysis_plan.status = analysis_plan.Status.RUNNING
        analysis_plan.save(update_fields=["status"])
    return execution, evidence_files


@transaction.atomic
def process_pericia_execution(
    execution: PericiaExecution,
    *,
    evidence_files: list[EvidenceFile] | None = None,
    source_paths: list[str] | None = None,
) -> PericiaExecution:
    pericia_point = execution.pericia_point
    analysis_plan = execution.analysis_plan
    device_analysis_result = execution.device_analysis_result
    evidence_files = _collect_evidence_files(
        evidence_files=evidence_files,
        source_paths=source_paths,
    )
    progress = {
        "phase": "running",
        "processed_files": 0,
        "total_files": len(evidence_files),
        "matched_files": 0,
        "findings_count": 0,
    }
    execution.status = PericiaExecution.Status.RUNNING
    execution.engine_metadata = {
        **(execution.engine_metadata or {}),
        "progress": progress,
    }
    execution.save(update_fields=["status", "engine_metadata"])

    unsupported_files: list[dict] = []
    failed_files: list[dict] = []
    analyzed_count = 0
    matched_files = set()
    findings_count = 0
    exported_artifacts: list[dict] = []
    context = _build_execution_context(
        pericia_point=pericia_point,
        analysis_plan=analysis_plan,
        device_analysis_result=device_analysis_result,
    )

    for evidence_file in evidence_files:
        extraction = extract_evidence_content(evidence_file)
        file_entry = {
            "source_path": evidence_file.source_path,
            "file_kind": evidence_file.file_kind,
            "reason": extraction.reason,
        }
        if extraction.status == "unsupported":
            unsupported_files.append(file_entry)
        elif extraction.status == "failed":
            failed_files.append(file_entry)
        else:
            analyzed_count += 1
            findings = match_pericia_point(pericia_point, extraction)
            if findings:
                matched_files.add(evidence_file.pk)

            for finding_index, finding in enumerate(findings, start=1):
                finding_record = PericiaFinding.objects.create(
                    execution=execution,
                    pericia_point=pericia_point,
                    device_analysis_result=device_analysis_result,
                    evidence_file=evidence_file,
                    matched_value=finding["matched_value"],
                    context=finding.get("context", ""),
                    confidence=finding.get("confidence"),
                    extraction_metadata=finding.get("extraction_metadata", {}),
                    engine_metadata=finding.get("engine_metadata", {}),
                    source_locator=finding.get("source_locator", {}),
                )
                artifact_entry = _export_finding_output(
                    execution=execution,
                    finding=finding_record,
                    evidence_file=evidence_file,
                    extraction=extraction,
                    export_context=context,
                    finding_index=finding_index,
                )
                if artifact_entry is not None:
                    exported_artifacts.append(artifact_entry)
                findings_count += 1

        progress = {
            "phase": "running",
            "processed_files": analyzed_count
            + len(unsupported_files)
            + len(failed_files),
            "total_files": len(evidence_files),
            "matched_files": len(matched_files),
            "findings_count": findings_count,
            "current_file": evidence_file.source_path,
        }
        execution.analyzed_files_count = analyzed_count
        execution.unsupported_files_count = len(unsupported_files)
        execution.failed_files_count = len(failed_files)
        execution.matched_files_count = len(matched_files)
        execution.findings_count = findings_count
        execution.unsupported_files = unsupported_files
        execution.failed_files = failed_files
        execution.engine_metadata = {
            **(execution.engine_metadata or {}),
            "progress": progress,
        }
        execution.save(
            update_fields=[
                "analyzed_files_count",
                "unsupported_files_count",
                "failed_files_count",
                "matched_files_count",
                "findings_count",
                "unsupported_files",
                "failed_files",
                "engine_metadata",
            ]
        )

    execution.status = PericiaExecution.Status.COMPLETED
    execution.engine_metadata = {
        **(execution.engine_metadata or {}),
        "export_root": context["export_root"],
        "exported_artifacts": exported_artifacts,
        "exported_artifacts_count": len(exported_artifacts),
        "progress": {
            "phase": "completed",
            "processed_files": analyzed_count + len(unsupported_files) + len(failed_files),
            "total_files": len(evidence_files),
            "matched_files": len(matched_files),
            "findings_count": findings_count,
        },
    }
    execution.finished_at = timezone.now()
    execution.save(
        update_fields=[
            "status",
            "engine_metadata",
            "finished_at",
        ]
    )
    if analysis_plan is not None and analysis_plan.status != analysis_plan.Status.COMPLETED:
        analysis_plan.status = analysis_plan.Status.COMPLETED
        analysis_plan.save(update_fields=["status"])
    return execution


@transaction.atomic
def execute_pericia_point(
    pericia_point: PericiaPoint,
    *,
    evidence_files: list[EvidenceFile] | None = None,
    source_paths: list[str] | None = None,
    analysis_plan=None,
    device_analysis_result=None,
) -> PericiaExecution:
    execution, prepared_files = prepare_pericia_execution(
        pericia_point,
        evidence_files=evidence_files,
        source_paths=source_paths,
        analysis_plan=analysis_plan,
        device_analysis_result=device_analysis_result,
    )
    return process_pericia_execution(execution, evidence_files=prepared_files)


def fail_pericia_execution(execution: PericiaExecution, message: str) -> PericiaExecution:
    progress = dict((execution.engine_metadata or {}).get("progress") or {})
    progress["phase"] = "failed"
    execution.status = PericiaExecution.Status.FAILED
    execution.engine_metadata = {
        **(execution.engine_metadata or {}),
        "progress": progress,
        "error": str(message),
    }
    execution.finished_at = timezone.now()
    execution.save(update_fields=["status", "engine_metadata", "finished_at"])
    if execution.analysis_plan_id and execution.analysis_plan.status != execution.analysis_plan.Status.PLANNED:
        execution.analysis_plan.status = execution.analysis_plan.Status.PLANNED
        execution.analysis_plan.save(update_fields=["status"])
    return execution


def execute_pericia_point_from_paths(
    pericia_point: PericiaPoint,
    paths: list[str | Path],
) -> PericiaExecution:
    return execute_pericia_point(
        pericia_point,
        source_paths=[str(Path(path)) for path in paths],
    )


def _collect_evidence_files(
    *,
    evidence_files: list[EvidenceFile] | None,
    source_paths: list[str] | None,
) -> list[EvidenceFile]:
    collected: list[EvidenceFile] = []
    seen_paths: set[str] = set()

    for evidence_file in list(evidence_files or []):
        source = Path(evidence_file.source_path)
        if source.exists() and source.is_dir():
            for child in _iter_searchable_files(source):
                child_key = str(child.resolve())
                if child_key in seen_paths:
                    continue
                seen_paths.add(child_key)
                collected.append(ensure_evidence_file(child))
            continue

        file_key = str(source.resolve()) if source.exists() else evidence_file.source_path
        if file_key in seen_paths:
            continue
        seen_paths.add(file_key)
        collected.append(evidence_file)

    for raw_path in source_paths or []:
        source = Path(raw_path).expanduser().resolve()
        if source.is_dir():
            for child in _iter_searchable_files(source):
                child_key = str(child.resolve())
                if child_key in seen_paths:
                    continue
                seen_paths.add(child_key)
                collected.append(ensure_evidence_file(child))
        elif source.exists() and source.is_file():
            file_key = str(source.resolve())
            if file_key in seen_paths:
                continue
            seen_paths.add(file_key)
            collected.append(ensure_evidence_file(source))

    return collected


def _iter_searchable_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name.startswith(".") or path.name.lower() in {
            ".ds_store",
            "thumbs.db",
            "desktop.ini",
        }:
            continue
        if "__macosx" in {part.lower() for part in path.parts}:
            continue
        yield path


def _build_execution_context(
    *,
    pericia_point: PericiaPoint,
    analysis_plan,
    device_analysis_result,
) -> dict:
    case = None
    evidence_item = None
    if device_analysis_result is not None:
        case = device_analysis_result.pericia_case
        evidence_item = device_analysis_result.evidence_item
    elif analysis_plan is not None:
        case = analysis_plan.pericia_case

    case_folder = slugify(getattr(case, "case_reference", "") or "sin-caso") or "sin-caso"
    device_folder = slugify(getattr(evidence_item, "label", "") or "sin-dispositivo") or "sin-dispositivo"
    point_folder = slugify(pericia_point.slug or pericia_point.name) or f"punto-{pericia_point.pk}"
    export_root = Path(settings.EVIDENCE_OUTPUT_PATH) / case_folder / device_folder / point_folder

    return {
        "case": case,
        "evidence_item": evidence_item,
        "export_root": str(export_root),
        "case_folder": case_folder,
        "device_folder": device_folder,
        "point_folder": point_folder,
    }


def _export_finding_output(
    *,
    execution: PericiaExecution,
    finding: PericiaFinding,
    evidence_file: EvidenceFile,
    extraction,
    export_context: dict,
    finding_index: int,
) -> dict | None:
    export_root = Path(export_context["export_root"])
    file_kind_folder = slugify(evidence_file.file_kind or "unknown") or "unknown"
    target_dir = export_root / file_kind_folder
    target_dir.mkdir(parents=True, exist_ok=True)

    source_path = Path(evidence_file.source_path)
    output_name = (
        f"{slugify(source_path.stem) or 'archivo'}"
        f"__match_{finding_index:03d}.json"
    )
    output_path = target_dir / output_name
    payload = {
        "case_reference": getattr(export_context["case"], "case_reference", ""),
        "device_label": getattr(export_context["evidence_item"], "label", ""),
        "pericia_point": {
            "id": execution.pericia_point_id,
            "name": execution.pericia_point.name,
            "slug": execution.pericia_point.slug,
        },
        "execution_id": execution.pk,
        "finding_id": finding.pk,
        "matched_value": finding.matched_value,
        "context": finding.context,
        "contextual_fragment": finding.contextual_fragment,
        "source_locator": finding.source_locator,
        "source": {
            "file_name": source_path.name,
            "folder_name": source_path.parent.name,
            "full_path": evidence_file.source_path,
            "file_kind": evidence_file.file_kind,
            "metadata": evidence_file.metadata or {},
            "extraction_metadata": finding.extraction_metadata or {},
            "dates": (finding.extraction_metadata or {}).get("filesystem_dates", {}),
        },
        "generated_at": timezone.now().isoformat(),
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )

    artifact = None
    if export_context["case"] is not None and export_context["evidence_item"] is not None:
        export_context["evidence_item"].evidence_files.add(evidence_file)
        artifact = PreservedArtifact.objects.create(
            pericia_case=export_context["case"],
            evidence_item=export_context["evidence_item"],
            source_finding=finding,
            artifact_kind=PreservedArtifact.ArtifactKind.EXTRACTED_FILE,
            display_name=output_path.name,
            storage_path=str(output_path),
            sha256=_sha256(output_path),
            metadata={
                "matched_value": finding.matched_value,
                "source_path": evidence_file.source_path,
                "file_kind": evidence_file.file_kind,
                "contextual_fragment": finding.contextual_fragment,
            },
        )

    return {
        "path": str(output_path),
        "artifact_id": artifact.pk if artifact is not None else None,
        "file_kind": evidence_file.file_kind,
        "finding_id": finding.pk,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()
