#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 13:08:08 2023

@author: ifly6
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# load

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

# find last observation; select full vote series only
last = votes.groupby('resolution_id').last()
votes = votes[votes['resolution_id'].isin(last.query('_day == 4').index)]

d4 = last[['time', 'votes_for', 'votes_against']].copy()
d4['_tv4'] = d4[['votes_for', 'votes_against']].sum(axis=1)
d4['_rs4'] = np.where(d4['votes_for'] > d4['votes_against'], 'pass', 'fail')

# construct the day before; create columns and select minimum difference
votes['_final'] = votes['resolution_id'].map(d4['time'])

# final t MinuS 1
votes['_ftms1'] = votes['_final'] - pd.offsets.Day(1)

# final t Minus 1 difference
votes['_ftm1d'] = abs(votes['_ftms1'] - votes['time'])

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

# day_results['res_diff'].value_counts()
# Out[251]:
# same    883
# diff     11
# Name: res_diff, dtype: int64

sns.set_style('whitegrid')

sns.violinplot(data=day_results, x='add_prop', y='res_diff') \
    .get_figure().savefig('plots/add_diff_vlplot.png', bbox_inches='tight')

plt.clf()
sns.histplot(data=day_results, x='add_prop', bins=32) \
    .get_figure().savefig('plots/add_prop_hist.png', bbox_inches='tight')

