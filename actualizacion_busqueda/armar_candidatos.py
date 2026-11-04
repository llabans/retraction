"""Arma la lista de candidatos para actualizar la búsqueda (8-ago-2023 a hoy).

Uso: python3 -I armar_candidatos.py retraction_watch.csv pubmed_pmids.txt identificadores_120.csv salida.csv
- retraction_watch.csv: https://gitlab.com/crossref/retraction-watch-data/-/raw/main/retraction_watch.csv
- pubmed_pmids.txt: PMIDs de la cadena ejecutada en PubMed, con fecha de entrada desde 2023/08/08
Fuente A = PubMed (cadena ejecutada); Fuente B = Retraction Watch (Clinical Study o término de ensayo en el título).
No incluye Scopus (sin acceso por API desde aquí).
"""
import csv, sys, re, datetime
rw_path, pm_path, base_path, out_path = sys.argv[1:5]
CUT = datetime.date(2023, 8, 7)
TRIAL = re.compile(r'random|trial|placebo', re.I)
def d(s):
    try: return datetime.datetime.strptime(s.split()[0], '%m/%d/%Y').date()
    except Exception: return None
rows = list(csv.DictReader(open(rw_path, encoding='utf-8', errors='replace')))
pmids = set(open(pm_path).read().split())
base = list(csv.DictReader(open(base_path, encoding='utf-8')))
base_doi = {r['original_doi'].lower().strip() for r in base if r['original_doi']}
base_pm = {r['original_pmid'].strip() for r in base if r['original_pmid']}
out, seen_pm = [], set()
for r in rows:
    if r['RetractionNature'] != 'Retraction':
        continue
    rd = d(r['RetractionDate'])
    in_pm = r['RetractionPubMedID'].strip() in pmids
    trialish = 'Clinical Study' in r['ArticleType'] or bool(TRIAL.search(r['Title']))
    if not (in_pm or (rd and rd > CUT and trialish)):
        continue
    if in_pm: seen_pm.add(r['RetractionPubMedID'].strip())
    out.append({
        'fuente': 'PubMed+RW' if in_pm else 'RW',
        'rw_id': r['Record ID'], 'titulo': r['Title'], 'revista': r['Journal'], 'editorial': r['Publisher'],
        'pais_rw': r['Country'], 'tipo_rw': r['ArticleType'], 'fecha_retraccion': rd,
        'fecha_original': d(r['OriginalPaperDate']), 'doi_original': r['OriginalPaperDOI'],
        'pmid_original': r['OriginalPaperPubMedID'], 'doi_nota': r['RetractionDOI'], 'pmid_nota': r['RetractionPubMedID'],
        'motivos_rw': r['Reason'], 'hindawi': r['Publisher'] == 'Hindawi',
        'ya_en_base_120': r['OriginalPaperDOI'].lower().strip() in base_doi or r['OriginalPaperPubMedID'].strip() in base_pm,
        'titulo_con_termino_ensayo': bool(TRIAL.search(r['Title'])),
    })
for p in sorted(pmids - seen_pm):
    out.append({'fuente': 'PubMed (no está en RW)', 'pmid_nota': p})
with open(out_path, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print(len(out), 'filas;', sum(1 for o in out if o['fuente'] != 'RW'), 'de PubMed')
