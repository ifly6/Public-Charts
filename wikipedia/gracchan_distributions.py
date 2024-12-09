# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 02:44:21 2023
@author: ifly6
"""
from os.path import expanduser

import numpy as np
import geopandas as gpd

import matplotlib.pyplot as plt
import contextily as cx
from shapely.geometry import Point, LineString
from xyzservices import TileProvider

CRS = 'ESRI:102031'
# CRS = 'EPSG:3857'


def get_coordinates(point):
    t = np.array(point.coords)[0]
    assert len(t) == 2
    return t[0], t[1]


gracch_cities = gpd.read_file(
    'shape files/gracchan distributions/gracchan cities.shp').to_crs(CRS)
gracch_cities.rename(columns={'city': 'name'}, inplace=True)
gracch_cities['marker'] = 'o'
gracch_cities['loc'] = 'tr'

gracch_cities.loc[gracch_cities['name'] == 'Napoli', 'loc'] = 'br'
gracch_cities.loc[gracch_cities['name'] == 'Paestum', 'loc'] = 'bl'
gracch_cities.loc[gracch_cities['name'] == 'Beneventum', 'loc'] = 'br'

gracch_distri = gpd.read_file(
    'shape files/gracchan distributions/gracchan distributions.shp').to_crs(CRS)
gracch_distri['colour'] = gracch_distri['likelihood'].replace(
    {'hatch': 'maroon',
     'probable': 'goldenrod'})

f, ax = plt.subplots(figsize=np.array([3, 2]) * 5)

gracch_distri.plot(edgecolor='black', linewidth=1, ax=ax,
                   alpha=0.5, color=gracch_distri['colour'])

for i, r in gracch_cities.iterrows():
    x, y = get_coordinates(r['geometry'])
    ax.plot([x], [y], marker=r['marker'], color='black',
            markersize=10 if r['marker'] == '*' else 5)

    vert = -4 + -12 if r['loc'].startswith('b') else 4
    hori = 5 if r['loc'].endswith('r') else -4
    text_loc = (hori, vert)

    ax.annotate(
        r['name'], fontsize=14,
        xy=(x, y), xytext=text_loc, textcoords='offset points',
        ha='right' if r['loc'].endswith('l') else 'left')

# plot latitude and longitude lines
xlim, ylim = ax.get_xlim(), ax.get_ylim()
lines = gpd.GeoSeries(data=[
    LineString([Point(longitude, latitude) for longitude
                in range(-15, 60 + 1)])
    for latitude in range(25, 55 + 1, 1)
] + [
    LineString([Point(longitude, latitude) for latitude
                in range(22, 55 + 1)])
    for longitude in range(-15, 60 + 1, 1)
], crs='EPSG:4326').to_crs(CRS)
lines.plot(ax=ax, color='black', linewidth=1, alpha=0.4)
ax.set(xlim=xlim, ylim=ylim)

tile_provider = TileProvider({
    'url': 'http://cawm.lib.uiowa.edu/tiles/{z}/{x}/{y}.png',
    'name': '',
    'attribution': '',
    'cross_origin': 'Anonymous'})
cx.add_basemap(
    ax, crs=gracch_distri.crs.to_string(), source=tile_provider,
    attribution=False, zoom=9)
ax.margins(0)
ax.set_axis_off()

f.savefig(
    'charts/roselaar_gracchan_land.svg', bbox_inches='tight', pad_inches=0,
    transparent=True)
