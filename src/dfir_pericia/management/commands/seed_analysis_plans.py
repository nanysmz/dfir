from __future__ import annotations

import re

from django.core.management.base import BaseCommand, CommandError

from dfir_pericia.analysis_playbooks import build_suggested_playbook_actions
from dfir_pericia.models import AnalysisPlan, PericiaCase, PericiaPoint


class Command(BaseCommand):
    help = (
        "Crea planes iniciales de analisis para cada punto solicitado de un caso "
        "que todavia no tenga plan asociado."
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

    def add_arguments(self, parser):
        parser.add_argument(
            "--case-id",
            type=int,
            help="ID del caso pericial donde se crearan los planes iniciales.",
        )
        parser.add_argument(
            "--case-reference",
            help="Referencia del caso pericial donde se crearan los planes iniciales.",
        )

    def handle(self, *args, **options):
        case_id = options.get("case_id")
        case_reference = options.get("case_reference")

        if not case_id and not case_reference:
            raise CommandError("Debes indicar --case-id o --case-reference.")

        if case_id and case_reference:
            raise CommandError("Usa solo uno de: --case-id o --case-reference.")

        case = self._resolve_case(case_id=case_id, case_reference=case_reference)
        requested_points = case.requested_points.order_by("order", "id")
        suggested_targets = self._collect_analysis_targets(case)

        created = 0
        skipped = 0

        for requested_point in requested_points:
            if AnalysisPlan.objects.filter(
                pericia_case=case,
                requested_point=requested_point,
            ).exists():
                skipped += 1
                continue

            terms = self._extract_terms(
                f"{requested_point.short_label or ''} {requested_point.literal_text or ''}"
            )
            point_name = (
                f"Plan inicial {case.case_reference} - punto {requested_point.order}"
            )
            pericia_point = PericiaPoint.objects.create(
                name=point_name,
                point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
                matching_mode=PericiaPoint.MatchingMode.ANY,
                parameters={"terms": terms},
                enabled=True,
            )

            AnalysisPlan.objects.create(
                pericia_case=case,
                requested_point=requested_point,
                pericia_point=pericia_point,
                label=(
                    f"Plan inicial - {requested_point.short_label or f'Punto {requested_point.order}'}"
                ),
                strategy_notes=(
                    "Generado automaticamente como plan inicial guiado. "
                    "Revisar taxonomia, acciones del playbook y alcance antes de ejecutar."
                ),
                analysis_targets=suggested_targets,
                scope_snapshot={
                    "search_terms": terms,
                    "execution_actions": build_suggested_playbook_actions(
                        f"{requested_point.short_label or ''} {requested_point.literal_text or ''}",
                        pericia_point_name=point_name,
                        point_family=PericiaPoint.PointFamily.TEXT_KEYWORD_SEARCH,
                    ),
                },
            )
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Planes iniciales procesados para {case.case_reference}: "
                f"{created} creados, {skipped} omitidos."
            )
        )

    def _extract_terms(self, text: str) -> list[str]:
        tokens = re.findall(r"[a-zA-Z0-9_]{4,}", text.lower())
        terms: list[str] = []
        seen: set[str] = set()
        for token in tokens:
            if token in self.STOPWORDS or token in seen:
                continue
            seen.add(token)
            terms.append(token)
            if len(terms) >= 8:
                break

        if not terms:
            return ["relevante"]
        return terms

    def _collect_analysis_targets(self, case: PericiaCase) -> list[str]:
        targets: list[str] = []
        seen: set[str] = set()

        for evidence_item in case.evidence_items.order_by("id"):
            for source_path in evidence_item.known_source_paths():
                normalized = str(source_path or "").strip()
                if not normalized or normalized in seen:
                    continue
                seen.add(normalized)
                targets.append(normalized)

        return targets

    def _resolve_case(
        self, *, case_id: int | None, case_reference: str | None
    ) -> PericiaCase:
        if case_id:
            try:
                return PericiaCase.objects.get(pk=case_id)
            except PericiaCase.DoesNotExist as exc:
                raise CommandError(
                    f"No existe un caso pericial con id={case_id}."
                ) from exc

        try:
            return PericiaCase.objects.get(case_reference=str(case_reference))
        except PericiaCase.DoesNotExist as exc:
            raise CommandError(
                "No existe un caso pericial con referencia="
                f"{case_reference}."
            ) from exc
