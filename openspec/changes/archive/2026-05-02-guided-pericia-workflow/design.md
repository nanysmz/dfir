## Context

El repositorio ya cuenta con dos capas relevantes: un dominio case-driven de pericia (`PericiaCase`, `RequestedPoint`, `EvidenceItem`, `AnalysisPlan`, `DeviceAnalysisResult`, `RequestedPointResponse`, `ReportSection`) y un backoffice en Django admin con `Unfold` como shell visual. Sin embargo, hoy la secuencia operativa está documentada y parcialmente sugerida, pero no orquestada como una guía de trabajo persistente y contextual.

El pedido no es crear otra UI paralela ni un wizard aislado del modelo. El pedido es hacer que el flujo existente sea completo y guiado paso a paso, respetando que el sistema es dockerizado y que el admin sigue siendo la superficie canónica de operación.

## Goals / Non-Goals

**Goals:**
- Definir una secuencia operativa explícita para la pericia completa dentro del admin.
- Mostrar progreso del caso y “siguiente paso” a partir del estado real de los objetos ya existentes.
- Guiar tanto el inicio como la reanudación de una pericia en curso desde la portada y desde el detalle del caso.
- Reducir errores de orden y omisiones con precondiciones y mensajes de desbloqueo por etapa.
- Mantener compatibilidad con el modelo actual y con el enfoque `Unfold` adoptado.

**Non-Goals:**
- Reemplazar Django admin por una aplicación nueva.
- Introducir un engine BPM o un workflow externo.
- Automatizar completamente la redacción del informe final.
- Forzar un flujo rígido que impida cargar información fuera de orden cuando el caso real lo requiera.

## Decisions

1. Usar un workflow guiado derivado del estado real del caso, no un wizard separado.

   La guía debe reflejar la realidad del caso y no vivir como estado paralelo frágil. La secuencia se debe calcular a partir de la presencia y completitud de documentos, puntos solicitados, evidencia, planes, resultados, respuestas e informe. Alternativa considerada: guardar un “current_step” manual, descartada porque se desincroniza fácilmente del contenido real del expediente.

2. Definir etapas operativas estables y visibles para toda pericia.

   La guía necesita una taxonomía simple y repetible. La secuencia propuesta es: caso, documentos, puntos solicitados, evidencia, planes de análisis, resultados por dispositivo, respuestas por punto, informe y revisión final. Alternativa considerada: guiar solo hasta análisis y dejar informe fuera de la secuencia, descartada porque el pedido explícito es cubrir la pericia completa.

3. Centralizar la lógica de progreso en un helper reutilizable de workflow.

   El dashboard, el detalle del caso, badges, CTA y validaciones de avance no deberían recalcular reglas por separado. Conviene una capa de servicio/helper que exponga etapas, estado, bloqueos y próxima acción. Alternativa considerada: lógica distribuida entre templates y admins, descartada por riesgo de divergencia.

4. Guiar desde dos superficies: home global y detalle del caso.

   La portada del admin sirve para iniciar o retomar trabajo; la ficha del caso sirve para operar con contexto fino. El flujo completo debe vivir en ambas escalas. Alternativa considerada: resolver todo solo desde `/admin/`, descartada porque la ejecución real necesita guía contextual por caso.

5. Tratar “completitud” como criterio operativo, no solo existencia de filas.

   Para que la guía sea útil, no alcanza con que exista un objeto. Por ejemplo: un punto solicitado sin texto útil no debería habilitar el siguiente paso; un informe sin secciones relevantes no debería marcar cierre real. Alternativa considerada: usar solo conteos de objetos, descartada porque produce falsos positivos de avance.

6. Mantener el flujo flexible bajo una secuencia recomendada.

   La guía debe empujar un orden recomendado y mostrar bloqueos o dependencias, pero sin impedir completamente la carga manual cuando el caso real llegue desordenado. Alternativa considerada: bloqueo duro de navegación, descartada por rigidez operativa.

## Risks / Trade-offs

- [Reglas de progreso demasiado superficiales] → Definir criterios de avance por etapa que contemplen contenido mínimo y no solo existencia.
- [Workflow excesivamente rígido] → Usar advertencias y CTA guiados antes que bloqueos totales de navegación.
- [Duplicación de lógica entre dashboard y admin del caso] → Centralizar cálculo de etapas y próximas acciones en un helper único.
- [Ruido visual en el admin] → Priorizar pocos CTA claros, tracker visible y mensajes de desbloqueo concretos.
- [Desalineación con futuros cambios del dominio] → Basar el flujo en capacidades y relaciones actuales, no en nombres de templates o hacks de UI.

## Migration Plan

1. Definir el modelo lógico de etapas y criterios de completitud por caso.
2. Implementar un helper de workflow reutilizable por dashboard y admins.
3. Integrar tracker, checklist y CTA en la home de `Unfold`.
4. Integrar guía contextual, progreso y acciones recomendadas en `PericiaCaseAdmin`.
5. Ajustar tests para cubrir progreso, bloqueos y navegación guiada.

Rollback: desactivar la capa guiada y volver al dashboard/CRUD actual sin alterar los modelos del dominio.

## Open Questions

- ¿La revisión final del informe debe ser una etapa explícita separada de “Informe” o solo un estado terminal derivado?
- ¿Qué criterios mínimos deben marcar “respuesta por punto completada” en casos con respuestas parciales?
- ¿Conviene ofrecer también una vista transversal “pericias en curso por etapa” en el changelist de casos?
