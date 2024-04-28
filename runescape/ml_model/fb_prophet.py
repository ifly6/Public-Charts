#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 10:21:48 2020

@author: ifly6
"""

raise RuntimeError('facebook prophet is not fit for solution')

###############
#             #
# try prophet #
#             #
###############
import fbprophet
from fbprophet.plot import add_changepoints_to_plot

predict_date = pd.Timestamp(datetime.date.today()) - pd.offsets.Day(1)
predict_date = pd.Timestamp('2019-03-15')

predict_var = 'Fire rune'
predict_var = predict_var.replace(' ', '_')

actual = ge_data[ge_data['ds'] > predict_date].copy()

shifted_df = ge_data.copy()
shifted_df.rename(columns={predict_var: 'y'}, inplace=True)
for i in [c for c in shifted_df.columns if not (c == 'y' or c == 'ds')]:
    shifted_df[i] = shifted_df[i].shift(7)

training_data = shifted_df[
    (shifted_df['ds'] <= predict_date) &
    (shifted_df['ds'] > predict_date - pd.offsets.Day(365))
].copy()

m = fbprophet.Prophet(changepoint_range=0.9, changepoint_prior_scale=0.5)
for i in [c for c in training_data.columns if not (c == 'y' or c == 'ds')]:
    m.add_regressor(i)

m.fit(training_data)

future = m.make_future_dataframe(periods=90)
for i in [c for c in training_data.columns if not (c == 'y' or c == 'ds')]:
    future[i] = future['ds'].map(shifted_df.set_index('ds')[i])

forecast = m.predict(future)
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

rel_actual = actual[actual['ds'] < future['ds'].max()]

fig = m.plot(forecast)
# a = add_changepoints_to_plot(fig.gca(), m, forecast)
plt.plot(rel_actual['ds'], rel_actual[predict_var], color='g', label='actual')
plt.title(predict_var.replace('_', ' '))
