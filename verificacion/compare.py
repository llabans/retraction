import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import *
A,ma=load('DATA/Base retraccion 5 (cuartiles revisados).dta')
C,mc=load('DATA/retraccion_continentes.dta')
R,mr=load('RAW/data_rectraction.dta')
X=pd.read_excel(B+'DATA/data2_')
print('xlsx', X.shape); print(X.columns.tolist()); print(X.head(10).to_string())
for nm,D in [('C',C),('R',R)]:
    print('=====',nm)
    print('id equal order', (A.id.values==D.id.values).all(), 'id unique', A.id.is_unique, D.id.is_unique, A.id.min(),A.id.max())
    common=[c for c in A.columns if c in D.columns]
    print('only in A',[c for c in A.columns if c not in D.columns],'only in',nm,[c for c in D.columns if c not in A.columns])
    M=A.merge(D,on='id',suffixes=('','_d'))
    for c in common:
        if c=='id': continue
        a=M[c]; d=M[c+'_d']
        try: a=pd.to_numeric(a); d=pd.to_numeric(d)
        except: pass
        diff=~((a==d)|(a.isna()&d.isna()))
        if diff.sum(): print(c,'ndiff',diff.sum(), list(zip(M.id[diff].astype(int).tolist()[:15], a[diff].tolist()[:15], d[diff].tolist()[:15])))
# RAW continent map
lr=mr.value_labels; la=ma.value_labels
M=A.merge(R,on='id')
print(pd.crosstab(M.continente_ensayo.map(la['continente_ensayo']), M.continente_eca.map(lr['continentes_eca'])))
print(pd.crosstab(M.continente_1er_autor.map(la['continente_1er_autor']), M.continente_primer_autor.map(lr['continentes_autor'])))
print(pd.crosstab(A.quartila_retrac, R.quartila_retrac))
print('RAW quart', R.quartila_retrac.value_counts().to_dict(), 'C quart', C.quartila_retrac.value_counts().to_dict())
for c in ['manipulacion','omision_info','falsificacion_no_especifica','autoplagio','plagio_a_otros','publi_duplicada']:
    print('RAW',c,R[c].value_counts(dropna=False).to_dict())
print(pd.crosstab(R.falsificacion,[R.manipulacion,R.omision_info]))
