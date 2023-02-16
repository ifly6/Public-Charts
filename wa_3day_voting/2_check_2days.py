#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 15:48:17 2023
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

# final - 2 days : (Final T MinuS 1)
votes['_ftms1'] = votes['_final'] - pd.offsets.Day(2)

# convert to differences : final t Minus 1 difference
votes['_ftm1d'] = abs(votes['_ftms1'] - votes['time'])

# select minimum difference and gen vars
d1bf = votes.sort_values('_ftm1d').groupby('resolution_id').first()
d2 = d1bf[['time', '_ftm1d', 'votes_for', 'votes_against']].copy()
d2['_tv2'] = d2[['votes_for', 'votes_against']].sum(axis=1)
d2['_rs2'] = np.where(d2['votes_for'] > d2['votes_against'], 'pass', 'fail')

# --------
# analysis
# --------

day_results = d4.join(d2, lsuffix='_d4', rsuffix='_d2')

# drop entries where _ftm1d is implausibly large
day_results = day_results[day_results['_ftm1d'].dt.seconds < 60 * 60 * 1.2]

day_results['add_prop'] = day_results.eval('(_tv4 - _tv2) / _tv4')
day_results['res_diff'] = np.where(
    day_results['_rs4'] == day_results['_rs2'],
    'same', 'diff')

day_results = day_results.join(
    rsltn.set_index('id')[['title', 'chamber', 'resolution_date']])

day_results['year'] = day_results['resolution_date'].dt.year
by_year = day_results.groupby('year')['add_prop'].describe().T \
    .drop(columns=[2014])

day_results['add_prop'].describe()
# ---
# count    895.000000
# mean       0.179092
# std        0.040726
# min        0.092358
# 25%        0.148995
# 50%        0.173692
# 75%        0.204804
# max        0.354197
# Name: add_prop, dtype: float64

pd.concat(
    [day_results['res_diff'].value_counts(),
      day_results['res_diff'].value_counts(normalize=True)],
    axis=1)
# ---
#       res_diff  res_diff
# same       878  0.981006
# diff        17  0.018994

# run simple regressions
smf.ols('add_prop ~ res_diff', data=day_results) \
    .fit(cov_type='HC3').summary2()
"""
                  Results: Ordinary least squares
===================================================================
Model:              OLS              Adj. R-squared:     0.019
Dependent Variable: add_prop         AIC:                -3205.2926
Date:               2023-02-16 15:51 BIC:                -3195.6989
No. Observations:   895              Log-Likelihood:     1604.6
Df Model:           1                F-statistic:        10.26
Df Residuals:       893              Prob (F-statistic): 0.00140
R-squared:          0.021            Scale:              0.0016263
-------------------------------------------------------------------
                     Coef.  Std.Err.    z    P>|z|   [0.025  0.975]
-------------------------------------------------------------------
Intercept            0.2210   0.0133 16.6439 0.0000  0.1950  0.2471
res_diff[T.same]    -0.0428   0.0133 -3.2038 0.0014 -0.0689 -0.0166
-------------------------------------------------------------------
Omnibus:              63.499        Durbin-Watson:           1.826
Prob(Omnibus):        0.000         Jarque-Bera (JB):        76.633
Skew:                 0.658         Prob(JB):                0.000
Kurtosis:             3.570         Condition No.:           14
===================================================================
"""

smf.ols('add_prop ~ res_diff + chamber', data=day_results) \
    .fit(cov_type='HC3').summary2()
"""
                  Results: Ordinary least squares
===================================================================
Model:              OLS              Adj. R-squared:     0.073
Dependent Variable: add_prop         AIC:                -3254.8247
Date:               2023-02-16 15:50 BIC:                -3240.4342
No. Observations:   895              Log-Likelihood:     1630.4
Df Model:           2                F-statistic:        33.84
Df Residuals:       892              Prob (F-statistic): 6.81e-15
R-squared:          0.075            Scale:              0.0015370
-------------------------------------------------------------------
                     Coef.  Std.Err.    z    P>|z|   [0.025  0.975]
-------------------------------------------------------------------
Intercept            0.2278   0.0128 17.7434 0.0000  0.2027  0.2530
res_diff[T.same]    -0.0410   0.0129 -3.1665 0.0015 -0.0663 -0.0156
chamber[T.SC]       -0.0192   0.0026 -7.3256 0.0000 -0.0243 -0.0140
-------------------------------------------------------------------
Omnibus:              58.192        Durbin-Watson:           1.833
Prob(Omnibus):        0.000         Jarque-Bera (JB):        68.186
Skew:                 0.643         Prob(JB):                0.000
Kurtosis:             3.417         Condition No.:           15
===================================================================
"""
