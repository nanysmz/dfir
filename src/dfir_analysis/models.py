from dfir_pericia.models import (
    AnalysisPlan,
    DeviceAnalysisResult,
    PericiaExecution,
    PericiaFinding,
    PericiaPoint,
)


class PericiaPointProxy(PericiaPoint):
    class Meta:
        proxy = True
        app_label = "dfir_analysis"
        verbose_name = PericiaPoint._meta.verbose_name
        verbose_name_plural = PericiaPoint._meta.verbose_name_plural


class AnalysisPlanProxy(AnalysisPlan):
    class Meta:
        proxy = True
        app_label = "dfir_analysis"
        verbose_name = AnalysisPlan._meta.verbose_name
        verbose_name_plural = AnalysisPlan._meta.verbose_name_plural


class DeviceAnalysisResultProxy(DeviceAnalysisResult):
    class Meta:
        proxy = True
        app_label = "dfir_analysis"
        verbose_name = DeviceAnalysisResult._meta.verbose_name
        verbose_name_plural = DeviceAnalysisResult._meta.verbose_name_plural


class PericiaExecutionProxy(PericiaExecution):
    class Meta:
        proxy = True
        app_label = "dfir_analysis"
        verbose_name = PericiaExecution._meta.verbose_name
        verbose_name_plural = PericiaExecution._meta.verbose_name_plural


class PericiaFindingProxy(PericiaFinding):
    class Meta:
        proxy = True
        app_label = "dfir_analysis"
        verbose_name = PericiaFinding._meta.verbose_name
        verbose_name_plural = PericiaFinding._meta.verbose_name_plural
