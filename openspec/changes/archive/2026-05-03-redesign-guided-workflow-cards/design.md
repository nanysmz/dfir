## Context

La home del admin ya cumple una funcion operativa importante: iniciar una
pericia, mostrar el flujo recomendado y permitir retomar casos existentes.
Sin embargo, la capa visual actual mezcla tres lenguajes al mismo tiempo:
hero, shortcuts y cards de checklist. Eso hace que las tarjetas del paso a
paso compitan entre si y no transmitan con suficiente claridad cual es el
orden, el estado ni la accion mas importante.

El proyecto ya usa `Unfold`, mantiene un workflow guiado derivado del estado
real del caso y toma `/admin/` como punto de entrada canonico del backoffice.
Por eso el cambio no necesita otra UI: necesita que las tarjetas del flujo
principal se sientan como una secuencia visual fuerte, escaneable y coherente
con el resto del admin.

## Goals / Non-Goals

**Goals:**
- Hacer que las tarjetas del paso a paso se lean como una ruta de trabajo
  ordenada, no como una grilla de accesos equivalentes.
- Darle a cada tarjeta una jerarquia clara entre numero de paso, titulo,
  descripcion, estado, prerequisitos y accion.
- Diferenciar visualmente estados como `listo`, `en curso`, `bloqueado` y
  `completado`.
- Integrar mejor el flujo principal con el bloque `Retomar pericias`.
- Mantener compatibilidad con `Unfold`, mobile y el enfoque dockerizado del
  proyecto.

**Non-Goals:**
- Rediseñar todo el admin o todas las paginas CRUD.
- Cambiar la logica de derivacion del workflow mas alla de lo necesario para
  exponer mejores estados visuales.
- Introducir animaciones complejas o dependencias nuevas de frontend.
- Reemplazar el bloque `Retomar pericias` por un dashboard distinto.

## Decisions

1. Usar tarjetas de etapa con estructura estable y semantica repetible.

   Cada tarjeta deberia incluir: numero de paso, nombre de etapa, resumen,
   badge de estado, mensaje de prerequisito o contexto, y CTA principal.
   Esto reduce ambigüedad y permite que el operador compare etapas rapido.
   Alternativa considerada: mantener cards libres con solo texto y link,
   descartada porque se parecen demasiado a shortcuts genericos.

2. Mostrar el flujo principal como secuencia priorizada y no solo como grilla.

   Aunque visualmente pueda seguir existiendo una grilla responsive, el diseño
   debe comunicar un orden explicito entre tarjetas. Eso puede reforzarse con
   numeracion, conectores visuales sutiles, contraste progresivo y una sola
   tarjeta destacada como siguiente paso natural. Alternativa considerada:
   mantener todas las tarjetas con el mismo peso visual, descartada porque
   diluye la accion principal.

3. Derivar el estado visual de cada tarjeta desde el workflow real.

   La tarjeta no debe inventar estado decorativo. Debe usar la informacion ya
   calculada por la capa de workflow para determinar si una etapa esta lista,
   bloqueada, en curso o completada. Alternativa considerada: mapear estados
   solo desde el numero de paso o desde texto fijo, descartada por riesgo de
   inconsistencia.

4. Separar visualmente `comenzar` de `retomar`.

   El bloque de flujo principal debe responder “como empiezo”, mientras que
   `Retomar pericias` debe responder “que caso sigo ahora”. Las dos zonas deben
   convivir sin competir por el mismo nivel de prioridad. Alternativa
   considerada: mezclar casos activos dentro de las mismas tarjetas de etapa,
   descartada porque ensucia la lectura del flujo base.

5. Mantener implementacion server-rendered y basada en componentes de Unfold.

   El cambio debe vivir en templates y contexto de Django, usando componentes y
   clases ya presentes en `Unfold`. Alternativa considerada: sumar una capa JS
   mas custom para interacciones complejas, descartada porque aumenta costo y
   no es necesaria para el objetivo.

## Risks / Trade-offs

- [Demasiada ornamentacion visual] → Mantener foco en estado, orden y CTA antes
  que en decoracion.
- [Tarjetas muy densas en mobile] → Diseñar con una estructura compacta y
  colapsar texto secundario de forma natural por layout, no por JS.
- [Estado visual ambiguo entre “listo” y “en curso”] → Definir una taxonomia
  pequeña y consistente de badges y mensajes.
- [Competencia entre hero, flujo y retomar] → Rebalancear jerarquia para que la
  primera accion visible sea siempre clara.
- [Ajustes de template fragiles frente a Unfold] → Reusar componentes nativos y
  evitar hacks de markup demasiado acoplados al tema.

## Migration Plan

1. Redefinir la estructura visual esperada de las tarjetas del flujo en la home.
2. Ajustar el contexto del dashboard para exponer el estado visual necesario.
3. Reescribir el bloque de cards del template usando componentes de `Unfold`.
4. Actualizar tests del admin para validar la nueva jerarquia y los estados.
5. Actualizar documentacion operativa del home guiado.

Rollback: volver al layout actual del home dejando intacta la logica del
workflow derivado.

## Open Questions

- ¿Conviene destacar solo una tarjeta como “siguiente paso recomendado” o varias
  segun disponibilidad del flujo?
- ¿El badge de estado debe usar solo color y texto o tambien iconografia
  distinta por etapa?
- ¿Vale la pena agregar una vista compacta adicional para resoluciones
  menores, o alcanza con un stacking mobile de las mismas tarjetas?
