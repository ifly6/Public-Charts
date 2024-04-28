# -*- coding: utf-8 -*-
"""
Created on Sun Feb 19 01:47:16 2023
@author: Imperium Anglorum
"""
from os.path import join

import pandas as pd
import seaborn as sns

import statsmodels.formula.api as smf
from linearmodels.panel import PanelOLS

# -------------------------------------------------------------------------------------------------
# load data

DATA_PATH = join('..', 'wa_3day_voting', 'data')

all_votes = pd.read_csv(
    join(DATA_PATH, 'all_vote_data_20230216.csv.xz'), parse_dates=['time'])
all_votes['time'] = all_votes['time'].dt.round('s')

all_rsltn = pd.read_csv(
    join(DATA_PATH, 'all_resolution_data_20230216.csv.xz'), parse_dates=['resolution_date'])

vote_data = all_votes \
    .merge(all_rsltn, left_on='resolution_id', right_on='id', how='left', validate='m:1') \
    .drop(columns=['resolution_id'])

# -------------------------------------------------------------------------------------------------
# generate columns

# year = self-explanatory
# repeal = repeal ? 1 : 0

vote_data['year'] = vote_data['time'].dt.year
vote_data['repeal'] = vote_data['title'].str.match('^[Rr]epeal').astype(int)

# cvf_prop = current vote total, FOR, proportion
# pvf_prop = prior vote total, FOR, proportion
# _hr = hours since the last observation
# _fw = for wins
# nf_diff = nations for difference
# na_diff = nations against difference
# mnf_prop = marginal nations for proportion, per hour
# cml_winp = cumulative win proportion (proportion of prior votes in resolution that were winning)

vote_data['cvf_prop'] = vote_data.eval('votes_for / (votes_for + votes_against)')
vote_data['pvf_prop'] = vote_data.groupby('id')['cvf_prop'].shift()

vote_data['_fw'] = vote_data.eval('votes_for > votes_against').astype(int)

vote_data['_hr'] = vote_data.groupby('id')['time'].diff().dt.seconds / (60 * 60)
vote_data['nf_diff'] = vote_data.groupby('id')['nations_for'].diff() / vote_data['_hr']
vote_data['na_diff'] = vote_data.groupby('id')['nations_against'].diff() / vote_data['_hr']


def clip_series(s, lower, upper):
    return s.clip(lower=s.quantile(lower), upper=s.quantile(upper))


vote_data['mnf_prop'] = clip_series(vote_data.eval('nf_diff / (nf_diff + na_diff)'), 0.01, 0.99)
vote_data['cml_winp'] = vote_data.groupby('id')['_fw'].cumsum() \
    / (vote_data.groupby('id')['_fw'].cumcount() + 1)

vote_data['SC'] = vote_data['chamber'].eq('SC').astype(int)

vote_data.dropna(subset=['pvf_prop', 'mnf_prop', 'cml_winp', 'chamber'], inplace=True)
vote_data.set_index(['id', 'time'], inplace=True)

# -------------------------------------------------------------------------------------------------
# histogram of difference between the nation-level marginal prop and the then-observed prop
# done for Magecastle

sns.histplot(
    data=(vote_data['mnf_prop'] - vote_data['cvf_prop']).rename(
        'Difference between marginal vote proportion by nation and\n'
        ' the then-observed vote proportion'),
    bins=50)

# -------------------------------------------------------------------------------------------------
# regressions

# nation-level marginal prop ~  \
#     total prop as observed + prop where for was winning at observation + campaign coef? \
#     + chamber + fe by proposal

naive_fit = smf.ols(
    'mnf_prop ~ pvf_prop:C(year) + cml_winp + SC + repeal',
    data=vote_data).fit(cov_type='HC3')
print(naive_fit.summary2())
"""
The naive fit, without proposal level fixed effects, will bias towards showing an effect from the
PVF_PROP variable. This is because the underlying like or dislike of the proposal by the players
as a whole will be absorbed into the PVF_PROP variable.

The parameter for PVF_PROP is approximately 0.736 ... but that is because the two are inherently
correlated. The extent to which the LEMMING EFFECT itself impacts votes has to be measured
independently of whether players like the proposal or not.
"""

