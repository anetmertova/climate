import os
import datetime
import configparser
import argparse
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def read_clim():

    # Function for reading climate data - t and n to be defined from API? 

    return t_q, n_q



def sybase_load_or_update(station, type, parameter, begin):

    # Function for loading or updating observations - same here
    return obs



def add_boxes(ax, x, column, indices, color):

    for i in indices:

        date = mdates.date2num(x.index[i])

        ax.add_patch(Rectangle((date, x.iloc[i][column]), 1, x.iloc[i]['p50'] - x.iloc[i][column], color=color, ec=None))



# Load climatological data

t_q, n_q = read_clim()



os.environ['TZ'] = 'UTC'

current_year = datetime.datetime.now().year



start_date = datetime.datetime.now() - datetime.timedelta(days=426)

start_year = start_date.year

start_month = start_date.month

os.environ['TZ'] = 'CET'

start = datetime.date(start_year, start_month, 1)



os.environ['TZ'] = 'GMT'

start = datetime.datetime(start_year, 1, 1)

os.environ['TZ'] = 'CET'



origin = datetime.datetime(1970, 1, 1)



# Load latest observations

obs = sybase_load_or_update(station=11320, type="tawes", parameter=['tlmin', 'tlmax', 'rr'], begin=start)



start = datetime.date(start_year, start_month, 1)

start = datetime.datetime.now() - datetime.timedelta(days=426)



obs.index = pd.to_datetime(obs.index, origin=origin)

datumsec = mdates.date2num(obs.index)

end = obs.index[-1] + datetime.timedelta(days=46)

idx = pd.to_datetime(datumsec, unit='s', origin=origin)



tmin = obs.resample('D').min()

tmax = obs.resample('D').max()



# Fixing last values if the observation time is out of bounds

if obs.index[-1].hour <= 19.1667 or obs.index[-1].hour > 5:

    tmax.iloc[-1] = np.nan

if obs.index[-1].hour <= 7.1667:

    tmin.iloc[-1] = np.nan



data = pd.merge(tmin, tmax, left_index=True, right_index=True, suffixes=('_min', '_max'))

data.dropna(inplace=True)



data['tmean'] = 0.5 * (data['tlmin'] + data['tlmax'])

data['yday'] = data.index.dayofyear



# Loading the climatological data

t_q.index = pd.to_datetime(t_q.index)

n_q.index = pd.to_datetime(n_q.index)

tmean = pd.merge(data, t_q, left_index=True, right_index=True)

tmean = tmean[(tmean.index <= end) & (tmean.index >= start)]



rr = obs['rr'].resample('D').sum().cumsum()

dummy = pd.to_datetime(rr.index.year * 1000 + rr.index.dayofyear, format='%Y%j', origin='CET')

rr = pd.Series(rr.values, index=dummy)



rr = rr[:-1]

rr = pd.merge(rr, n_q, left_index=True, right_index=True)

rr = rr[(rr.index <= end) & (rr.index > start)]



date_dummy = rr.index[-1].strftime('%b-%d')



# PLOT

tmean = tmean.round(1)



fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(19.2, 10.8))

fig.patch.set_facecolor('#000014')



# Plotting tmean

ax1.set_title('Climate Station University/Innsbruck: Daily Mean Temperature [°C]', color='white', fontsize=15)

ax1.set_facecolor('gray95')

ax1.grid(True, which='both', axis='y', color='gray50', linestyle='--', linewidth=0.5)

ax1.set_xlim(tmean.index.min(), tmean.index.max())

ax1.xaxis.set_major_locator(mdates.MonthLocator())

ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

ax1.xaxis.set_minor_locator(mdates.DayLocator())

ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}'))

ax1.tick_params(axis='x', colors='white', labelsize=10)

ax1.tick_params(axis='y', colors='white', labelsize=10)



# Plot boxes

idx_low = tmean[tmean['tmean'] < tmean['p0']].index

idx_high = tmean[tmean['tmean'] > tmean['p100']].index

add_boxes(ax1, tmean, 'tmean', idx_low, '#000ECA')

add_boxes(ax1, tmean, 'tmean', idx_high, '#850000')

add_boxes(ax1, tmean, 'p0', idx_low, '#5659B6')

add_boxes(ax1, tmean, 'p100', idx_high, '#A74243')



# Plot percentiles

ax1.plot(tmean['p50'], color='black', linewidth=3, drawstyle='steps-post')

ax1.plot(tmean['p0'], color='black', linewidth=0.75, linestyle='-', drawstyle='steps-post')

ax1.plot(tmean['p100'], color='black', linewidth=0.75, linestyle='-', drawstyle='steps-post')



# Plot current date line

ax1.axvline(x=datetime.datetime.now(), color='black', linewidth=1)

ax1.axvline(x=datetime.datetime.now() - datetime.timedelta(days=365), color='black', linewidth=1.5, linestyle='--')



# Add text annotations for year lines

for year in range(current_year - 1, current_year + 2):

    ax1.axvline(x=datetime.datetime(year, 1, 1), color='black')

    ax1.text(datetime.datetime(year, 1, 1), tmean['tmean'].max(), str(year), color='white', fontsize=10)


# Plotting rr

ax2.set_facecolor('gray95')

ax2.grid(True, which='both', axis='y', color='gray50', linestyle='--', linewidth=0.5)

ax2.set_xlim(rr.index.min(), rr.index.max())

