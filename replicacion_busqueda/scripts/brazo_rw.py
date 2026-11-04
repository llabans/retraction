"""Brazo Retraction Watch: retracciones con fecha de nota 2003-01-01..2023-08-07 cuyo original es un ensayo clínico.
Ensayo = PMID original con tipo de publicación PubMed Clinical Trial/RCT (lista pt_trials_retracted_all.txt)
         o título con término explícito de diseño de ensayo; se excluyen protocolos, metaanálisis y revisiones."""
import csv, re, sys, datetime
rw, ptf, out = sys.argv[1:4]
pt = set(open(ptf).read().split())
D = lambda s: (lambda x: x)(datetime.datetime.strptime(s.split()[0], '%m/%d/%Y').date()) if s.strip() else None
TRIAL = re.compile(r'randomi[sz]|clinical trial|controlled trial|placebo[- ]controlled|double[- ]blind|single[- ]blind|cross[- ]?over trial|phase (i{1,3}|[123])\b|\btrial\b', re.I)
NOT = re.compile(r'protocol|meta[- ]?analy|systematic review|rationale and design|study design|review of', re.I)
lo, hi = datetime.date(2003,1,1), datetime.date(2023,8,7)
res = []
for r in csv.DictReader(open(rw, encoding='utf-8', errors='replace')):
    if r['RetractionNature'] != 'Retraction': continue
    try: d = D(r['RetractionDate'])
    except Exception: continue
    if not d or not (lo <= d <= hi): continue
    op = r['OriginalPaperPubMedID'].strip(); op = '' if op in ('0','') else op
    by_pt = op in pt
    by_ti = bool(TRIAL.search(r['Title'])) and not NOT.search(r['Title'])
    if not (by_pt or by_ti): continue
    res.append(dict(rw_id=r['Record ID'], orig_pmid=op, orig_doi=r['OriginalPaperDOI'].lower().strip(), notice_pmid=r['RetractionPubMedID'].strip(),
        notice_doi=r['RetractionDOI'].lower().strip(), fecha_nota=d.isoformat(), titulo=r['Title'], revista=r['Journal'], pais=r['Country'],
        tipo_rw=r['ArticleType'], criterio=('PT' if by_pt else '') + ('+' if by_pt and by_ti else '') + ('titulo' if by_ti else ''), motivos_rw=r['Reason']))
w = csv.DictWriter(open(out,'w',newline='',encoding='utf-8'), fieldnames=res[0].keys()); w.writeheader(); w.writerows(res)
import collections
print(len(res), collections.Counter(x['criterio'] for x in res))
