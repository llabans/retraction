import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import *
import numpy as np
df,meta=load('DATA/Base retraccion 5 (cuartiles revisados).dta')
vl=meta.value_labels
df['cuartil']=df.quartila_retrac.map({1:'Q1',2:'Q2',3:'Q3',4:'Q4'})
df['t']=df.año_retraccion-df.año_publicacion
print('t==tiempo_retracion all:', (df.t==df.tiempo_retracion).all(), 'neg:',(df.t<0).sum(), 'min/max',df.t.min(),df.t.max())
N=len(df)
r=lambda x,d=1: round(x,d)
print('N',N)
rec=((df.año_retraccion>=2018)&(df.año_retraccion<=2023)).sum(); print('2018-23',rec, r(100*rec/N))
q=df.cuartil.value_counts(); print(q.to_dict(), {k:r(100*v/N) for k,v in q.items()})
print('Q1+Q2',q.Q1+q.Q2, r(100*(q.Q1+q.Q2)/N))
print('mean sd', r(df.t.mean()), r(df.t.std()))
for k in ['Q1','Q2','Q3','Q4']:
    s=df.t[df.cuartil==k]; print(k, r(s.mean()), r(s.std()), len(s))
ce=df.continente_ensayo.map(vl['continente_ensayo']); ca=df.continente_1er_autor.map(vl['continente_1er_autor'])
print('ens',ce.value_counts().to_dict(), {k:r(100*v/N) for k,v in ce.value_counts().items()})
print('aut',ca.value_counts().to_dict(), {k:r(100*v/N) for k,v in ca.value_counts().items()})
print('asia q1', ((ce=='Asia')&(df.cuartil=='Q1')).sum(), r(100*((ce=='Asia')&(df.cuartil=='Q1')).sum()/(ce=='Asia').sum()))
print('africa q2', ((ce=='Africa')&(df.cuartil=='Q2')).sum(), r(100*((ce=='Africa')&(df.cuartil=='Q2')).sum()/(ce=='Africa').sum()))
print(pd.crosstab(ce,df.cuartil,margins=True)); print(pd.crosstab(ca,df.cuartil,margins=True))
per=pd.cut(df.año_retraccion,[2002,2007,2012,2017,2023],labels=['2003-2007','2008-2012','2013-2017','2018-2023'])
print(pd.crosstab(per,df.cuartil,margins=True))
print('años_retrac_grupo vs per'); print(pd.crosstab(df.años_retrac_grupo, per))
pp=pd.cut(df.año_publicacion,[2002,2007,2012,2017,2023],labels=['2003-2007','2008-2012','2013-2017','2018-2023'])
print('periodo_publicacion', pp.value_counts(dropna=False).to_dict())
reasons=["fabricacion","falsificacion","manipulacion","omision_info","falsificacion_no_especif","errores_metodologicos_estadistic","plagio","autoplagio","plagio_a_otros","publi_duplicada","salami","errores_autoria","revision_pares","error_administ"]
for v in reasons:
    x=pd.to_numeric(df[v])==1
    ct=df.cuartil[x].value_counts()
    print(f'{v:35s} n={x.sum():3d} ({r(100*x.sum()/N)}) ', {k:(ct.get(k,0), r(100*ct.get(k,0)/x.sum())) for k in ['Q1','Q2','Q3','Q4']})
b={v:(pd.to_numeric(df[v])==1) for v in reasons}
plag_any=(b['plagio']|b['autoplagio']|b['plagio_a_otros']|b['publi_duplicada']).sum()
main=['fabricacion','falsificacion','errores_metodologicos_estadistic','salami','errores_autoria','revision_pares','error_administ']
tot=sum(b[v].sum() for v in main)+plag_any
print('plag_any',plag_any,'total razones',tot)
for v,n in [('fals',b['falsificacion'].sum()),('met',b['errores_metodologicos_estadistic'].sum()),('plag',plag_any),('fab',b['fabricacion'].sum())]:
    print(v,n, 'of reasons',r(100*n/tot),'of trials',r(100*n/N))
F=b['falsificacion'].sum(); P=plag_any
print('manip',r(100*b['manipulacion'].sum()/F),'omis',r(100*b['omision_info'].sum()/F),'noesp',r(100*b['falsificacion_no_especif'].sum()/F))
print('auto',r(100*b['autoplagio'].sum()/P),'otros',r(100*b['plagio_a_otros'].sum()/P),'dup',r(100*b['publi_duplicada'].sum()/P))
# reasons per trial
nre=sum(b[v].astype(int) for v in main)+ (b['plagio']|b['autoplagio']|b['plagio_a_otros']|b['publi_duplicada']).astype(int)
print('reasons per trial', nre.value_counts().sort_index().to_dict())
# consistency
for parent,subs in [('falsificacion',['manipulacion','omision_info','falsificacion_no_especif']),('plagio',['autoplagio','plagio_a_otros','publi_duplicada'])]:
    pa=b[parent]
    anysub=sum(b[s].astype(int) for s in subs)
    print(parent,'parent=1 & no sub:',(pa&(anysub==0)).sum(),' parent=1 & >1 sub:',(pa&(anysub>1)).sum(), ' sub=1 & parent!=1:',((anysub>0)&~pa).sum(),
       ' parent=0 but sub nonmissing:',((~pa)&df[subs].notna().any(axis=1)).sum(), ' parent=1 but sub missing:',(pa&df[subs].isna().any(axis=1)).sum())
    print(pd.crosstab(pd.to_numeric(df[parent]), df[subs].notna().all(axis=1)))
# Table S1
print('S1 period n', per.value_counts().sort_index().to_dict())
for v in reasons:
    print(f'{v:35s}', pd.crosstab(b[v],per).loc[True].to_dict() if b[v].any() else {})
# year counts
print('by year', df.año_retraccion.value_counts().sort_index().to_dict())
print(pd.crosstab(df.año_retraccion, df.cuartil).loc[[2016,2017,2018,2019,2020,2021,2022,2023]])
