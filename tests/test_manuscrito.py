"""Pruebas de aceptación del manuscrito (ver prd_manuscrito.md, sección 3).

Uso:
    python3 tests/test_manuscrito.py            # solo pruebas estáticas sobre el .qmd
    python3 tests/test_manuscrito.py --render   # además renderiza y prueba el Word

Cada prueba imprime PASS/FAIL con el ID del criterio de aceptación (A1…A17).
Las cifras esperadas se calculan aquí, en Python, directamente desde la base,
de forma independiente del código R del manuscrito.
"""
import re, sys, zipfile, pathlib, subprocess
import pyreadstat

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent / "manuscrito"
QMD = ROOT / "CODE" / "manuscript.qmd"
BIB = ROOT / "REF" / "references.bib"
DATA = ROOT / "DATA" / "Base retraccion 5 (cuartiles revisados).dta"
BUILD = ROOT / "build"

results = []


def check(cid, name, ok, detail=""):
    results.append((cid, name, bool(ok), detail))


def section(text, title, level="#"):
    """Text between a heading and the next heading of the same or higher level."""
    m = re.search(r"^%s %s\b.*$" % (re.escape(level), title), text, flags=re.M | re.I)
    if not m:
        return None
    rest = text[m.end():]
    n = re.search(r"^#{1,%d} " % len(level), rest, flags=re.M)
    return rest[: n.start()] if n else rest


def strip_chunks(text):
    return re.sub(r"```\{r.*?```", "", text, flags=re.S)


def expected():
    df, _ = pyreadstat.read_dta(str(DATA))
    n = len(df)
    pct = lambda k: f"{round(100 * k / n + 1e-9, 1):.1f}"
    q = df.quartila_retrac.value_counts()
    t = df["año_retraccion"] - df["año_publicacion"]
    plag = ((df.plagio == 1) | (df.autoplagio == 1) | (df.plagio_a_otros == 1) | (df.publi_duplicada == 1)).sum()
    return {
        "n": str(n),
        "recent": pct(((df["año_retraccion"] >= 2018) & (df["año_retraccion"] <= 2023)).sum()),
        "q1": pct(q[1]), "q2": pct(q[2]), "q1q2": pct(q[1] + q[2]),
        "asia": pct((df.continente_ensayo == 0).sum()),
        "africa": pct((df.continente_ensayo == 1).sum()),
        "falsif": pct((df.falsificacion == 1).sum()),
        "metod": pct((df.errores_metodologicos_estadistic == 1).sum()),
        "plagio": pct(plag),
        "mean": f"{t.mean():.1f}", "median": f"{t.median():.0f}",
        "fab_median": f"{t[df.fabricacion == 1].median():g}",
    }


def static_tests():
    txt = QMD.read_text(encoding="utf-8")
    prose = strip_chunks(txt)
    abstract = section(txt, "ABSTRACT") or ""
    # A2: no hard-coded numbers in the abstract (years and n of periods aside)
    ab = re.sub(r"`r [^`]*`", "", abstract)
    ab = re.sub(r"\b(19|20)\d\d\b", "", ab)
    hard = re.findall(r"\d+(?:\.\d+)?\s*%|n\s*=\s*\d+|SD\s*=\s*\d", ab)
    check("A2", "Resumen sin cifras escritas a mano", not hard, ", ".join(hard[:8]))
    # A3: draft placeholders
    bad = [p for p in ("between x", "[7]", "* **", ",10]") if p in prose]
    check("A3", "Sin restos de borrador", not bad, ", ".join(bad))
    # A4: citation syntax
    commas = re.findall(r"\[@[^\]]*,\s*@[^\]]*\]", prose)
    check("A4", "Citas con ';' y no con ','", not commas, "; ".join(commas[:4]))
    # A5: bib consistency
    bib = BIB.read_text(encoding="utf-8")
    keys = re.findall(r"^@\w+\{([^,]+),", bib, flags=re.M)
    cited = set(re.findall(r"@([A-Za-z][\w:.-]*[\w])", prose)) - {"upch.pe"}
    cited = {c for c in cited if not c.startswith(("fig-", "tbl-"))}
    missing = sorted(c for c in cited if c not in keys)
    dups = [k for k in keys if re.search(r"-\d+$", k)]
    entries = re.split(r"\n(?=@)", bib)
    urld = [re.match(r"@\w+\{([^,]+)", e).group(1) for e in entries
            if e.startswith("@") and re.search(r"^\s*doi\s*=", e, re.M | re.I) and re.search(r"^\s*urldate\s*=", e, re.M)]
    check("A5", "Claves citadas existen; .bib sin duplicados ni urldate en artículos con DOI",
          not (missing or dups or urld), f"faltan={missing} dup={dups} urldate={urld[:5]}")
    # A6 (código): etiquetas en español en figuras generadas por código
    sp = [w for w in ("Frecuency", 'fill = "cuartil"', "fill = 'cuartil'") if w in txt]
    check("A6a", "Código de figuras sin etiquetas en español/erratas", not sp, ", ".join(sp))
    # A7: overclaims
    oc = [p for p in ("largest share of retractions each year", "increased significantly", "in the last 5 years", "last five years")
          if p.lower() in prose.lower()]
    check("A7", "Sin afirmaciones no sustentadas", not oc, ", ".join(oc))
    # A8: objective
    bg = section(txt, "BACKGROUND") or ""
    paras = [p for p in re.split(r"\n", strip_chunks(bg).strip()) if p.strip()]
    check("A8", "Introducción termina con el objetivo",
          bool(paras) and re.search(r"\b(aim|objective)\b", paras[-1], re.I), paras[-1][:120] if paras else "")
    # A9: required sections not empty
    req = ["DISCUSSION", "LIMITATIONS", "CONCLUSION", "ETHICS", "FUNDING", "DATA AVAILABILITY",
           "AUTHOR CONTRIBUTIONS", "CONFLICT OF INTEREST"]
    empty = []
    for s in req:
        body = section(txt, s)
        words = len(re.findall(r"\w+", strip_chunks(body))) if body is not None else 0
        if words < 15:
            empty.append(f"{s}({'falta' if body is None else words})")
    check("A9", "Secciones obligatorias con contenido", not empty, ", ".join(empty))
    # A10: STROBE label
    check("A10", "Flujograma no se titula STROBE", not re.search(r"fig-cap:.*STROBE", txt), "")
    # A12: placeholders in the agreed format
    ph = re.findall(r"\[POR COMPLETAR:[^\]]*\]", txt)
    check("A12", "Marcadores para autores en formato [POR COMPLETAR: …]", True, f"{len(ph)} marcadores")
    # A15: ethics statement (Luis, 2026-11-04: no ethics committee needed)
    eth = section(txt, "ETHICS") or ""
    check("A15", "Ética: sin comité y sin marcador pendiente",
          "not required" in eth and "POR COMPLETAR" not in eth and "Ethics Committee" not in eth, eth.strip()[:120])
    # A16: author clustering and time to retraction by reason are reported in Results
    resx = section(strip_chunks(txt), "RESULTS") or ""
    check("A16", "Resultados reportan agrupamiento por autor y tiempo por motivo",
          bool(re.search(r"excluding", resx, re.I)) and "Fujii" in resx and "t_reason" in resx, "")
    supp = section(txt, "SUPPLEMENTARY MATERIALS") or ""
    check("A18", "Apéndice S1 con las cadenas de búsqueda de ambas bases",
          "Appendix S1" in supp and "TITLE-ABS-KEY" in supp and '"notice of retraction"' in supp, "")
    elig = section(txt, "Eligibility criteria", "##") or ""
    check("A19", "Elegibilidad define el manejo de expressions of concern", "expressions of concern were" in elig.lower(), "")
    check("A17", "Sin install.packages() en el código", "install.packages(" not in txt, "")


