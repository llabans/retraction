import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import *
pd.set_option('display.width',250)
A,ma=load('DATA/Base retraccion 5 (cuartiles revisados).dta')
R,mr=load('RAW/data_rectraction.dta')
C,mc=load('DATA/retraccion_continentes.dta')
M=A.merge(R,on='id',suffixes=('','_r'))
print(pd.crosstab(M.continente_ensayo.map(ma.value_labels['continente_ensayo']), M.continente_eca.map(mr.value_labels['continentes_eca'])).to_string())
d=M[M.continente_ensayo.map(ma.value_labels['continente_ensayo'])!=M.continente_eca.map(mr.value_labels['continentes_eca']).replace('Ocenia','Oceania')]
print(d[['id','pais_eca','continente_ensayo','continente_eca']])
for nm,D in [('RAW',R),('C',C),('A',A)]:
    rec=D[D.año_retraccion>=2018]
    q=rec.quartila_retrac.value_counts()
    print(nm,'recent',len(rec),q.to_dict(), 'Q1%',round(100*q[1]/len(rec),1),'Q2%',round(100*q[2]/len(rec),1),'Q1+Q2%',round(100*(q[1]+q[2])/len(rec),1))
    D=D.copy(); D['t']=D.año_retraccion-D.año_publicacion
    print(' t by q', D.groupby('quartila_retrac').t.agg(['mean','std','count']).round(1).to_dict('index'))
vs=['fabricacion','falsificacion','errores_metodologicos_estadistic','plagio','salami','errores_autoria','revision_pares','error_administ']
for nm,D in [('RAW',R),('A',A)]:
    s={v:int((pd.to_numeric(D[v])==1).sum()) for v in vs}; tot=sum(s.values())
    print(nm,s,'tot',tot,{v:round(100*n/tot,1) for v,n in s.items()})
# RAW consistency
for c in ['manipulacion','omision_info','falsificacion_no_especifica']:
    print('RAW',c,'=1 & fals=0:', ((R[c]==1)&(R.falsificacion==0)).sum())
for c in ['autoplagio','plagio_a_otros','publi_duplicada']:
    print('RAW',c,'=1 & plagio=0:', ((R[c]==1)&(R.plagio==0)).sum())
print('RAW fals=1 no sub', ((R.falsificacion==1)&(R[['manipulacion','omision_info','falsificacion_no_especifica']].sum(axis=1)==0)).sum())
print('RAW plag=1 no sub', ((R.plagio==1)&(R[['autoplagio','plagio_a_otros','publi_duplicada']].sum(axis=1)==0)).sum())
# Asia in RAW by quartile
print(pd.crosstab(R.continente_eca.map(mr.value_labels['continentes_eca']), R.quartila_retrac))
