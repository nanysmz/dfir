## Context

`AnalysisPlan` ya tiene una restricción lógica clara: `requested_point` debe
pertenecer al mismo `pericia_case`. El modelo lo valida al guardar, pero el
formulario del admin todavía expone un dropdown demasiado amplio y eso traslada
al operador una decisión que el sistema ya conoce por contexto.

En la práctica, el operador primero selecciona la pericia y recién después
elige cuál punto solicitado dentro de ese caso quiere planificar. Si el
selector no se reduce a ese subconjunto, el formulario muestra opciones
irrelevantes y favorece errores evitables.

## Goals / Non-Goals

**Goals:**
- Hacer que `Requested point` se limite a los puntos del caso seleccionado.
- Mantener ese comportamiento tanto en alta como en edición.
- Reducir la posibilidad de combinaciones inválidas antes del `save()`.

**Non-Goals:**
- No rediseñar el modelo `AnalysisPlan`.
- No cambiar la semántica de `RequestedPoint`.
- No introducir una dependencia frontend compleja si el problema puede
  resolverse con un filtrado de formulario simple o con una mejora pequeña.

## Decisions

### 1. El queryset de `requested_point` debe derivarse del caso seleccionado

El formulario debe construir `requested_point.queryset` a partir de:
- `instance.pericia_case` en edición
- `data["pericia_case"]` en POST
- `initial["pericia_case"]` cuando aplique

Eso hace que el dropdown ya nazca consistente con el caso activo.

Alternativa considerada: dejar el queryset amplio y depender solo de la
validación del modelo. Se descarta porque corrige demasiado tarde.

### 2. La mejora ideal es dependiente también en la UI

Si el operador cambia `Pericia case` en un formulario nuevo, el selector de
`Requested point` debería reaccionar y mostrar solo las opciones válidas para el
nuevo caso. Según el nivel de soporte ya presente en el admin, esto puede
resolverse:
- solo server-side en el request actual
- o con una pequeña mejora JS/autocomplete dependiente

La primera entrega puede empezar por server-side si eso deja el flujo correcto
al cargar y guardar; la segunda lo hace más natural en la interacción.

### 3. La validación del modelo sigue siendo respaldo, no primera línea de UX

Aunque el selector quede bien filtrado, la validación de integridad en
`AnalysisPlan.clean()` debe mantenerse para cubrir casos no interactivos,
ediciones parciales o manipulaciones del request.

## Risks / Trade-offs

- [El filtro puede no reaccionar cuando el usuario cambia el caso en caliente]
  → Mitigación: contemplar una mejora JS ligera si el comportamiento server-side
  no alcanza para el flujo real.
- [Un plan existente podría abrir con un queryset vacío si el caso no se
  resuelve bien] → Mitigación: priorizar `instance.pericia_case` en edición.
- [El admin podría seguir mostrando la opción antigua seleccionada aunque ya no
  sea válida tras cambiar de caso] → Mitigación: asegurar fallback de valor
  actual y revalidación clara.

## Migration Plan

1. Filtrar `requested_point` en el formulario a partir del caso activo.
2. Agregar tests para alta y edición de `AnalysisPlan`.
3. Verificar si hace falta reacción dinámica adicional cuando cambia el caso en
   la UI del admin dockerizado.

## Open Questions

- ¿Alcanza con el filtrado server-side del form en este admin, o el flujo real
  necesita actualización dinámica al cambiar `Pericia case` sin recargar?
