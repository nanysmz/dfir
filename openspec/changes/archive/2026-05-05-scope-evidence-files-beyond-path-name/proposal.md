## Why

Los archivos y carpetas de evidencia no pueden identificarse de forma confiable solo por nombre visible, porque dispositivos de distintas pericias pueden contener estructuras equivalentes con contenido diferente. Si el sistema colapsa o interpreta esos elementos como si fueran la misma evidencia por apariencia superficial, se pierde trazabilidad pericial y se introducen asociaciones incorrectas entre casos.

## What Changes

- Definir una identidad de archivo/carpeta de evidencia que no dependa solo del nombre mostrado ni de similitudes aparentes entre rutas.
- Reforzar el scoping de evidencia por pericia y dispositivo asociado para evitar mezclar archivos equivalentes de contextos distintos.
- Hacer visible en el admin cuándo dos elementos comparten nombre pero pertenecen a pericias o dispositivos distintos.
- Preparar el modelo y el workflow para basarse en contexto pericial y contenido verificable al vincular evidencia derivada.

## Capabilities

### New Capabilities
- `evidence-file-contextual-identity`: identidad contextual de archivos y carpetas de evidencia basada en pericia, dispositivo asociado y contenido verificable, en lugar de depender solo del nombre visible.

### Modified Capabilities
- `evidence-item-source-unification`: la derivación y vinculación de archivos desde una fuente primaria debe preservar contexto pericial/dispositivo aunque existan nombres repetidos en otros casos.
- `evidence-source-selection`: el guardado y la resolución de fuentes no deben asumir equivalencia entre elementos por coincidencia de nombre o estructura aparente.
- `admin-workflow-ui`: la UI de evidencia debe distinguir claramente archivos homónimos pertenecientes a pericias o dispositivos diferentes.

## Impact

- Modelo y reglas de identificación/vinculación de `EvidenceFile`.
- Lógica de derivación desde `EvidenceItem` y fuentes primarias.
- Admin de evidencia y listados donde hoy puede inducirse equivalencia por nombre.
- Tests de colisión entre nombres repetidos en distintas pericias o dispositivos.
