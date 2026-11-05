"""Comparación de ramas de búsqueda y tamizaje (diseño: comparacion_ramas/diseno_preregistrado.md).

Uso (desde retracciones_checklist/, con python3 -I):
    python3 -I comparacion_ramas/scripts/comparar_ramas.py --raiz . --salida comparacion_ramas/resultados

Entradas (todas privadas, fuera del repositorio público):
    extension_2003_2026/datos/estandar_referencia.csv     estándar de referencia (112 positivos, 24 negativos)
    replicacion_busqueda/datos/brazo_rw.csv               R2 (estrategia E4)
    extension_2003_2026/datos/universo_candidatos.csv     R2 extendida (estratos RW_CS, PM_SOLO, PM_CADENA)
    comparacion_ramas/entradas/P1_pubmed_tiab_pmids.txt   R3-P1
    comparacion_ramas/entradas/P1_nuevos_rw.csv           R3-P1 fuera de R2, con fecha de nota de RW
    comparacion_ramas/entradas/P1_nuevos_sin_rw_fechas.txt
    comparacion_ramas/entradas/P3_openalex_*.txt          R3-P3
    comparacion_ramas/resultados/clave_cegamiento.json    clave del tamizaje ciego
    comparacion_ramas/resultados/salida_S2.jsonl, salida_S3.jsonl  salidas de los agentes
    comparacion_ramas/resultados/R4_verificacion.csv      verificación de la rama 4
"""
import argparse
import csv
import json
import math
import os
import random

SEMILLA = int("2026" + "1104")  # misma semilla del protocolo


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0.0, c - h), min(1.0, c + h))


def fmt(k, n):
    p, lo, hi = wilson(k, n)
    return f"{k}/{n} ({100*p:.1f}%; IC95% {100*lo:.1f}-{100*hi:.1f})"


