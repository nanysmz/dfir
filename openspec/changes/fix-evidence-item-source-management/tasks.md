## 1. Modelo y compatibilidad de fuentes

- [x] 1.1 Introducir un modelo o estructura persistente para registrar multiples fuentes por `EvidenceItem`, con distincion entre fuente primaria y fuentes asociadas.
- [x] 1.2 Agregar la migracion de compatibilidad que pueble la nueva estructura desde `EvidenceItem.source_path` y preserve la proyeccion hacia `source_path` y `evidence_file`.
- [x] 1.3 Definir y cubrir con tests la politica de resincronizacion de `evidence_files` cuando cambia la fuente primaria.

## 2. Validacion y flujo de admin

- [x] 2.1 Corregir la validacion de rutas para aceptar aliases montados y fuentes ya vinculadas al reabrir o guardar un `EvidenceItem`.
- [x] 2.2 Actualizar el formulario y admin de `EvidenceItem` para separar visualmente fuente principal, fuentes asociadas y archivos de evidencia resueltos.
- [x] 2.3 Agregar tests de admin para los casos de seleccionar, editar, reemplazar y guardar una fuente principal y multiples fuentes asociadas sin errores espurios.

## 3. Metadata del dispositivo e informe

- [x] 3.1 Estructurar en `EvidenceItem` los datos tecnicos necesarios para describir el dispositivo ofrecido: tipo, interfaz, marca, modelo, numero de serie, capacidad y observaciones.
- [x] 3.2 Ajustar el comportamiento de `Tipo de dispositivo` para que siga precargando defaults utiles y conviva con la edicion manual de la metadata estructurada.
- [x] 3.3 Agregar soporte y tests para reutilizar esa metadata en el workflow del informe, especialmente en la futura redaccion de `elementos ofrecidos`.
