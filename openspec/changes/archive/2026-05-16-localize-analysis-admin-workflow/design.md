## Context

El proyecto ya declara `LANGUAGE_CODE = "es-ar"` y
`TIME_ZONE = "America/Argentina/Buenos_Aires"`, pero el admin todavia expone
varios puntos del flujo de analisis con mezcla de español e ingles:

- etiquetas como `Pericia point`, `Label`, `Strategy notes` o `Analysis targets`
- mensajes de ayuda parcialmente en ingles
- una secuencia operatoria del modulo de analisis que no queda explicita

Ademas, el formulario de `Planes de analisis` ya modela `analysis_targets`
como alcance de evidencia, pero la experiencia visible no esta permitiendo al
operador seleccionar de manera clara y confiable las ubicaciones reales del
volumen montado para un plan como `Correos`.

Por ultimo, el usuario necesita saber cual es el orden practico dentro de
`Administracion de Analisis`: que objeto configurar primero, que despues, y
que resultado deberia salir de cada etapa.

## Goals / Non-Goals

**Goals:**
- Asegurar que la superficie visible del backoffice orientado al flujo
  principal quede en español consistente con Buenos Aires, Argentina.
- Corregir la UX de `analysis_targets` para que el operador pueda seleccionar
  ubicaciones montadas como alcance real del plan.
- Hacer explicita la secuencia operatoria del modulo `Analisis`.

**Non-Goals:**
- No internacionalizar todo el stack de Django o librerias de terceros fuera
  del flujo operador principal.
- No rediseñar por completo el modelo interno de `AnalysisPlan`.
- No cambiar en este paso la logica profunda de ejecucion del motor analitico.

## Decisions

### 1. La localizacion operatoria debe priorizar el flujo principal, no solo la configuracion global

No alcanza con tener `es-ar` y `America/Argentina/Buenos_Aires` en settings.
El cambio debe revisar nombres visibles, ayudas contextuales, badges y textos
de navegacion del flujo pericial para que el operador no encuentre ingles en
los pasos cotidianos.

Alternativa considerada: limitarse a settings e idioma base. Se descarta
porque el problema reportado ocurre en etiquetas y pantallas ya renderizadas.

### 2. `Analysis targets` debe presentarse como selector de alcance montado y no como campo tecnico opaco

El plan debe dejar claro que esos targets representan las carpetas o archivos
del dispositivo sobre los que correra el playbook. La interfaz debe:

- mostrar opciones navegables desde el volumen montado
- permitir seleccion multiple visible
- dejar claro que el target es el alcance del plan, no una nota libre

Alternativa considerada: mantener el modelo actual y solo traducir el label.
Se descarta porque no resuelve la dificultad operatoria para seleccionar la
ubicacion.

### 3. El modulo de analisis debe exponer un orden recomendado por responsabilidades

La propuesta es expresar una secuencia clara:

1. `Puntos de pericia` como catalogo reusable de tecnicas y criterios
2. `Planes de analisis` como playbooks por caso y por punto solicitado
3. `Ejecuciones` como corrida concreta del plan sobre targets definidos
4. `Resultados por dispositivo` como salida tecnica revisable

Eso puede aparecer como ayuda contextual, texto de modulo, home guiado o
resumen en la vista del plan.

Alternativa considerada: asumir que el operador ya entiende el orden por los
nombres de los modelos. Se descarta porque hoy hay ambigüedad entre tecnica,
plan y ejecucion.

## Risks / Trade-offs

- [Traducir parcialmente puede dejar una UI mezclada] -> Mitigacion: cubrir
  especificamente las pantallas del flujo principal de analisis y sus textos de
  ayuda.
- [Cambiar el widget de `analysis_targets` puede afectar tests o datos
  existentes] -> Mitigacion: preservar el almacenamiento como lista y ajustar
  solo la experiencia de seleccion.
- [Agregar demasiado texto explicativo puede sobrecargar la pantalla] ->
  Mitigacion: usar ayuda contextual breve y orientada a accion.

## Migration Plan

1. Auditar las etiquetas visibles del modulo `Analisis` y normalizarlas al
   español del flujo pericial.
2. Ajustar el formulario de `AnalysisPlan` para que `analysis_targets` sea
   seleccionable de manera clara desde ubicaciones montadas.
3. Incorporar textos o ayudas que expliquen el orden operativo entre catalogo,
   planes, ejecuciones y resultados.
4. Cubrir con tests de admin el render localizado y la seleccion de targets.

## Open Questions

- El orden recomendado del modulo de analisis debe verse solo como ayuda
  textual o tambien reflejarse en la navegacion lateral?
- `analysis_targets` debe ofrecer archivos y carpetas siempre, o limitarse por
  tipo de punto de pericia?