def mcnemar_exacta(b, c):
    """Prueba exacta de McNemar (binomial bilateral) para pares discordantes b, c."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def kappa(pares):
    n = len(pares)
    if n == 0:
        return float("nan")
    po = sum(1 for a, b in pares if a == b) / n
    pa = sum(1 for a, _ in pares if a) / n
    pb = sum(1 for _, b in pares if b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def kappa_bootstrap(pares, reps=2000):
    rng = random.Random(SEMILLA)
    vals = []
    for _ in range(reps):
        m = [pares[rng.randrange(len(pares))] for _ in pares]
        k = kappa(m)
        if not math.isnan(k):
            vals.append(k)
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]


def leer_csv(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def conjunto(filas):
    P = {x["orig_pmid"] for x in filas if x.get("orig_pmid")}
    D = {x["orig_doi"].lower() for x in filas if x.get("orig_doi")}
    N = {x["notice_pmid"] for x in filas if x.get("notice_pmid")}
    return P, D, N


def pertenece(r, P, D=frozenset(), N=frozenset()):
    return bool((r["orig_pmid"] and r["orig_pmid"] in P)
                or (r["orig_doi"] and r["orig_doi"].lower() in D)
                or (r["notice_pmid"] and r["notice_pmid"] in N))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--salida", default="comparacion_ramas/resultados")
    a = ap.parse_args()
    R = lambda *p: os.path.join(a.raiz, *p)
    ent = lambda f: R("comparacion_ramas", "entradas", f)

    ref = leer_csv(R("extension_2003_2026", "datos", "estandar_referencia.csv"))
    pos = [x for x in ref if x["etiqueta"] == "positivo"]
    solo_eca = [x for x in pos if x["eca"] == "si"]

    e4 = leer_csv(R("replicacion_busqueda", "datos", "brazo_rw.csv"))
    uni = [x for x in leer_csv(R("extension_2003_2026", "datos", "universo_candidatos.csv"))
           if x["periodo"] != "2023/08-2026"]
    p1 = set(open(ent("P1_pubmed_tiab_pmids.txt")).read().split())

    # P3 OpenAlex: con PMID (lista de PMIDs con término de ensayo en el título) y sin PMID (DOIs)
    p3_pmid = set()
    if os.path.exists(ent("P3_openalex_conpmid_titulo_ensayo.txt")):
        p3_pmid = {t for t in open(ent("P3_openalex_conpmid_titulo_ensayo.txt")).read().split() if t.isdigit()}
    p3_doi = set()
    if os.path.exists(ent("P3_openalex_sinpmid_titulo_ensayo.txt")):
        p3_doi = {t.split("|")[0].lower() for t in open(ent("P3_openalex_sinpmid_titulo_ensayo.txt")).read().strip().split(";")}

    E4 = conjunto(e4)
    UNI = conjunto(uni)
    ramas = {
        "R1 humana original": lambda r: r["ref_id"] != "B2.1",  # por construcción; remdesivir no estaba
        "R2 RW + PubMed (E4)": lambda r: pertenece(r, *E4),
        "R2-ext (E4 + RW_CS + PM)": lambda r: pertenece(r, *UNI),
        "R3-P1 PubMed texto": lambda r: pertenece(r, p1),
        "R3-P3 OpenAlex": lambda r: pertenece(r, p3_pmid, p3_doi),
        "R3 = R2 + P1 + P3": lambda r: pertenece(r, *E4) or pertenece(r, p1) or pertenece(r, p3_pmid, p3_doi),
        "R3 + estratos R2-ext": lambda r: pertenece(r, *UNI) or pertenece(r, p1) or pertenece(r, p3_pmid, p3_doi),
    }
    out = []
    det = {}
    for nombre, f in ramas.items():
        hit = [r["ref_id"] for r in pos if f(r)]
        hit_eca = [r for r in solo_eca if f(r)]
        det[nombre] = set(hit)
        out.append({"rama": nombre, "recuperacion": fmt(len(hit), len(pos)),
                    "solo_eca": fmt(len(hit_eca), len(solo_eca)),
                    "perdidos": ",".join(r["ref_id"] for r in pos if not f(r))})

    # McNemar R2 vs R3
    b = len(det["R2 RW + PubMed (E4)"] - det["R3 = R2 + P1 + P3"])
    c = len(det["R3 = R2 + P1 + P3"] - det["R2 RW + PubMed (E4)"])
    os.makedirs(a.salida, exist_ok=True)
    with open(os.path.join(a.salida, "recuperacion_por_rama.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    for o in out:
        print(o)
    print(f"McNemar R2 vs R3: discordantes {b}/{c}, p exacta = {mcnemar_exacta(b, c):.3f}")

    # Tamizaje ciego
    clave_p = os.path.join(a.salida, "clave_cegamiento.json")
    if os.path.exists(clave_p):
        clave = {k["codigo"]: k for k in json.load(open(clave_p))}
        for brazo in ("S2", "S3"):
            sp = os.path.join(a.salida, f"salida_{brazo}.jsonl")
            if not os.path.exists(sp):
                continue
            dec = {}
            for line in open(sp, encoding="utf-8"):
                line = line.strip()
                if line:
                    j = json.loads(line)
                    dec[j["record_id"]] = j["decision"]
            for regla in ("unsure=incluir", "unsure=excluir"):
                pares = []
                tp = fn = tn = fp = 0
                for cod, k in clave.items():
                    d = dec.get(cod, "unsure")
                    inc = d == "include" or (d == "unsure" and regla == "unsure=incluir")
                    verdad = k["etiqueta"] == "positivo"
                    pares.append((inc, verdad))
                    tp += inc and verdad
                    fn += (not inc) and verdad
                    tn += (not inc) and (not verdad)
                    fp += inc and (not verdad)
                kp = kappa(pares)
                lo, hi = kappa_bootstrap(pares)
                n_uns = sum(1 for v in dec.values() if v == "unsure")
                print(f"{brazo} [{regla}] sens {fmt(tp, tp+fn)}; espec {fmt(tn, tn+fp)}; "
                      f"kappa {kp:.2f} (IC95% {lo:.2f}-{hi:.2f}); unsure {n_uns}; faltantes {len(clave)-len(dec)}")


if __name__ == "__main__":
    main()
