## 1. Backend de navegación montada

- [x] 1.1 Ajustar el endpoint de rutas montadas para devolver solamente entradas de primer nivel cuando no se indique un directorio actual.
- [x] 1.2 Agregar soporte para listar hijos directos de una carpeta montada seleccionada y resolver rutas ya guardadas dentro del árbol.

## 2. UI del selector en admin

- [x] 2.1 Reemplazar el comportamiento plano actual del selector de `fuente primaria de evidencia del dispositivo` por una experiencia de navegación por niveles.
- [x] 2.2 Mostrar contexto de ubicación actual y una acción para volver al directorio padre sin perder el formulario.
- [x] 2.3 Mantener compatibilidad con rutas tipeadas manualmente y con valores existentes al editar registros.

## 3. Validación y cobertura

- [x] 3.1 Verificar que el guardado siga aceptando archivos y carpetas válidos elegidos desde la navegación o ingresados manualmente.
- [x] 3.2 Agregar tests de backend y admin para primer nivel inicial, navegación a subdirectorios y reapertura de rutas ya guardadas.
