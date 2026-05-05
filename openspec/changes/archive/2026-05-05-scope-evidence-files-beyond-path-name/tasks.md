## 1. Identidad contextual de evidencia

- [x] 1.1 Revisar las reglas actuales de identificación y unicidad de `EvidenceFile` para detectar dónde todavía se infiere equivalencia por nombre o ruta aparente.
- [x] 1.2 Definir e implementar una identidad contextual mínima basada en pericia, dispositivo asociado y señal verificable de contenido cuando exista.

## 2. Vinculación desde fuentes primarias

- [x] 2.1 Ajustar la derivación y vinculación de archivos desde `EvidenceItem` para que nombres repetidos en otras pericias no provoquen reutilización indebida.
- [x] 2.2 Preservar trazabilidad explícita del caso y dispositivo que originan cada vínculo de evidencia derivada.

## 3. UI y validación

- [x] 3.1 Hacer visible en el admin cuándo existen archivos o carpetas homónimos pertenecientes a contextos periciales distintos.
- [x] 3.2 Agregar tests con nombres repetidos en distintas pericias/dispositivos para verificar que el sistema no mezcle identidad ni asociaciones.
