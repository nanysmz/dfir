## Why

El backoffice todavia mezcla etiquetas en ingles con una operacion pensada para
peritos de Buenos Aires, y eso se nota especialmente en el modulo de analisis.
Ademas, el formulario de `Planes de analisis` no esta permitiendo definir bien
`Analysis targets`, y el modulo carece de una secuencia explicita que indique
en que orden conviene trabajar.

## What Changes

- Unificar la experiencia operatoria del admin para que los textos visibles del
  flujo principal queden en español, con referencias temporales consistentes
  con `GMT-3` y `America/Argentina/Buenos_Aires`.
- Corregir el flujo de `Analisis -> Planes de analisis` para que el operador
  pueda seleccionar y editar el alcance de `Analysis targets` como ubicaciones
  reales de evidencia dentro del volumen montado.
- Aclarar el orden recomendado del modulo `Administracion de Analisis`,
  diferenciando catalogo reusable, planes por caso, ejecuciones y resultados.
- Mejorar la terminologia visible del modulo de analisis para que evite
  combinaciones confusas de nombres en ingles y español.

## Capabilities

### New Capabilities
- `analysis-admin-operational-order`: cubre la secuencia recomendada del modulo
  de analisis para que el operador entienda que crear, que parametrizar, que
  ejecutar y que revisar en cada etapa.

### Modified Capabilities
- `admin-workflow-ui`: cambia la localizacion visible del admin y la claridad
  del flujo operatorio en el modulo de analisis.
- `pericia-report-workflow`: cambia como el flujo guiado explica la etapa de
  analisis dentro de la secuencia general del caso.
- `analysis-plan-playbooks`: cambia la forma en que un plan de analisis define
  y permite editar el alcance de ubicaciones objetivo para su ejecucion.

## Impact

- Codigo afectado: `src/dfir_analysis/`, `src/dfir_core/admin_forms.py`,
  `src/dfir_cases/admin.py`, `src/dfir_app/settings.py`, assets JS del admin,
  y tests de admin y workflow.
- Riesgos principales: cambiar textos visibles sin cubrir todos los puntos del
  flujo, romper el selector actual de `analysis_targets`, o introducir una
  secuencia operatoria confusa entre catalogo, planes y ejecuciones.
- Sistemas afectados: Django admin tematico, formularios de analisis,
  workflow guiado por caso y consistencia de localizacion del backoffice.
