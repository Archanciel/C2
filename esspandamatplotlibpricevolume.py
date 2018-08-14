import matplotlib
#matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
from matplotlib import style
import matplotlib.dates as mdates
import datetime

style.use('ggplot')

df = pd.read_csv('secondary-2018-08-12-21-32-56.csv', index_col=0, sep='\t')

#df['100ma'] = df['Close'].rolling(window=100, min_periods=0).mean()
print(df.head())
l = df['TIMESTAMP (MS)'].tolist()
xx = [datetime.datetime.fromtimestamp(x / 1000) for x in l]
print(xx)
myFmt = mdates.DateFormatter('%H:%M:%S')
plt.gca().xaxis.set_major_formatter(myFmt)

ax1 = plt.subplot2grid((6,1), (0,0), rowspan=5, colspan=1)
ax2v = plt.subplot2grid((6,1), (5,0), rowspan=1, colspan=1, sharex=ax1)
ax2v.set_ylim(0, 0.8 * df['VOLUME'].max())

ax1.plot(df.index, df['PRICE'])
#ax1.plot(df.index, df['100ma'])
ax2v.bar(df.index, df['VOLUME'])

#plt.savefig('myfig')
plt.show()