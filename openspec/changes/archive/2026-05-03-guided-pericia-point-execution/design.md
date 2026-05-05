## Context

El motor `PericiaPoint` ya existia como capa reusable de ejecucion sobre
`EvidenceFile`, pero el flujo real del repo evoluciono hacia una pericia guiada
por caso y dispositivo. Hoy el codigo ya puede expandir carpetas, extraer
contenido de varios formatos, registrar hallazgos estructurados y exportar
salidas por caso/dispositivo/punto, pero esa forma de operar no esta
consolidada en OpenSpec ni conectada visualmente al admin mediante una accion
guiada.

Ademas, este proyecto es dockerizado: tanto la lectura de evidencia como la
escritura de salidas deben pensarse en rutas visibles dentro del contenedor,
especialmente bajo `EVIDENCE_INPUT_PATH` y `EVIDENCE_OUTPUT_PATH`.

## Goals / Non-Goals

**Goals:**
- Formalizar que un punto de pericia puede tomar como entrada una carpeta y
  expandirse recursivamente a archivos analizables.
- Formalizar el registro de metadata, fechas y multiples ocurrencias por archivo.
- Formalizar la exportacion de resultados y la creacion de `PreservedArtifact`.
- Diseñar una accion guiada de admin para ejecutar el analisis desde el
  workflow del caso.

**Non-Goals:**
- No rediseñar toda la UX de analisis ni reemplazar Celery.
- No resolver OCR pesado ni soporte total de formatos heredados como `.doc`.
- No diseñar un scheduler complejo; el foco es el disparo guiado y trazable.

## Decisions

### 1. La ejecucion operara sobre carpetas o archivos, pero la unidad de analisis seguira siendo `EvidenceFile`

Aunque la entrada pueda ser una carpeta, la expansion recursiva debe materializar
o resolver `EvidenceFile` por cada archivo encontrado. Esto preserva el modelo
de hallazgos existente y evita introducir una entidad paralela de “job por
carpeta”.

### 2. La salida exportada se organizara por caso/dispositivo/punto/tipo

La estructura de salida debe seguir la logica operativa del laboratorio:

```text
EVIDENCE_OUTPUT_PATH/
  <nro_pericia>/
    <dispositivo>/
      <punto_pericia>/
        <tipo_archivo>/
          <match>.json
```

Esto hace que el operador pueda navegar la evidencia exportada sin depender de
la base y mejora la trazabilidad para informe y auditoria.

### 3. Cada ocurrencia exportada debe corresponder a un `PreservedArtifact`

Cuando la ejecucion tiene contexto de caso y dispositivo, cada match exportado
debe crear un `PreservedArtifact` enlazado al `PericiaFinding`. Esto conecta la
salida operativa con el workflow de informe sin una etapa manual intermedia.

### 4. El boton debe vivir en el workflow, no en un menu tecnico aislado

La accion de ejecutar un punto no deberia esconderse solo en comandos o CRUD
de bajo nivel. El lugar natural es el admin guiado, probablemente desde:
- `AnalysisPlan`
- `DeviceAnalysisResult`
- o el bloque de acciones guiadas del caso

La mejor ubicacion depende de cuanto contexto minimo exijamos antes de correr
el analisis.

## Risks / Trade-offs

- [Exportar un artefacto por ocurrencia puede generar muchos archivos] →
  conviene que el diseño del boton y del workflow haga visible el volumen
  esperado y permita ejecuciones acotadas por dispositivo o plan.
- [El soporte parcial de formatos puede dar una falsa sensacion de cobertura] →
  el workflow debe exponer claramente archivos soportados, no soportados y
  fallidos.
- [Disparar desde admin puede invitar a ejecuciones repetidas] → el boton debe
  mostrar contexto y probablemente enlazar a ejecuciones previas o pedir alcance
  explicito.

## Migration Plan

1. Sincronizar OpenSpec con el motor que ya existe en codigo.
2. Diseñar la accion guiada del admin y definir su punto de entrada canonico.
3. Implementar el boton y cubrirlo con tests de admin + ejecucion.

## Open Questions

- El boton deberia ejecutar:
  - un `AnalysisPlan`,
  - un `DeviceAnalysisResult`,
  - o ambos segun el contexto?
- Queremos ejecucion sincrona desde admin para casos chicos o siempre asíncrona
  via Celery con feedback de estado?
