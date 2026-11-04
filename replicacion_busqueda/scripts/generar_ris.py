"""Genera archivos RIS para cada estrategia a partir de los identificadores recuperados y de los metadatos de
Retraction Watch (RW). NO es el export nativo de PubMed: el contenedor no tiene acceso a E-utilities y la consulta se
hizo por el servidor MCP de PubMed, que devuelve PMID. Cada registro lleva AN (PMID), DO (DOI) y N1 con la procedencia.
Uso: python3 -I generar_ris.py retraction_watch.csv <dir_salida> <pm_protocolo_46.txt> <pm_ejecutada_132.txt> <pt_trials_retracted_all.txt> <brazo_rw.csv> <tamizaje_pubmed.csv>"""
import csv, sys, os, datetime
rwp, outd, f46, f132, fpt, frw, ftam = sys.argv[1:8]
rw = list(csv.DictReader(open(rwp, encoding='utf-8', errors='replace')))
by_notice, by_orig = {}, {}
for r in rw:
    p = r['RetractionPubMedID'].strip(); o = r['OriginalPaperPubMedID'].strip()
    if p not in ('','0'): by_notice.setdefault(p, []).append(r)
    if o not in ('','0'): by_orig.setdefault(o, []).append(r)
tam = {}
for t in csv.DictReader(open(ftam)): tam.setdefault(t['notice_pmid'], []).append(t)
def yr(s):
    try: return datetime.datetime.strptime(s.split()[0], '%m/%d/%Y').year
    except Exception: return ''
def rec(lines):
    return '\n'.join(f'{k}  - {v}' for k, v in lines if v not in ('', None)) + '\nER  - \n\n'
def notice_rec(pmid):
    rows = [r for r in by_notice.get(pmid, []) if r['RetractionNature'] in ('Retraction','Reinstatement')] or by_notice.get(pmid, [])
    t = tam.get(pmid, [])
    if rows:
        r = rows[0]
        L = [('TY','JOUR'),('TI','Retraction notice: ' + ' / '.join(x['Title'] for x in rows)),('JO', r['Journal']),('PB', r['Publisher']),
             ('PY', yr(r['RetractionDate'])),('DA', r['RetractionDate'].split()[0]),('DO', r['RetractionDOI']),('AN', pmid),
             ('UR', f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/'),('KW','Retraction of Publication')]
        for x in rows: L.append(('N1', f"Retracta: PMID {x['OriginalPaperPubMedID']} DOI {x['OriginalPaperDOI']} | RW {x['Record ID']} {x['RetractionNature']} | Motivos RW: {x['Reason']}"))
    else:
        L = [('TY','JOUR'),('TI', (t[0]['titulo'] if t else '')),('AN', pmid),('UR', f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/'),
             ('N1', 'Artículo retractado: PMID ' + (t[0]['orig_pmid'] if t else '') + ' DOI ' + (t[0]['orig_doi'] if t else '')),('N1','Sin registro en Retraction Watch; metadatos tomados de PubMed (MCP)')]
    L.append(('N1','Registro reconstruido (no es export nativo de PubMed)'))
    return rec(L)
def orig_rec(pmid):
    rows = by_orig.get(pmid, [])
    if not rows: return rec([('TY','JOUR'),('AN',pmid),('UR',f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/'),('N1','Artículo retractado (PT Retracted Publication + Clinical Trial/RCT); sin registro en RW: completar metadatos con el export nativo de PubMed')])
    r = rows[0]
    L = [('TY','JOUR'),('TI', r['Title']),('JO', r['Journal']),('PB', r['Publisher']),('PY', yr(r['OriginalPaperDate'])),('DO', r['OriginalPaperDOI']),
         ('AN', pmid),('UR', f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/'),('KW','Retracted Publication')]
    for a in r['Author'].split(';'):
        if a.strip(): L.append(('AU', a.strip()))
    for x in rows: L.append(('N1', f"RW {x['Record ID']}: {x['RetractionNature']} {x['RetractionDate'].split()[0]} | nota PMID {x['RetractionPubMedID']} DOI {x['RetractionDOI']} | Motivos: {x['Reason']}"))
    L.append(('N1','Registro reconstruido desde Retraction Watch (no es export nativo de PubMed)'))
    return rec(L)
os.makedirs(outd, exist_ok=True)
for name, f in (('E1_pubmed_cadena_protocolo.ris', f46), ('E2_pubmed_cadena_ejecutada.ris', f132)):
    ids = open(f).read().split()
    open(os.path.join(outd, name), 'w', encoding='utf-8').write(''.join(notice_rec(p) for p in ids))
ids = open(fpt).read().split()
open(os.path.join(outd, 'E3_pubmed_tipo_publicacion.ris'), 'w', encoding='utf-8').write(''.join(orig_rec(p) for p in ids))
out = []
for r in csv.DictReader(open(frw, encoding='utf-8')):
    L = [('TY','JOUR'),('TI', r['titulo']),('JO', r['revista']),('DO', r['orig_doi']),('AN', r['orig_pmid']),('DA', r['fecha_nota']),
         ('KW','Retracted Publication'),('N1', f"RW {r['rw_id']} | nota PMID {r['notice_pmid']} DOI {r['notice_doi']} | fecha de retracción {r['fecha_nota']} | criterio ensayo: {r['criterio']} | país RW: {r['pais']} | motivos: {r['motivos_rw']}")]
    out.append(rec(L))
open(os.path.join(outd, 'E4_retraction_watch.ris'), 'w', encoding='utf-8').write(''.join(out))
for fn in sorted(os.listdir(outd)): print(fn, open(os.path.join(outd, fn), encoding='utf-8').read().count('ER  - '))
