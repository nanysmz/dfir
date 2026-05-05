## Context

El repositorio ya permite crear `AnalysisPlan`, disparar un `PericiaPoint` y
registrar `PericiaExecution` con sus resultados. Sin embargo, entre “plan listo”
y “hallazgos disponibles” hay una zona ciega para el operador: no queda
claramente expresado si el análisis todavía no empezó, si está corriendo, si ya
terminó o si falló a mitad de camino.

Como el proyecto es dockerizado y ya usa `Celery`, la ejecución puede tardar lo
suficiente como para que el feedback operativo pase a ser parte del producto, no
solo un detalle técnico. En especial, una pericia guiada por caso necesita
mostrar si la etapa de análisis está activa y cuánto se avanzó para decidir el
siguiente paso.

## Goals / Non-Goals

**Goals:**
- Exponer estado de ejecución del análisis en lenguaje operativo.
- Mostrar avance visible del análisis desde surfaces del admin ya usadas por el
  operador.
- Distinguir claramente “plan creado”, “ejecución en curso”, “completado” y
  “fallido”.

**Non-Goals:**
- No rediseñar el motor de matching ni el pipeline de extracción.
- No construir un monitor de jobs genérico para todo el sistema.
- No prometer progreso byte-a-byte o precisión falsa si la tarea no la soporta.

## Decisions

### 1. La fuente canónica de estado debe seguir siendo `PericiaExecution`

El sistema ya modela una ejecución concreta. La UI debe derivar su feedback de
ese objeto, no crear un estado paralelo en el admin. Si hace falta más
granularidad, se extiende el record de ejecución o su actualización durante la
tarea.

Alternativa considerada: guardar estado solo en `AnalysisPlan.status`. Se
descarta porque pierde detalle histórico y mezcla planificación con ejecución.

### 2. El progreso visible debe ser aproximado pero útil

No hace falta un porcentaje perfecto para que el operador entienda si el
análisis avanza. Una estrategia válida es mostrar:
- estado textual (`pendiente`, `en ejecución`, `completado`, `fallido`)
- contadores parciales (`archivos procesados / totales` cuando existan)
- timestamp de inicio/fin

Si el total no se conoce desde el primer momento, la UI puede mostrar progreso
indeterminado o actividad en curso en lugar de un porcentaje falso.

### 3. El feedback debe vivir donde el operador ya trabaja

La visibilidad principal debería aparecer en:
- el `AnalysisPlan` asociado
- el bloque guiado del caso cuando esa etapa esté activa

Eso evita obligar al operador a abrir `PericiaExecution` solo para saber si el
análisis está corriendo.

### 4. La ejecución asíncrona necesita una transición explícita de estados

Cuando el operador dispara el análisis desde admin, el sistema debe marcar que
la ejecución fue encolada o iniciada antes de que existan resultados finales.
La tarea debe actualizar el estado hasta completar o fallar, de forma que la UI
pueda reflejar algo más que “no hay resultados todavía”.

## Risks / Trade-offs

- [El progreso puede parecer más preciso de lo que realmente es] → Mitigación:
  usar etiquetas honestas como “en curso” o contadores parciales cuando no haya
  porcentaje confiable.
- [La UI puede duplicar información entre plan, ejecución y caso] → Mitigación:
  definir una fuente canónica en `PericiaExecution` y mostrar resúmenes
  derivados en otras surfaces.
- [Ejecuciones cortas pueden saltar demasiado rápido de pendiente a completo] →
  Mitigación: priorizar consistencia de estado sobre animaciones complejas.

## Migration Plan

1. Formalizar el requisito de visibilidad de ejecución en OpenSpec.
2. Extender la UI del admin para resumir estado y progreso desde la ejecución.
3. Asegurar que la tarea de análisis actualice estados intermedios útiles.
4. Verificar el flujo completo en el entorno dockerizado.

## Open Questions

- ¿El caso necesita mostrar progreso agregado de varios planes en paralelo o
  alcanza con resumir el último/actual?
- ¿Conviene mostrar “encolado” y “ejecutando” como estados distintos desde la
  primera versión?
