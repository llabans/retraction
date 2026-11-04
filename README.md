# retraction

Retraction notes in clinical trials: análisis bibliométrico de ensayos clínicos retractados (2003–2023).

Este repositorio es público y contiene **solo código y documentación de métodos**. Los datos no están aquí
(ver [Datos](#datos)).

## Estructura

| Carpeta | Contenido |
|---|---|
| `manuscrito/CODE/manuscript_analysis.R` | Todo el código R del manuscrito (tablas, figuras y objetos que se citan en el texto), extraído del `.qmd` en el mismo orden |
| `manuscrito/CODE/00_cambios_raw_a_base5.R` | Registro de cambios entre la base RAW y la base 5 (cuartiles revisados) |
| `manuscrito/CODE/paquetes_R.txt` | Paquetes de R y versiones probadas |
| `tests/` | Pruebas de aceptación del manuscrito (`test_manuscrito.py`) y render sin Quarto (`render.py`: knitr + pandoc) |
| `verificacion/` | Recálculo independiente de las cifras en Python (pandas + pyreadstat) y emparejamiento con PMID/DOI |
| `replicacion_busqueda/` | Replicación de la búsqueda: estrategias exactas (E1–E5), metodología de tamizaje y scripts |
| `actualizacion_busqueda/` | Script que arma la lista de candidatos para actualizar la búsqueda desde agosto de 2023 |
| `tools/verificar_sin_datos.py` | Revisión automática de que no se publiquen datos (corre en GitHub Actions) |

## Datos

No se publican en este repositorio:

- La base de ensayos (`manuscrito/DATA/*.dta`), la base RAW y los identificadores (PMID/DOI) de los registros.
- Los exports de las búsquedas (PubMed, Scopus, RIS) y las listas de PMID de cada estrategia.
- El tamizaje registro por registro y sus decisiones (`replicacion_busqueda/datos/`).
- El texto del manuscrito (`manuscript.qmd`, Word), las tablas y las figuras generadas desde los datos.

El `.gitignore` excluye esas carpetas y formatos. Para correr el código, copia las carpetas privadas
(`manuscrito/DATA/`, `manuscrito/RAW/`, `manuscrito/SOURCE/`, `replicacion_busqueda/datos/`) en las mismas rutas
dentro de tu copia local. Git las ignorará.

La única fuente externa es pública: Retraction Watch Database (distribución abierta de Crossref).

## Cómo correr

```bash
# R: desde la carpeta manuscrito/ (ahí está retraction.Rproj, que here::here() usa como raíz)
cd manuscrito && Rscript CODE/manuscript_analysis.R && cd ..

# Recálculo independiente en Python
pip install pandas pyreadstat
python3 verificacion/replicate.py

# Pruebas de aceptación (requieren además manuscrito/CODE/manuscript.qmd, que es privado)
python3 tests/test_manuscrito.py --render

# Antes de cada commit
python3 tools/verificar_sin_datos.py
```

## Licencia

GPL-3.0 (ver `LICENSE`).
