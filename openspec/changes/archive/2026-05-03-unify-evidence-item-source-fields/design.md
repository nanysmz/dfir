## Context

El formulario de `EvidenceItem` hoy mezcla tres capas:

- una referencia primaria (`Evidence file`)
- una carpeta de evidencia del dispositivo (`source_path`)
- y una colección derivada de archivos vinculados (`evidence_files`)

Para el modelo interno eso puede ser tolerable, pero para el operador la
distinción no es obvia. En la práctica, cuando un dispositivo tiene una carpeta
montada, esa carpeta ya define el universo de evidencia y los archivos
vinculados aparecen como derivación de esa decisión. Mantener además un
`Evidence file` visible puede duplicar intención y generar estados ambiguos.

## Goals / Non-Goals

**Goals:**
- Definir una única fuente primaria clara para el operador en `EvidenceItem`.
- Hacer que la carpeta del dispositivo y los archivos derivados se comporten de
  forma coherente con la misma lógica que hoy percibe el operador en
  `Evidence file`.
- Determinar si `Evidence file` sigue siendo necesario en la UI principal o si
  debe quedar solo como detalle interno o avanzado.
- Preservar compatibilidad con el motor pericial, que necesita `EvidenceFile`
  trazables para ejecutar búsquedas, hallazgos y exportaciones.

**Non-Goals:**
- No reemplazar `EvidenceFile` como entidad interna del dominio.
- No rediseñar toda la topología de `EvidenceItem` o de `PreservedArtifact`.
- No romper compatibilidad con datos existentes si el campo visible cambia de rol.

## Decisions

### 1. La carpeta del dispositivo debe convertirse en la fuente primaria visible

Cuando el caso opera sobre una carpeta montada por dispositivo, esa carpeta es
la mejor representación operatoria del origen de evidencia. Desde ahí pueden
derivarse los archivos vinculados y, si hace falta, también una referencia
principal específica.

Alternativa considerada: mantener `Evidence file` y `source_path` como dos
entradas primarias equivalentes. Se descarta porque duplica intención y obliga
al operador a decidir algo que el sistema puede derivar.

### 2. `archivos de evidencia` debe presentarse como derivación, no como carga manual paralela

El bloque de archivos vinculados debe leerse como resultado de la carpeta
seleccionada o de la fuente primaria resuelta, no como un tercer origen
independiente. La UX debería reforzar que esos archivos son el conjunto
materializado que el sistema encontró y vinculó.

Alternativa considerada: permitir edición totalmente separada de
`evidence_files` en el flujo principal. Se descarta para el flujo guiado porque
vuelve a abrir ambigüedad; podría seguir existiendo solo como capacidad
avanzada o secundaria.

### 3. `Evidence file` debe evaluarse como detalle avanzado o candidato a retiro de la UI principal

El campo no necesariamente debe desaparecer del modelo, pero sí puede dejar de
ser parte del formulario principal si su semántica queda cubierta por:
- carpeta primaria del dispositivo
- archivos derivados vinculados
- evidencia principal resuelta automáticamente

Alternativa considerada: eliminar inmediatamente el campo del modelo. Se
descarta en esta etapa porque el motor y varias relaciones todavía lo usan como
ancla explícita.

### 4. La simplificación debe preservar una representación interna explícita

Aunque la UI se simplifique, el sistema debe seguir pudiendo identificar:
- la raíz primaria del dispositivo
- el archivo concreto usado como evidencia principal, si existe
- el conjunto de archivos derivados vinculados

Eso permite que la ejecución de puntos periciales y la trazabilidad de
hallazgos no pierdan resolución.

## Risks / Trade-offs

- [Ocultar `Evidence file` demasiado pronto puede frustrar casos donde el
  operador sí quiere fijar un archivo principal] → Mitigación: evaluar si queda
  como campo avanzado, autocalculado o visible solo en ciertos roles/estados.
- [Unificar UX sin aclarar semántica interna puede mover la confusión a otro
  lugar] → Mitigación: hacer explícita la jerarquía “carpeta primaria →
  archivos derivados → referencia principal”.
- [Datos existentes pueden tener `evidence_file` sin `source_path`] →
  Mitigación: contemplar reglas de compatibilidad y fallback en la migración de
  UX.

## Migration Plan

1. Identificar cuál debe ser la fuente primaria visible en `EvidenceItem`.
2. Ajustar el formulario y la presentación de archivos derivados para responder
   a esa decisión.
3. Resolver si `Evidence file` queda oculto, avanzado o eliminado del flujo
   principal.
4. Cubrir con tests los escenarios de carpeta primaria, archivos derivados y
   compatibilidad con datos existentes.

## Open Questions

- `Evidence file` debería:
  - desaparecer de la UI principal,
  - quedar como campo avanzado,
  - o autocompletarse sin edición directa?
- `archivos de evidencia` debería admitir edición manual complementaria o solo
  reflejar el resultado de la carpeta primaria?
