## Context

Después de redefinir `AnalysisPlan` como playbook, apareció la siguiente
limitación: las acciones todavía son demasiado libres. El analista necesita que
cada acción diga explícitamente qué revisar y cómo hacerlo.

Ejemplo real:

```text
Punto solicitado:
"Identificación de programas P2P instalados"

Acción concreta:
- carpeta: ActividadReciente
- tipo de archivo: html
- criterio: palabras clave
- términos: torrent, emule, p2p, utorrent, bittorrent, ares
```

Eso ya no es una nota informal: es una unidad operativa del análisis.

## Goals / Non-Goals

**Goals**

- Traducir varios puntos del catálogo a acciones concretas y repetibles.
- Darle estructura mínima a cada acción del plan.
- Permitir que el admin exprese esa estructura de manera clara.
- Mantener la distinción entre:
  - punto solicitado
  - plan del caso
  - acción ejecutable
  - técnica reusable
  - ejecución concreta

**Non-Goals**

- No implementar todavía un motor completamente distinto por cada categoría del
  catálogo.
- No crear todavía una tabla separada obligatoria para acciones si una primera
  versión con JSON estructurado cubre bien el caso.
- No resolver en este mismo cambio todos los extractores específicos del mundo
  forense.

## Decisions

### 1. `AnalysisPlan` mantiene playbook, pero cada acción pasa a ser estructurada

Cada acción deberá incluir, como mínimo:

```json
{
  "order": 1,
  "label": "Buscar indicadores de software P2P en ActividadReciente",
  "action_family": "keyword_search",
  "path_scope": ["ActividadReciente"],
  "file_kinds": ["html"],
  "search_criteria": {
    "mode": "any",
    "terms": ["torrent", "emule", "p2p", "utorrent", "bittorrent", "ares"]
  },
  "pericia_point_id": 123,
  "pericia_point_name": "Busqueda de palabras en texto/html",
  "expected_outputs": [
    "ruta completa",
    "archivo fuente",
    "contexto de coincidencia",
    "fechas y metadatos"
  ]
}
```

### 2. La representación inicial será JSON estructurado dentro del playbook

Primera versión:

- `scope_snapshot.analysis_playbook.actions[]` se vuelve la fuente principal
- se agrega estructura, validación y ayuda de UI
- se conserva compatibilidad con `execution_actions` textual como fallback

Esto permite avanzar sin una migración de muchas tablas nuevas.

### 3. El catálogo se aterriza en acciones operativas concretas

Los siguientes puntos del catálogo deberán tener acciones base explícitas:

#### A. Identificación de programas P2P instalados

- revisar `ActividadReciente`
- archivos `html`
- términos: `torrent`, `emule`, `p2p`, `utorrent`, `bittorrent`, `ares`

#### B. Identificación de correos electrónicos, credenciales y autocompletado

- revisar `CuentaGmail`
- archivos `html`, `txt`, `json`
- términos: `@gmail.com`, `@hotmail.com`, `correo`, `email`, `login`, `password`

#### C. Extracción y análisis integral de archivos

- revisar `ArchivosOfimatica`, `ArchivosPDF`
- archivos `doc`, `docx`, `pdf`, `txt`
- criterios: palabras clave derivadas del punto y metadata relevante

#### D. Recuperación de comunicaciones

- revisar `Usuarios`, `ActividadReciente`
- archivos `html`, `txt`, `json`
- términos: `whatsapp`, `sms`, `mensaje`, `chat`, `telegram`, `voip`

#### E. Material multimedia relevante

- revisar `Imagenes`, `ImagenesVideos`
- archivos `jpg`, `jpeg`, `png`, `gif`, `mp4`, `mov`
- criterio: detección multimedia + nombres/etiquetas relevantes

#### F. Recuperación de archivos eliminados

- revisar `PapeleraReciclaje`
- archivos `*`
- criterio: inventario + términos derivados del punto

### 4. El admin debe hablar de acciones ejecutables y no solo de estrategias

La UI del plan deberá dejar claro:

- qué punto solicitado se está respondiendo
- qué acciones concretas lo componen
- qué carpeta revisa cada acción
- qué tipo de archivo aplica
- qué criterio de búsqueda usa

### 5. La técnica reusable sigue siendo una dependencia de la acción

La acción no reemplaza a `PericiaPoint`. La acción expresa el uso case-specific
de una técnica reusable sobre un scope concreto.

```text
RequestedPoint
  -> AnalysisPlan
      -> Action
          -> path_scope
          -> file_kinds
          -> search_criteria
          -> PericiaPoint reusable
              -> PericiaExecution
```

## Risks / Trade-offs

- Si la estructura queda muy rígida, algunos puntos abiertos pueden sentirse
  forzados.
  Mitigación: permitir acciones mixtas con `notes` y `expected_outputs`.

- Si todo queda solo en JSON, puede faltar ergonomía de consulta.
  Mitigación: mantener JSON ahora y evaluar modelo separado en un cambio futuro
  si el volumen crece.

- Algunos nombres de carpetas son muy dependientes del origen de evidencia.
  Mitigación: modelar `path_scope` como paths relativos sugeridos, no como
  contratos absolutos.

## Migration Plan

1. Agregar estructura formal a `analysis_playbook.actions`.
2. Derivar acciones estructuradas desde planes existentes donde solo haya texto.
3. Cargar playbooks concretos para varios puntos del catálogo.
4. Adaptar el admin para editar y mostrar acciones estructuradas.
5. Ajustar la ejecución para priorizar la estructura nueva.

## Open Questions

- ¿Conviene que `path_scope` permita múltiples carpetas por acción o una sola?
- ¿`file_kinds` debería usar los `EvidenceFile.FileKind` actuales o aceptar
  extensiones concretas además de esa clasificación?
- ¿Algunos puntos deberían sugerir varias acciones por carpeta en lugar de una
  sola acción compuesta?
