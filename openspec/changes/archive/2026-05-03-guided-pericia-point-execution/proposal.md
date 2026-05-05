## Why

El repositorio ya tiene un motor pericial reutilizable y ahora tambien soporta
ejecutar puntos sobre carpetas reales de evidencia, pero ese comportamiento no
quedo formalizado en OpenSpec ni todavia se expone como accion guiada desde el
admin. Sin esa captura, el codigo y la especificacion vuelven a divergir, y el
operador sigue sin una forma directa de disparar el analisis desde el workflow
del caso.

## What Changes

- Formalizar que un punto de pericia puede ejecutarse sobre carpetas de
  evidencia y expandirse recursivamente a sus archivos.
- Formalizar la extraccion y matching sobre varios tipos de archivo, incluyendo
  registro de metadata, fechas y ocurrencias multiples.
- Formalizar la exportacion de cada ocurrencia al volumen de salida con
  estructura por `nro_pericia/dispositivo/punto/tipoArchivo`.
- Formalizar la creacion de artefactos preservados derivados de los hallazgos.
- Agregar una accion guiada en admin para ejecutar el analisis desde el
  contexto del caso, plan o dispositivo.

## Capabilities

### New Capabilities
- `guided-pericia-point-runner`: cubre la ejecucion operativa de puntos de
  pericia sobre carpetas o archivos de evidencia con salida exportable.

### Modified Capabilities
- `pericia-points`: cambian los requisitos de ejecucion, matching, metadata y
  trazabilidad exportable del motor base.
- `admin-workflow-ui`: agrega una accion guiada para disparar la ejecucion del
  analisis desde el backoffice.

## Impact

- Codigo afectado: `src/dfir_pericia/extractors.py`,
  `src/dfir_pericia/matchers.py`, `src/dfir_pericia/services.py`,
  `src/dfir_pericia/tasks.py`, `src/dfir_pericia/management/commands/`,
  `src/dfir_analysis/admin.py`, `src/dfir_cases/admin.py`.
- Runtime afectado: volumen `EVIDENCE_OUTPUT_PATH`, ejecucion Celery/admin y
  trazabilidad de artefactos preservados.
- Tests afectados: ejecucion pericial, workflow de caso y admin guiado.
