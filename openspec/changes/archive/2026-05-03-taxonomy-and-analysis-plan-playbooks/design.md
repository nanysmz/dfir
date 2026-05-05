## Context

El CSV de puntos periciales frecuentes muestra que la mayoría de los “puntos de
pericia” reales no son búsquedas técnicas atómicas, sino objetivos de análisis
de alto nivel. Ejemplos como “Determinación de accesos y logs de cuentas”,
“Recuperación de comunicaciones” o “Detección de malware” no se resuelven con
una sola técnica reusable, sino con un conjunto de acciones coordinadas.

El modelo actual ya tiene varias piezas valiosas:
- `RequestedPoint`: el punto literal del caso
- `PericiaPoint`: técnica reusable
- `AnalysisPlan`: puente actual
- `PericiaExecution`: corrida concreta
- `RequestedPointResponse`: respuesta consolidada

Pero hoy `AnalysisPlan` queda demasiado plano, porque parece unir un punto
solicitado con una sola estrategia, cuando en realidad debería expresar cómo
ese punto se traduce en varias acciones ejecutables.

## Goals / Non-Goals

**Goals:**
- Definir una taxonomía completa y operativa para los 25 puntos del catálogo.
- Clarificar la frontera semántica entre punto solicitado, técnica reusable,
  plan de análisis y ejecución.
- Redefinir `AnalysisPlan` como playbook o receta de acciones por caso.

**Non-Goals:**
- No implementar todavía todas las nuevas familias técnicas derivadas de la
  taxonomía.
- No rediseñar toda la UI final del módulo de análisis en este mismo change.
- No volver `PericiaPoint` un modelo puramente case-scoped.

## Decisions

### 1. `RequestedPoint` sigue siendo el objetivo investigativo del caso

El punto solicitado mantiene lenguaje judicial/investigativo. No debe
reducirse a una técnica reusable ni a una query concreta.

### 2. `PericiaPoint` pasa a representar técnicas atómicas o reusables

`PericiaPoint` no es el equivalente del punto pericial judicial. Es una pieza
de bajo nivel del análisis, por ejemplo:
- buscar correos
- extraer credenciales
- detectar material multimedia
- revisar logs de actividad

### 3. `AnalysisPlan` debe convertirse en playbook de acciones

La unidad conceptual correcta es:

```text
RequestedPoint
   -> AnalysisPlan
        -> acciones ejecutables
             -> PericiaPoint reusable
             -> target device(s)
             -> scope
             -> execution(s)
```

Eso permite que un mismo punto solicitado use varias acciones, y que esas
acciones se apliquen a uno o varios dispositivos.

### 4. Taxonomía operativa completa de los 25 puntos

La taxonomía propuesta es:

```text
A. Detección de amenazas e intrusión
01. Detección de malware (troyanos, spyware, etc.) y análisis de intrusión.
14. Determinación de vectores de ataque (phishing, MITM, malware).

B. Detección y recuperación de material ilícito o multimedia relevante
02. Detección de material ilícito (incluyendo pornografía infantil o M.A.S.I.).
03. Detección de material multimedia relevante (imágenes, videos, audios) vinculado a la investigación.
24. Recuperación de comunicaciones (SMS, WhatsApp, redes sociales, VoIP).

C. Reconstrucción de actividad y cronología
04. Determinación de accesos y logs de cuentas (IP, fechas, horarios).
05. Determinación de actividad reciente y última actividad registrada.
09. Determinación de fechas de impresiones realizadas.

D. Recuperación, extracción y análisis de archivos
06. Determinación de eliminación de archivos y recuperación de los mismos.
16. Extracción y análisis integral de archivos (incluyendo eliminados).
17. Identificación de archivos o documentación específica vinculada a personas o entidades.

E. Comunicación, mensajería y redes sociales
07. Determinación de existencia de aplicaciones de mensajería y uso para distribución de material.
18. Identificación de contactos, llamadas, mensajes y actividad en redes sociales.
24. Recuperación de comunicaciones (SMS, WhatsApp, redes sociales, VoIP).

F. Credenciales, cuentas y acceso
04. Determinación de accesos y logs de cuentas (IP, fechas, horarios).
08. Determinación de existencia de software para desbloqueo de dispositivos.
13. Determinación de uso de software de acceso remoto.
19. Identificación de correos electrónicos, credenciales almacenadas y formularios de autocompletado.
22. Identificación de usuarios de los dispositivos y perfiles de uso.

G. Programas, artefactos de ejecución y anonimización
10. Determinación de programas instalados y ejecutados, incluyendo herramientas de anonimización.
13. Determinación de uso de software de acceso remoto.
21. Identificación de programas P2P instalados.

H. Transferencia, fraude y trazas económicas
11. Determinación de transferencia de archivos (P2P, descargas directas, chat, correo).
12. Determinación de uso de billeteras virtuales.
15. Extracción de información específica (CBU, cuentas destino, IPs, geolocalización).
20. Identificación de documentación de terceros utilizada en posibles fraudes.
25. Recuperación de evidencia vinculada a fraudes (capturas, transferencias, logs).

I. Categoría abierta / hallazgos relevantes
23. Obtención de cualquier otro dato relevante para la investigación.
```

La superposición entre categorías es intencional: algunos puntos pertenecen a
más de una perspectiva operativa. La taxonomía no es un árbol rígido, sino un
mapa de familias de trabajo forense.

### 5. Cada categoría sugiere playbooks base

Cada grupo taxonómico debe poder sugerir uno o más playbooks de acciones. Por
ejemplo:
- `Reconstrucción de actividad y cronología`:
  revisar logs, timestamps, sesiones, actividad reciente
- `Credenciales, cuentas y acceso`:
  correos, formularios, credenciales, tokens, wallets, perfiles
- `Transferencia, fraude y trazas económicas`:
  P2P, descargas, transferencias, CBU, cuentas destino, evidencia de fraude

## Risks / Trade-offs

- [La taxonomía puede quedar demasiado rígida] → Mitigación: permitir múltiples
  categorías por punto o relación flexible con playbooks.
- [El cambio puede sentirse grande para la UI actual] → Mitigación: separar la
  redefinición conceptual de la implementación incremental del admin.
- [Seguir llamando “PericiaPoint” tanto a técnica como a punto judicial genera
  confusión] → Mitigación: reforzar en modelo y UI que `RequestedPoint` es el
  objetivo del caso y `PericiaPoint` es la técnica reusable.

## Migration Plan

1. Formalizar la taxonomía en OpenSpec.
2. Introducir el concepto de playbook de acciones en `AnalysisPlan`.
3. Adaptar progresivamente forms/admin/workflow para que el análisis se arme
   desde acciones derivadas de cada punto solicitado.
4. Implementar la evolución del modelo y de la UI en cambios posteriores o en
   el apply de este mismo change si se decide seguir.

## Open Questions

- ¿Un `RequestedPoint` debe tener un solo `AnalysisPlan` con varias acciones, o
  varios `AnalysisPlan` más pequeños?
- ¿Las acciones ejecutables deben modelarse como JSON estructurado, relación
  separada o plantilla reusable?
- ¿Conviene capturar la taxonomía en una tabla/modelo o alcanza con metadata y
  playbooks sugeridos en una primera versión?
