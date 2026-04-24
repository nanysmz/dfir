from django.contrib import admin

from .models import EvidenceFile, PericiaExecution, PericiaFinding, PericiaPoint


@admin.register(EvidenceFile)
class EvidenceFileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "file_kind", "source_path", "updated_at")
    search_fields = ("display_name", "source_path", "sha256")
    list_filter = ("file_kind",)


@admin.register(PericiaPoint)
class PericiaPointAdmin(admin.ModelAdmin):
    list_display = ("name", "point_family", "matching_mode", "enabled", "updated_at")
    list_filter = ("point_family", "matching_mode", "enabled")
    search_fields = ("name", "slug")


@admin.register(PericiaExecution)
class PericiaExecutionAdmin(admin.ModelAdmin):
    list_display = (
        "pericia_point",
        "status",
        "analyzed_files_count",
        "findings_count",
        "started_at",
    )
    list_filter = ("status", "pericia_point__point_family")


@admin.register(PericiaFinding)
class PericiaFindingAdmin(admin.ModelAdmin):
    list_display = ("pericia_point", "evidence_file", "matched_value", "confidence")
    search_fields = ("matched_value", "context", "evidence_file__source_path")
