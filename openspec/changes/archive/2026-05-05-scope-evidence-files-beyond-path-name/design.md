## Context

En una práctica pericial real, dos dispositivos de distintas pericias pueden contener carpetas o archivos con los mismos nombres, e incluso con estructuras internas muy parecidas, pero con contenido completamente distinto. Si el sistema infiere identidad de evidencia a partir del nombre visible, del basename o de una ruta aparente sin considerar contexto pericial y contenido verificable, puede terminar mezclando asociaciones entre casos diferentes.

El modelo actual ya vincula `EvidenceFile` con `EvidenceItem` y deriva archivos desde fuentes primarias, pero el cambio necesita formalizar que la identidad operativa de la evidencia no depende solo de cómo se llama un archivo o carpeta. Esto toca reglas de vinculación, UI del admin y posiblemente criterios de unicidad o resolución.

## Goals / Non-Goals

**Goals:**
- Definir una identidad contextual de evidencia que incluya pericia, dispositivo asociado y contenido verificable cuando exista.
- Evitar equivalencias implícitas entre archivos/carpetas homónimos de contextos distintos.
- Hacer visible en la UI cuándo existen nombres repetidos pero evidencias distintas.
- Preservar trazabilidad correcta al derivar archivos desde fuentes primarias.

**Non-Goals:**
- Rediseñar por completo el flujo de importación o adquisición forense.
- Resolver en este cambio deduplicación global de contenido entre todos los casos.
- Reemplazar toda la semántica de rutas montadas por un sistema de almacenamiento nuevo.

## Decisions

### La identidad operativa no depende solo del nombre
El sistema debe tratar nombres coincidentes como insuficientes para establecer identidad. La equivalencia entre dos archivos o carpetas requerirá, como mínimo, mismo contexto pericial o una verificación explícita basada en contenido o referencia canónica soportada.

Rationale:
- Evita cruces incorrectos entre pericias.
- Alinea el sistema con la lógica forense: el nombre es descriptivo, no identidad suficiente.

Alternativa considerada:
- Mantener identidad implícita por nombre/ruta visible. Se descarta porque es precisamente el riesgo que el cambio busca eliminar.

### El contexto pericial/dispositivo debe participar en la vinculación
La resolución de evidencia derivada desde `EvidenceItem` debe preservar el caso y el dispositivo que originan esa relación, incluso si otro caso produce archivos con nombres equivalentes.

Rationale:
- La trazabilidad requiere saber de qué dispositivo/caso proviene una asociación.
- Reduce la posibilidad de reutilizar evidencia ajena por homonimia.

### La UI debe mostrar homonimia sin colapsar contexto
La interfaz de evidencia debe poder mostrar que existen nombres repetidos en distintos contextos y destacar que se trata de evidencias diferentes.

Rationale:
- El operador necesita confiar en lo que ve sin abrir muchos registros.
- La diferenciación visible es tan importante como la regla de backend.

## Risks / Trade-offs

- [Mayor complejidad en reglas de identidad] → Mitigar documentando claramente qué se considera coincidencia válida y cubriéndolo con tests de colisión.
- [Tensión con unicidades existentes] → Mitigar definiendo transición explícita si alguna restricción actual resulta demasiado estrecha para la nueva premisa.
- [UI más densa en listados] → Mitigar con resúmenes compactos y detalle ampliado solo cuando haga falta.

## Migration Plan

- Revisar si las reglas actuales de unicidad o resolución necesitan ampliarse para contemplar contexto pericial.
- Ajustar el flujo de derivación y asociación antes de introducir cambios visuales que dependan de esa identidad corregida.
- Verificar con fixtures de nombres repetidos en distintas pericias que el sistema no mezcle asociaciones.

## Open Questions

- Si la identidad contextual debe reflejarse también en restricciones de base de datos o si alcanza con reglas de aplicación.
- Si el contenido verificable mínimo será `sha256`, ruta canónica por caso, o una combinación de ambos según disponibilidad.
