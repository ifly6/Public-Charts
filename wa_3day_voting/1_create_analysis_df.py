#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 13:08:08 2023
@author: Imperium Anglorum
"""
import pandas as pd
import numpy as np

import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns

# ---------
# load data
# ---------

rsltn = pd.read_csv(
    'data/all_resolution_data_20230216.csv.xz',
    parse_dates=['resolution_date'])
votes = pd.read_csv(
    'data/all_vote_data_20230216.csv.xz',
    parse_dates=['time'])

votes = votes.merge(
    rsltn, left_on='resolution_id', right_on='id',
    how='left', validate='m:1')

votes['date'] = votes['time'].dt.round('D')
votes['_dst'] = votes['resolution_id'].map(
    votes.groupby('resolution_id')['date'].min())
votes['_day'] = (votes['date'] - votes['_dst']).dt.days

# -------------------------------
# CONSTRUCT DATA IN TWO DATA SETS
# -------------------------------

# find last observation; select full vote series only; gen vars
last = votes.groupby('resolution_id').last()
votes = votes[votes['resolution_id'].isin(last.query('_day == 4').index)]

d4 = last[['time', 'votes_for', 'votes_against']].copy()
d4['_tv4'] = d4[['votes_for', 'votes_against']].sum(axis=1)
d4['_rs4'] = np.where(d4['votes_for'] > d4['votes_against'], 'pass', 'fail')
d4['_pc4'] = d4['votes_for'] / d4['_tv4']

# construct the day before; create columns and select minimum difference
# get final
votes['_final'] = votes['resolution_id'].map(d4['time'])

# final - 1 day : (Final T MinuS 1)
votes['_ftms1'] = votes['_final'] - pd.offsets.Day(1)

# convert to differences : final t Minus 1 difference
votes['_ftm1d'] = abs(votes['_ftms1'] - votes['time'])

# select minimum difference and gen vars
d1bf = votes.sort_values('_ftm1d').groupby('resolution_id').first()
d3 = d1bf[['time', '_ftm1d', 'votes_for', 'votes_against']].copy()
d3['_tv3'] = d3[['votes_for', 'votes_against']].sum(axis=1)
d3['_rs3'] = np.where(d3['votes_for'] > d3['votes_against'], 'pass', 'fail')
d3['_pc3'] = d3['votes_for'] / d3['_tv3']

# --------
# analysis
# --------

day_results = d4.join(d3, lsuffix='_d4', rsuffix='_d3')

# drop entries where _ftm1d is implausibly large
day_results = day_results[day_results['_ftm1d'].dt.seconds < 60 * 60 * 1.2]

day_results['add_prop'] = day_results.eval('(_tv4 - _tv3) / _tv4')
day_results['res_diff'] = np.where(
    day_results['_rs4'] == day_results['_rs3'],
    'same', 'diff')

day_results['vtf_diff'] = day_results['_pc4'] - day_results['_pc3']

day_results = day_results.join(
    rsltn.set_index('id')[['title', 'chamber', 'resolution_date']])

day_results['year'] = day_results['resolution_date'].dt.year
by_year = day_results.groupby('year')['add_prop'].describe().T \
    .drop(columns=[2014])

# day_results['add_prop'].describe()
# Out[250]:
# count    894.000000
# mean       0.077928
# std        0.024187
# min        0.003668
# 25%        0.061248
# 50%        0.073483
# 75%        0.089872
# max        0.180737
# Name: add_prop, dtype: float64

# pd.concat(
#     [day_results['res_diff'].value_counts(),
#       day_results['res_diff'].value_counts(normalize=True)],
#     axis=1)
# Out[256]:
#       res_diff  res_diff
# same       883  0.987696
# diff        11  0.012304

sns.set_style('whitegrid')

sns.violinplot(data=day_results, x='add_prop', y='res_diff') \
    .get_figure().savefig('plots/add_diff_vlplot.png', bbox_inches='tight')

plt.clf()
sns.histplot(data=day_results, x='add_prop', bins=32) \
    .get_figure().savefig('plots/add_prop_hist.png', bbox_inches='tight')

# run simple regressions
# nb these regressions are reversed to avoid having to use a logit model ;
# there should be simultaneous causality
smf.ols('add_prop ~ res_diff', data=day_results) \
    .fit(cov_type='HC3').summary2()
"""
                  Results: Ordinary least squares
===================================================================
Model:              OLS              Adj. R-squared:     0.022
Dependent Variable: add_prop         AIC:                -4135.3201
Date:               2023-02-16 15:34 BIC:                -4125.7287
No. Observations:   894              Log-Likelihood:     2069.7
Df Model:           1                F-statistic:        4.222
Df Residuals:       892              Prob (F-statistic): 0.0402
R-squared:          0.023            Scale:              0.00057236
-------------------------------------------------------------------
                     Coef.  Std.Err.    z    P>|z|   [0.025  0.975]
-------------------------------------------------------------------
Intercept            0.1106   0.0161  6.8819 0.0000  0.0791  0.1421
res_diff[T.same]    -0.0331   0.0161 -2.0546 0.0399 -0.0646 -0.0015
-------------------------------------------------------------------
Omnibus:              129.479       Durbin-Watson:          1.845
Prob(Omnibus):        0.000         Jarque-Bera (JB):       233.478
Skew:                 0.893         Prob(JB):               0.000
Kurtosis:             4.755         Condition No.:          18
===================================================================
"""

smf.ols('add_prop ~ res_diff + chamber', data=day_results) \
    .fit(cov_type='HC3').summary2()
"""
                  Results: Ordinary least squares