fe_fit0 = PanelOLS.from_formula(
    'mnf_prop ~ pvf_prop + cml_winp + EntityEffects',
    data=vote_data).fit(cov_type='robust')
print('\n'.join(s.rstrip() for s in str(fe_fit0.summary).split('\n')))

fe_fit1 = PanelOLS.from_formula(
    'mnf_prop ~ pvf_prop:C(year) + cml_winp + EntityEffects',
    data=vote_data).fit(cov_type='robust')
print('\n'.join(s.rstrip() for s in str(fe_fit1.summary).split('\n')))
# SC and repeal vars are absorbed by proposal fixed effects
"""
                          PanelOLS Estimation Summary
================================================================================
Dep. Variable:               mnf_prop   R-squared:                        0.0916
Estimator:                   PanelOLS   R-squared (Between):              0.8377
No. Observations:               70098   R-squared (Within):               0.0916
Date:                Sun, Feb 19 2023   R-squared (Overall):              0.8264
Time:                        04:36:58   Log-likelihood                 7.696e+04
Cov. Estimator:                Robust
                                        F-statistic:                      3497.8
Entities:                         742   P-value                           0.0000
Avg Obs:                       94.472   Distribution:                 F(2,69354)
Min Obs:                       30.000
Max Obs:                       151.00   F-statistic (robust):             1561.3
                                        P-value                           0.0000
Time periods:                   70098   Distribution:                 F(2,69354)
Avg Obs:                       1.0000
Min Obs:                       1.0000
Max Obs:                       1.0000

                             Parameter Estimates
==============================================================================
            Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
------------------------------------------------------------------------------
cml_winp       0.1181     0.0058     20.495     0.0000      0.1068      0.1294
pvf_prop       0.4819     0.0133     36.353     0.0000      0.4559      0.5078
==============================================================================

F-test for Poolability: 57.918
P-value: 0.0000
Distribution: F(741,69354)

Included effects: Entity
"""
"""
                          PanelOLS Estimation Summary
================================================================================
Dep. Variable:               mnf_prop   R-squared:                        0.0991
Estimator:                   PanelOLS   R-squared (Between):              0.8062
No. Observations:               70098   R-squared (Within):               0.0991
Date:                Sun, Feb 19 2023   R-squared (Overall):              0.7956
Time:                        04:27:09   Log-likelihood                 7.725e+04
Cov. Estimator:             Clustered
                                        F-statistic:                      847.34
Entities:                         742   P-value                           0.0000
Avg Obs:                       94.472   Distribution:                 F(9,69347)
Min Obs:                       30.000
Max Obs:                       151.00   F-statistic (robust):             56.796
                                        P-value                           0.0000
Time periods:                   70098   Distribution:                 F(9,69347)
Avg Obs:                       1.0000
Min Obs:                       1.0000
Max Obs:                       1.0000

                                Parameter Estimates
===================================================================================
                          Parameter  Std. Err.  T-stat  P-value  Lower CI  Upper CI
-----------------------------------------------------------------------------------
cml_winp                     0.1225     0.0058  21.046   0.0000    0.1111    0.1339
C(year)[T.2016]:pvf_prop     1.1060     0.0616  17.946   0.0000    0.9852    1.2268 -- dubious
C(year)[T.2017]:pvf_prop     0.3931     0.0202  19.506   0.0000    0.3536    0.4326
C(year)[T.2018]:pvf_prop     0.4840     0.0193  25.030   0.0000    0.4461    0.5219
C(year)[T.2019]:pvf_prop     0.3928     0.0210  18.699   0.0000    0.3516    0.4339
C(year)[T.2020]:pvf_prop     0.4131     0.0206  20.030   0.0000    0.3727    0.4535
C(year)[T.2021]:pvf_prop     0.3696     0.0182  20.325   0.0000    0.3339    0.4052
C(year)[T.2022]:pvf_prop     0.5306     0.0240  22.151   0.0000    0.4837    0.5776
C(year)[T.2023]:pvf_prop     0.5423     0.0249  21.748   0.0000    0.4935    0.5912
===================================================================================

F-test for Poolability: 58.781
P-value: 0.0000
Distribution: F(741,69347)

Included effects: Entity
"""
