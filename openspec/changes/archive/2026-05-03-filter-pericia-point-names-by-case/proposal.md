## Why

Hoy el alta de `Puntos de pericia` en `Analisis` expone `Name` como un campo
libre y sin contexto de pericia. Eso obliga al operador a recordar o reescribir
manualmente el punto correcto, mezcla definiciones globales con casos ajenos y
favorece inconsistencias entre lo pedido en una pericia y el nombre usado en la
estrategia de análisis.

## What Changes

- Permitir que el flujo de alta/edición de `Puntos de pericia` se inicie desde
  una `Pericia case` concreta.
- Hacer que `Name` pueda seleccionarse desde los puntos solicitados o puntos de
  pericia asociados con esa pericia, en lugar de depender solo de texto libre
  global.
- Mantener la posibilidad de reutilización del catálogo de `PericiaPoint`, pero
  priorizando una UX guiada por caso cuando el operador trabaja dentro de una
  pericia específica.
- Evitar que el operador vea o seleccione nombres irrelevantes de otras
  pericias en el flujo normal del admin.

## Capabilities

### New Capabilities
- `pericia-point-case-scoped-name-selection`: cubre la selección contextual del
  nombre del punto de pericia a partir de una pericia concreta.

### Modified Capabilities
- `pericia-points`: cambia la forma en que se inicia y completa la definición
  de un punto cuando existe contexto de pericia.
- `admin-workflow-ui`: cambia la UX del formulario de `Puntos de pericia` para
  responder al caso seleccionado y mostrar solo opciones relevantes.
- `pericia-report-workflow`: cambia el puente entre puntos solicitados del caso
  y estrategias operativas creadas desde el dominio de análisis.

## Impact

- Código afectado: `src/dfir_core/admin_forms.py`,
  `src/dfir_analysis/admin.py` y probablemente JS liviano del admin para
  reaccionar al cambio de pericia.
- Tests afectados: formularios y vistas del admin de `PericiaPoint`.
- Riesgo principal: mantener la distinción entre catálogo reutilizable y uso
  contextual por caso sin romper flujos existentes donde un punto todavía se
  crea manualmente.
