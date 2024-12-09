# -*- coding: utf-8 -*-
'''
Created on Thu Mar 16 00:06:03 2023

@author: ifly6
'''
import re
import glob
import os
from os.path import basename, expanduser, join

import contextily as cx
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import xyzservices.providers as xyz
from shapely.geometry import Point, LineString
from shapely.ops import unary_union
from xyzservices import TileProvider

plt.rcParams['font.family'] = 'Arial'


def zoom(ax, xf, yf):
    x1, x2 = ax.get_xlim()
    y1, y2 = ax.get_ylim()
    ax.set_xlim(x1 - (x2 - x1) * xf, x2 + (x2 - x1) * xf)
    ax.set_ylim(y1 - (y2 - y1) * yf, y2 + (y2 - y1) * yf)


CRS = 'ESRI:102031'

# load shape files
geodf = gpd.read_file('roman ager 241 bc smoothed.shp').to_crs(CRS)

# split the data
geodf_fullcit = geodf[geodf['status'].eq('full')]
geodf_halfcit = geodf[geodf['status'].eq('half')]

# join all the areas so there are no overlapping regions
fullcit_area = gpd.GeoSeries(unary_union([
    i.buffer(0) for i in geodf_fullcit['geometry'].values]), crs=CRS)
halfcit_area = gpd.GeoSeries(unary_union([
    i.buffer(0) for i in geodf_halfcit['geometry'].values]), crs=CRS)

# load urban footprints
cities = gpd.read_file(
    join('..', 'shape files, awmc', 'Cultural Shapefiles Apr 2024',
         'urban footprints', 'urban_footprint.shp'), crs='EPSG:4326').to_crs(CRS)
cities.geometry = cities.geometry.centroid  # map to points

# load pleiades places
places = gpd.read_file(
    join(
        '..', 'shape files, awmc', 'Cultural Shapefiles Apr 2024',
        'pleiades places', 'pleiades_places.shp')).to_crs(CRS)
my_places = places.loc[places['TITLE'].str.lower().isin(
    i.lower() for i in '''
Roma
Paestum
#Brundisium
Brundisium/Brentesion
#Regium
Rhegion/Regium
#Croton
Croto(n)
#Heraclea
Lanuvium
Camerinum
Armiminum
Arretium
Volterrae
Velathri/Volaterrae
#Paestum
#Poseidonia/Paestum
Pisae
Salernum
Volsinii
Syracusae/Syrakousai'''.split('\n') if not i.startswith('#') and len(i) > 0
), ['TITLE', 'geometry']]
my_places['name'] = my_places['TITLE'].replace({
    'Croto(n)': 'Croton', 'Rhegion/Regium': 'Regium',
    'Poseidonia/Paestum': 'Paestum', 'Velathri/Volaterrae': 'Volaterrae',
    'Brundisium/Brentesion': 'Brundisium', 'Syracusae/Syrakousai': 'Syracusae'
})

# produce the final list of cities to plot
plotted_cities = my_places
plotted_cities['marker'] = 'o'
plotted_cities['loc'] = 'br'

# adjust to-be-plotted label positions
plotted_cities.loc[lambda d: d['name'] == 'Falerii Veteres', 'loc'] = 'tl'
plotted_cities.loc[lambda d: d['name'] == 'Ostia', 'loc'] = 'bl'
plotted_cities.loc[lambda d: d['name'] == 'Praeneste', 'loc'] = 'tr'
plotted_cities.loc[lambda d: d['name'] == 'Arretium', 'loc'] = 'tr'
plotted_cities.loc[lambda d: d['name'] == 'Pisae', 'loc'] = 'bl'
plotted_cities.loc[lambda d: d['name'] == 'Roma', 'loc'] = 'tl'
plotted_cities.loc[lambda d: d['name'] == 'Camerinum', 'loc'] = 'tr'
plotted_cities.loc[lambda d: d['name'] == 'Salernum', 'loc'] = 'bl'
plotted_cities.loc[lambda d: d['name'] == 'Paestum', 'loc'] = 'bl'
plotted_cities.loc[lambda d: d['name'] == 'Lanuvium', 'loc'] = 'bl'
plotted_cities.loc[lambda d: d['name'] == 'Volaterrae', 'loc'] = 'bl'

# ----------------------------------------------------------------------------
# do the plot

f, ax = plt.subplots(figsize=(20, 20))
fullcit_area.plot(ax=ax, edgecolor='black',
                  color='maroon', linewidth=1, alpha=0.4)
halfcit_area.plot(ax=ax, edgecolor='black',
                  color='yellow', linewidth=1, alpha=0.6)

# plot each city
for i, r in plotted_cities.iterrows():
    if r['name'] != 'Roma':
        continue

    x, y = tuple(r.geometry.coords)[0]
    ax.plot([x], [y], marker=r['marker'], color='black',
            markersize=10 if r['marker'] == '*' else 5)

    vert = -4 + (-8 if r['loc'].startswith('b') else 6)
    hori = 4 if r['loc'].endswith('r') else -3
    text_loc = (hori, vert)

    ax.annotate(
        r['name'], fontsize=20,
        xy=(x, y), xytext=text_loc, textcoords='offset points',
        ha='right' if r['loc'].endswith('l') else 'left')

# add lat and long lines; retain existing plot
xlim, ylim = ax.get_xlim(), ax.get_ylim()
lines = gpd.GeoSeries(data=[
    LineString([Point(longitude, latitude) for longitude
                in range(-20, 60 + 1)])
    for latitude in range(25, 55 + 1, 2)
] + [
    LineString([Point(longitude, latitude) for latitude
                in range(22, 55 + 1)])
    for longitude in range(-20, 60 + 1, 2)
], crs='EPSG:4326').to_crs(CRS)
lines.plot(ax=ax, color='black', linewidth=1, alpha=0.4)
ax.set(xlim=xlim, ylim=ylim)
zoom(ax, -0.1, -0.1)

# add a base map
print('getting base map')
tile_provider = TileProvider({
    'url': 'http://cawm.lib.uiowa.edu/tiles/{z}/{x}/{y}.png',
    'name': '',
    'attribution': '',
    'cross_origin': 'Anonymous'}
)
cx.add_basemap(
    ax, crs=geodf.crs.to_string(),
    # source=cx.providers.Stamen.TerrainBackground,
    # source=cx.providers.Esri.WorldPhysical,
    source=tile_provider,
    attribution=False,
    zoom=10  # render on 10 or 11, draft on 6
)
print('base map retrieved')

ax.margins(0)
ax.set_axis_off()

# save the figure
os.makedirs('charts', exist_ok=True)
f.savefig(
    'charts/roman republic 241bc zoomed.svg', bbox_inches='tight', pad_inches=0,
    transparent=True)
