## Why

La home actual del admin ya expone el flujo pericial, pero las tarjetas del
paso a paso todavia se sienten mas cercanas a accesos rapidos que a una guia
operativa clara. Hace falta rediseñarlas para que el inicio de una pericia sea
mas evidente, mas escaneable y mas consistente con la promesa de flujo guiado.

## What Changes

- Rediseñar las tarjetas del paso a paso en `/admin/` para que funcionen como
  una secuencia visual de etapas, no solo como cards sueltas.
- Incorporar jerarquia visual mas fuerte para `Paso`, titulo, estado, CTA y
  prerequisitos de cada etapa.
- Diferenciar visualmente etapas listas para empezar, etapas en curso, etapas
  bloqueadas y etapas ya completadas.
- Mejorar la relacion entre las tarjetas del flujo principal y el bloque
  `Retomar pericias` para que el operador entienda rapido si debe iniciar o
  continuar.
- Ajustar la documentacion y los tests del admin para reflejar el nuevo diseño
  guiado del home.

## Capabilities

### New Capabilities
- `guided-workflow-card-design`: define el comportamiento visual y estructural
  de las tarjetas del paso a paso en la home del admin

### Modified Capabilities
- `admin-workflow-ui`: cambia la forma en que la portada del admin presenta y
  prioriza el flujo guiado de una pericia

## Impact

- Afecta `templates/admin/index.html`
- Afecta el contexto expuesto desde `src/dfir_core/admin.py`
- Puede requerir pequeños ajustes en `src/dfir_pericia/workflow.py`
- Impacta tests de admin y documentacion operativa del backoffice
