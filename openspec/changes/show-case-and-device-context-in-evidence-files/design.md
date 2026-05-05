## Context

`Archivos de evidencia` funciona hoy como un catálogo técnico de `EvidenceFile`, pero la vista principal carece de contexto pericial suficiente: el operador ve la ruta y el tipo de archivo, pero no a qué caso pertenece ni qué dispositivos o elementos de evidencia lo están utilizando. Esa carencia se vuelve especialmente problemática cuando varias pericias comparten estructuras de carpetas similares o cuando un archivo deriva de más de un dispositivo asociado.

El cambio impacta principalmente el admin de `EvidenceFileProxy`, sus querysets y la manera en que se presentan relaciones ya existentes con `EvidenceItem`. No debería exigir un rediseño del modelo de datos; la información ya está en las relaciones entre archivos, elementos de evidencia y pericias.

## Goals / Non-Goals

**Goals:**
- Mostrar en la lista de `Archivos de evidencia` el caso o pericia relacionado con cada archivo.
- Mostrar también los dispositivos o elementos de evidencia asociados al archivo.
- Distinguir visualmente casos simples, archivos compartidos y archivos sin contexto asociado.
- Reutilizar relaciones existentes entre `EvidenceFile` y `EvidenceItem`.

**Non-Goals:**
- Redefinir `EvidenceFile` como entidad dependiente de una sola pericia.
- Cambiar la lógica de derivación de archivos desde la fuente primaria.
- Resolver en este cambio una navegación avanzada por pericia dentro del catálogo de archivos.

## Decisions

### Exponer el contexto desde relaciones derivadas
La pericia y los dispositivos asociados se obtendrán a partir de los `EvidenceItem` relacionados con cada `EvidenceFile`, en lugar de duplicar esa referencia dentro del propio archivo.

Rationale:
- Evita inconsistencia entre relaciones existentes y campos redundantes.
- Conserva la flexibilidad de archivos compartidos entre varios elementos de evidencia.

Alternativa considerada:
- Agregar FK directa desde `EvidenceFile` a `PericiaCase`. Se descarta porque simplifica mal un modelo donde un archivo puede relacionarse con más de un item o quedar temporalmente huérfano.

### Mostrar resumen compacto en lista y detalle ampliado en formulario
La lista debe dar una lectura rápida de `pericia` y `dispositivos asociados`, mientras que el detalle del archivo puede mostrar un resumen más claro y completo si hay múltiples asociaciones.

Rationale:
- La grilla necesita señal operativa rápida sin sobrecargarse.
- El detalle puede explicar mejor relaciones compartidas o huérfanas.

Alternativa considerada:
- Mostrar únicamente ids o counts. Se descarta porque no resuelve el problema de contexto humano.

### Representar explícitamente archivos sin contexto
Si un `EvidenceFile` no está vinculado a ningún `EvidenceItem`, la UI debe indicarlo como archivo sin asociación pericial visible en lugar de dejar campos vacíos ambiguos.

Rationale:
- Evita que el operador interprete la ausencia de datos como error visual.
- Hace más fácil detectar material cargado pero no integrado al caso.

## Risks / Trade-offs

- [Sobrecarga visual en la grilla] → Mitigar con resúmenes compactos, truncado razonable y detalle ampliado solo en el formulario.
- [Consultas pesadas por relaciones M2M] → Mitigar con `prefetch_related` o anotaciones acotadas en el admin.
- [Archivos compartidos entre varios dispositivos] → Mitigar mostrando pluralidad explícita en lugar de forzar una sola asociación visible.

## Migration Plan

- No requiere migración de datos.
- Desplegar cambios de admin y queryset juntos.
- Verificar con casos reales que archivos con una, varias o ninguna asociación se muestren correctamente.

## Open Questions

- Si conviene sumar filtros rápidos por `PericiaCase` en `Archivos de evidencia` en este mismo cambio o dejarlo para una iteración posterior.
- Si la columna de dispositivos debe mostrar labels completos o un resumen con contador y primer/primeros nombres.
