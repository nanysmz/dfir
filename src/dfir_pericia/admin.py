from django.contrib import admin
from django.utils.html import format_html, format_html_join

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
    readonly_fields = (
        "pericia_point",
        "analysis_plan",
        "device_analysis_result",
        "status",
        "scope_snapshot",
        "engine_metadata",
        "analyzed_files_count",
        "unsupported_files_count",
        "failed_files_count",
        "matched_files_count",
        "findings_count",
        "unsupported_files",
        "failed_files",
        "started_at",
        "finished_at",
    )
    fields = readonly_fields

    def has_add_permission(self, request):
        return False


@admin.register(PericiaFinding)
class PericiaFindingAdmin(admin.ModelAdmin):
    list_display = ("pericia_point", "evidence_file", "matched_value", "confidence")
    search_fields = ("matched_value", "context", "evidence_file__source_path")
    readonly_fields = (
        "execution",
        "pericia_point",
        "device_analysis_result",
        "evidence_file",
        "matched_value",
        "finding_fragment_preview",
        "context",
        "confidence",
        "extraction_metadata",
        "engine_metadata",
        "source_locator",
        "created_at",
    )
    fields = readonly_fields

    def has_add_permission(self, request):
        return False

    @admin.display(description="fragmento contextual")
    def finding_fragment_preview(self, obj):
        if obj is None:
            return "Se completa automaticamente desde el hallazgo."
        fragment = obj.contextual_fragment
        lines = fragment.get("lines", []) if isinstance(fragment, dict) else []
        if not lines:
            return format_html(
                "<span style='color:#64748b;'>{}</span>",
                "No hay fragmento contextual disponible.",
            )
        return format_html(
            "<div style='display:flex;flex-direction:column;gap:0.2rem;"
            "font-family:monospace;white-space:pre-wrap;background:#0f172a;"
            "color:#e2e8f0;padding:0.85rem;border-radius:0.75rem;'>"
            "{}"
            "</div>",
            format_html_join(
                "",
                "{}",
                ((self._render_fragment_line(line),) for line in lines),
            ),
        )

    @staticmethod
    def _render_fragment_line(line):
        line_number = line.get("line_number", "")
        text = str(line.get("text") or "")
        if line.get("is_match"):
            return format_html(
                "<div style='background:#7c2d12;color:#fff7ed;"
                "padding:0.18rem 0.35rem;border-radius:0.45rem;'>"
                "<strong>{:>4}</strong> | {}"
                "</div>",
                line_number,
                text,
            )
        return format_html(
            "<div><span style='color:#94a3b8;'>{:>4}</span> | {}</div>",
            line_number,
            text,
        )
