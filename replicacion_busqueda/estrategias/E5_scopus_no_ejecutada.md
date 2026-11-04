# E5 · Scopus · cadena del protocolo (NO ejecutada en esta replicación)

| Campo | Valor |
|---|---|
| Base de datos | Scopus (Elsevier) |
| Estado | **No ejecutada**: el entorno no tiene acceso a Scopus (ni web ni API, y la API requiere clave institucional) |
| Resultados originales | 128 registros (7-ago-2023), export `manuscrito/SOURCE/scopus_07.08.23.ris` |

## Cadena del protocolo

```
(TITLE-ABS-KEY("retracted article") OR TITLE-ABS-KEY("retracted note") OR TITLE-ABS-KEY("statement of retraction") OR TITLE-ABS-KEY("retracted notice"))
AND (TITLE-ABS-KEY("clinical trial") OR TITLE-ABS-KEY("randomized controlled trial") OR TITLE-ABS-KEY("controlled clinical trial"))
```

## Por qué importa

39 de los 120 artículos de la base **no** se recuperan con ninguna cadena de PubMed (E1 o E2), así que entraron solo por Scopus. Sin Scopus, la cadena de PubMed por sí sola no puede pasar de alrededor de 68% de concordancia con la base.

## Cómo correrla para la extensión (desde la UPCH o con VPN institucional)

1. Scopus → Advanced search → pegar la cadena y agregar `AND PUBYEAR > 2022`. Después, filtrar por fecha de carga, o comparar con el export de 2023 para quedarse solo con lo nuevo.
2. Export → RIS, con todos los campos (citation, bibliographical, abstract & keywords).
3. Guardar como `scopus_AAAA-MM-DD.ris` junto con el número de resultados y la cadena exacta.
