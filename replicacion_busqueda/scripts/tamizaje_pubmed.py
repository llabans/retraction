"""Tamizaje independiente de los 132 registros de PubMed (cadena ejecutada reconstruida).
Unidad: artículo retractado. Decisiones tomadas por Claude (revisor único) sin ver la base de 120.
Uso: python3 -I tamizaje_pubmed.py pubmed132_rw.csv tamizaje_pubmed.csv pm_protocolo_46.txt decisiones_tamizaje.json
Entrada: pubmed132_rw.csv (mapeo nota->original vía Retraction Watch). Salida: tamizaje_pubmed.csv"""
import csv, sys, json
src, out = sys.argv[1], sys.argv[2]
prot = set(open(sys.argv[3]).read().split())
rows = list(csv.DictReader(open(src)))
# Las decisiones (exclusiones, zonas grises, correcciones al mapeo de RW y notas sin registro en RW)
# están en un archivo de datos aparte, que no se publica: datos/decisiones_tamizaje.json
# Claves: DROP_RW (rw_id a descartar), DROP_NATURE ([notice_pmid, naturaleza] a descartar),
#         EXTRA (notas sin registro en RW, con su original identificado a mano), FIX_PMID (PMID erróneo en RW -> reemplazo),
#         EXC (PMID/DOI del original -> motivo de exclusión X1–X6), GRAY (PMID/DOI del original -> zona gris).
cfg = json.load(open(sys.argv[4], encoding='utf-8'))
DROP_RW = set(cfg['DROP_RW'])
DROP_NATURE = {tuple(x) for x in cfg['DROP_NATURE']}
EXTRA = cfg['EXTRA']
FIX_PMID = cfg['FIX_PMID']
EXC = cfg['EXC']
GRAY = cfg['GRAY']
EXTRA_NOTICES = {e['notice_pmid'] for e in EXTRA}
res = []
for r in rows + EXTRA:
    if r.get('rw_id') in DROP_RW or (r['notice_pmid'], r['nature']) in DROP_NATURE: continue
    op = FIX_PMID.get(r['orig_pmid'], r['orig_pmid'])
    if r['notice_pmid'] in EXTRA_NOTICES and not r.get('rw_id') and r not in EXTRA: continue
    key = op or r['orig_doi']
    dec = 'excluir' if key in EXC else 'incluir'
    res.append(dict(notice_pmid=r['notice_pmid'], en_cadena_protocolo='si' if r['notice_pmid'] in prot else 'no',
        orig_pmid=op, orig_doi=r['orig_doi'].lower(), titulo=r['title'], tipo_rw=r.get('type',''), naturaleza=r['nature'],
        fecha_nota=r['ret_date'], decision=dec, motivo=EXC.get(key,''), zona_gris=GRAY.get(key,'')))
w = csv.DictWriter(open(out,'w',newline=''), fieldnames=res[0].keys()); w.writeheader(); w.writerows(res)
inc = [x for x in res if x['decision']=='incluir']
print('filas', len(res), 'notas', len({x['notice_pmid'] for x in res}), 'incluidos(art)', len(inc), 'notas con incluidos', len({x['notice_pmid'] for x in inc}),
      '| protocolo: incl', sum(x['en_cadena_protocolo']=='si' for x in inc), 'gris', sum(bool(x['zona_gris']) for x in inc))
