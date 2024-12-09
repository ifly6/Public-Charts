# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 19:05:23 2023

@author: ifly6
"""
from os.path import expanduser

import numpy as np
import pandas as pd
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


romans = gpd.read_file(
    'shape files/social war combatants/roman lands.shp').to_crs(CRS)
romans['colour'] = 'maroon'

rebels0 = gpd.read_file(
    'shape files/social war combatants/insurgents initial.shp').to_crs(CRS)
rebels0['colour'] = 'darkgreen'

rebels1 = gpd.read_file(
    'shape files/social war combatants/insurgents later.shp').to_crs(CRS)
rebels1['colour'] = 'lightgreen'

sw_cities = pd.DataFrame([
    {'name': 'Rome', 'x': 12.482778, 'y': 41.893333, 'marker': '*', 'loc': 'bl'},
    {'name': 'Asculum', 'x': 13.575364475637551,
        'y': 42.853713817923634, 'loc': 'br'},
    {'name': 'Nola', 'x': 14.52778458612593, 'y': 40.92636713696328},
    # {'name': 'Herculaneum', 'x': 14.348775188641591, 'y': 40.80589217338841},
    {'name': 'Firmum', 'x': 13.719029483982627, 'y': 43.15884994676438},
    {'name': 'Canusium', 'x': 16.065918002764924, 'y': 41.22276782963963},
    {'name': 'Aesernia', 'x': 14.233211459103114, 'y': 41.59610766191039,
     'marker': '*', 'loc': 'tr'},
    # {'name': 'Fucine lake', 'x': 13.539669464241276, 'y': 42.00897153049778, 'loc': 'br'},
    {'name': 'Bovianum', 'y':  41.48313984635348, 'x': 14.473218037560407,
     'loc': 'br', 'marker': '*'},
    {'name': 'Corfinium', 'y': 42.12202382668247,
        'x': 13.840385449010704, 'marker': '*'},
    {'name': 'Pompeii', 'y': 40.74893540733072,
        'x': 14.499087708982334, 'loc': 'bl'},
    {'name': 'Rhegium', 'y': 38.1098623481343,
        'x': 15.647309018382721, 'loc': 'br'}
])
sw_cities['marker'] = sw_cities['marker'].fillna('o')
sw_cities['loc'] = sw_cities['loc'].fillna('tr')

sw_cities = gpd.GeoDataFrame(
    sw_cities, geometry=gpd.points_from_xy(sw_cities['x'], sw_cities['y']),
    crs='epsg:4326').to_crs(CRS)

f, ax = plt.subplots(figsize=np.array([3, 2]) * 9)
romans.plot(edgecolor='black', linewidth=1, ax=ax,
            alpha=0.5, color=romans['colour'])
rebels0.plot(edgecolor='black', linewidth=1, ax=ax,
             alpha=0.5, color=rebels0['colour'])
rebels1.plot(edgecolor='black', linewidth=1, ax=ax,
             alpha=0.5, color=rebels1['colour'])

for i, r in sw_cities.iterrows():
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

ax.margins(0)
ax.set_axis_off()

x1, x2 = ax.get_xlim()
y1, y2 = ax.get_ylim()
ax.set_xlim(x1 - (x2 - x1) * 0.25, x2 + (x2 - x1) * 0.1)
ax.set_ylim(y1 - (y2 - y1) * 0.25, y2 + (y2 - y1) * 0.1)

# ax.set_xlim(*(1e6 * np.array([1.1, 2.1])))
# ax.set_ylim(*(1e6 * np.array([4.5, 5.5])))

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
    ax, crs=romans.crs.to_string(), source=tile_provider,
    attribution=False)

f.savefig(
    'charts/social_war_map.svg', bbox_inches='tight', pad_inches=0,
    transparent=True)
