from django.contrib import admin
from unfold.admin import ModelAdmin

from dfir_core.admin_forms import ReportSectionAdminForm
from .models import ReportSectionProxy, RequestedPointResponseProxy


@admin.register(RequestedPointResponseProxy)
class RequestedPointResponseAdmin(ModelAdmin):
    list_display = ("requested_point", "pericia_case", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("requested_point__literal_text", "pericia_case__case_reference")
    filter_horizontal = (
        "device_analysis_results",
        "executions",
        "findings",
        "preserved_artifacts",
    )
    list_filter_submit = True
    warn_unsaved_form = True


@admin.register(ReportSectionProxy)
class ReportSectionAdmin(ModelAdmin):
    form = ReportSectionAdminForm
    list_display = ("pericia_case", "order", "section_type", "title")
    list_filter = ("section_type",)
    search_fields = ("title", "content", "pericia_case__case_reference")
    filter_horizontal = ("responses", "device_analysis_results", "preserved_artifacts")
    list_filter_submit = True
    warn_unsaved_form = True
