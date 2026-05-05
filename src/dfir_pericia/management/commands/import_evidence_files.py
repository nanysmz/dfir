from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from dfir_pericia.extractors import infer_file_kind
from dfir_pericia.models import EvidenceFile


class Command(BaseCommand):
    help = "Importa en lote los archivos de evidencia desde un directorio."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default=str(settings.EVIDENCE_INPUT_PATH),
            help="Directorio raiz a escanear. Por defecto usa EVIDENCE_INPUT_PATH.",
        )

    def handle(self, *args, **options):
        root = Path(options["path"]).resolve()
        if not root.exists() or not root.is_dir():
            raise CommandError(f"El directorio de entrada no existe: {root}")

        created_count = 0
        updated_count = 0
        discovered_files = 0

        for path in sorted(root.rglob("*")):
            if path.is_dir() or path.name.startswith("."):
                continue

            discovered_files += 1
            stat = path.stat()
            _, created = EvidenceFile.objects.update_or_create(
                identity_scope=EvidenceFile.IDENTITY_SCOPE_GLOBAL,
                source_path=str(path),
                defaults={
                    "display_name": path.name,
                    "file_kind": infer_file_kind(path),
                    "size_bytes": stat.st_size,
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Importacion completada: "
                f"{discovered_files} archivos detectados, "
                f"{created_count} creados, "
                f"{updated_count} actualizados."
            )
        )