ax2.xaxis.set_major_locator(mdates.MonthLocator())

ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

ax2.xaxis.set_minor_locator(mdates.DayLocator())

ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}'))

ax2.tick_params(axis='x', colors='white', labelsize=10)

ax2.tick_params(axis='y', colors='white', labelsize=10)


# Plot boxes

idx_low = rr[rr['rr'] < rr['p0']].index

idx_high = rr[rr['rr'] > rr['p100']].index

add_boxes(ax2, rr, 'rr', idx_low, '#7E3100')

add_boxes(ax2, rr, 'rr', idx_high, '#491CC4')

add_boxes(ax2, rr, 'p0', idx_low, '#A15C00')

add_boxes(ax2, rr, 'p100', idx_high, '#6E5FBE')


# Plot percentiles

ax2.plot(rr['p50'], color='black', linewidth=3, drawstyle='steps-post')

ax2.plot(rr['p0'], color='black', linewidth=0.75, linestyle='-', drawstyle='steps-post')

ax2.plot(rr['p100'], color='black', linewidth=0.75, linestyle='-', drawstyle='steps-post')


# Plot current date line

ax2.axvline(x=datetime.datetime.now(), color='black', linewidth=1)

ax2.text(datetime.datetime(current_year - 1, 1, 1), rr['rr'].max(), str(current_year - 1), color='white', fontsize=10)

ax2.text(datetime.datetime(current_year, 1, 1), rr['rr'].max(), str(current_year), color='white', fontsize=10)

ax2.text(datetime.datetime(current_year + 1, 1, 1), rr['rr'].max(), str(current_year + 1), color='white', fontsize=10)


# Add text annotations

ax2.text(start + datetime.timedelta(days=5), rr.loc[datetime.datetime.now() - datetime.timedelta(days=365)].values[0] + 15, "last year's", color='white', fontsize=6)

ax2.text(start + datetime.timedelta(days=5), rr.loc[datetime.datetime.now() - datetime.timedelta(days=365)].values[0] - 15, 'level', color='white', fontsize=6)

# Save plot

plt.savefig('../images/climate.png', dpi=100, bbox_inches='tight', facecolor=fig.get_facecolor())

plt.close(fig)



#SECOND PLOT

# Define colors
col_brown = ["#7E3100", "#A15C00", "#C49270"]
col_blue = ["#491CC4", "#6E5FBE", "#9D96D0"]

# Define functions for adding boxes
def boxes(df, column, indices, color):
    for i in indices:
        date = mdates.date2num(df.index[i])
        plt.gca().add_patch(plt.Rectangle((date, df.iloc[i][column]), 1, df.iloc[i]['p50'] - df.iloc[i][column], color=color, ec=None))

# Plotting
fig, ax = plt.subplots(figsize=(12, 6))

# Plotting precipitation
ax.plot(rr.index, rr['rr'], color='black', label='Observations')

# Lines to help the reader
ax.axhline(y=rr['p0'], linestyle='--', color='gray', linewidth=0.5)
ax.axhline(y=rr['p100'], linestyle='--', color='gray', linewidth=0.5)

# Plot boxes
idx_low = rr[rr['rr'] < rr['p0']].index
idx_high = rr[rr['rr'] > rr['p100']].index
boxes(rr, 'rr', idx_low, col_brown[0])
boxes(rr, 'rr', idx_high, col_blue[0])
boxes(rr, 'p0', idx_low, col_brown[1])
boxes(rr, 'p100', idx_high, col_blue[1])

# Plot boxes for 25/75 percentiles
idx_low = rr[(rr['rr'] >= rr['p0']) & (rr['rr'] < rr['p25'])].index
idx_high = rr[(rr['rr'] <= rr['p100']) & (rr['rr'] > rr['p75'])].index
boxes(rr, 'rr', idx_low, col_brown[1])
boxes(rr, 'rr', idx_high, col_blue[1])
boxes(rr, 'p25', idx_low, col_brown[2])
boxes(rr, 'p75', idx_high, col_blue[2])

# Plot boxes for 0/100 percentiles
idx_low = rr[rr['rr'] <= rr['p0']].index
idx_high = rr[rr['rr'] >= rr['p100']].index
boxes(rr, 'p25', idx_low, col_brown[2])
boxes(rr, 'p75', idx_high, col_blue[2])

# Plot boxes for 25/75 percentiles within range
idx_low = rr[(rr['rr'] <= rr['p50']) & (rr['rr'] > rr['p25'])].index
idx_high = rr[(rr['rr'] >= rr['p50']) & (rr['rr'] < rr['p75'])].index
boxes(rr, 'rr', idx_low, col_brown[2])
boxes(rr, 'rr', idx_high, col_blue[2])

# Plot current date line
ax.axvline(x=datetime.now(), color='black', linewidth=1)

# Adding legend
legend_text = ["Percentiles Relative to 1981-2010", ">100", "75-100", "50-75", "25-50", "0-25", "<0", "Median 1981-2010", "Extremes 1877-2015"]
ax.legend(legend_text, loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)

# Formatting x-axis
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.xaxis.set_minor_locator(mdates.DayLocator())

# Adding labels and title
ax.set_ylabel('Annually Accumulated Precipitation Sum [l/m²]')
ax.set_title('Precipitation')

# Save plot
plt.savefig('precipitation_plot.png', dpi=300, bbox_inches='tight')
plt.show()




