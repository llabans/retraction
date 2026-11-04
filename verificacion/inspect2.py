import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from load import *
df,meta=load('DATA/Base retraccion 5 (cuartiles revisados).dta')
pd.set_option('display.width',250); pd.set_option('display.max_rows',500)
for c in df.columns:
    if c in ('titulo','autores','id'): continue
    print('---',c, df[c].map(repr).value_counts(dropna=False).to_dict())
