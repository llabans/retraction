"""Verifica que el repositorio no contenga datos: revisa los archivos versionados (git ls-files) y falla si
encuentra un formato de datos o un identificador que parezca PMID o DOI dentro de un archivo.

Uso: python3 tools/verificar_sin_datos.py            (desde la raíz del repositorio)
Se corre también en GitHub Actions en cada push y pull request (.github/workflows/sin_datos.yml).
"""
import re, subprocess, sys, pathlib

PERMITIDOS = {".py", ".R", ".r", ".md", ".sh", ".yml", ".yaml", ".Rproj", ""}
ARCHIVOS_PERMITIDOS = {"LICENSE", ".gitignore", "manuscrito/CODE/paquetes_R.txt"}
DOI = re.compile(r"\b10\.\d{4,9}/\S+")
PMID = re.compile(r"(?<![\w.])\d{7,9}(?![\w.])")

files = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout.split("\n")
problemas = []
for f in filter(None, files):
    p = pathlib.Path(f)
    if f not in ARCHIVOS_PERMITIDOS and p.suffix not in PERMITIDOS:
        problemas.append(f"{f}: formato no permitido ({p.suffix})")
        continue
    if f == "LICENSE":
        continue
    texto = p.read_text(encoding="utf-8", errors="replace")
    for nombre, rx in (("DOI", DOI), ("posible PMID", PMID)):
        for m in rx.finditer(texto):
            linea = texto.count("\n", 0, m.start()) + 1
            problemas.append(f"{f}:{linea}: {nombre} {m.group(0)[:40]}")

if problemas:
    print("Se encontraron posibles datos en el repositorio:\n  " + "\n  ".join(problemas))
    sys.exit(1)
print(f"OK: {len([f for f in files if f])} archivos versionados, ninguno con datos.")
