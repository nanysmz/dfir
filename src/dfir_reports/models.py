from dfir_pericia.models import ReportSection, RequestedPointResponse


class RequestedPointResponseProxy(RequestedPointResponse):
    class Meta:
        proxy = True
        app_label = "dfir_reports"
        verbose_name = RequestedPointResponse._meta.verbose_name
        verbose_name_plural = RequestedPointResponse._meta.verbose_name_plural


class ReportSectionProxy(ReportSection):
    class Meta:
        proxy = True
        app_label = "dfir_reports"
        verbose_name = ReportSection._meta.verbose_name
        verbose_name_plural = ReportSection._meta.verbose_name_plural
