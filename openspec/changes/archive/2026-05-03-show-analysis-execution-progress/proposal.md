## Why

Hoy, una vez cargados los planes de análisis, el operador puede disparar una
ejecución, pero no tiene una señal clara de que el análisis está corriendo de
verdad, cuánto avanzó ni en qué estado quedó. Eso vuelve opaca una etapa crítica
del workflow y obliga a inferir el progreso mirando objetos técnicos en lugar de
recibir feedback operativo directo.

## What Changes

- Mostrar explícitamente cuándo un análisis está pendiente, en ejecución,
  completado, fallido o bloqueado.
- Exponer avance visible de la ejecución desde el contexto del plan, del caso o
  ambos, sin obligar al operador a navegar a modelos técnicos para entender qué
  está pasando.
- Hacer que la ejecución guiada del análisis deje trazas de progreso y estado
  consumibles por la UI del admin.
- Permitir distinguir análisis todavía no iniciados de análisis ya lanzados
  pero incompletos.

## Capabilities

### New Capabilities
- `analysis-execution-progress-visibility`: cubre el seguimiento visible del
  estado y avance de ejecuciones de análisis disparadas desde el workflow
  pericial.

### Modified Capabilities
- `admin-workflow-ui`: cambia la UX del backoffice para mostrar estado y avance
  del análisis después de crear los planes.
- `pericia-report-workflow`: cambia la etapa de análisis para distinguir planes
  preparados de ejecuciones efectivamente corriendo o finalizadas.
- `pericia-points`: cambia las expectativas de ejecución para incluir señales de
  progreso y estado consumibles por la UI.

## Impact

- Código afectado: `src/dfir_analysis/admin.py`, `src/dfir_pericia/tasks.py`,
  `src/dfir_pericia/services.py`, `src/dfir_pericia/workflow.py`, y templates o
  bloques del admin guiado.
- Tests afectados: admin guiado, ejecuciones periciales y workflow del caso.
- Riesgo principal: mantener feedback de progreso útil sin convertir la UI en
  una consola técnica ni introducir falsa precisión si la ejecución todavía no
  reporta granularidad suficiente.
