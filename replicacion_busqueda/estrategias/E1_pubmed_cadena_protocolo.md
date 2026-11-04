# E1 · PubMed · cadena del protocolo (Apéndice S1)

| Campo | Valor |
|---|---|
| Base de datos | PubMed (MEDLINE + PubMed-not-MEDLINE) |
| Interfaz | Servidor MCP de PubMed (equivalente a E-utilities `esearch`); sin filtros adicionales |
| Fecha de ejecución | 2026-11-04 |
| Ejecutado por | Claude (replicación independiente) |
| Resultados | **46** registros (fecha de entrada ≤ 2023-08-07); 80 sin límite de fecha |
| Archivos | `datos/pm_protocolo_46.txt` (PMID), `ris/E1_pubmed_cadena_protocolo.ris` (los de `datos/` y `ris/` no se publican en este repositorio) |

## Cadena exacta

```
("notice of retraction" OR "retraction note") AND ("clinical trial" OR "randomized controlled trial" OR "controlled clinical trial") AND 1900/01/01:2023/08/07[edat]
```

Traducción de PubMed:

```
("notice of retraction"[All Fields] OR "retraction note"[All Fields]) AND ("clinical trial"[All Fields] OR "randomized controlled trial"[All Fields] OR "controlled clinical trial"[All Fields]) AND 1900/01/01:2023/08/07[Date - Entry]
```

## Límite de fecha

El límite `[edat]` (fecha de entrada en PubMed) ≤ 7-ago-2023 reproduce la fecha de la búsqueda original. No se aplicó límite de fecha de publicación porque el protocolo no lo indica. El criterio «nota publicada en 2003–2023» se aplica en el tamizaje.

## Comparación con la búsqueda original (7-ago-2023)

- El export original (`manuscrito/SOURCE/Pubmed_07.08.23.txt`) tiene **76** registros. Esta cadena da hoy 46.
- 45 de los 46 están en el export original. El otro es una nota de 2025 con fecha de entrada anómala.
- 31 registros del export original no contienen «notice of retraction» ni «retraction note». La mayoría se titulan «Retraction notice», así que **la cadena que se ejecutó en 2023 no es la del protocolo**. Ver E2.

## Para la extensión 2023–2026

Cambiar el límite a `2023/08/08:3000[edat]`. Esta cadena **no** debe usarse sola: es la menos sensible (39 de los 120 artículos de la base).
