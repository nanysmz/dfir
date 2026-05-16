## Why

La lista de `Archivos de evidencia` hoy muestra nombre, tipo y ruta, pero no deja ver fácilmente a qué pericia pertenece cada archivo ni con qué dispositivos está asociado. Eso obliga a abrir varios registros o reconstruir contexto desde la ruta, dificultando la revisión operativa y la trazabilidad rápida del material analizado.

## What Changes

- Mostrar en `Archivos de evidencia` referencias visibles a la pericia asociada y a los dispositivos o elementos de evidencia que usan cada archivo.
- Hacer que ese contexto también esté disponible dentro del detalle del archivo para entender rápidamente su rol dentro del caso.
- Mejorar la UX del admin para distinguir archivos huérfanos, archivos compartidos por más de un dispositivo y archivos ligados a una sola pericia.
- Mantener la lógica actual de vinculación entre `EvidenceFile` y `EvidenceItem`, sin cambiar el modelo conceptual del archivo de evidencia.

## Capabilities

### New Capabilities
- `evidence-file-case-context`: contexto visible de pericia y dispositivos asociados para cada archivo de evidencia dentro del backoffice.

### Modified Capabilities
- `admin-workflow-ui`: la grilla y el detalle de `Archivos de evidencia` deben mostrar contexto operativo suficiente para ubicar cada archivo dentro de la pericia actual.
- `evidence-item-source-unification`: los archivos derivados de una fuente primaria deben presentarse con su vínculo visible hacia los dispositivos que los resolvieron.

## Impact

- Admin de `EvidenceFileProxy` y posible detalle del registro.
- Querysets o anotaciones para exponer pericia y dispositivos relacionados.
- Tests del admin de evidencia y de relaciones entre `EvidenceFile` y `EvidenceItem`.
