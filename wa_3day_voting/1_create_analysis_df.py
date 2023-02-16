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
