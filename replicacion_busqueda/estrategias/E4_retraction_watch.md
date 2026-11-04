# E4 · Retraction Watch Database (Crossref)

| Campo | Valor |
|---|---|
| Fuente | Retraction Watch Database, distribución abierta de Crossref: `https://gitlab.com/crossref/retraction-watch-data/-/raw/main/retraction_watch.csv` |
| Fecha de descarga | 2026-11-04 (último registro con fecha de retracción 2026-10-15; 73,597 filas; SHA-256 empieza por `e5351ee51ab3f1da`) |
| Resultados | **1,058** candidatos a ensayo clínico retractado con nota 2003-01-01 a 2023-08-07 |
| Archivos | `datos/brazo_rw.csv`, `ris/E4_retraction_watch.ris`, `scripts/brazo_rw.py` (los de `datos/` y `ris/` no se publican en este repositorio) |

## Filtros (en este orden)

1. `RetractionNature == "Retraction"`. Se excluyen correcciones, expresiones de preocupación y reinstauraciones.
2. `RetractionDate` entre 2003-01-01 y 2023-08-07 (fecha de la nota, como en el manuscrito).
3. El original es un ensayo clínico si cumple **al menos una** condición:
   - **PT**: su PMID está en E3 (PubMed lo tipifica como Clinical Trial o RCT y como Retracted Publication). 894 registros.
   - **Título**: el título contiene un término explícito de diseño de ensayo y ninguno de exclusión. 164 registros más.

```
Términos de ensayo: randomi[sz] | clinical trial | controlled trial | placebo[- ]controlled | double[- ]blind |
                    single[- ]blind | cross[- ]?over trial | phase (I|II|III|1|2|3) | \btrial\b
Términos de exclusión: protocol | meta[- ]?analy | systematic review | rationale and design | study design | review of
```

## Precisión estimada

- Estrato PT (894): alta, porque NLM asigna el tipo de publicación.
- Estrato solo título (164): en una muestra aleatoria de 30 hubo 7 falsos positivos (23%), como «randomized algorithms», «trial of labor» o comentarios sobre un ensayo. Requiere tamizaje manual.
- Precisión global estimada: alrededor de 96%, es decir, unos 1,020 ensayos elegibles antes del tamizaje manual.

## Lo que este filtro automático no capta

Tiene una sensibilidad de 107/113 frente a los ensayos verdaderos de la base. Pierde los ensayos sin tipo de publicación PubMed y sin término de diseño en el título (4 de la base), los que RW registra como «Reinstatement» (una retracción y reemplazo de JAMA) y los que no están en RW (1).

**Para recuperarlos**, revisar a mano los 1,136 registros del tipo `ArticleType` «Clinical Study» que quedan fuera del filtro, o completar con E2 y Scopus.

## Para la extensión 2023–2026

El mismo script con `lo = 2023-08-08` y `hi =` la fecha de descarga. Guardar la copia del CSV descargado con su fecha y su SHA-256.
