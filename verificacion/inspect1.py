import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import *
for p in ['DATA/Base retraccion 5 (cuartiles revisados).dta','DATA/retraccion_continentes.dta','RAW/data_rectraction.dta']:
    df,meta=load(p)
    print('=====',p,df.shape)
    for c in df.columns:
        lab=meta.variable_to_label.get(c)
        print(c, df[c].dtype, 'nmiss=',df[c].isna().sum() + (df[c].astype(str).str.strip()=='').sum() if df[c].dtype==object else df[c].isna().sum(), 'labelset=',lab, '|', meta.column_names_to_labels.get(c))
    print(meta.value_labels)
