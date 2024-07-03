
import sys
import subprocess
import pandas as pd
import numpy as np
from datetime import datetime
from scipy.stats import gaussian_kde
from statsmodels.gam.api import GLMGam, BSplines
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

def read_clim(stationnr, date):
    data = pd.read_csv("climate_ibk.csv", sep=";")

    data['month'] = (data['date'] // 100).astype(int)
    data['day'] = (data['date'] % 100).astype(int)
    
    current_year = datetime.now().year

def generate_date(year, row):
    year = int(year)
    month = int(row['month'])
    day = int(row['day'])
    return datetime(year, month, day)
    
    date0 = data.apply(lambda row: generate_date(current_year + 1, row), axis=1)
    date1 = data.apply(lambda row: generate_date(current_year, row), axis=1)
    date2 = data.apply(lambda row: generate_date(current_year - 1, row), axis=1)
    date3 = data.apply(lambda row: generate_date(current_year - 2, row), axis=1)
    
    data0 = pd.DataFrame(data.iloc[:, 1:].values, index=date0)
    data1 = pd.DataFrame(data.iloc[:, 1:].values, index=date1)
    data2 = pd.DataFrame(data.iloc[:, 1:].values, index=date2)
    data3 = pd.DataFrame(data.iloc[:, 1:].values, index=date3)
    
    data_combined = pd.concat([data3, data2, data1, data0]).dropna()
    
    t = data_combined.iloc[:, 1:3]
    n = data_combined.iloc[:, 4:6]
    
    def calculate_quantiles(df):
        return df.apply(lambda x: np.percentile(x, [0, 25, 50, 75, 100]), axis=1)
    
    t_q = calculate_quantiles(t)
    t_q = pd.DataFrame(t_q.tolist(), index=t.index, columns=['p0', 'p25', 'p50', 'p75', 'p100'])
    
    bsplines = BSplines(t.index.map(mdates.date2num), df=[50], degree=[3])
    gam_model = GLMGam.from_formula('p25 ~ bsplines', data=t_q, smoother=bsplines)
    gam_result = gam_model.fit()
    
    t_q['p25'] = gam_result.fittedvalues
    t_q['p50'] = t['tmean']
    t_q['p75'] = gam_result.fittedvalues
    t_q['p100'] = t['tmax']
    
    n_q = calculate_quantiles(n)
    n_q = pd.DataFrame(n_q.tolist(), index=t.index, columns=['p0', 'p25', 'p50', 'p75', 'p100'])
    
    return {'t_q': t_q, 'n_q': n_q}

stationnr = 11320
date = '20240517'
result = read_clim(stationnr, date)
print(result)







