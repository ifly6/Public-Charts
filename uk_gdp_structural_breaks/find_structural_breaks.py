#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 21:48:55 2023

@author: ifly6
"""
import pandas as pd
import matplotlib.pyplot as plt
import ruptures as rpt

n_bkps = 5  # number of breakpoints; want 5 to find the great depression
data = pd.read_csv('RGDPMPUKA.csv', parse_dates=['DATE'], index_col=0)

# detection
algo = rpt.Dynp(model="l2").fit(data['RGDPMPUKA_PC1'].values)
result = algo.predict(n_bkps=n_bkps)

# display
f, ax = rpt.display(data, result, result, computed_chg_pts_linewidth=1)
ax[0].axes.set_xticklabels([
    int(t.get_text().replace('−', '-')) + data.index.min().year
    for t in ax[0].axes.get_xticklabels()]
)
