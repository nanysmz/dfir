## Why

La taxonomía del catálogo de puntos periciales ya quedó definida, pero todavía
no está suficientemente aterrizada en acciones operativas concretas. Hoy el
`AnalysisPlan` puede guardar acciones como texto libre, lo que no alcanza para
expresar con claridad:

- qué carpeta o subcarpeta del dispositivo debe revisarse
- qué tipos de archivo aplican
- qué criterio de búsqueda debe usarse
- qué técnica reusable respalda cada acción

Esto se vuelve evidente con ejemplos reales del catálogo, como:

- `Identificación de programas P2P instalados`
  - revisar `ActividadReciente`
  - solo archivos `html`
  - palabras clave `torrent`, `emule`, `p2p`, `utorrent`, `bittorrent`

Si las acciones siguen en texto libre, el módulo de análisis no termina de
expresar qué se va a ejecutar ni cómo se relaciona cada punto solicitado con
las búsquedas concretas del caso.

## What Changes

- Definir una primera batería de playbooks concretos para varios puntos del CSV
  frecuente.
- Exigir que cada acción del `AnalysisPlan` tenga estructura mínima:
  `path_scope`, `file_kinds`, `search_criteria`, `action_family`,
  `pericia_point`.
- Hacer que el admin del módulo de análisis muestre y edite esas acciones como
  acciones ejecutables estructuradas, no solo como texto libre.
- Mantener compatibilidad con los planes ya existentes, derivando acciones
  estructuradas desde el texto cuando todavía no exista estructura completa.

## Impact

- El módulo de análisis pasa de “plan = texto + técnica” a “plan = conjunto de
  acciones ejecutables”.
- La taxonomía queda aterrizada operativamente y sirve mejor como base de
  ejecución y seguimiento.
- Se reduce ambigüedad para el analista y se prepara el camino para ejecutar
  acciones específicas por carpeta, tipo de archivo y criterio de búsqueda.
