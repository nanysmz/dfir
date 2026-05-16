## Context

`EvidenceItem` hoy mezcla una ruta visible (`source_path`), una referencia
principal (`evidence_file`) y una coleccion derivada (`evidence_files`). Esa
combinacion resolvia parcialmente el linking interno, pero no alcanza para el
flujo operador que muestra el admin:

- puede quedar una ruta visible que el usuario entiende como valida
- pueden existir archivos ya vinculados para ese dispositivo
- y aun asi el formulario puede rechazar el guardado de la fuente primaria

Ademas, el caso real necesita algo mas rico que una sola ruta. Un mismo
dispositivo puede quedar respaldado por varias carpetas o archivos relevantes,
con una fuente principal elegida por el operador y otras fuentes asociadas que
deben poder editarse o reemplazarse sin romper trazabilidad.

Por ultimo, el tipo de dispositivo ya sugiere metadatos tecnicos, pero todavia
no existe una forma suficientemente estructurada y confiable de reutilizarlos
en la redaccion de `elementos ofrecidos`.

## Goals / Non-Goals

**Goals:**
- Eliminar los falsos negativos de validacion cuando una fuente ya vinculada es
  reabierta, corregida o vuelta a guardar.
- Permitir que cada `EvidenceItem` administre una fuente principal y multiples
  fuentes asociadas editables.
- Mantener compatibilidad con el linking interno existente hacia
  `evidence_file` y `evidence_files`.
- Dejar la metadata del dispositivo en una forma reutilizable para redactar
  `elementos ofrecidos`.

**Non-Goals:**
- No reemplazar `EvidenceFile` como entidad interna reusable.
- No resolver en este cambio la generacion final automatica del texto del
  informe completo.
- No rediseñar toda la estructura de resultados tecnicos o artefactos
  preservados.

## Decisions

### 1. Introducir un registro explicito de fuentes por dispositivo

Se agregara una entidad hija de `EvidenceItem` para representar cada fuente
asociada al dispositivo. Cada registro de fuente debera guardar como minimo:

- `source_path`
- tipo de origen (`file` o `directory`)
- rol (`primary` o `supporting`)
- orden o prioridad visible
- metadata opcional de observaciones

La fuente marcada como `primary` sera la que el operador entiende como fuente
principal del dispositivo. Las demas quedaran como fuentes asociadas.

Alternativa considerada: seguir usando solo `source_path` mas
`evidence_files`. Se descarta porque no permite multiples fuentes editables ni
expresa cual es la principal sin sobrecargar otros campos.

### 2. Mantener `source_path` y `evidence_file` como proyecciones de compatibilidad

Durante la transicion, `EvidenceItem.source_path` seguira existiendo como
proyeccion del `source_path` de la fuente primaria. Del mismo modo,
`EvidenceItem.evidence_file` seguira reflejando la referencia principal
resuelta para no romper el resto del dominio.

Cuando la fuente primaria cambie:
- se actualiza la proyeccion `source_path`
- se recalcula o reasocia `evidence_file`
- y se resincroniza `evidence_files` segun la politica de derivacion vigente

Alternativa considerada: migrar de una vez todo el codigo a la nueva entidad y
retirar `source_path`. Se descarta por el alto riesgo de impacto transversal.

### 3. La validacion debe resolver aliases montados y fuentes ya existentes antes de fallar

La validacion de una fuente no debe limitarse a interpretar literalmente el
texto visible. Debe:

- reconocer aliases de montaje como `/evidence/input/...`
- comparar contra los roots configurados del runtime
- aceptar fuentes ya existentes ligadas al dispositivo
- permitir editar o reemplazar la fuente sin exigir recrear manualmente los
  archivos derivados

Alternativa considerada: exigir siempre una nueva seleccion desde el
autocompletado. Se descarta porque vuelve fragil el flujo de edicion y no
resuelve el caso reportado.

### 4. La UI de `EvidenceItem` debe separar “fuente principal” de “fuentes asociadas”

El formulario principal mostrara un bloque claro con:

- una fuente principal editable
- un inline o bloque repetible de fuentes asociadas
- un resumen de archivos derivados resueltos desde la fuente principal

Eso evita que `archivos de evidencia` se perciba como el lugar donde se carga
la fuente del dispositivo.

Alternativa considerada: usar un solo campo multivalor de texto. Se descarta
porque no permite distinguir jerarquia ni brindar buenas validaciones.

### 5. La descripcion ofrecida del dispositivo debe basarse en metadata estructurada

El tipo de dispositivo seguira siendo un disparador de defaults, pero la
descripcion reportable se construira desde campos estructurados de metadata:

- clase o tipo de dispositivo
- medio e interfaz
- marca
- modelo
- numero de serie
- capacidad
- observaciones tecnicas normalizadas

Con esos datos, el workflow podra producir o sugerir un texto del estilo:
`Una (01) unidad de almacenamiento, disco electromecanico, tipo HDD, conexion SATA...`

Alternativa considerada: guardar solo texto libre para `elementos ofrecidos`.
Se descarta porque dificulta reutilizacion, consistencia y edicion posterior.

## Risks / Trade-offs

- [Una nueva entidad de fuentes agrega complejidad de modelo] -> Mitigacion:
  mantener `source_path` y `evidence_file` como proyecciones compatibles
  mientras el resto del sistema migra gradualmente.
- [Cambiar la fuente primaria puede dejar archivos derivados obsoletos] ->
  Mitigacion: recalcular los vinculados desde la nueva primaria y dejar
  explicitado que las fuentes asociadas no redefinen por si solas el set
  derivado principal.
- [La metadata historica puede no traer todos los datos para `elementos
  ofrecidos`] -> Mitigacion: compatibilidad con valores parciales y fallback a
  texto incompleto pero valido.
- [El operador podria confundir fuentes asociadas con evidencia derivada] ->
  Mitigacion: separar visualmente “fuentes del dispositivo” de “archivos de
  evidencia resueltos”.

## Migration Plan

1. Agregar el nuevo modelo de fuentes por dispositivo y poblarlo desde
   `source_path` en datos existentes.
2. Mantener sincronizada la proyeccion de la fuente primaria hacia
   `EvidenceItem.source_path` y `EvidenceItem.evidence_file`.
3. Adaptar formularios y admin para editar fuente principal y fuentes
   asociadas desde la misma pantalla.
4. Ajustar la logica de validacion y resincronizacion de `evidence_files`.
5. Introducir campos de metadata estructurada para descripcion ofrecida y
   conectarlos con el workflow de informe.

## Open Questions

- Las fuentes asociadas deben participar tambien del set derivado de
  `evidence_files`, o solo documentarse como origen adicional?
- La fuente primaria deberia aceptar multiples carpetas cuando el dispositivo
  se entrega fragmentado, o en ese caso siempre debe elegirse una sola como
  canonicamente primaria?
- La descripcion de `elementos ofrecidos` se guardara como snapshot editable en
  el dispositivo, o se renderizara siempre desde metadata viva?
