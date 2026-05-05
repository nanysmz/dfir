from __future__ import annotations

from dfir_pericia.models import (
    AnalysisPlan,
    DeviceAnalysisResult,
    EvidenceFile,
    EvidenceItem,
    PericiaCase,
    PericiaDocument,
    PericiaExecution,
    PericiaFinding,
    PericiaPoint,
    PreservedArtifact,
    ReportSection,
    RequestedPoint,
    RequestedPointResponse,
)


def test_dfir_pericia_model_labels_are_localized():
    expected_labels = {
        EvidenceFile: ("archivo de evidencia", "archivos de evidencia"),
        PericiaPoint: ("punto de pericia", "puntos de pericia"),
        PericiaCase: ("caso pericial", "casos periciales"),
        PericiaDocument: ("documento pericial", "documentos periciales"),
        RequestedPoint: ("punto solicitado", "puntos solicitados"),
        EvidenceItem: ("elemento de evidencia", "elementos de evidencia"),
        AnalysisPlan: ("plan de analisis", "planes de analisis"),
        DeviceAnalysisResult: (
            "resultado de analisis por dispositivo",
            "resultados de analisis por dispositivo",
        ),
        PericiaExecution: ("ejecucion de pericia", "ejecuciones de pericia"),
        PericiaFinding: ("hallazgo de pericia", "hallazgos de pericia"),
        PreservedArtifact: ("artefacto preservado", "artefactos preservados"),
        RequestedPointResponse: (
            "respuesta a punto solicitado",
            "respuestas a puntos solicitados",
        ),
        ReportSection: ("seccion del informe", "secciones del informe"),
    }

    for model, (verbose_name, verbose_name_plural) in expected_labels.items():
        assert model._meta.verbose_name == verbose_name
        assert model._meta.verbose_name_plural == verbose_name_plural
