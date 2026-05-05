## Context

Hoy la selección de rutas montadas para `EvidenceFile` y para la `fuente primaria de evidencia del dispositivo` se apoya en un endpoint de autocomplete que devuelve una mezcla de raíces montadas y subrutas descendientes. Esa estrategia funciona para datasets pequeños, pero en montajes reales vuelve difícil distinguir la raíz del dispositivo, entender la estructura disponible y elegir una carpeta interna sin ruido visual.

El cambio impacta formularios admin, una vista backend de descubrimiento de rutas y el JavaScript que hoy consume sugerencias. También debe preservar compatibilidad con rutas ya resueltas o escritas manualmente, porque existen registros previos y validaciones que dependen de aceptar archivos y carpetas reales dentro del volumen montado.

## Goals / Non-Goals

**Goals:**
- Mostrar solamente entradas de primer nivel cuando el operador inicia la selección de una fuente primaria montada.
- Permitir navegar dentro de carpetas bajo demanda sin perder contexto de dónde está parado el operador.
- Mantener la aceptación de archivos y carpetas válidos ya guardados o tipeados manualmente.
- Reutilizar, en lo posible, la infraestructura actual de mounted roots y validación de rutas.

**Non-Goals:**
- Reemplazar todo el sistema de selección de archivos del admin por un explorador genérico para cualquier modelo.
- Cambiar las reglas de negocio de validación de `EvidenceFile` o `EvidenceItem` más allá de cómo se descubre la ruta.
- Implementar un árbol completo expandible con carga masiva de todo el volumen en una sola respuesta.

## Decisions

### Usar navegación por nivel en vez de autocomplete plano
La vista inicial del selector deberá listar únicamente archivos y carpetas inmediatamente contenidos en cada raíz montada. Cuando el operador elija entrar en una carpeta, el cliente pedirá explícitamente el contenido de ese nivel.

Rationale:
- Reduce ruido y evita mezclar rutas raíz con descendientes profundos.
- Hace visible la estructura montada real del dispositivo.
- Escala mejor que devolver muchas subrutas en una sola búsqueda inicial.

Alternativa considerada:
- Mantener autocomplete plano y filtrar resultados por prefijo. Se descarta porque sigue exponiendo listas extensas y no comunica bien la noción de “entrar” en una carpeta.

### Preservar compatibilidad con rutas existentes mediante resolución explícita
El backend debe seguir aceptando rutas canónicas ya guardadas y rutas ingresadas manualmente, incluso si no fueron elegidas desde la nueva navegación. El widget debe poder arrancar mostrando una ruta existente y permitir reabrirla dentro del browser.

Rationale:
- Evita romper registros existentes o flujos donde el operador pega una ruta conocida.
- Permite editar sin forzar una nueva selección desde cero.

Alternativa considerada:
- Limitar el guardado a rutas seleccionadas solo desde el browser. Se descarta porque complica migraciones y reduce flexibilidad operativa.

### Separar “listar nivel” de “buscar por texto”
La experiencia principal del campo será navegar por niveles. La búsqueda textual puede seguir existiendo como soporte, pero no debe ser el mecanismo que cargue descendientes profundos por defecto.

Rationale:
- Mantiene una UX predecible para browsing.
- Permite seguir encontrando rutas conocidas sin perder la jerarquía como comportamiento principal.

Alternativa considerada:
- Quitar toda búsqueda textual. Se descarta porque algunos operadores ya trabajan con rutas conocidas y necesitan acceso directo.

## Risks / Trade-offs

- [Mayor complejidad del widget] → Mitigar con una API simple de `list root / list children / resolve existing path` y tests de integración sobre los estados de navegación.
- [Confusión entre seleccionar carpeta y entrar en carpeta] → Mitigar con acciones visuales separadas, por ejemplo una acción para navegar y otra para confirmar la ruta actual.
- [Rendimiento en carpetas muy grandes] → Mitigar limitando cada respuesta al nivel solicitado y evitando precargar descendientes.
- [Incompatibilidad con rutas antiguas] → Mitigar con una ruta de resolución explícita para valores existentes y cobertura de tests sobre edición.

## Migration Plan

- No requiere migración de datos.
- Desplegar backend y frontend del selector en conjunto.
- Verificar después del despliegue que formularios con rutas ya guardadas puedan abrir, validar y re-guardar sin cambios manuales.

## Open Questions

- Si el mismo browser debe reutilizarse luego para `Analysis targets` o si por ahora queda acotado a fuente primaria y `EvidenceFile`.
- Si la búsqueda textual seguirá visible desde el primer render o quedará secundaria detrás de la navegación por carpetas.
