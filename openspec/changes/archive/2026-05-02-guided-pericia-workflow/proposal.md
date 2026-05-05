## Why

El sistema ya modela la pericia completa y tiene un backoffice temático, pero el recorrido operativo todavía depende demasiado de saber de memoria qué hacer después. Hace falta convertir ese flujo en una experiencia guiada, paso a paso, para reducir omisiones, re-trabajo y fricción al abrir o continuar una pericia.

## What Changes

- Convertir el flujo de la pericia en una secuencia guiada y explícita dentro del admin, desde la apertura del caso hasta el cierre del informe.
- Agregar indicadores de progreso, precondiciones y siguientes acciones recomendadas para cada etapa operativa del caso.
- Hacer que la experiencia guiada viva tanto en la portada del admin como dentro de la ficha del caso pericial, para poder retomar una pericia en curso sin perder contexto.
- Vincular cada paso del flujo con los objetos reales ya modelados: documentos, puntos solicitados, evidencia, planes, resultados, respuestas e informe.
- Incorporar validaciones de completitud operativa para distinguir entre “caso creado” y “paso realmente listo para continuar”.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `admin-workflow-ui`: el admin pasa de mostrar accesos rápidos a ofrecer guía contextual, progreso y próximos pasos accionables.
- `pericia-report-workflow`: el workflow del caso incorpora una secuencia operativa explícita con criterios de avance por etapa.

## Impact

- Affected code: configuración de Unfold, dashboard del admin, clases admin por dominio, helpers de estado/progreso del caso, formularios y vistas guiadas del caso pericial.
- Affected systems: Django admin como superficie principal de operación del flujo pericial.
- Dependencies: sin nuevas integraciones externas obligatorias; el cambio se apoya en el modelo existente y en `django-unfold` ya adoptado.
