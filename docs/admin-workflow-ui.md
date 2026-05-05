# Admin Workflow UI

El backoffice del sistema usa Django admin con el tema `Unfold` como
superficie principal de trabajo.

## Acceso

Con el stack levantado:

```bash
bin/dfirctl
```

abrir:

```text
http://localhost:8000/admin/
```

## Estructura de navegacion

El sidebar del admin queda agrupado por dominio:

- `Flujo pericial`
  - `Inicio`
  - `Casos periciales`
  - `Evidencia`
  - `Analisis`
  - `Informe`
- `Administracion del sistema`
  - `Usuarios`
  - `Grupos`

## Inicio recomendado del flujo

La portada del admin muestra una columna principal `Empezar una pericia` con
tarjetas secuenciales:

- `Paso 1`: iniciar nueva pericia
- `Paso 2`: registrar evidencia
- `Paso 3`: planificar y ejecutar analisis
- `Paso 4`: cerrar informe

Cada tarjeta expone:

- numero de paso
- titulo de la etapa
- estado visual (`Listo`, `En curso`, `Bloqueado`, `Completado` o `Siguiente`)
- mensaje corto de contexto o prerequisito
- accion principal para entrar a esa etapa

Ademas, cuando ya existen casos, la home muestra un bloque `Retomar pericias`
con:

- porcentaje de avance por caso
- etapa actual derivada del estado real del expediente
- siguiente paso recomendado
- acceso directo para retomar la pericia

La idea es separar dos preguntas operativas distintas:

- `como empiezo una pericia nueva`
- `que caso conviene retomar ahora`

## Uso operativo sugerido

1. crear el `Caso pericial`
2. cargar `Documentos periciales`
3. registrar `Puntos solicitados`
4. incorporar `Evidencia`
5. definir `Planes de analisis`
6. revisar `Resultados de analisis por dispositivo`
7. consolidar `Respuestas a puntos solicitados`
8. completar `Secciones del informe`

## Guia contextual dentro del caso

La ficha de `Casos periciales` expone una tarjeta de `Progreso guiado` que
resume:

- etapa actual
- siguiente etapa recomendada
- porcentaje de avance
- bloqueos o requisitos faltantes por etapa
- accesos rapidos para sembrar tipos de dispositivo y planes iniciales

La guia no bloquea el CRUD manual, pero deja visible el orden recomendado para
evitar omisiones.

## Notas

- El admin mantiene locale `es-ar`.
- La timezone por defecto sigue siendo `America/Argentina/Buenos_Aires`.
- `Usuarios` y `Grupos` tambien se renderizan con `Unfold`, para no mezclar
  estilos dentro del backoffice.
