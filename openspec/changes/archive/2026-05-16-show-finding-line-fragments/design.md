## Context

Los hallazgos textuales hoy guardan un `matched_value`, un `context` corto y un
`source_locator` básico con offsets. Eso alcanza para búsquedas simples, pero
no para mostrar evidencia legible en el admin ni para exportar un fragmento que
el operador pueda revisar rápidamente con suficiente contexto.

El sistema ya genera hallazgos desde texto normalizado y desde OCR/labels de
imagen. Para texto, el matcher conoce la posición exacta de la coincidencia
dentro del contenido, lo que permite reconstruir un fragmento por líneas en vez
de un recorte fijo por caracteres. Para imagen u otros formatos no lineales, el
cambio debe degradar con gracia y seguir mostrando el `context` actual cuando no
exista una noción clara de línea.

## Goals / Non-Goals

**Goals:**
- Preservar, para hallazgos textuales, una ventana contextual basada en líneas
  con la línea coincidente identificada explícitamente.
- Hacer que el admin y los artefactos exportados puedan mostrar ese contexto
  con resaltado de la línea del hallazgo.
- Mantener compatibilidad con hallazgos viejos y con hallazgos no textuales.

**Non-Goals:**
- Rediseñar en este cambio la estrategia de cardinalidad entre puntos
  solicitados, puntos de pericia y planes de análisis.
- Implementar renderizado rico de texto con HTML complejo o anotaciones
  colaborativas.
- Resolver en este cambio todos los formatos no textuales con semántica de
  líneas equivalente.

## Decisions

### El fragmento contextual vive estructurado en metadatos del hallazgo
Se almacenará una estructura derivada del matcher con:
- índice de línea coincidente
- líneas anteriores y posteriores
- contenido textual completo del fragmento
- offsets o localizadores ya existentes cuando apliquen

Rationale:
- Permite renderizar el mismo dato en admin, exportaciones y futuras vistas.
- Evita recalcular el fragmento en cada lectura si el contenido original ya no
  está disponible o si cambian las rutas.

Alternativa considerada:
- Recalcular el fragmento al vuelo desde `EvidenceFile`. Se descarta porque
  introduce dependencia fuerte del archivo actual y hace más frágil la
  trazabilidad histórica del hallazgo.

### Para texto se usará ventana por líneas, no por caracteres
El matcher textual dejará de persistir solo un recorte fijo por caracteres y
pasará a construir una ventana aproximada de `+- 10` líneas alrededor de la
coincidencia.

Rationale:
- La lectura forense suele depender del contexto inmediato por renglones.
- Resaltar una línea completa es mucho más interpretable que un substring.

Alternativa considerada:
- Mantener ventana por caracteres y solo resaltar el substring. Se descarta
  porque puede cortar frases y no comunica bien ubicación dentro del documento.

### El admin debe degradar con gracia cuando no haya fragmento lineal
Si un hallazgo viejo o no textual no tiene estructura por líneas, la UI seguirá
mostrando el `context` corto existente.

Rationale:
- Evita migraciones destructivas o necesidad de recalcular todos los hallazgos
  históricos antes de poder usar la nueva UI.

### La exploración de múltiples acciones queda como criterio, no como cambio de modelo
La revisión conceptual sugiere mantener como default `1 plan = varias acciones`
cuando el objetivo pericial y el alcance son los mismos, y reservar planes
separados para estrategias realmente independientes.

Rationale:
- El modelo actual ya soporta `structured_actions` múltiples por plan.
- Este cambio de hallazgos no requiere redefinir esa cardinalidad para aportar
  valor inmediato.

## Risks / Trade-offs

- [Mayor tamaño en `engine_metadata` o `source_locator`] → Mitigar usando una
  estructura compacta y evitando duplicar texto innecesario fuera del fragmento.
- [Hallazgos viejos sin fragmento enriquecido] → Mitigar con fallback al campo
  `context`.
- [Diferencias entre formatos textuales y no textuales] → Mitigar definiendo
  explícitamente degradación para OCR/imágenes y cubriéndolo en tests.

## Migration Plan

- Extender el pipeline de matching textual para poblar el fragmento enriquecido
  en hallazgos nuevos.
- Mantener compatibilidad de lectura con hallazgos existentes.
- Ajustar exportaciones y admin para leer primero el fragmento estructurado y,
  si no existe, usar `context`.

## Open Questions

- Si el fragmento estructurado conviene vivir en `source_locator`,
  `engine_metadata` o un campo dedicado de `PericiaFinding`.
- Si el resaltado en admin debe ser solo visual por línea o también marcar el
  substring exacto dentro de esa línea.
