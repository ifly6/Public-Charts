#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 21:48:55 2023

@author: ifly6
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ruptures as rpt

# n_bkps = 1  # number of breakpoints; want 5+

# find
data = pd.read_csv('RGDPMPUKA.csv', parse_dates=['DATE'])
data['DATE'] = data['DATE'] - pd.offsets.Day(1)
data.set_index('DATE', inplace=True)

for n_bkps in [1, 3, 5, 7]:

    # detection
    algo = rpt.Dynp(model="l2").fit(data['RGDPMPUKA_PC1'].values)
    result = algo.predict(n_bkps=n_bkps)

    # display
    f, al = rpt.display(data, result, result, computed_chg_pts_linewidth=1,
                        figsize=(10, 5))
    ax = al[0]
    ax.axes.set_xticklabels([
        int(t.get_text().replace('−', '-')) + data.index.min().year
        for t in ax.axes.get_xticklabels()]
    )

    ax.axhline(0, color='black', linewidth='1')

    # add average lines
    for i in range(len(result)):
        left = 0 if i == 0 else result[i - 1]
        right = result[i]
        mean = np.average(data['RGDPMPUKA_PC1'].values[left:right])
        ax.hlines(mean, left, right,
                  color='black', linewidth=1, linestyle='dashed')

    # add in break point labels
    for index, i in enumerate(np.array(result)):
        tb = -1 if index % 2 == 0 else 1
        y = str(i + data.index.min().year)
        t = ax.text(i, 20 * tb, y, va='center', ha='center', fontsize=8)
        t.set_bbox(dict(facecolor='white', alpha=1, edgecolor='black'))

    ax.set_ylim(-22, 22)
    # ax.set_xlim(0, len(data))  # don't use; screws up labels

    ax.set_title(
        f'Structural breaks ({n_bkps} per ruptures) in UK real GDP growth data')
    f.savefig(f'uk gdp growth structural breaks n{n_bkps}.jpg',
              bbox_inches='tight')
