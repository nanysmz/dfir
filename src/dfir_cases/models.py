from dfir_pericia.models import PericiaCase, PericiaDocument, RequestedPoint


class PericiaCaseProxy(PericiaCase):
    class Meta:
        proxy = True
        app_label = "dfir_cases"
        verbose_name = PericiaCase._meta.verbose_name
        verbose_name_plural = PericiaCase._meta.verbose_name_plural


class PericiaDocumentProxy(PericiaDocument):
    class Meta:
        proxy = True
        app_label = "dfir_cases"
        verbose_name = PericiaDocument._meta.verbose_name
        verbose_name_plural = PericiaDocument._meta.verbose_name_plural


class RequestedPointProxy(RequestedPoint):
    class Meta:
        proxy = True
        app_label = "dfir_cases"
        verbose_name = RequestedPoint._meta.verbose_name
        verbose_name_plural = RequestedPoint._meta.verbose_name_plural
