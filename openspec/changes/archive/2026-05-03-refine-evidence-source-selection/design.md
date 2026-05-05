## Context

La capa de evidencia del admin ya soporta rutas montadas para varios objetos,
pero el comportamiento no era consistente. `EvidenceItem` trabaja sobre una
carpeta del dispositivo e importa su contenido en forma recursiva, mientras que
`EvidenceFile` todavia validaba solo archivos regulares y el campo
`evidence_file` dentro de `EvidenceItem` dependia de un dropdown de objetos ya
cargados. A la vez, el detalle de caso expone una accion guiada para sembrar
plantillas de dispositivos, pero esa accion no diferenciaba entre un caso vacio
y uno donde el operador ya habia creado dispositivos manualmente.

El proyecto corre en un entorno dockerizado y las rutas relevantes viven dentro
de los mounts visibles para el contenedor. Por eso, la UX del admin tiene que
ser explicita respecto de carpetas y archivos, sin asumir filesystem del host.

## Goals / Non-Goals

**Goals:**
- Unificar la semantica de seleccion de rutas de evidencia para que
  `EvidenceFile` pueda representar tanto un archivo puntual como una carpeta.
- Hacer que la evidencia principal de un `EvidenceItem` tambien pueda elegirse
  por ruta y crearse o vincularse automaticamente al guardar.
- Hacer que el autocompletado de rutas muestre carpetas y archivos con rotulos
  distinguibles.
- Hacer que `Parent item` muestre una jerarquia mas expresiva para el operador.
- Evitar que la accion guiada de carga de plantillas agregue lotes duplicados
  sobre casos que ya tienen elementos de evidencia.
- Mantener el cambio acotado al admin y a la validacion de rutas, sin exigir un
  rediseño del pipeline de extraccion.

**Non-Goals:**
- No introducir un nuevo modelo separado para carpetas de evidencia.
- No cambiar el pipeline de extraccion para procesar carpetas como contenido
  analizable por si mismas.
- No redefinir las etapas del workflow pericial fuera del guardarrail de seed.

## Decisions

### 1. `EvidenceFile` aceptara rutas de archivo o directorio

`EvidenceFileAdminForm.clean_source_path()` validara que la ruta exista y sea
`is_file()` o `is_dir()`. Esto mantiene una sola entidad de referencia para
fuentes de evidencia y evita crear una jerarquia paralela solo para carpetas.

Alternativa considerada: crear un modelo nuevo para directorios de evidencia.
Se descarta porque agregaria complejidad en relaciones, formularios y queries
sin resolver un problema que hoy puede cubrirse con una validacion mas amplia.

### 2. El autocompletado de `Evidence file` devolvera archivos y carpetas

El endpoint `mounted_path_search_view` devolvera ambos tipos de entrada y
rotulara las carpetas como `[dir] ...`. El valor persistido seguira siendo la
ruta absoluta visible para el contenedor, mientras que la etiqueta ayuda a la
lectura del operador.

Alternativa considerada: usar dos campos separados, uno para archivo y otro
para carpeta. Se descarta porque obligaria al operador a decidir antes de
explorar la ruta y duplicaria la interfaz.

### 3. `EvidenceItem` seleccionara evidencia principal por ruta

El campo `evidence_file` del formulario de `EvidenceItem` debe comportarse como
un selector por ruta montada y resolver internamente el `EvidenceFile`
correspondiente. Esto evita depender de que el archivo o carpeta ya exista
como fila previa en la base.

Alternativa considerada: conservar el `ForeignKey` visible y obligar al
operador a precargar `EvidenceFile` antes de usarlo en un dispositivo. Se
descarta porque rompe el flujo guiado y agrega pasos artificiales.

### 4. `Parent item` mostrara el contexto de carpeta montada

La etiqueta visible del selector debe priorizar la raiz montada de pericia o
dispositivo y luego la etiqueta del item. Eso ayuda a entender si el item cuelga
de la carpeta del caso, de un dispositivo concreto o de otra rama derivada.

Alternativa considerada: mantener solo `case_reference - label`. Se descarta
porque en la practica oculta la topologia real de la evidencia montada.

### 5. La accion guiada de seed solo correra sobre casos vacios

La vista de admin y el comando `seed_device_types` trataran la existencia de
cualquier `EvidenceItem` como señal suficiente para bloquear la siembra
automatica. En ese caso, la vista responde con warning y preserva la navegacion
de vuelta a `Elementos de evidencia`.

Alternativa considerada: sembrar solo plantillas faltantes. Se descarta porque
los dispositivos creados manualmente no necesariamente representan “huecos” a
rellenar, y completar automaticamente podria seguir sorprendiendo al operador.

## Risks / Trade-offs

- [Una carpeta cargada como `EvidenceFile` no sera analizada como contenido
  directo] → El sistema la conserva como referencia valida y el pipeline ya la
  tratara como `unknown` o no soportada cuando corresponda.
- [Mostrar archivos y carpetas en un mismo dropdown puede confundir] → El
  autocompletado usa rotulos `[dir]` para hacer visible la diferencia.
- [Bloquear el seed sobre cualquier caso no vacio puede ser mas conservador de
  lo deseado] → Es preferible evitar inflar el caso; el operador mantiene el
  CRUD directo para agregar exactamente los dispositivos que necesite.

## Migration Plan

1. Actualizar formularios y endpoints de admin para aceptar carpetas en
   `EvidenceFile`.
2. Actualizar `EvidenceItem` para seleccionar evidencia principal por ruta y
   mostrar mejor el contexto de `Parent item`.
3. Ajustar el comando y la vista guiada de seed para abortar si el caso ya
   tiene elementos de evidencia.
4. Cubrir ambos comportamientos con tests server-side en el entorno dockerizado.

## Open Questions

- Si una carpeta queda asociada como `EvidenceFile`, mas adelante puede valer la
  pena explicitar visualmente que se trata de una fuente contenedora y no de un
  archivo individual.
