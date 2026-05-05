## 1. Estructura base del informe

- [x] 1.1 Definir la lista estándar de secciones del informe con su orden institucional para nuevas pericias.
- [x] 1.2 Crear una inicialización idempotente que garantice esas secciones en cada `PericiaCase` sin duplicarlas.

## 2. Integración con el workflow y admin

- [x] 2.1 Ajustar el flujo del módulo `Informe` para mostrar la secuencia fija de secciones en el orden esperado.
- [x] 2.2 Diferenciar en la UI la estructura estándar de secciones del contenido editable específico del caso.

## 3. Contenido derivado y validación

- [x] 3.1 Preparar las secciones derivables para que `Elementos ofrecidos` e `Información obtenida` puedan poblarse desde datos del caso sin perder edición manual.
- [x] 3.2 Agregar tests para alta de pericia, creación idempotente de secciones y orden visible de la plantilla del informe.
