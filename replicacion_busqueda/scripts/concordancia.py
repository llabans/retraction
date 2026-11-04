"""Concordancia a nivel de artículo entre la replicación independiente y la base de 120 (identificadores_120.csv).
Empareja por PMID o DOI del artículo original; si la base no tiene ninguno de los dos, por PMID de la nota.
Se corre dentro de datos/ (no publicado), con base120.csv, tamizaje_pubmed.csv, brazo_rw.csv, retraction_watch.csv,
pm_export_luis_76.txt y, opcionalmente, p79_ids.txt."""
import csv, collections, datetime
n = lambda s: (s or '').strip().lower()
base = list(csv.DictReader(open('base120.csv', encoding='utf-8')))
pm = list(csv.DictReader(open('tamizaje_pubmed.csv')))
rw = list(csv.DictReader(open('brazo_rw.csv', encoding='utf-8')))
rwall = list(csv.DictReader(open('retraction_watch.csv', encoding='utf-8', errors='replace')))
ex76 = set(open('pm_export_luis_76.txt').read().split())
# ids de la base marcados como posibles no-ensayos (P-79): lista privada, un id por línea, en p79_ids.txt
import os
P79 = set(open('p79_ids.txt').read().split()) if os.path.exists('p79_ids.txt') else set()
def keys(rows, p='orig_pmid', d='orig_doi'):
    return {n(r[p]) for r in rows if n(r[p]) not in ('','0')} | {n(r[d]) for r in rows if n(r[d]) not in ('','unavailable')}
def nkeys(rows): return {n(r['notice_pmid']) for r in rows if n(r['notice_pmid'])}
def hit(b, rows):
    ks = keys(rows)
    if n(b['original_pmid']) in ks or n(b['original_doi']) in ks: return True
    return not n(b['original_pmid']) and not n(b['original_doi']) and n(b['notice_pmid']) in nkeys(rows)
inc = [r for r in pm if r['decision']=='incluir']
arms = {'A_protocolo': [r for r in inc if r['en_cadena_protocolo']=='si'], 'B_ejecutada': inc,
        'B_recuperado': pm, 'C_RW': rw}
# RW por original, para explicar ausencias
rwidx = collections.defaultdict(list)
for r in rwall:
    for k in (n(r['OriginalPaperPubMedID']), n(r['OriginalPaperDOI']), 'n'+n(r['RetractionPubMedID'])):
        if k not in ('','0','unavailable','n','n0'): rwidx[k].append(r)
out = []
for b in base:
    row = dict(id=b['id'], original_pmid=b['original_pmid'], original_doi=b['original_doi'], notice_pmid=b['notice_pmid'],
               titulo=b['original_title'][:120], en_export_pubmed_2023='si' if b['notice_pmid'] in ex76 else 'no', P79='si' if b['id'] in P79 else '')
    for a, rows in arms.items(): row[a] = 'si' if hit(b, rows) else 'no'
    rr = rwidx.get(n(b['original_pmid'])) or rwidx.get(n(b['original_doi'])) or rwidx.get('n'+n(b['notice_pmid'])) or []
    row['en_RW'] = 'si' if rr else 'no'
    row['RW_naturaleza_fecha'] = '; '.join(f"{r['RetractionNature']} {r['RetractionDate'].split()[0]}" for r in rr)
    # motivo de no-concordancia
    why = []
    if row['B_ejecutada']=='no':
        if row['B_recuperado']=='si': why.append('B: recuperado pero excluido en mi tamizaje')
        elif row['en_export_pubmed_2023']=='si': why.append('B: estaba en el export PubMed 2023 pero la cadena hoy no lo recupera')
        else: why.append('B: no recuperado por la cadena PubMed (vino de Scopus)')
    if row['C_RW']=='no':
        if not rr: why.append('C: no está en Retraction Watch')
        elif not any(r['RetractionNature']=='Retraction' for r in rr): why.append('C: RW no lo registra como retracción')
        else:
            ds = [datetime.datetime.strptime(r['RetractionDate'].split()[0], '%m/%d/%Y').date() for r in rr if r['RetractionNature']=='Retraction']
            if all(d > datetime.date(2023,8,7) or d < datetime.date(2003,1,1) for d in ds): why.append('C: fecha de retracción en RW fuera de ventana')
            else: why.append('C: no clasificado como ensayo (sin PT de ensayo ni término en el título)')
    row['motivo_no_concordancia'] = ' | '.join(why)
    out.append(row)
w = csv.DictWriter(open('concordancia_base120.csv','w',newline='',encoding='utf-8'), fieldnames=out[0].keys()); w.writeheader(); w.writerows(out)
N = len(base); N113 = N - len(P79)
for a in list(arms)+['en_RW']:
    s = sum(r[a]=='si' for r in out); s2 = sum(r[a]=='si' for r in out if r['P79']!='si')
    print(f"{a:14s} {s:3d}/{N} ({100*s/N:.1f}%)   sin P-79: {s2}/{N113} ({100*s2/N113:.1f}%)")
u = sum(r['B_ejecutada']=='si' or r['C_RW']=='si' for r in out); print('B∪C', u)
print(collections.Counter(m for r in out for m in r['motivo_no_concordancia'].split(' | ') if m))
# inverso
bk = {n(b['original_pmid']) for b in base if n(b['original_pmid'])} | {n(b['original_doi']) for b in base if n(b['original_doi'])}
bn = {n(b['notice_pmid']) for b in base if not n(b['original_pmid']) and not n(b['original_doi'])}
def inbase(r): return n(r['orig_pmid']) in bk or n(r['orig_doi']) in bk or n(r['notice_pmid']) in bn
extra = []
for r in inc:
    if inbase(r): continue
    cat = 'nota en export PubMed 2023 de Luis (excluida por él)' if r['notice_pmid'] in ex76 else 'no estaba en el export PubMed 2023 (deriva de indexación de PubMed)'
    extra.append(dict(r, categoria=cat))
w = csv.DictWriter(open('incluidos_replica_no_en_base.csv','w',newline='',encoding='utf-8'), fieldnames=extra[0].keys()); w.writeheader(); w.writerows(extra)
print('B incluidos no en base:', len(extra), collections.Counter(e['categoria'] for e in extra), 'gris:', sum(bool(e['zona_gris']) for e in extra))
rwx = [r for r in rw if not inbase(dict(r))]
print('C (RW) elegibles no en base:', len(rwx), 'de', len(rw))
