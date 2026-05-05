from __future__ import annotations

from django.apps import apps

from dfir_analysis.models import (
    AnalysisPlanProxy,
    DeviceAnalysisResultProxy,
    PericiaExecutionProxy,
    PericiaFindingProxy,
    PericiaPointProxy,
)
from dfir_cases.models import (
    PericiaCaseProxy,
    PericiaDocumentProxy,
    RequestedPointProxy,
)
from dfir_evidence.models import (
    EvidenceFileProxy,
    EvidenceItemProxy,
    PreservedArtifactProxy,
)
from dfir_reports.models import ReportSectionProxy, RequestedPointResponseProxy


def test_domain_apps_are_registered_with_spanish_labels():
    assert apps.get_app_config("dfir_cases").verbose_name == "Casos periciales"
    assert apps.get_app_config("dfir_evidence").verbose_name == "Evidencia"
    assert apps.get_app_config("dfir_analysis").verbose_name == "Analisis"
    assert apps.get_app_config("dfir_reports").verbose_name == "Informe"


def test_proxy_models_are_grouped_under_domain_apps():
    expected_labels = {
        PericiaCaseProxy: "dfir_cases",
        PericiaDocumentProxy: "dfir_cases",
        RequestedPointProxy: "dfir_cases",
        EvidenceFileProxy: "dfir_evidence",
        EvidenceItemProxy: "dfir_evidence",
        PreservedArtifactProxy: "dfir_evidence",
        PericiaPointProxy: "dfir_analysis",
        AnalysisPlanProxy: "dfir_analysis",
        DeviceAnalysisResultProxy: "dfir_analysis",
        PericiaExecutionProxy: "dfir_analysis",
        PericiaFindingProxy: "dfir_analysis",
        RequestedPointResponseProxy: "dfir_reports",
        ReportSectionProxy: "dfir_reports",
    }

    for model, app_label in expected_labels.items():
        assert model._meta.proxy is True
        assert model._meta.app_label == app_label
