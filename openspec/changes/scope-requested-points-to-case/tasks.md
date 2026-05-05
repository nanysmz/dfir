## 1. Reforzar scoping por pericia

- [x] 1.1 Ajustar formularios y/o formsets de `RequestedPoint` para que el alta
  inline sugiera el próximo `order` disponible dentro de la pericia actual.
- [x] 1.2 Mantener y reforzar la validación de unicidad por
  `(pericia_case, order)` con mensajes claros orientados al caso.

## 2. Alinear UX del admin

- [x] 2.1 Actualizar la experiencia de `Puntos solicitados` en `Casos
  periciales` para que quede explícito que pertenecen solo a esa pericia.
- [x] 2.2 Alinear el admin dedicado de `Puntos solicitados` con la misma lógica
  y feedback operatorio.

## 3. Cubrir con tests

- [x] 3.1 Agregar tests para el alta inline y la sugerencia de `order`
  secuencial por caso.
- [x] 3.2 Agregar tests para conflictos de orden dentro de una misma pericia y
  para reutilización válida del mismo orden en pericias diferentes.
