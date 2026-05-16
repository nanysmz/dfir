## Why

Hoy cada hallazgo conserva un `context` corto, pero no alcanza para mostrar de
forma confiable dónde apareció la coincidencia dentro del texto analizado. En
una pericia, el operador necesita ver una fracción legible del documento, con
la línea exacta resaltada y suficiente contexto alrededor para interpretar el
hallazgo sin perder trazabilidad.

## What Changes

- Agregar soporte para fragmentos textuales por líneas alrededor del hallazgo,
  incluyendo línea coincidente y líneas vecinas.
- Hacer visible en el admin y en las salidas derivadas de hallazgos un bloque
  de contexto legible con resaltado de la línea encontrada.
- Preservar compatibilidad con hallazgos no textuales o hallazgos viejos que
  solo tengan `context` corto.
- Definir una representación estructurada del fragmento para que pueda
  reutilizarse tanto en UI como en exportaciones.

## Capabilities

### New Capabilities
- `finding-context-fragments`: representación estructurada de contexto por
  líneas para cada hallazgo textual, con línea coincidente identificada y
  ventana configurable alrededor.

### Modified Capabilities
- `admin-workflow-ui`: el admin de hallazgos y resultados debe mostrar el
  fragmento textual con la línea del hallazgo resaltada.
- `pericia-report-workflow`: las salidas derivadas y la trazabilidad del
  hallazgo deben poder incluir el fragmento contextual legible, no solo el
  valor encontrado.

## Impact

- Matchers y persistencia de `PericiaFinding`.
- Exportaciones JSON o artefactos derivados de hallazgos.
- Admin de hallazgos/resultados y cualquier vista que hoy muestre `context`.
- Tests de matching textual, admin y exportación.
