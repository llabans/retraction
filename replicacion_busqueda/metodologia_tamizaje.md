# Metodología de tamizaje aplicada en la replicación independiente

Versión 1.0 · 2026-11-04 · Aplicada por Claude como revisor único, **sin mirar la base de 120** hasta terminar el tamizaje.

## 1. Unidad de análisis

El **artículo retractado**. Si una nota retracta varios artículos, cada artículo es un registro (p. ej., una nota que retracta dos ensayos del mismo autor). Si un artículo tiene varias notas (corrección, expresión de preocupación y retracción), se usa solo la retracción.

## 2. Vinculación nota → artículo retractado

1. Por el PMID de la nota en Retraction Watch (`RetractionPubMedID`), que da el PMID y DOI del original. 125 de 132 notas se vincularon así.
2. Si no estaba en RW, búsqueda manual en PubMed por el título citado en la nota (3 casos).
3. Si el registro de PubMed es el propio artículo retractado (sin nota aparte), el original es ese mismo PMID.
4. Se corrigieron dos errores de vinculación de RW: una nota asignada al artículo equivocado y un PMID del original erróneo (en ese caso se usa el DOI).

## 3. Criterios (tomados del manuscrito)

**Incluir** si se cumplen las tres condiciones:

| # | Criterio | Fuente del dato |
|---|---|---|
| I1 | Es una retracción o retiro formal del artículo, incluida la *retracción y reemplazo* y el retiro de un artículo en prensa | Tipo de nota (PubMed), `RetractionNature` (RW), título de la nota |
| I2 | La nota se publicó entre el 1-ene-2003 y el 7-ago-2023 (no importa el año del ensayo) | `RetractionDate` (RW) o fecha de la nota (PubMed) |
| I3 | El artículo retractado es un **ensayo clínico**: estudio prospectivo en **humanos** que **asigna** a los participantes a una o más intervenciones para evaluar sus efectos sobre desenlaces de salud (definición OMS/ICMJE). Incluye ensayos no aleatorizados, de un solo brazo y de fase I | Tipo de publicación PubMed; título; resumen si hay duda |

**Excluir**:

| Código | Motivo |
|---|---|
| X1 | No es una nota de retracción ni un artículo retractado (p. ej., un estudio bibliométrico sobre retracciones) |
| X2 | Corrección, erratum o retiro de un corrigendum sin retracción del artículo; expresión de preocupación |
| X3 | Nota fuera de la ventana 2003-01-01 a 2023-08-07 |
| X4 | No es ensayo: observacional, metaanálisis, revisión sistemática, carta, editorial, estándar biológico, subestudio de biomarcadores pronósticos, experimento fisiológico sin intervención terapéutica ni desenlace clínico |
| X5 | Ensayo en animales (veterinario) |
| X6 | Protocolo de ensayo sin resultados |

## 4. Zonas grises (se incluyeron, pero se marcan para que los autores decidan)

| Situación | Decisión | n en E2 |
|---|---|---|
| Retracción y reemplazo (JAMA, JAMA Psychiatry) | Incluir: es una retracción formal | 4 |
| Retiro de un artículo en prensa (Elsevier «WITHDRAWN») | Incluir | 1 |
| Retiro de una versión aceptada que se publicó por error y se republicó después | Incluir | 1 |
| Estudio piloto de un solo brazo con intervención | Incluir (cumple I3) | 1 |

Si los autores definen «clinical trial» como **solo ECA** (marcador pendiente P-31), hay que excluir además los ensayos no aleatorizados. En E2 son pocos (p. ej., un estudio piloto de un solo brazo).

## 5. Orden de decisión

1. ¿Es nota de retracción o artículo retractado? Si no → X1.
2. ¿Es retracción (no corrección ni expresión de preocupación)? Si no → X2.
3. ¿La fecha de la nota está en la ventana? Si no → X3.
4. Identificar el artículo original (sección 2).
5. ¿Es un ensayo? Primero el tipo de publicación de PubMed: si tiene Clinical Trial o RCT, se acepta salvo evidencia en contra. Si no lo tiene, leer el título y luego el resumen. → X4, X5 o X6, o incluir.
6. Anotar la zona gris si corresponde.

En E2, 36 de los 129 originales no tenían tipo de publicación de ensayo y se revisaron por resumen. 25 resultaron ensayos y 11 no (cifra corregida en C-24). Por otro lado, 2 originales que sí tenían tipo de publicación de ensayo se excluyeron al leerlos: un protocolo y un subestudio de biomarcadores.

## 6. Resultado del tamizaje (E2, 132 registros)

- 137 filas (artículos), porque 4 notas retractan más de un artículo.
- **119 artículos incluidos**. 7 están en zona gris.
- 18 excluidos: metaanálisis 3, protocolos 3, cartas 2, editorial 1, observacionales 2, veterinario 1, subestudio de biomarcadores 1, revisión Cochrane 1, estándar biológico 1, estudio bibliométrico 1, retiro de corrigendum 1, nota de 2025 1.
- Corrección C-24: un registro se había excluido como «experimento fisiológico», pero se declara ECA; ahora está incluido. Lección para el formulario: si el título o el resumen dicen *randomized*, no se excluye por X4 sin una segunda opinión.

Detalle: `datos/tamizaje_pubmed.csv`. El código está en `scripts/tamizaje_pubmed.py`; las decisiones registro por registro (`EXC`, `GRAY` y correcciones) están en `datos/decisiones_tamizaje.json`. Ninguno de los dos archivos de `datos/` se publica en este repositorio.

## 7. Recomendaciones para la extensión 2023–2026

- **Dos revisores independientes** con este mismo formulario, y kappa sobre una muestra piloto de unos 50 registros antes de seguir. En la base original no consta si el tamizaje fue por duplicado (marcador pendiente).
- Registrar el motivo de exclusión con los códigos X1–X6 y la zona gris en una columna aparte.
- Para la clasificación de «ensayo», usar primero el tipo de publicación de PubMed del original y luego el resumen. No usar solo el título: en E4, el 23% de los candidatos que se identificaron solo por el título no eran ensayos.
- Fijar la definición de «clinical trial» **antes** de tamizar (P-31).
