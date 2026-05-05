# manual-analysis-execution-ux Design

## Context

El sistema ya distingue entre:

- `AnalysisPlan`: receta case-driven por punto solicitado
- `PericiaExecution`: corrida concreta

La exploracion confirmo que el modelo manual sigue siendo deseable por control
pericial y trazabilidad. El problema no es "manual vs automatico" sino la falta
de una señal clara para iniciar el trabajo.

## Decision 1: Modelo mixto de disparo manual

Se adopta un modelo mixto:

1. nivel caso: `Ejecutar planes listos`
2. nivel lista de planes: `Ejecutar este plan`

La accion a nivel caso resuelve el inicio operativo del analisis. La accion por
fila preserva el control fino, la reejecucion selectiva y el trabajo
iterativo.

## Decision 2: Una ejecucion por plan

Aunque un `AnalysisPlan` pueda contener multiples `analysis_targets`, el modelo
operativo se mantiene como:

```text
1 plan + N targets = 1 ejecucion
```

No se propone multiplicar ejecuciones por target en esta etapa. Eso mantiene la
trazabilidad mas simple y evita ruido operativo al trabajar con varios
dispositivos o varias carpetas dentro de un mismo objetivo analitico.

## Decision 3: Estados operativos visibles derivados

El estado persistido del plan puede seguir siendo relativamente compacto, pero
la UX necesita estados visibles mas expresivos. La interfaz deberia poder
mostrar:

- `Incompleto`
- `Listo`
- `En cola`
- `En ejecucion`
- `Completado`
- `Completado con observaciones`
- `Fallido`
- `Omitido`

Estos estados se derivan de:

- configuracion del plan
- disponibilidad de targets
- ultima ejecucion asociada
- incidencias tecnicas registradas por la ejecucion

## Decision 4: Semantica de `Completado con observaciones`

Se incorpora una categoria visible intermedia para ejecuciones utiles con
incidencias parciales. Esta categoria aplica cuando la corrida termino y dejo
resultados utilizables, pero hubo advertencias relevantes, por ejemplo:

- archivos no soportados
- archivos fallidos
- targets sin contenido util
- exportaciones parciales
- otros warnings tecnicos del motor

`Fallido` debe reservarse para una ejecucion que no pudo producir un resultado
tecnicamente util como unidad.

## Decision 5: Criterio de planes listos

Un plan es elegible para `Ejecutar planes listos` cuando:

- pertenece al caso actual
- tiene `pericia_point`
- tiene uno o mas `analysis_targets`
- no esta omitido
- no tiene una ejecucion activa (`pending` o `running`)

Por defecto, el disparo masivo incluye solo planes listos no ejecutados
activamente. No reejecuta automaticamente los `Completados` ni los `Fallidos`.
Las reejecuciones y reintentos quedan como accion manual por fila.

## UX Outline

### Caso pericial

```text
Analisis
- Planes listos: N
- Activos: N
- Fallidos: N
- Completados: N

[Ejecutar planes listos]
[Ver planes de analisis]
[Ver ejecuciones]
```

### Lista de planes

```text
Correos      Listo                     [Ejecutar este plan]
Wallets      En cola                   [Ver ejecucion]
PDF          Completado               [Reejecutar]
Imagenes     Fallido                  [Reintentar]
Chats        Completado c/obs.        [Ver resultado]
```

### Detalle del plan

```text
Plan: Correos
Targets: 2
Estado: Listo

[Iniciar analisis de este plan]
```

## Risks

- [Ambiguedad entre estado persistido y estado visible] -> Resolver con reglas
  de derivacion claras y texto consistente en UI
- [Reejecuciones accidentales] -> Excluir planes activos y completados del
  disparo masivo por defecto
- [Interpretar como fallo una corrida parcial util] -> Usar `Completado con
  observaciones` en vez de escalar a `Fallido`
- [Resumen masivo poco claro] -> El disparo por caso debe informar cuantos
  planes fueron lanzados, omitidos, o ya estaban activos
