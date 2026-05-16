## 1. Fragmento contextual del hallazgo

- [x] 1.1 Diseñar y persistir una estructura de fragmento por líneas para hallazgos textuales, con línea coincidente identificada y ventana aproximada de `+- 10` líneas.
- [x] 1.2 Ajustar los matchers y la creación de `PericiaFinding` para poblar el fragmento estructurado sin romper compatibilidad con `context`.

## 2. Trazabilidad y salidas derivadas

- [x] 2.1 Actualizar exportaciones o artefactos derivados de hallazgos para incluir el fragmento contextual cuando exista.
- [x] 2.2 Definir fallback consistente para hallazgos viejos o no textuales sin fragmento lineal.

## 3. UI y validación

- [x] 3.1 Mostrar en admin el fragmento del hallazgo con la línea coincidente resaltada y las líneas vecinas visibles.
- [x] 3.2 Agregar tests de matching, persistencia, exportación y admin para validar el fragmento estructurado y el fallback.
