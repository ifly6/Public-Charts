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


def process(df):
    df.sort_values(by='time', inplace=True)
    try:
        d3 = df[lambda d: d['_day'] == 3].iloc[-1]
        d4 = df[lambda d: d['_day'] == 4].iloc[-1]
        return {
            'day3_tv': d3[['votes_for', 'votes_against']].sum(),
            'day3_rs': 'pass' if d3['votes_for'] > d3['votes_against'] else 'fail',
            'day4_tv': d4[['votes_for', 'votes_against']].sum(),
            'day4_rs': 'pass' if d4['votes_for'] > d4['votes_against'] else 'fail'}
    except:
        return {}


l = votes.groupby('resolution_id').apply(process)
day_results = pd.DataFrame(l.values.tolist(), index=l.index) \
    .dropna(axis=0)

day_results['add_prop'] = day_results.eval('(day4_tv - day3_tv) / day4_tv')
day_results['res_diff'] = np.where(
    day_results['day3_rs'] == day_results['day4_rs'],
    'same', 'diff')

# day_results['add_prop'].describe()
# Out[56]:
# count    920.000000
# mean       0.040935
# std        0.027867
# min       -0.029080
# 25%        0.013572
# 50%        0.042191
# 75%        0.059209
# max        0.155788
# Name: add_prop, dtype: float64

# day_results['res_diff'].value_counts()
# Out[55]:
# same    913
# diff      7
# Name: res_diff, dtype: int64

sns.set_style('whitegrid')

sns.stripplot(data=day_results, x='add_prop', y='res_diff')
sns.histplot(data=day_results, x='add_prop', bins=64)