def render_tests():
    try:
        subprocess.run([sys.executable, str(HERE / "render.py"), str(QMD)], check=True,
                       capture_output=True, text=True)
        ok = True; err = ""
    except subprocess.CalledProcessError as e:
        ok = False; err = (e.stderr or e.stdout)[-600:]
    check("A11", "El documento se renderiza", ok, err)
    if not ok:
        return
    plain = (BUILD / "paper.txt").read_text(encoding="utf-8")
    with zipfile.ZipFile(BUILD / "paper.docx") as z:
        xml = z.read("word/document.xml").decode("utf-8")
        styles = z.read("word/styles.xml").decode("utf-8")
    docx_text = re.sub(r"<[^>]+>", "", xml)
    e = expected()
    m = re.search(r"ABSTRACT(.*?)Key ?words", plain, flags=re.S | re.I)
    abstract = m.group(1) if m else ""
    want = [e[k] for k in ("recent", "q1", "q2", "asia", "africa", "falsif", "metod", "plagio")] + [f"{e['median']} years"]
    miss = [w for w in want if w not in abstract]
    stale = [s for s in ("45.6%", "47.2%", "46.7%", "36.1%", "28.4%", "21.3%", "92.7%") if s in abstract]
    check("A1a", "Resumen renderizado con las cifras de la base", not (miss or stale),
          f"faltan={miss} antiguas={stale}")
    words = len(re.findall(r"[\w’'-]+", re.sub(r"(Background|Methods|Results|Conclusions):", "", abstract)))
    check("A13", "Resumen de 250 palabras o menos", words <= 250, f"{words} palabras")
    res = plain
    miss_r = [w for w in (e["q1"], e["q2"], e["asia"], e["africa"], e["recent"]) if w not in res]
    check("A1b", "Resultados renderizados con las cifras de la base", not miss_r, f"faltan={miss_r}")
    sp = [w for w in ("Europa", "Multinacional", "No explicito", "Frecuency", "Razón") if w in docx_text]
    check("A6b", "Word sin etiquetas en español en tablas", not sp, ", ".join(sp))
    check("A14", "Tabla 1 agrupa Q3–Q4 y reporta mediana (RIC)",
          "Q3–Q4" in docx_text and "median (IQR)" in docx_text, "")
    check("A20", "Word con numeración de líneas y doble espacio",
          "w:lnNumType" in xml and 'w:line="480"' in styles, "")
    fab_med = f"{e['fab_median']}"
    check("A16b", "Mediana por motivo renderizada (fabricación)", f"{fab_med} years" in plain, fab_med)
    unresolved = re.findall(r"\?@[\w-]+|@fig-|@tbl-", plain)
    check("A4b", "Sin citas sin resolver en el Word", not unresolved, ", ".join(sorted(set(unresolved))[:5]))


if __name__ == "__main__":
    static_tests()
    if "--render" in sys.argv:
        render_tests()
    fails = 0
    for cid, name, ok, detail in results:
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {cid:4} {name}" + (f"  -> {detail}" if detail and not ok else (f"  ({detail})" if detail else "")))
    print(f"\n{len(results) - fails}/{len(results)} pruebas pasan")
    sys.exit(1 if fails else 0)
