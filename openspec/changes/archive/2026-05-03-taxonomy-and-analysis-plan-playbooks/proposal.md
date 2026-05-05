## Why

Hoy el módulo de análisis mezcla tres niveles distintos: el punto pericial
pedido por la autoridad, la estrategia técnica reusable y la ejecución concreta
sobre evidencia. Eso vuelve ambiguo el rol de `AnalysisPlan` y hace que muchos
puntos del dominio real parezcan “demasiado grandes” para el modelo actual.

## What Changes

- Definir una taxonomía operativa completa para los 25 puntos periciales
  frecuentes del catálogo aportado por el usuario.
- Formalizar que `RequestedPoint` representa un objetivo investigativo y que
  `PericiaPoint` representa técnicas reusables de bajo nivel.
- Redefinir `AnalysisPlan` como la relación explícita entre un punto pericial
  del caso y un conjunto de acciones ejecutables, no solo como un link simple
  a una estrategia reusable.
- Preparar el sistema para que un punto solicitado pueda disparar varios pasos
  de análisis, potencialmente por dispositivo y por tipo de evidencia.

## Capabilities

### New Capabilities
- `pericia-point-taxonomy`: cubre la clasificación operativa de los puntos
  periciales frecuentes y su traducción conceptual a familias de análisis.
- `analysis-plan-playbooks`: cubre la definición de `AnalysisPlan` como receta o
  playbook de acciones ejecutables vinculadas a un punto pericial del caso.

### Modified Capabilities
- `pericia-report-workflow`: cambia la semántica de la etapa de análisis para
  tratar los planes como traducción del punto solicitado a acciones concretas.
- `pericia-points`: cambia el papel de `PericiaPoint` para ubicarlo como técnica
  reusable y no como equivalente directo del punto pericial judicial.
- `admin-workflow-ui`: cambia las expectativas de la UX del análisis para que
  el operador vea y gestione acciones técnicas derivadas de un punto del caso.

## Impact

- Código afectado: `src/dfir_pericia/models.py`, `src/dfir_core/admin_forms.py`,
  `src/dfir_analysis/admin.py`, `src/dfir_pericia/workflow.py` y tests del
  workflow de análisis.
- Impacto de dominio: clarifica la relación entre `RequestedPoint`,
  `AnalysisPlan`, `PericiaPoint`, `PericiaExecution` y `RequestedPointResponse`.
- Riesgo principal: el cambio es semántico y transversal; si no se explicita
  bien, el sistema puede seguir mezclando objetivo investigativo, técnica y
  ejecución como si fueran la misma cosa.
