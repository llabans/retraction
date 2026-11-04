# E2 · PubMed · cadena ejecutada (reconstruida)

| Campo | Valor |
|---|---|
| Base de datos | PubMed |
| Interfaz | Servidor MCP de PubMed (E-utilities `esearch`) |
| Fecha de ejecución | 2026-11-04 |
| Resultados | **132** registros (fecha de entrada ≤ 2023-08-07) |
| Archivos | `datos/pm_ejecutada_132.txt`, `datos/pubmed132_rw.csv` (con el artículo retractado según Retraction Watch), `ris/E2_pubmed_cadena_ejecutada.ris` (los de `datos/` y `ris/` no se publican en este repositorio) |

## Cadena exacta

```
("notice of retraction" OR "retraction note" OR "retraction notice") AND ("clinical trial" OR "randomized controlled trial" OR "controlled clinical trial") AND 1900/01/01:2023/08/07[edat]
```

## Por qué esta cadena

Agrega «retraction notice» a la cadena del protocolo. Es la reconstrucción más simple que explica el export original: en el archivo de 2023, 13 títulos empiezan por «Retraction notice» y 2 por «Retraction Notice.». Los autores deben confirmarla (marcador 15 de la trazabilidad).

## Reproducibilidad frente al export original (76 registros)

| | n |
|---|---|
| Registros del export de 2023 que la cadena recupera hoy | 63 / 76 |
| Registros del export de 2023 que hoy ya no recupera | 13 (sobre todo ruido: «retraction» dental, artículos retractados sin término de nota) |
| Registros nuevos que hoy recupera y en 2023 no | 69 |

**El mismo texto de búsqueda no devuelve el mismo conjunto tres años después.** PubMed agregó resúmenes y notas a registros antiguos y cambió el mapeo automático de términos. Por eso la búsqueda por texto libre del aviso no es reproducible en el tiempo. Hay que fijar y guardar el export de cada corrida.

## Para la extensión 2023–2026

```
("notice of retraction" OR "retraction note" OR "retraction notice") AND ("clinical trial" OR "randomized controlled trial" OR "controlled clinical trial") AND 2023/08/08:3000[edat]
```

Exportar desde la web de PubMed: *Send to → Citation manager* (RIS) y *Send to → File → PubMed* (MEDLINE), con fecha en el nombre del archivo.
