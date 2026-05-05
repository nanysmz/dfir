## Why

La selección de `fuente primaria de evidencia del dispositivo` mezcla en un solo listado entradas del primer nivel y subrutas profundas del volumen montado. Eso vuelve confusa la elección inicial, dificulta entender qué se montó realmente y hace más probable seleccionar una ruta interna por accidente.

## What Changes

- Cambiar la experiencia de selección de `fuente primaria de evidencia del dispositivo` para que la vista inicial muestre solamente archivos y carpetas del primer nivel de cada raíz montada.
- Incorporar navegación explícita dentro de carpetas para explorar niveles internos solo cuando el operador lo necesite.
- Mantener compatibilidad con rutas ya guardadas, rutas tipeadas manualmente y validación de archivos o carpetas válidas dentro del volumen montado.
- Mejorar la comunicación visual del selector para que quede claro cuándo se está viendo la raíz montada y cuándo se está navegando dentro de una carpeta.

## Capabilities

### New Capabilities
- `mounted-source-tree-navigation`: navegación operativa por árbol montado para elegir una ruta de evidencia sin aplanar todo el contenido en un solo autocomplete.

### Modified Capabilities
- `evidence-source-selection`: la selección de rutas de evidencia deja de exponer subrutas profundas en la vista inicial y pasa a priorizar el primer nivel con exploración bajo demanda.
- `admin-workflow-ui`: la interfaz admin debe presentar el selector de fuente primaria con contexto de navegación y acciones claras para entrar, volver y confirmar rutas.

## Impact

- Código del admin de evidencia y formularios de `EvidenceItem`/`EvidenceFile`.
- Endpoint o vista de búsqueda/listado de rutas montadas.
- JavaScript del widget de autocomplete o browser de rutas montadas.
- Tests de formularios, admin y comportamiento del selector de rutas.
