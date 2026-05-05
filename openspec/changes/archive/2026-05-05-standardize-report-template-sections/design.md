## Context

El modelo de informe adjunto confirma que la pericia técnica utiliza una secuencia estable de secciones, con pocas variaciones entre casos: `Objeto`, `Elementos ofrecidos`, `Herramientas`, `Metodología`, `Información obtenida`, `Conclusiones`, `Evidencia` y `Anexo`. Hoy el sistema ya contempla composición de secciones de informe, pero no queda garantizado que toda pericia nueva nazca con esa estructura base ni que el orden se preserve de forma consistente.

El cambio impacta el flujo de alta de pericia, la representación interna de secciones del informe y la interfaz admin donde esas secciones se editan. También debe coexistir con contenido que se completa desde evidencia, análisis y respuestas por punto, sin volver rígida la edición final del perito.

## Goals / Non-Goals

**Goals:**
- Crear una estructura inicial uniforme de secciones para cada pericia nueva.
- Preservar un orden fijo compatible con el modelo pericial adjunto.
- Diferenciar secciones puramente estructurales de aquellas que se nutren de datos del caso.
- Mantener edición manual sobre el contenido final sin perder la plantilla base.

**Non-Goals:**
- Automatizar completamente la redacción final del informe.
- Congelar el texto interno de cada sección para todos los casos.
- Resolver en este cambio la exportación DOCX/PDF final o el formateo exacto de foja, índice y numeración avanzada.

## Decisions

### Sembrar secciones base al crear la pericia
Cada `PericiaCase` nueva deberá crear o garantizar una colección inicial de secciones del informe con el orden estándar definido por la plantilla.

Rationale:
- Evita que cada operador tenga que reconstruir la estructura.
- Reduce diferencias accidentales entre informes del mismo organismo.

Alternativa considerada:
- Generar la plantilla recién al entrar a `Informe`. Se descarta porque retrasa el estado inicial del caso y complica validar completitud del flujo.

### Tratar la plantilla como estructura editable, no como documento cerrado
La plantilla define presencia y orden de secciones, y puede incluir texto base sugerido, pero cada sección sigue siendo editable por caso.

Rationale:
- El informe pericial necesita consistencia estructural, no rigidez total del texto.
- Permite adaptar metodología, conclusiones y anexos a las particularidades del expediente.

Alternativa considerada:
- Guardar bloques totalmente bloqueados por plantilla. Se descarta porque limita demasiado el criterio pericial.

### Distinguir secciones de contenido derivable
`Elementos ofrecidos` e `Información obtenida` deben quedar preparadas para poblarse o asistirse desde datos del caso y análisis, mientras que `Herramientas`, `Metodología` o `Conclusiones` pueden partir de texto base más editorial.

Rationale:
- Aprovecha la información ya estructurada del sistema.
- Evita confundir texto fijo con contenido técnico que cambia por caso.

Alternativa considerada:
- Tratar todas las secciones como texto libre homogéneo. Se descarta porque pierde oportunidad de reutilización y validación.

## Risks / Trade-offs

- [Plantilla demasiado rígida para casos especiales] → Mitigar permitiendo edición manual del contenido y, si hiciera falta, extensibilidad futura de secciones adicionales.
- [Duplicación de secciones en casos ya creados] → Mitigar con una inicialización idempotente que cree faltantes sin repetir secciones existentes.
- [Confusión entre texto sugerido y texto definitivo] → Mitigar diferenciando claramente contenido base de contenido revisado por el operador.

## Migration Plan

- Incorporar una rutina idempotente para crear secciones estándar en casos nuevos y, si corresponde, completar casos existentes que aún no tengan estructura.
- Validar en ambiente de desarrollo que una pericia ya creada no duplique secciones al reabrirse.
- Verificar que el orden visible en admin coincida con la plantilla establecida.

## Open Questions

- Si `Herramientas` y `Metodología` deben nacer con un texto institucional predeterminado o solo con títulos vacíos.
- Si `Evidencia` y `Anexo` deben diferenciarse también por tipo de adjunto o mantenerse como secciones narrativas generales en esta etapa.
