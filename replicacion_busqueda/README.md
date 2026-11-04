# Replicación independiente de la búsqueda (2026-11-04)

Código y documentación de la replicación de la búsqueda y del tamizaje. Los datos (listas de PMID, exports RIS,
tamizaje registro por registro, concordancia con la base) **no** están en este repositorio.

- `estrategias/`: un .md por estrategia (E1–E4 ejecutadas; E5 Scopus no ejecutada), con la cadena exacta y la fecha
- `metodologia_tamizaje.md`: criterios, orden de decisión y zonas grises
- `scripts/`: código para reproducir (Python 3, `python3 -I`)
  - `brazo_rw.py`: brazo Retraction Watch (E4)
  - `tamizaje_pubmed.py`: tamizaje de la cadena ejecutada (E2); las decisiones se leen de `datos/decisiones_tamizaje.json`
  - `concordancia.py`: concordancia con la base de 120
  - `generar_ris.py`: RIS reconstruido por estrategia

Fuente pública: Retraction Watch Database, distribución abierta de Crossref
(`https://gitlab.com/crossref/retraction-watch-data/-/raw/main/retraction_watch.csv`). Guarda la copia descargada con su
fecha y su SHA-256.

## Orden de ejecución

```bash
cd datos/   # carpeta local, ignorada por git
python3 -I ../scripts/brazo_rw.py retraction_watch.csv pt_trials_retracted_all.txt brazo_rw.csv
python3 -I ../scripts/tamizaje_pubmed.py pubmed132_rw.csv tamizaje_pubmed.csv pm_protocolo_46.txt decisiones_tamizaje.json
python3 -I ../scripts/concordancia.py          # requiere base120.csv (identificadores de la base, privado)
python3 -I ../scripts/generar_ris.py retraction_watch.csv ../ris pm_protocolo_46.txt pm_ejecutada_132.txt \
        pt_trials_retracted_all.txt brazo_rw.csv tamizaje_pubmed.csv
```
