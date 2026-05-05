## Why

El informe pericial sigue una estructura muy estable en la práctica, pero hoy el sistema no la representa como una plantilla fija reutilizable. Eso obliga a rearmar secciones repetidas, dificulta mantener consistencia entre pericias y retrasa la redacción final aunque el contenido técnico ya esté disponible.

## What Changes

- Definir una plantilla base de informe pericial con secciones estables derivadas del modelo adjunto: `Objeto`, `Elementos ofrecidos`, `Herramientas`, `Metodología`, `Información obtenida`, `Conclusiones`, `Evidencia` y `Anexo`.
- Hacer que cada pericia nueva parta de esa estructura predefinida, preservando capacidad de edición del contenido específico del caso.
- Diferenciar entre secciones estructurales fijas y bloques que se pueblan desde datos del caso, evidencia y análisis.
- Preparar el flujo para que el informe final se apoye en un orden uniforme y en textos base reutilizables, en vez de depender de carga manual ad hoc.

## Capabilities

### New Capabilities
- `report-template-sections`: plantilla estructural del informe técnico pericial con secciones fijas, orden estable y texto base reutilizable por caso.

### Modified Capabilities
- `pericia-report-workflow`: el armado del informe deja de partir de secciones totalmente libres y pasa a usar una estructura inicial predefinida basada en el modelo pericial.
- `admin-workflow-ui`: la interfaz de informe debe mostrar y gestionar esa estructura fija de secciones en un orden claro y consistente.

## Impact

- Modelado y seed inicial de secciones del informe dentro de la pericia.
- Formularios y admin del módulo `Informe`.
- Lógica de composición de contenido para combinar texto base con datos del caso.
- Tests del flujo de creación de pericia e inicialización/orden de secciones del informe.
