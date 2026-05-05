from __future__ import annotations

import pytest
from django.core.management import call_command

from dfir_pericia.models import EvidenceFile


@pytest.mark.django_db
def test_import_evidence_files_imports_all_files_recursively(tmp_path):
    top_level = tmp_path / "report.txt"
    nested_dir = tmp_path / "browser" / "content"
    nested_dir.mkdir(parents=True)
    nested_file = nested_dir / "Web_Accounts.html"

    top_level.write_text("contenido", encoding="utf-8")
    nested_file.write_text("<p>mail analyst@example.com</p>", encoding="utf-8")

    call_command("import_evidence_files", "--path", str(tmp_path))

    files = EvidenceFile.objects.order_by("source_path")
    assert files.count() == 2
    assert list(files.values_list("display_name", flat=True)) == [
        "Web_Accounts.html",
        "report.txt",
    ]
    assert set(files.values_list("file_kind", flat=True)) == {
        EvidenceFile.FileKind.TEXT,
        EvidenceFile.FileKind.HTML,
    }
