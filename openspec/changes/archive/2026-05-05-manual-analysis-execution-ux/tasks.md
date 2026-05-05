## 1. Disparo manual visible

- [x] 1.1 Definir en las specs del admin una accion principal a nivel caso para `Ejecutar planes listos`.
- [x] 1.2 Definir en las specs del admin una accion contextual por fila o por plan para `Ejecutar este plan`, `Ver ejecucion`, `Reintentar` o `Reejecutar`.

## 2. Estados operativos y elegibilidad

- [x] 2.1 Capturar los estados operativos visibles derivados del plan y de su ultima ejecucion.
- [x] 2.2 Capturar el criterio de elegibilidad de `planes listos` y el comportamiento del disparo masivo.

## 3. Semantica de resultado y workflow

- [x] 3.1 Incorporar la categoria visible `Completado con observaciones` para ejecuciones utiles con incidencias parciales.
- [x] 3.2 Alinear el workflow del caso para que la etapa `Analisis` avance desde planes listos hacia ejecuciones y revision de resultados.
- [x] 3.3 Capturar que un plan puede tener multiples targets pero se ejecuta como una sola corrida por plan.
