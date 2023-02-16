#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 13:01:03 2023
@author: Imperium Anglorum
"""
import pandas as pd
import sqlite3

PATH = ...  # REDACTED
conn = sqlite3.connect(PATH)

all_votes = pd.read_sql_query(
    '''
    select *
    from eurobackend_wavote;
    ''',
    conn, parse_dates=['time'])

all_resolutions = pd.read_sql_query(
    '''
    select *
    from eurobackend_waresolution;
    ''',
    conn, parse_dates=['resolution_date'])

all_votes.drop(columns=['id'], inplace=True)  # hide implementation detail

all_votes.to_csv('data/all_vote_data_20230216.csv.xz', index=False)
all_resolutions.to_csv('data/all_resolution_data_20230216.csv.xz', index=False)

