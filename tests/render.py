"""Renderiza el manuscrito sin Quarto: knitr -> markdown -> pandoc (citeproc) -> docx + texto plano.

Uso:  python3 tests/render.py [ruta_qmd]
Salida: manuscrito/build/paper.docx y manuscrito/build/paper.txt

Limitaciones del entorno (sin Quarto, sin DiagrammeR/rnaturalearth/countrycode/gganimate/gtsummary):
- Los chunks que generan el flujograma y el mapa no se ejecutan; se usan los PNG ya guardados en FIGURES/.
- Las referencias cruzadas de Quarto (@fig-x, @tbl-x) se reemplazan por "Figure n"/"Table n".
"""
import re, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1] / "manuscrito"
QMD = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "CODE" / "manuscript.qmd"
BUILD = ROOT / "build"
SKIP_CHUNKS = {"strobe_flowchart_LABEL", "world_map_animation"}
MISSING_LIBS = ("gtsummary", "DiagrammeR", "DiagrammeRsvg", "rnaturalearth", "countrycode", "gganimate")


def preprocess(text: str) -> str:
    # 1) chunks que dependen de paquetes no disponibles -> eval=FALSE
    def chunk_header(m):
        label = m.group(1)
        if label in SKIP_CHUNKS:
            return m.group(0)[:-1] + ", eval=FALSE}"
        return m.group(0)
    text = re.sub(r"```\{r ([A-Za-z0-9_]+)[^}]*\}", chunk_header, text)
    # 2) library() de paquetes ausentes
    text = re.sub(r"^\s*library\((%s)\).*$" % "|".join(MISSING_LIBS), "", text, flags=re.M)
    # 3) referencias cruzadas de Quarto
    figs, tbls = {}, {}
    for kind, store in (("fig", figs), ("tbl", tbls)):
        for lab in re.findall(r"#\|\s*label:\s*(%s-[A-Za-z0-9_-]+)" % kind, text):
            store.setdefault(lab, len(store) + 1)
    def xref(m):
        lab = m.group(1)
        if lab in figs:
            return f"Figure {figs[lab]}"
        if lab in tbls:
            return f"Table {tbls[lab]}"
        return m.group(0)
    text = re.sub(r"@((?:fig|tbl)-[A-Za-z0-9_-]+)", xref, text)
    return text


def main():
    BUILD.mkdir(exist_ok=True)
    src = QMD.read_text(encoding="utf-8")
    pre = BUILD / "paper_pre.Rmd"
    pre.write_text(preprocess(src), encoding="utf-8")
    md = BUILD / "paper.md"
    r = (
        "knitr::opts_knit$set(root.dir=%r, rmarkdown.pandoc.to='docx');"
        "knitr::opts_chunk$set(fig.path=%r, echo=FALSE, warning=FALSE, message=FALSE);"
        "knitr::knit(%r, output=%r, quiet=TRUE)"
    ) % (str(QMD.parent), str(BUILD / "fig-"), str(pre), str(md))
    subprocess.run(["Rscript", "-e", r], check=True, cwd=QMD.parent)
    # bibliography/csl/reference-doc paths are relative to CODE/
    ref = re.search(r"^\s*reference-doc:\s*(\S+)", src, flags=re.M)
    for out in ("paper.docx", "paper.txt"):
        subprocess.run(
            ["pandoc", str(md), "--citeproc", "-o", str(BUILD / out),
             "--resource-path", f"{QMD.parent}:{ROOT}"] + (["-t", "plain", "--wrap=none"] if out.endswith("txt") else (["--reference-doc", ref.group(1)] if ref else [])),
            check=True, cwd=QMD.parent)
    print("OK", BUILD / "paper.docx")


if __name__ == "__main__":
    main()
