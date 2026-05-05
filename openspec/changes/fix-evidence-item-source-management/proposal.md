## Why

El flujo de `Evidencia -> Elementos de evidencia` todavia falla en un caso
central: un dispositivo puede mostrar una fuente primaria ya vinculada y, aun
asi, rechazar el guardado con el error de ruta invalida. Eso rompe la
confiabilidad operatoria y deja al analista sin una forma segura de mantener,
editar o corregir la evidencia base de cada dispositivo.

Al mismo tiempo, la UI actual trata la fuente primaria como un solo valor,
cuando en la practica un dispositivo puede quedar respaldado por una o varias
carpetas y archivos. Tambien falta una representacion mas directa del tipo y
la descripcion del dispositivo para redactar `elementos ofrecidos` en el
informe tecnico.

## What Changes

- Corregir la validacion y persistencia de la fuente primaria de evidencia para
  que el admin acepte, reabra y vuelva a guardar rutas ya vinculadas sin
  rechazos espurios.
- Redefinir la administracion de fuentes de un `EvidenceItem` para que cada
  dispositivo pueda tener una fuente principal editable y, ademas, una o
  varias fuentes asociadas complementarias, todas trazables desde el admin.
- Aclarar la UX del bloque de fuentes para que el operador pueda seleccionar,
  editar o cambiar la fuente principal del dispositivo sin perder los archivos
  derivados ya resueltos.
- Enriquecer los metadatos del tipo de dispositivo para soportar la redaccion
  posterior de `elementos ofrecidos`, incluyendo atributos como marca, modelo,
  numero de serie, interfaz y capacidad.
- Hacer que la informacion estructurada del dispositivo quede lista para ser
  reutilizada por el flujo de informe, en especial por la seccion `elementos
  ofrecidos`.

## Capabilities

### New Capabilities
- `device-offered-item-description`: cubre la representacion estructurada de un
  dispositivo para reutilizar sus datos tecnicos en la redaccion de `elementos
  ofrecidos`.

### Modified Capabilities
- `evidence-source-selection`: cambia como el admin valida, guarda y vuelve a
  editar rutas de evidencia para dispositivos cuando la ruta ya existe o debe
  corregirse.
- `evidence-item-source-unification`: amplía la nocion de fuente primaria
  canonica para permitir una fuente principal editable junto con multiples
  fuentes asociadas por dispositivo.
- `admin-workflow-ui`: cambia la UX del formulario de `EvidenceItem` para que
  el bloque de fuentes sea editable, entendible y consistente con la evidencia
  ya vinculada.
- `pericia-report-workflow`: cambia la informacion que un dispositivo expone
  hacia el informe para poblar `elementos ofrecidos` con descripcion tecnica
  reusable.

## Impact

- Codigo afectado: `src/dfir_core/admin_forms.py`,
  `src/dfir_evidence/admin.py`, `src/dfir_cases/admin.py`,
  `src/dfir_pericia/models.py`, posibles migraciones de metadatos, y tests de
  admin, workflow e informe.
- Riesgos principales: cambiar la semantica visible de `source_path` y
  `evidence_files`, introducir fuentes multiples sin perder compatibilidad con
  datos existentes, y acoplar correctamente la metadata del dispositivo con la
  redaccion del informe.
- Sistemas afectados: backoffice Django admin, linking y sincronizacion de
  `EvidenceFile`, flujo guiado del caso, y generacion de contenido para el
  informe pericial.