===================================================================
Model:              OLS              Adj. R-squared:     0.074
Dependent Variable: add_prop         AIC:                -4183.2492
Date:               2023-02-16 15:34 BIC:                -4168.8621
No. Observations:   894              Log-Likelihood:     2094.6
Df Model:           2                F-statistic:        30.41
Df Residuals:       891              Prob (F-statistic): 1.68e-13
R-squared:          0.076            Scale:              0.00054187
-------------------------------------------------------------------
                     Coef.  Std.Err.    z    P>|z|   [0.025  0.975]
-------------------------------------------------------------------
Intercept            0.1167   0.0156  7.4759 0.0000  0.0861  0.1473
res_diff[T.same]    -0.0342   0.0157 -2.1816 0.0291 -0.0649 -0.0035
chamber[T.SC]       -0.0112   0.0015 -7.2440 0.0000 -0.0142 -0.0082
-------------------------------------------------------------------
Omnibus:              129.223       Durbin-Watson:          1.867
Prob(Omnibus):        0.000         Jarque-Bera (JB):       236.356
Skew:                 0.885         Prob(JB):               0.000
Kurtosis:             4.792         Condition No.:          19
===================================================================
"""

# run some more complex resolutions which attempt to find some kind of
# intensive margin effect on vote differences from add_prop
smf.ols('vtf_diff ~ add_prop + chamber', data=day_results) \
    .fit(cov_type='HC3').summary2()
"""
                  Results: Ordinary least squares
===================================================================
Model:              OLS              Adj. R-squared:     0.013     
Dependent Variable: vtf_diff         AIC:                -4280.3173
Date:               2023-02-16 22:31 BIC:                -4265.9302
No. Observations:   894              Log-Likelihood:     2143.2    
Df Model:           2                F-statistic:        3.905     
Df Residuals:       891              Prob (F-statistic): 0.0205    
R-squared:          0.015            Scale:              0.00048612
-------------------------------------------------------------------
                Coef.   Std.Err.     z     P>|z|    [0.025   0.975]
-------------------------------------------------------------------
Intercept       0.0080    0.0063   1.2730  0.2030  -0.0043   0.0204
chamber[T.SC]  -0.0050    0.0023  -2.2249  0.0261  -0.0094  -0.0006
add_prop       -0.0719    0.0770  -0.9332  0.3507  -0.2229   0.0791
------------------------------------------------------------------
Omnibus:            1455.995      Durbin-Watson:         2.014     
Prob(Omnibus):      0.000         Jarque-Bera (JB):      920811.937
Skew:               -9.899        Prob(JB):              0.000     
Kurtosis:           158.974       Condition No.:         48        
===================================================================
"""

smf.ols('add_prop ~ abs(vtf_diff) + chamber', data=day_results) \
    .fit(cov_type='HC3').summary2()
"""
                  Results: Ordinary least squares
===================================================================
Model:              OLS              Adj. R-squared:     0.120     
Dependent Variable: add_prop         AIC:                -4228.5553
Date:               2023-02-16 22:35 BIC:                -4214.1682
No. Observations:   894              Log-Likelihood:     2117.3    
Df Model:           2                F-statistic:        35.24     
Df Residuals:       891              Prob (F-statistic): 1.87e-15  
R-squared:          0.121            Scale:              0.00051510
-------------------------------------------------------------------
                Coef.   Std.Err.     z     P>|z|    [0.025   0.975]
-------------------------------------------------------------------
Intercept       0.0802    0.0014  59.1840  0.0000   0.0775   0.0828
chamber[T.SC]  -0.0113    0.0015  -7.5014  0.0000  -0.0143  -0.0084
abs(vtf_diff)   0.3145    0.1088   2.8916  0.0038   0.1013   0.5276
------------------------------------------------------------------
Omnibus:              116.294       Durbin-Watson:          1.840  
Prob(Omnibus):        0.000         Jarque-Bera (JB):       213.508
Skew:                 0.807         Prob(JB):               0.000  
Kurtosis:             4.769         Condition No.:          55     
===================================================================
"""

smf.ols('abs(vtf_diff) ~ add_prop', 
        data=day_results.query('chamber == "GA"')) \
    .fit(cov_type='HC3').summary2()
"""
                  Results: Ordinary least squares
===================================================================
Model:              OLS              Adj. R-squared:     0.134     
Dependent Variable: abs(vtf_diff)    AIC:                -3279.3451
Date:               2023-02-16 22:37 BIC:                -3270.9319
No. Observations:   496              Log-Likelihood:     1641.7    
Df Model:           1                F-statistic:        28.65     
Df Residuals:       494              Prob (F-statistic): 1.33e-07  
R-squared:          0.136            Scale:              7.8416e-05
-------------------------------------------------------------------
             Coef.    Std.Err.      z     P>|z|     [0.025   0.975]
-------------------------------------------------------------------
Intercept   -0.0033     0.0021   -1.5623  0.1182   -0.0074   0.0008
add_prop     0.1416     0.0264    5.3528  0.0000    0.0897   0.1934
-------------------------------------------------------------------
Omnibus:             365.105       Durbin-Watson:          1.945   
Prob(Omnibus):       0.000         Jarque-Bera (JB):       6710.335
Skew:                3.011         Prob(JB):               0.000   
Kurtosis:            19.983        Condition No.:          41      
===================================================================
"""
