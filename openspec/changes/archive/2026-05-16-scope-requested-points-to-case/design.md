## Context

El dominio ya modela `RequestedPoint` como una entidad dependiente de
`PericiaCase` y además impone unicidad por `(pericia_case, order)`. Sin
embargo, la carga inline dentro de `Casos periciales` sigue dejando demasiado
trabajo manual al operador: nuevos formularios pueden arrancar con el mismo
`order`, el mensaje de error es técnico y el flujo no deja suficientemente
claro que esos puntos existen solo dentro de la pericia actual.

El cambio afecta varias capas relacionadas:

- modelo y reglas de negocio de `RequestedPoint`
- formulario admin inline y admin dedicado
- workflow guiado del caso
- tests del backoffice

## Goals / Non-Goals

**Goals:**
- reforzar que un `Punto solicitado` es estrictamente local a una pericia
- evitar colisiones evitables de `order` al crear nuevos puntos en inline
- mejorar los mensajes y defaults del admin para que el operador no perciba
  mezcla entre puntos de distintas pericias
- preservar la unicidad por caso y el orden secuencial dentro de la pericia

**Non-Goals:**
- no transformar `RequestedPoint` en un catálogo reutilizable global
- no cambiar la semántica de `AnalysisPlan` ni `PericiaPoint`
- no rediseñar toda la UX de inline del caso
- no cambiar todavía cómo se responden los puntos en el informe

## Decisions

### 1. Mantener `RequestedPoint` como entidad case-local

No se introduce ninguna capa compartida ni reutilizable. La decisión es
reforzar el diseño actual:

- cada `RequestedPoint` pertenece a una sola `PericiaCase`
- el orden es único dentro de esa pericia
- el admin debe presentar esa relación de forma explícita

Alternativa considerada: permitir “copiar” o “referenciar” puntos entre casos.
Se descarta porque agrega ambigüedad conceptual donde el usuario justamente
está pidiendo aislamiento estricto por pericia.

### 2. Resolver el `order` como secuencia local sugerida por el formulario

El conflicto de la captura muestra que el problema no es de identidad global,
sino de ergonomía operativa. El formulario debe sugerir el próximo `order`
disponible para la pericia actual y conservar los órdenes ya existentes al
editar.

Alternativa considerada: dejar el `order` completamente manual y confiar solo
en la restricción de base. Se descarta porque lleva a errores repetibles y
mensajes tardíos.

### 3. Convertir el mensaje de validación en lenguaje de caso

Si hay conflicto de orden, la validación debe explicarlo como:

- un orden ya usado dentro de esta pericia
- no como una referencia técnica genérica al constraint de Django

Alternativa considerada: no tocar mensajes y apoyarse en el error actual. Se
descarta porque el mensaje actual no ayuda a entender el contexto del caso.

### 4. Alinear la UX inline y el admin dedicado

La regla de “solo de esta pericia” no debe vivir solo en el modelo. Debe verse
igual en:

- inline de `Casos periciales`
- admin dedicado de `Puntos solicitados`
- workflow guiado que resume el estado del caso

Esto evita que el usuario vea comportamientos inconsistentes según desde dónde
edite el punto.

## Risks / Trade-offs

- [Autonumeración sorprendente] -> Mitigar mostrando el `order` sugerido pero
  manteniendo capacidad de edición manual cuando haga falta reordenar.
- [Conflictos en múltiples formularios inline sin guardar] -> Mitigar validando
  también dentro del formset antes de llegar a la base de datos.
- [Ambigüedad entre “pertenece al caso” y “orden dentro del caso”] ->
  Mitigar con labels y mensajes que nombren siempre a la pericia actual.
- [Cambio de UX sin cambio de modelo] -> Es aceptable porque el modelo actual
  ya expresa la regla correcta; el problema principal es de experiencia y
  validación temprana.
