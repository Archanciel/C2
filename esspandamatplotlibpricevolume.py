import matplotlib
#matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
from matplotlib import style

style.use('ggplot')

df = pd.read_csv('primary.csv', index_col=0)
#df['100ma'] = df['Close'].rolling(window=100, min_periods=0).mean()
print(df.head())

ax1 = plt.subplot2grid((6,1), (0,0), rowspan=5, colspan=1)
ax2v = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1, sharex=ax1)
ax2v.set_ylim(0, 1 * df['VOLUME'].max())

ax1.plot(df.index, df['PRICE'])
#ax1.plot(df.index, df['100ma'])
ax2v.bar(df.index, df['VOLUME'])

#plt.savefig('myfig')
plt.show()