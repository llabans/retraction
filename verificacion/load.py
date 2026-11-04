import os, pathlib, pyreadstat, pandas as pd
# Carpeta manuscrito/ con DATA/ y RAW/ (no publicadas). Cambiar con la variable de entorno RETRACTION_MANUSCRITO.
B = os.environ.get('RETRACTION_MANUSCRITO', str(pathlib.Path(__file__).resolve().parents[1] / 'manuscrito')) + '/'
def load(p):
    df,meta=pyreadstat.read_dta(B+p, apply_value_formats=False)
    return df,meta
