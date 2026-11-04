# E3 · PubMed · artículos retractados con tipo de publicación de ensayo

| Campo | Valor |
|---|---|
| Base de datos | PubMed |
| Interfaz | Servidor MCP de PubMed (`esearch`, paginado de 200 en 200, orden por fecha de publicación) |
| Fecha de ejecución | 2026-11-04 |
| Resultados | **1,502** artículos (sin límite de fecha); 1,368 tienen registro en Retraction Watch; 894 tienen fecha de retracción 2003-01-01 a 2023-08-07 según RW |
| Archivos | `datos/pt_trials_retracted_all.txt`, `ris/E3_pubmed_tipo_publicacion.ris` (los de `datos/` y `ris/` no se publican en este repositorio) |

## Cadena exacta

```
"Retracted Publication"[pt] AND ("Clinical Trial"[pt] OR "Randomized Controlled Trial"[pt])
```

`"Clinical Trial"[pt]` incluye las fases I–IV y el ensayo controlado. Esta estrategia busca el **artículo retractado** y no la nota, así que no depende de cómo se redactó el aviso.

## Uso en la replicación

No se usó sola. Sirvió como clasificador objetivo de «ensayo clínico» en el brazo de Retraction Watch (E4). Si el PMID del artículo original está en esta lista, el registro cuenta como ensayo.

## Limitaciones

- La ventana temporal del estudio es la de la **nota** (2003–2023). PubMed no tiene un campo de fecha de retracción, así que la fecha se toma de Retraction Watch.
- PubMed no siempre marca el artículo como «Retracted Publication». Por ejemplo, un ensayo de la base no está marcado aunque la revista lo retractó en 2017.
- Algunos artículos retractados pierden el tipo de publicación de ensayo, o nunca lo tuvieron. De los 120 artículos de la base, 94 están en esta lista.

## Para la extensión 2023–2026

La misma cadena, cruzando con la fecha de retracción de Retraction Watch > 2023-08-07.
