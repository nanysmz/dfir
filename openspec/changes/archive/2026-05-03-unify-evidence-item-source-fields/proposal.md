## Why

Hoy `EvidenceItem` expone tres superficies relacionadas pero semánticamente
desalineadas: `Evidence file`, `carpeta de evidencia del dispositivo` y
`archivos de evidencia`. Eso obliga al operador a interpretar diferencias
internas del modelo en lugar de seguir un flujo claro de carga, y además deja
abierta la duda de si `Evidence file` sigue siendo necesario una vez que la
carpeta del dispositivo y los archivos derivados funcionan correctamente.

## What Changes

- Unificar el comportamiento operatorio de `Evidence file`, `carpeta de
  evidencia del dispositivo` y `archivos de evidencia` para que respondan a una
  misma lógica de rutas montadas y evidencia derivada.
- Definir una fuente primaria canónica para cada `EvidenceItem`, evitando que
  el operador tenga que elegir entre varios campos que parecen representar la
  misma cosa.
- Evaluar y, si resulta redundante, simplificar la UI removiendo `Evidence file`
  del flujo principal de edición del operador.
- Preservar la trazabilidad interna necesaria para ejecuciones periciales,
  reportes y artefactos preservados aunque cambie la UI visible.

## Capabilities

### New Capabilities
- `evidence-item-source-unification`: cubre la representación canónica de la
  fuente primaria y derivada de un `EvidenceItem` en el admin operador.

### Modified Capabilities
- `pericia-report-workflow`: cambia cómo un elemento de evidencia organiza y
  expone su fuente primaria dentro del flujo guiado del caso.
- `admin-workflow-ui`: cambia la UX del formulario de evidencia para eliminar
  ambigüedad entre rutas, carpeta primaria y archivos vinculados.

## Impact

- Código afectado: `src/dfir_core/admin_forms.py`, `src/dfir_evidence/admin.py`,
  `src/dfir_cases/admin.py`, `src/dfir_pericia/models.py`, y tests de admin y
  workflow.
- Riesgo principal: cambio semántico en el formulario de `EvidenceItem` y
  posible reducción o retiro del campo visible `Evidence file`.
- Sistemas afectados: backoffice dockerizado, linking de `EvidenceFile`,
  sincronización de archivos derivados y ejecución pericial posterior.
