## Why

Al crear o editar una pericia nueva, los `Puntos solicitados` deben quedar
inequivocamente asociados a esa pericia y no generar ambiguedades operativas ni
errores evitables en el alta inline. Hoy el dominio ya modela el punto por
caso, pero la UX sigue permitiendo choques de orden y mensajes confusos que
hacen parecer que el punto no es estrictamente local al caso actual.

## What Changes

- Ajustar la experiencia de carga de `Puntos solicitados` para que el alta
  inline dentro de una pericia proponga y preserve un orden local al caso en
  vez de empujar colisiones manuales.
- Reforzar la validacion y el mensaje operatorio para que cualquier conflicto de
  `order` se explique como un problema interno de esa pericia, no como una
  posible mezcla con otros casos.
- Alinear la UX del admin para que crear, editar y borrar puntos solicitados se
  entienda como una operacion exclusiva del caso actual.
- Mantener la restriccion de unicidad por `pericia_case + order`, pero volverla
  mas amigable y predecible en formularios inline y flujos guiados.

## Capabilities

### New Capabilities

- `requested-point-case-scoping`: cubre la experiencia operatoria y las reglas
  para que los puntos solicitados existan y se administren como datos propios
  de una unica pericia.

### Modified Capabilities

- `admin-workflow-ui`: cambia la UX del admin en la carga inline de `Puntos
  solicitados` para evitar colisiones de orden y reforzar el contexto de caso.
- `pericia-report-workflow`: aclara que los puntos solicitados se capturan y
  ordenan dentro del caso pericial actual, sin compartirse entre pericias.

## Impact

- Codigo afectado: `RequestedPoint`, formularios admin de caso y puntos
  solicitados, validaciones inline, tests de admin y workflow.
- Sin impacto API externo.
- Sin dependencias nuevas.
