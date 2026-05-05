from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from dfir_pericia.models import (
    AnalysisPlan,
    DeviceAnalysisResult,
    EvidenceFile,
    PericiaPoint,
)
from dfir_pericia.services import execute_pericia_point


class Command(BaseCommand):
    help = (
        "Ejecuta un punto de pericia sobre una o mas rutas o sobre el contexto "
        "de un dispositivo ya cargado en el caso."
    )

    def add_arguments(self, parser):
        parser.add_argument("--point-id", type=int, required=True)
        parser.add_argument("--analysis-plan-id", type=int)
        parser.add_argument("--device-analysis-result-id", type=int)
        parser.add_argument(
            "--path",
            action="append",
            dest="paths",
            help="Ruta de archivo o carpeta a procesar. Puede repetirse.",
        )
        parser.add_argument(
            "--evidence-file-id",
            action="append",
            dest="evidence_file_ids",
            type=int,
            help="ID de archivo de evidencia ya cargado. Puede repetirse.",
        )

    def handle(self, *args, **options):
        pericia_point = self._resolve_point(options["point_id"])
        analysis_plan = self._resolve_analysis_plan(options.get("analysis_plan_id"))
        device_result = self._resolve_device_result(
            options.get("device_analysis_result_id")
        )
        evidence_files = self._resolve_evidence_files(options.get("evidence_file_ids"))
        paths = [str(Path(path).expanduser().resolve()) for path in options.get("paths") or []]

        if not paths and not evidence_files and device_result is not None:
            evidence_item = device_result.evidence_item
            if evidence_item.source_path:
                paths.append(str(Path(evidence_item.source_path).expanduser().resolve()))
            evidence_files.extend(list(evidence_item.associated_evidence_files()))

        if not paths and not evidence_files:
            raise CommandError(
                "Debes indicar al menos una --path, un --evidence-file-id o un --device-analysis-result-id con evidencia asociada."
            )

        execution = execute_pericia_point(
            pericia_point,
            evidence_files=evidence_files or None,
            source_paths=paths or None,
            analysis_plan=analysis_plan,
            device_analysis_result=device_result,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Ejecucion completada: "
                f"id={execution.pk}, analizados={execution.analyzed_files_count}, "
                f"hallazgos={execution.findings_count}, "
                f"exportados={execution.engine_metadata.get('exported_artifacts_count', 0)}."
            )
        )

    def _resolve_point(self, point_id: int) -> PericiaPoint:
        try:
            return PericiaPoint.objects.get(pk=point_id)
        except PericiaPoint.DoesNotExist as exc:
            raise CommandError(
                f"No existe un punto de pericia con id={point_id}."
            ) from exc

    def _resolve_analysis_plan(self, analysis_plan_id: int | None):
        if not analysis_plan_id:
            return None
        try:
            return AnalysisPlan.objects.get(pk=analysis_plan_id)
        except AnalysisPlan.DoesNotExist as exc:
            raise CommandError(
                f"No existe un plan de analisis con id={analysis_plan_id}."
            ) from exc

    def _resolve_device_result(self, device_result_id: int | None):
        if not device_result_id:
            return None
        try:
            return DeviceAnalysisResult.objects.get(pk=device_result_id)
        except DeviceAnalysisResult.DoesNotExist as exc:
            raise CommandError(
                "No existe un resultado de analisis por dispositivo con "
                f"id={device_result_id}."
            ) from exc

    def _resolve_evidence_files(self, evidence_file_ids: list[int] | None) -> list[EvidenceFile]:
        if not evidence_file_ids:
            return []
        evidence_files = list(EvidenceFile.objects.filter(pk__in=evidence_file_ids))
        found_ids = {item.pk for item in evidence_files}
        missing = [item_id for item_id in evidence_file_ids if item_id not in found_ids]
        if missing:
            raise CommandError(
                "No existen los archivos de evidencia con id="
                + ", ".join(str(item_id) for item_id in missing)
                + "."
            )
        return evidence_files
