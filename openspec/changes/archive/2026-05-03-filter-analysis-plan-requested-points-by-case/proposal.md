## Why

Hoy el formulario de `Planes de analisis` deja desplegar `Requested point`
desde todo el universo de puntos cargados, aunque el operador ya haya elegido
una `Pericia case`. Eso genera ruido, riesgo de selección equivocada y una UX
que contradice el propio modelo, donde un plan solo puede vincularse a puntos
del mismo caso.

## What Changes

- Filtrar el campo `Requested point` para que solo muestre puntos asociados con
  la `Pericia case` seleccionada en el formulario.
- Mantener el filtrado tanto al abrir un plan existente como al crear uno nuevo
  y cambiar el caso dentro del flujo de edición.
- Preservar la validación de integridad del modelo como respaldo, pero evitar
  que el error llegue al operador recién al guardar.

## Capabilities

### New Capabilities
- `analysis-plan-dependent-requested-point-filter`: cubre el filtrado dependiente
  del selector `Requested point` por caso pericial.

### Modified Capabilities
- `pericia-report-workflow`: cambia la forma en que un plan de análisis expone
  y selecciona los puntos solicitados dentro del caso.
- `admin-workflow-ui`: cambia la UX del formulario de `Planes de analisis` para
  que el selector responda al caso ya elegido.

## Impact

- Código afectado: `src/dfir_core/admin_forms.py`, posiblemente
  `src/dfir_analysis/admin.py` y el JS del admin si hace falta reacción dinámica.
- Tests afectados: formularios de admin y vistas del backoffice para
  `AnalysisPlan`.
- Riesgo principal: asegurar que el filtro funcione tanto en formularios nuevos
  como en edición de planes ya existentes sin perder compatibilidad.
