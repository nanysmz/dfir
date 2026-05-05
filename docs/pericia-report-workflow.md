# Pericia Report Workflow

Esta capa del sistema organiza la pericia como un caso completo orientado al
informe tecnico final, no solo como una coleccion de hallazgos aislados.

## Flujo general

```text
Pericia
  -> documentos fuente
  -> puntos solicitados
  -> evidencia del caso
  -> plan de analisis
  -> resultados por dispositivo
  -> respuestas por punto
  -> secciones del informe
  -> revision final
```

## Flujo guiado derivado del caso

El sistema ahora deriva una guia paso a paso a partir del contenido real del
caso, sin guardar un wizard paralelo.

```text
Caso
  -> Documentos
  -> Puntos solicitados
  -> Evidencia
  -> Planes de analisis
  -> Resultados por dispositivo
  -> Respuestas por punto
  -> Informe
  -> Revision final
```

Cada etapa se calcula con criterios operativos:

- `Documentos`: existe al menos un documento con titulo y contenido util
- `Puntos solicitados`: existe al menos un punto literal del requerimiento
- `Evidencia`: existe al menos un elemento de evidencia del caso
- `Planes de analisis`: cada punto solicitado tiene al menos un plan y hay
  puntos reutilizables disponibles en el catalogo
- `Resultados por dispositivo`: cada elemento de evidencia tiene un resultado
  tecnico no pendiente
- `Respuestas por punto`: cada punto tiene una respuesta al menos parcial con
  resumen tecnico y rationale u observaciones
- `Informe`: existen como minimo las secciones `objeto`,
  `informacion obtenida` y `conclusiones`
- `Revision final`: se habilita cuando respuestas e informe minimo ya estan
  completos

## Modelos principales

La app [`dfir_pericia`](../src/dfir_pericia/) ahora distingue:

- `PericiaCase`: expediente tecnico del caso
- `PericiaDocument`: requerimiento judicial, informe tecnico, anexos u otros
- `RequestedPoint`: punto literal pedido por la autoridad
- `EvidenceItem`: dispositivo, imagen forense, copia de trabajo u otro insumo
- `AnalysisPlan`: playbook del caso que traduce un punto pedido en acciones
  ejecutables y tecnicas reutilizables
- `DeviceAnalysisResult`: resultado tecnico por evidencia para poblar
  `informacion obtenida`
- `RequestedPointResponse`: respuesta tecnica consolidada para un punto pedido
- `ReportSection`: seccion estructurada del informe final
- `PreservedArtifact`: archivo, captura o muestra resguardada para respaldar el
  informe

## Relacion entre puntos pedidos y estrategias reutilizables

Los puntos solicitados de la causa no se mezclan con los `PericiaPoint`
reutilizables:

```text
RequestedPoint
  -> AnalysisPlan (playbook)
      -> acciones ejecutables
          -> PericiaPoint reusable
              -> PericiaExecution
                  -> PericiaFinding
```

Esto permite que:

- el texto judicial quede preservado tal cual fue pedido
- el playbook de analisis pueda ajustarse por caso
- una misma estrategia reusable sirva para muchas pericias
- un mismo punto solicitado derive varias acciones coordinadas

## Taxonomia operativa de puntos solicitados

El sistema deriva familias operativas para puntos periciales recurrentes. No
reemplazan el texto judicial, pero ayudan a sugerir playbooks base:

- `Deteccion de amenazas e intrusion`
- `Material ilicito o multimedia relevante`
- `Reconstruccion de actividad y cronologia`
- `Recuperacion, extraccion y analisis de archivos`
- `Comunicacion, mensajeria y redes sociales`
- `Credenciales, cuentas y acceso`
- `Programas, artefactos de ejecucion y anonimización`
- `Transferencia, fraude y trazas economicas`
- `Hallazgos relevantes adicionales`

Cada `AnalysisPlan` conserva esa taxonomia junto con sus acciones ejecutables
en `scope_snapshot.analysis_playbook`, para que el admin muestre con claridad:

- que punto solicitado se esta respondiendo
- que familias operativas cubre
- que acciones concretas se van a ejecutar
- que tecnica reusable respalda esas acciones

## Acciones estructuradas del plan

Las acciones del playbook ya no se piensan solo como texto libre. Cada una
puede expresar, como minimo:

- `label`: que se va a revisar
- `path_scope`: carpeta o subcarpeta sugerida dentro del dispositivo
- `file_kinds`: tipos o familias de archivo a priorizar
- `search_criteria`: modo de busqueda y terminos
- `expected_outputs`: que evidencia deberia preservarse o citarse
- `pericia_point`: tecnica reusable asociada

Ejemplo operativo:

```json
{
  "label": "Buscar indicadores de software P2P en ActividadReciente",
  "path_scope": ["ActividadReciente"],
  "file_kinds": ["html"],
  "search_criteria": {
    "mode": "any",
    "terms": ["torrent", "emule", "p2p", "utorrent", "bittorrent", "ares"]
  }
}
```

Con esto, el modulo de analisis expresa mejor como un punto solicitado se
traduce en acciones tecnicas concretas sobre carpetas y tipos de archivo
especificos.

