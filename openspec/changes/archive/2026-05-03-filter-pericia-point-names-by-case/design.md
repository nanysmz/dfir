## Context

`PericiaPoint` hoy funciona como un catálogo reutilizable de estrategias de
análisis. Sin embargo, el uso real del admin está cada vez más guiado por caso:
el operador entra a una pericia, carga puntos solicitados, arma planes de
análisis y ejecuta estrategias. En ese contexto, crear un `PericiaPoint` con un
`Name` libre y sin referencia al caso deja una brecha entre el lenguaje del
expediente y el catálogo técnico.

La necesidad no parece ser volver `PericiaPoint` estrictamente case-scoped en
datos, sino hacer que el formulario pueda nacer con una pericia activa y
ofrecer como nombre opciones derivadas de ese caso.

## Goals / Non-Goals

**Goals:**
- Permitir crear o editar un `PericiaPoint` desde una pericia seleccionada.
- Hacer que `Name` ofrezca solo nombres relevantes para esa pericia cuando
  exista contexto de caso.
- Mantener compatibilidad con la naturaleza reutilizable del catálogo de
  `PericiaPoint`.

**Non-Goals:**
- No convertir `PericiaPoint` en un modelo exclusivamente ligado a una pericia.
- No reemplazar `RequestedPoint` por `PericiaPoint`.
- No rediseñar el pipeline de ejecución ni el modelo de `AnalysisPlan`.

## Decisions

### 1. El contexto de pericia será explícito en el formulario

El admin de `PericiaPoint` debe aceptar una `Pericia case` seleccionada, ya sea
como campo visible o como valor preseleccionado desde navegación contextual.
Ese contexto ordena el resto de las opciones del formulario.

Alternativa considerada: inferir el caso solo desde querystring o desde la
pantalla anterior. Se descarta como única estrategia porque no deja visible el
contexto actual ni permite corregirlo fácilmente.

### 2. `Name` debe ofrecer selección contextual, sin perder fallback manual

Cuando hay una pericia seleccionada, `Name` debe comportarse como selector de
opciones relevantes del caso, derivadas de sus puntos solicitados o de las
definiciones ya asociadas a esa pericia. Cuando no hay contexto de caso, el
formulario puede conservar el fallback libre o global para no romper flujos
preexistentes.

Alternativa considerada: reemplazar siempre `Name` por texto libre autogenerado
desde `RequestedPoint`. Se descarta porque eliminaría control en casos donde el
analista necesita ajustar la formulación técnica.

### 3. La UI debe reaccionar si cambia la pericia

Si el operador cambia la `Pericia case` en la misma pantalla, el selector de
`Name` debe refrescarse para no mantener opciones ajenas al nuevo caso. La
solución esperable es una mejora JS ligera siguiendo el patrón ya usado en otros
formularios dependientes del admin.

### 4. La integridad sigue respaldada por validación server-side

Aunque el selector quede contextualizado, el backend debe seguir validando que
las asociaciones o nombres derivados respeten el caso activo y no provengan de
una pericia distinta.

## Risks / Trade-offs

- [La UX puede volverse confusa si conviven selección contextual y texto libre]
  → Mitigación: definir una jerarquía clara entre modo contextual y fallback
  manual/global.
- [El catálogo reutilizable puede parecer case-scoped aunque no lo sea]
  → Mitigación: dejar explícito que el caso guía el nombre sugerido, no la
  propiedad permanente del modelo.
- [El cambio puede requerir endpoint o JS adicional en el admin]
  → Mitigación: reutilizar el patrón liviano ya adoptado para otros selects
  dependientes en el backoffice.

## Migration Plan

1. Agregar el contexto de `Pericia case` al flujo del admin de `PericiaPoint`.
2. Hacer que `Name` cargue opciones filtradas por la pericia activa.
3. Añadir reacción dinámica cuando cambie el caso dentro del formulario.
4. Verificar el comportamiento en tests de formulario y en el admin dockerizado.

## Open Questions

- ¿`Name` debe alimentarse solo desde `RequestedPoint` o también desde puntos de
  pericia ya usados previamente en esa misma pericia?
- ¿El fallback sin caso debe seguir siendo texto libre puro o conviene ofrecer
  también un catálogo global sugerido?
