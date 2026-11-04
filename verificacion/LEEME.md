Scripts en Python (pandas + pyreadstat) que recalculan, de forma independiente del código R, las cifras del manuscrito.
Leen las bases desde `manuscrito/DATA/` y `manuscrito/RAW/`, que **no** están en el repositorio. `load.py` toma la carpeta
`manuscrito/` del repositorio, o la que indique la variable de entorno `RETRACTION_MANUSCRITO`.

- `replicate.py`: cifras del texto y de las tablas
- `dq.py`: calidad de datos
- `compare.py`, `raw_old.py`: comparación entre versiones de la base
- `inspect1.py`, `inspect2.py`: inventario de variables y valores
- `doi_pmid/emparejar_exports.py`: empareja cada registro con su nota de PubMed/Scopus (PMID y DOI)

Ojo: la salida de estos scripts muestra datos a nivel de registro. No la subas al repositorio.
