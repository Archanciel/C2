import matplotlib
#matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
from matplotlib import style
import matplotlib.dates as mdates
import datetime

style.use('ggplot')

#df = pd.read_csv('secondary-2018-08-12-21-32-56.csv', index_col=0, sep='\t')
df = pd.read_csv('secondary-2018-08-19-22-44-28.csv', index_col=0, sep='\t')

#df['100ma'] = df['Close'].rolling(window=100, min_periods=0).mean()
print(df.head())
l = df['TIMESTAMP'].tolist()
xx = [datetime.datetime.fromtimestamp(x / 1000).strftime("%M:%S") for x in l]
print(xx)
myFmt = mdates.DateFormatter('%H:%M:%S')
plt.gca().xaxis.set_major_formatter(myFmt)

ax1Price = plt.subplot2grid((6, 1), (0, 0), rowspan=5, colspan=1)
ax2Volume = plt.subplot2grid((6, 1), (5, 0), rowspan=1, colspan=1, sharex=ax1Price)
ax2Volume.set_ylim(0, 0.3 * df['VOLUME'].max())

ax1Price.plot(df.index, df['PRICE'])
ax2Volume.bar(df.index, df['VOLUME'])

# setting the 2 levels X axis labels
xfmtMajor = mdates.DateFormatter('%M:%S')
ax1Price.xaxis.set_major_locator(mdates.SecondLocator(interval=60))
ax1Price.xaxis.set_major_formatter(xfmtMajor)

xfmtMinor = mdates.DateFormatter('%S')
ax1Price.xaxis.set_minor_locator(mdates.SecondLocator(interval=30))
ax1Price.xaxis.set_minor_formatter(xfmtMinor)

# defining the vertical interval between the major and minor X axis label rows
ax1Price.get_xaxis().set_tick_params(which='major', pad=20)

#fig.autofmt_xdate()

#plt.savefig('myfig')
plt.show()