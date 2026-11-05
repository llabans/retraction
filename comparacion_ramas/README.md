# Comparación de ramas de búsqueda y tamizaje (IA con y sin herramientas)

Código de un estudio metodológico anidado en la revisión de ensayos clínicos retractados. Compara cuatro ramas para identificar y tamizar ensayos retractados:

| Rama | Búsqueda | Tamizaje |
|---|---|---|
| R1 | Búsqueda humana original (PubMed + Scopus) | Un revisor humano |
| R2 | Retraction Watch + tipo de publicación de ensayo en PubMed | Modelo de lenguaje sin herramientas, sobre metadatos |
| R3 | R2 + texto libre en PubMed, Europe PMC y OpenAlex, con verificación cruzada en Crossref | Modelo con acceso en vivo a PubMed (servidor MCP) |
| R4 | Memoria del modelo, sin herramientas (control) | — |

**Este repositorio no contiene datos.** Las listas de candidatos, el estándar de referencia y las salidas de los agentes son privados.

## Contenido

- `scripts/comparar_ramas.py`: sensibilidad relativa por rama (IC de Wilson), McNemar exacta, y sensibilidad, especificidad y kappa (IC bootstrap) del tamizaje ciego.
- `scripts/decodificar_delta36.py`: decodifica y verifica (n y suma) las listas de PMID exportadas desde el navegador.
- `scripts/harness_navegador.md`: consultas a E-utilities, Europe PMC, OpenAlex y Crossref ejecutadas desde el navegador.
- `prompts/`: instrucciones literales de los agentes: S2 sin herramientas, S3 con PubMed y R4 de memoria. `{INPUT}` y `{OUTPUT}` son las rutas de entrada y salida.

## Reproducir

Desde la carpeta privada del proyecto, que tiene la estructura de datos esperada:

```
python3 -I comparacion_ramas/scripts/comparar_ramas.py --raiz . --salida comparacion_ramas/resultados
```
