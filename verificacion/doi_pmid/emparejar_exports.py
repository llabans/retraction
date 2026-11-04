"""Empareja cada registro de la base con su nota en los exports de PubMed (MEDLINE) y Scopus (RIS) por similitud de título.
Uso: python3 emparejar_exports.py salida.csv [correcciones_manuales.json]
- La carpeta manuscrito/ se toma de la variable de entorno RETRACTION_MANUSCRITO (por defecto, ../../manuscrito/ desde este script).
- correcciones_manuales.json (dato privado, no se publica): {"id": ["notice_pmid", "notice_doi"], ...} para registros
  que el emparejamiento automático no resuelve.
"""
import re, os, json, pathlib, pandas as pd, difflib, pyreadstat, sys
B=os.environ.get('RETRACTION_MANUSCRITO', str(pathlib.Path(__file__).resolve().parents[2]/'manuscrito'))+'/'
df,_=pyreadstat.read_dta(B+'DATA/Base retraccion 5 (cuartiles revisados).dta')
def norm(t):
    t=str(t).lower()
    t=re.sub(r'^(retraction note to|retraction note|retraction notice to|retraction notice|notice of retraction|statement of retraction|retracted article|retracted|retraction|erratum)\s*[:.\-]?\s*','',t)
    t=re.sub(r'\[retraction\].*','',t); t=re.sub(r'\(.*?\)','',t)
    return re.sub(r'[^a-z0-9 ]','',t).strip()
# pubmed medline
recs=[]; cur={}; key=None
for line in open(B+'SOURCE/Pubmed_07.08.23.txt',encoding='utf-8-sig'):
    if not line.strip():
        if cur: recs.append(cur); cur={}
        continue
    if line[:4].strip() and line[4:6]=='- ':
        key=line[:4].strip(); val=line[6:].rstrip()
        cur.setdefault(key,[]).append(val)
    elif key: cur[key][-1]+=' '+line.strip()
if cur: recs.append(cur)
pm=[]
for r in recs:
    doi=[x.replace(' [doi]','') for x in r.get('LID',[])+r.get('AID',[]) if '[doi]' in x]
    rof=' | '.join(r.get('ROF',[]))
    pm.append(dict(src='pubmed',notice_pmid=r['PMID'][0],notice_doi=doi[0] if doi else '',title=r.get('TI',[''])[0],
                   ab=' '.join(r.get('AB',[])),rof=rof,year=r.get('DP',[''])[0][:4]))
# scopus ris
sc=[]; cur={}
for line in open(B+'SOURCE/scopus_07.08.23.ris',encoding='utf-8-sig'):
    m=re.match(r'^([A-Z][A-Z0-9])  - ?(.*)',line.rstrip('\n'))
    if not m: continue
    k,v=m.groups()
    if k=='ER':
        sc.append(cur); cur={}; continue
    cur.setdefault(k,[]).append(v)
scs=[dict(src='scopus',notice_pmid='',notice_doi=(r.get('DO') or [''])[0],title=(r.get('TI') or r.get('T1') or [''])[0],
          ab=' '.join(r.get('AB',[])),rof='',year=(r.get('PY') or [''])[0][:4]) for r in sc]
allr=pd.DataFrame(pm+scs); allr['n']=allr.title.map(norm)
out=[]
for _,row in df.iterrows():
    nt=norm(row.titulo)
    best=None;bs=0
    for i,r in allr.iterrows():
        s=difflib.SequenceMatcher(None,nt,r.n).ratio() if nt and r.n else 0
        if s>bs: bs=s;best=i
    if best is None:
        out.append(dict(id=("%g" % round(row.id,1)),score=0,titulo=str(row.titulo)[:90],matched='',src='',notice_pmid='',notice_doi='',original_pmid='',rof=''))
        continue
    # prefer pubmed record with same doi if exist
    r=allr.loc[best]
    pmr=allr[(allr.src=='pubmed')&(allr.n==r.n)] if r.src=='scopus' else allr.loc[[best]]
    pmid=pmr.notice_pmid.iloc[0] if len(pmr) else ''
    rofm=re.search(r'PMID: (\d+)',pmr.rof.iloc[0]) if len(pmr) else None
    dois=allr[allr.n==r.n].notice_doi.tolist()
    out.append(dict(id=("%g" % round(row.id,1)),score=round(bs,2),titulo=row.titulo[:90],matched=r.title[:90],src=r.src,
       notice_pmid=pmid,notice_doi=next((d for d in dois if d),''),original_pmid=rofm.group(1) if rofm else '',
       rof=pmr.rof.iloc[0][:150] if len(pmr) else ''))
o=pd.DataFrame(out)
fix={k:tuple(v) for k,v in json.load(open(sys.argv[2],encoding='utf-8')).items() if not k.startswith('_')} if len(sys.argv)>2 else {}
for k,(p,d) in fix.items():
    m=o.id==k; o.loc[m,'notice_pmid']=p; o.loc[m,'notice_doi']=d; o.loc[m,'score']=1.0; o.loc[m,'src']='pubmed (corrección manual)'
for k,(p,_) in fix.items():
    rr=allr[allr.notice_pmid==p]; m=re.search(r'PMID: (\d+)',rr.rof.iloc[0]) if len(rr) else None
    if m: o.loc[o.id==k,'original_pmid']=m.group(1)
# DOIs of the original article mentioned in notice abstracts
abmap={}
for _,r in allr.iterrows():
    for d in re.findall(r'10\.\d{4,9}/[^\s,;)\]]+',r.ab):
        d=d.rstrip('.')
        if d.lower()!=r.notice_doi.lower(): abmap.setdefault(r.n,[]).append(d)
o['original_doi_en_nota']=[ '; '.join(dict.fromkeys(abmap.get(norm(t) if norm(t) else '',[]))) for t in df.titulo]

o.to_csv(sys.argv[1],index=False)
print((o.score>=0.9).sum(),'>=0.9;', (o.score<0.9).sum(),'<0.9')
print('notice_doi',(o.notice_doi!='').sum(),'notice_pmid',(o.notice_pmid!='').sum(),'orig_pmid',(o.original_pmid!='').sum())
print(o[o.score<0.9][['id','score','titulo','matched']].to_string())