## Informacion obtenida

La seccion `informacion obtenida` se piensa por dispositivo o evidencia:

```text
PericiaCase
  -> EvidenceItem
      -> DeviceAnalysisResult
          -> Findings
          -> PreservedArtifact
```

Cada resultado por dispositivo puede quedar como:

- analizado
- parcialmente analizado
- no analizable
- inaccesible
- con seguimiento tecnico requerido

Esto permite reflejar tanto hallazgos positivos/negativos como limitaciones
tecnicas reales del caso.

## Respuesta por punto

El informe final necesita una capa intermedia entre findings y conclusiones.
`RequestedPointResponse` agrupa:

- resultados por dispositivo
- ejecuciones de estrategias reutilizables
- hallazgos concretos
- artefactos preservados
- observaciones tecnicas

Con eso se puede responder cada punto solicitado de forma trazable.

## Secciones del informe

`ReportSection` representa el esqueleto del informe tecnico. En esta etapa se
modelan al menos:

- objeto
- elementos ofrecidos
- herramientas
- metodologia
- informacion obtenida
- conclusiones
- evidencia
- anexos

La redaccion final sigue siendo asistida y revisable por el analista.

## Workflow inicial en Django admin

La primera superficie operativa queda pensada para el admin tematico del
proyecto:

1. crear `PericiaCase`
2. cargar `PericiaDocument`
3. registrar `RequestedPoint`
4. asociar `EvidenceItem`
5. crear `AnalysisPlan`
6. ejecutar `PericiaPoint` con contexto de caso
7. revisar `DeviceAnalysisResult`
8. consolidar `RequestedPointResponse`
9. ensamblar `ReportSection`

Esto deja el dominio listo para una futura UI dedicada sin perder trazabilidad.

## Como iniciar un flujo hoy

Hoy el flujo se inicia desde Django admin. La secuencia recomendada es esta:

1. levantar el stack:

```bash
bin/dfirctl
```

2. entrar al admin:

```text
http://localhost:8000/admin/
```

3. crear la pericia en `Pericia cases`:
- `case_reference`: identificador de la causa o IPP
- `authority_name`: fiscalia, juzgado u organismo
- `authority_unit`: unidad o secretaria
- `jurisdiction`: departamento judicial / jurisdiccion
- `report_date`: fecha del informe
- `analyst_name`: nombre del perito
- `summary`: descripcion breve del caso

4. dentro de esa pericia, cargar los documentos fuente en `Pericia documents`:
- requerimiento judicial
- acta de apertura
- anexos si existen

5. registrar los puntos solicitados en `Requested points`:
- `order`: orden del punto
- `short_label`: etiqueta corta para ubicarlo rapido
- `literal_text`: texto exacto del punto pedido

6. registrar la evidencia en `Evidence items`:
- un dispositivo original
- una imagen forense
- una copia de trabajo
- una extraccion logica

7. para cada punto solicitado, crear un `Analysis plan`:
- elegir el `RequestedPoint`
- elegir el `PericiaPoint` reusable
- anotar `analysis_targets` con las fuentes a revisar, por ejemplo:
  - `SAM`
  - `Web History`
  - `Installed Programs`
  - `AppData`

8. crear o actualizar `Device analysis results` para cada dispositivo:
- estado tecnico
- observaciones
- motivo tecnico si no pudo analizarse
- recomendacion de seguimiento si aplica

9. ejecutar estrategias reutilizables y vincular sus resultados:
- las corridas quedan en `Pericia executions`
- los hallazgos quedan en `Pericia findings`

10. consolidar la respuesta por punto en `Requested point responses`:
- resumen tecnico
- observaciones
- rationale
- vinculos a findings, ejecuciones, resultados por dispositivo y artefactos preservados

11. armar el esqueleto del informe en `Report sections`:
- objeto
- elementos ofrecidos
- herramientas
- metodologia
- informacion obtenida
- conclusiones
- evidencia / anexos

12. realizar la `Revision final`:
- verificar consistencia entre puntos solicitados, respuestas y conclusiones
- confirmar que no queden resultados pendientes sin justificar
- validar que el informe minimo ya este armado antes del cierre operativo

## Flujo minimo recomendado

Si queres empezar una pericia nueva con el menor recorrido posible:

```text
PericiaCase
  -> PericiaDocument (requerimiento)
  -> RequestedPoint
  -> EvidenceItem
  -> AnalysisPlan
  -> DeviceAnalysisResult
  -> RequestedPointResponse
  -> ReportSection
```

## Que queda manual y que queda automatizable

Hoy:
- la apertura del caso y la carga documental son manuales
- la definicion de puntos solicitados es manual
- el plan de analisis es manual asistido
- las estrategias reutilizables pueden ejecutar hallazgos tecnicos
- la consolidacion del informe sigue siendo asistida por el perito

Mas adelante:
- se puede extraer texto de oficios y requerimientos
- se pueden sugerir puntos solicitados
- se pueden prearmar respuestas por punto
- se puede generar un borrador de informe tecnico
