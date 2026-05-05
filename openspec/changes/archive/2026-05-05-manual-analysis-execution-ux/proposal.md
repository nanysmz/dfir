# manual-analysis-execution-ux Proposal

## Summary

Refinar la UX operativa del modulo `Analisis` para que el modelo de ejecucion
manual sea evidente y accionable. El cambio introduce un modelo mixto de
disparo manual:

- boton por caso para `Ejecutar planes listos`
- accion por fila para `Ejecutar este plan`
- estados operativos visibles mas expresivos para distinguir planes listos,
  en cola, en ejecucion, completados, completados con observaciones y fallidos

## Motivation

Hoy existe una accion para ejecutar un plan desde su vista de detalle, pero eso
no resuelve del todo la pregunta operativa principal: "ya cargue evidencia y
prepare los planes, como empiezo el analisis?". Si todos los planes siguen
siendo manuales, el sistema necesita mostrar un punto de arranque claro tanto a
nivel caso como a nivel lista de planes.

Tambien hace falta distinguir mejor entre:

- el plan como receta o unidad de planificacion
- la ejecucion como corrida concreta
- el resultado util con incidencias parciales frente a una falla total

## Scope

Este cambio captura decisiones de producto y UX para:

- hacer visible el inicio manual del analisis a nivel caso y a nivel lista
- definir el criterio de `planes listos`
- definir estados operativos visibles derivados de la ultima ejecucion
- introducir la semantica de `Completado con observaciones`
- aclarar la relacion entre multiples targets y una sola ejecucion por plan

## Non-Goals

- no implementa auto-ejecucion al guardar
- no cambia aun el motor de ejecucion ni la logica de Celery
- no redefine el modelo completo de `PericiaExecution`
- no cambia todavia el informe tecnico

## Affected Specs

- `admin-workflow-ui`: agrega entradas operativas visibles para iniciar el
  analisis manualmente y resume estados accionables
- `pericia-report-workflow`: aclara como el workflow del caso arranca
  ejecuciones y usa estados derivados para avanzar
- `analysis-plan-playbooks`: formaliza que un plan puede tener multiples
  targets pero se ejecuta como una sola corrida por plan
