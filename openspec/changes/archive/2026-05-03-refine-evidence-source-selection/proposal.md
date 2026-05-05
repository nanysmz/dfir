## Why

El flujo de evidencia todavia tenia dos asperezas operativas: `Evidence file`
solo aceptaba archivos regulares aunque en la practica tambien necesitamos
apuntar a carpetas completas, y la accion guiada para cargar plantillas de
dispositivos podia inflar un caso ya iniciado creando muchos elementos
adicionales. Esto genera errores de carga, confusion visual y estados de caso
que no reflejan la realidad del expediente.

## What Changes

- Permitir que `Evidence file` seleccione y valide tanto archivos como
  carpetas dentro de los volumenes montados o en otras rutas validas del
  filesystem visible para el contenedor.
- Hacer que el autocompletado de `Evidence file` sugiera carpetas y archivos
  con rotulos distinguibles para que el operador sepa que esta eligiendo.
- Hacer que `Evidence item` use tambien seleccion por ruta montada para su
  evidencia principal, sin depender de un dropdown de objetos ya precargados.
- Hacer que `Parent item` muestre el contexto de la carpeta montada o de la
  pericia, para que el operador vea de que raiz de evidencia cuelga cada
  dispositivo.
- Hacer que la accion guiada de carga de plantillas de dispositivos solo se
  ejecute en casos sin elementos de evidencia existentes.
- Mostrar una advertencia explicita cuando el operador intente cargar el lote
  guiado sobre un caso que ya tiene dispositivos o fuentes de evidencia.

## Capabilities

### New Capabilities
- `evidence-source-selection`: cubre la seleccion y validacion de rutas de
  evidencia en admin para archivos y carpetas, incluyendo evidencia principal y
  jerarquia visible de parent item.

### Modified Capabilities
- `admin-workflow-ui`: la accion guiada para cargar tipos de dispositivo cambia
  su comportamiento para evitar duplicaciones en casos ya iniciados.

## Impact

- Codigo afectado: `src/dfir_core/admin_forms.py`,
  `src/dfir_evidence/admin.py`,
  `src/dfir_pericia/management/commands/seed_device_types.py`,
  `src/dfir_cases/admin.py`.
- Superficies afectadas: admin de `Evidence file`, admin de `Evidence item`,
  acciones guiadas en detalle de caso.
- Tests afectados: formularios de admin, endpoints de autocompletado y flujo
  guiado de seed de dispositivos.
