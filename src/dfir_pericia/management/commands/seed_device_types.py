from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from dfir_core.admin_forms import EvidenceItemAdminForm
from dfir_pericia.models import EvidenceItem, PericiaCase


class Command(BaseCommand):
    help = (
        "Crea un lote inicial de elementos de evidencia basados en plantillas "
        "de tipos de dispositivo para un caso pericial."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--case-id",
            type=int,
            help="ID del caso pericial donde se creara el lote.",
        )
        parser.add_argument(
            "--case-reference",
            help="Referencia del caso pericial donde se creara el lote.",
        )

    def handle(self, *args, **options):
        case_id = options.get("case_id")
        case_reference = options.get("case_reference")

        if not case_id and not case_reference:
            raise CommandError("Debes indicar --case-id o --case-reference.")

        if case_id and case_reference:
            raise CommandError("Usa solo uno de: --case-id o --case-reference.")

        case = self._resolve_case(case_id=case_id, case_reference=case_reference)

        if case.evidence_items.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"El caso {case.case_reference} ya tiene elementos de evidencia cargados. "
                    "No se generaron plantillas adicionales."
                )
            )
            return

        created = 0
        skipped = 0

        existing_template_keys = set(
            EvidenceItem.objects.filter(pericia_case=case).values_list(
                f"metadata__{EvidenceItemAdminForm.DEVICE_TYPE_METADATA_KEY}", flat=True
            )
        )

        for template_key, config in EvidenceItemAdminForm.DEVICE_TEMPLATE_DATA.items():
            if not template_key:
                continue

            if template_key in existing_template_keys:
                skipped += 1
                continue

            metadata = dict(config.get("metadata") or {})
            metadata[EvidenceItemAdminForm.DEVICE_TYPE_METADATA_KEY] = template_key
            metadata[EvidenceItemAdminForm.LEGACY_DEVICE_TYPE_METADATA_KEY] = template_key

            label = EvidenceItemAdminForm.next_device_label_for_case(case)

            EvidenceItem.objects.create(
                pericia_case=case,
                label=label,
                role=config["role"],
                acquisition_status=config["acquisition_status"],
                metadata=metadata,
            )
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Lote inicial procesado para {case.case_reference}: "
                f"{created} creados, {skipped} omitidos."
            )
        )

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
