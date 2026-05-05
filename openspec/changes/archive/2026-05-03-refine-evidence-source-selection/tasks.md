## 1. Evidence Source Paths

- [x] 1.1 Permitir que `EvidenceFileAdminForm` valide y acepte rutas que sean
  archivos o carpetas existentes.
- [x] 1.2 Actualizar el help text de `EvidenceFile` para explicar que la ruta
  puede apuntar a un archivo o a una carpeta de evidencia.
- [x] 1.3 Extender el endpoint de autocompletado de `EvidenceFile` para
  devolver archivos y carpetas con rotulos distinguibles.
- [x] 1.4 Hacer que `EvidenceItem` seleccione su evidencia principal por ruta
  montada y cree o vincule el `EvidenceFile` correspondiente.
- [x] 1.5 Hacer que `Parent item` muestre el contexto de la carpeta montada o
  de la pericia.

## 2. Guided Evidence Safety

- [x] 2.1 Hacer que `seed_device_types` no genere plantillas adicionales cuando
  el caso ya tiene elementos de evidencia.
- [x] 2.2 Hacer que la accion guiada del admin muestre warning y preserve la
  navegacion a `Elementos de evidencia` cuando el seed queda bloqueado.

## 3. Verification

- [x] 3.1 Cubrir formularios y autocompletado con tests que validen seleccion
  de archivos y carpetas para `EvidenceFile`.
- [x] 3.2 Cubrir con tests el flujo guiado donde un caso con dispositivos
  existentes no debe inflarse con un lote nuevo de plantillas.
- [x] 3.3 Verificar estos cambios en el entorno dockerizado del proyecto.
