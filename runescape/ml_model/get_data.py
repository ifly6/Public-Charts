#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 02:48:07 2020

@author: ifly6
"""
import requests
import datetime

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

import matplotlib.pyplot as plt

hannah = abs(int(str(hash('hannah'))[0:6]))

cti_url = 'https://runescape.wiki/w/RuneScape:Grand_Exchange_Market_Watch/Common_Trade_Index'
url = 'https://runescape.fandom.com/wiki/Module:Exchange/{}/Data'

item_list = [
    'Coal',
    'Steel bar',
    'Gold ore',
    'Nature rune',
    'Death rune',
    'Fire rune',
    'Blood rune',
    'Pure essence',
    'Yew logs',
    'Magic logs',
    'Cowhide',
    'Raw lobster',
    'Raw monkfish',
    'Flax',
    'Soft clay',
    'Limpwurt root',
    'Snape grass',
    'Clean snapdragon',
    'Clean kwuarm',
    'Red chinchompa',
    'Oak plank',
    'Shark',
    'Green dragonhide',
    'Dragon bones',
    'Frost dragon bones',
    'Reinforced dragon bones',
    'Mahogany plank',
    'Cannonball',
    'Rune arrow',
]
item_list = [s.replace(' ', '_') for s in item_list]

df_list = []
for item in item_list:
    soup = BeautifulSoup(requests.get(url.format(item)).content, 'lxml')
    item_data = soup.select('pre')[0].text.replace('return', '') \
        .replace('{', '') \
        .replace('}', '') \
        .replace(',', '') \
        .replace('\'', '') \
        .split('\n')
    item_data = [s.strip() for s in item_data if s.strip() != '']

    series = pd.Series(item_data).str.split(':', expand=True)
    series.columns = ['unix_ts', 'price', 'volume'] if series.columns.size == 3 \
        else ['unix_ts', 'price']

    series['price'] = pd.to_numeric(series['price'])

    series['dt'] = pd.to_datetime(series['unix_ts'], unit='s')
    series.drop_duplicates(keep='last', subset=['dt'], inplace=True)

    df_list.append(series.set_index('dt').rename(columns={'price': item})[item])
    print(f'got data for {item}')

ge_data = pd.concat(df_list, axis='columns')
ge_data = ge_data \
    .reindex(pd.date_range(start=ge_data.index.min(), end=ge_data.index.max(), freq='D'))

ge_data.reset_index(inplace=True)
ge_data.rename(columns={'index': 'ds'}, inplace=True)

ge_data.to_csv('ge_data.csv.gz', index=True)


################
#              #
# scikit learn #
#              #
################
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor

predict_date = pd.Timestamp(datetime.date.today()) - pd.offsets.Day(1)
predict_date = pd.Timestamp('2020-02-15')

predict_var = 'Nature rune'
predict_var = predict_var.replace(' ', '_')

predict_ahead = 7
training_period = 90

actual = ge_data[ge_data['ds'] > predict_date].copy()

# training_data = ge_data[
#     (ge_data['ds'] <= predict_date) &
#     (ge_data['ds'] > predict_date - pd.offsets.Day(365))
# ].copy()

shifted_df = ge_data.copy()
for i in [c for c in shifted_df.columns if not (c == predict_var or c == 'ds')]:
    shifted_df[i] = shifted_df[i].shift(predict_ahead)

training_data = shifted_df[
    (shifted_df['ds'] < predict_date) &
    (shifted_df['ds'] >= predict_date - pd.offsets.Day(round(training_period)))
].copy().dropna()

other_columns = [c for c in training_data.columns if not (c == predict_var or c == 'ds')]
X_train, X_test, y_train, y_test = train_test_split(
    training_data[other_columns], training_data[predict_var],
    train_size=0.8, test_size=0.2, random_state=hannah)

ilen = len(item_list)
model = MLPRegressor(max_iter=100000, random_state=hannah, tol=1e-30,
                     hidden_layer_sizes=(ilen, ilen, ilen, ilen, ilen * 6))
model.fit(X_train, y_train)
y_hat = model.predict(X_test)

# first check?
# f, a = plt.subplots(figsize=(11, 8.5))
# a.plot(np.linspace(y_test.min(), y_test.max(), 50),
#        np.linspace(y_test.min(), y_test.max(), 50), 'black')
# a.scatter(y_test, y_hat)
# a.set_xlabel('test_y')
# a.set_ylabel('predicted_y')

# out of sample
oos_df = shifted_df[
    (shifted_df['ds'] > predict_date - pd.offsets.Day(training_period)) &
    (shifted_df['ds'] <= predict_date + pd.offsets.Day(predict_ahead))
].copy().dropna()

oos_y = oos_df[predict_var] #.shift(predict_ahead)
oos_yhat = model.predict(oos_df[other_columns])

f, oos = plt.subplots(figsize=(11, 8.5))

oos.plot(oos_y.reset_index(drop=True), label='historical')
oos.plot(oos_yhat, label='predicted')

oos.set_xlabel('time')
oos.set_ylabel('price')
oos.set_title(predict_var)

oos.legend(frameon=False)

# model.score(oos_df[other_columns], oos_y)
print('{} iterations, {} layers'.format(model.n_iter_, model.n_layers_))

###############
#             #
# try prophet #
#             #
###############
import fbprophet

m = fbprophet.Prophet(changepoint_range=0.9, changepoint_prior_scale=0.5)
m.fit(training_data.rename(columns={predict_var: 'y'}))

future = m.make_future_dataframe(periods=predict_ahead)

forecast = m.predict(future)
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

rel_actual = actual[actual['ds'] < future['ds'].max()]

fig = m.plot(forecast)
plt.plot(rel_actual['ds'], rel_actual[predict_var], color='g', label='actual')
plt.title(predict_var.replace('_', ' '))
