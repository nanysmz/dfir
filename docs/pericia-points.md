# Pericia Points

Esta primera implementación convierte a los puntos de pericia en un dominio
persistente dentro de Django. La idea es separar tres responsabilidades:

- definición del punto de pericia
- extracción de contenido normalizado
- ejecución que produce hallazgos trazables

## Modelos

La app [`dfir_pericia`](../src/dfir_pericia/) agrega:

- `EvidenceFile`: referencia persistente a un archivo de evidencia
- `PericiaPoint`: definición configurable del punto de pericia
- `PericiaExecution`: registro inmutable de una corrida
- `PericiaFinding`: hallazgo individual generado por una ejecución

Los `PericiaPoint` soportan por ahora tres familias:

- `text_email_search`
- `text_keyword_search`
- `image_characteristic_detection`

## Pipeline

La ejecución sigue este flujo:

```text
archivo -> extractor -> contenido normalizado -> matcher -> hallazgo
```

### Extractores iniciales

- `txt`, `log`, `csv`: texto plano soportado
- `html`, `htm`: HTML convertido a texto normalizado
- `pdf`, `doc`, `docx` y ofimática similar: reportados como `unsupported`
- imágenes: contrato soportado con etiquetas, detecciones y OCR precargado en
  metadata; el motor visual real queda para un cambio posterior

### Matchers iniciales

- email: `exact`, `domain`, `regex`
- keywords: `any`, `all`, `phrase`, `regex`
- imágenes: etiquetas por nombre con umbral de confianza

## Trazabilidad

Cada `PericiaFinding` conserva:

- valor encontrado
- contexto alrededor del match
- archivo fuente
- localizador de origen
- metadata de extracción
- metadata de motor

`PericiaExecution` además separa:

- archivos analizados
- archivos no soportados
- archivos fallidos
- archivos con hallazgos

## Extensión futura

Este corte deja preparados puntos claros de expansión para:

- OCR sobre PDF escaneado e imágenes
- extractores reales para PDF y ofimática
- motores de visión para personas, rostros y nudity score
- reutilización de puntos por caso y futura generación de reporte técnico
