#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd

fips = pd.read_csv('https://gist.github.com/dantonnoriega/bf1acd2290e15b91e6710b6fd3be0a53/'
                   'raw/11d15233327c8080c9646c7e1f23052659db251d/us-state-ansi-fips.csv') \
    .rename(columns=str.strip) \
    .rename(columns={
        'stname': 'name',
        'st': 'fips',
        'stusps': 'stalp'
    })
fips['name_proc'] = fips['name'].str.strip().str.lower()

covid_raw = pd.read_csv('http://hgis.uw.edu/virus/assets/virus.csv')
covid_df = covid_raw.copy().set_index('datetime').unstack().reset_index() \
    .rename(columns={'level_0': 'geography', 'datetime': 'dt', 0: 'data'})

covid_us = covid_df[covid_df['geography'].isin(fips['name_proc'])].copy() \
    .rename(columns={'geography': 'state'})
covid_us['fips'] = covid_us['state'].map(fips.set_index('name_proc')['fips'])

new_columns = ['confirmed', 'suspected', 'cured', 'dead']
covid_us[new_columns] = covid_us['data'].str.split('-', expand=True)
for c in new_columns:
    covid_us[c] = pd.to_numeric(covid_us[c], errors='coerce')

covid_us.sort_values(by=['fips', 'dt'], inplace=True)
covid_us.to_csv('uwhgis_covid.csv', index=False)
