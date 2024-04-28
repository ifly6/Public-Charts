# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 00:06:03 2023

@author: ifly6
"""
import re
import glob
from os.path import expanduser, basename

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import contextily as cx

# https://www.naturalearthdata.com/downloads/10m-raster-data/10m-natural-earth-2/
TILES_PATH = expanduser(r"~\Documents\GIS map tiles\NE2_LR_LC_SR_W_DR\NE2_LR_LC_SR_W_DR.tif")

# load shape files
shape_files = glob.glob('shape files/roman republic/*.shp')
geodfs = {basename(f): gpd.read_file(f).to_crs(epsg=3857) for f in shape_files}

territories = {
    k: v.assign(source=k) for k, v in geodfs.items()
    if re.match('roman republic \d{2}bc\.shp', k)}
territories = gpd.GeoDataFrame(
    pd.concat([gdf.dissolve() for _, gdf in territories.items()]), geometry='geometry'
).reset_index(drop=True)
territories['year'] = territories['source'].str.extract(r'(\d{2})(?=bc)', expand=False) \
    .astype(int)
territories.sort_values(by='year', ascending=False, inplace=True)

differences = territories['geometry'].difference(territories['geometry'].shift(1))
differences = gpd.GeoDataFrame(
    geometry=gpd.GeoSeries(np.where(differences.isnull(), territories['geometry'], differences),
                           name='geometry'),
    crs='epsg:3857')
differences['colour'] = ['maroon', 'orange', 'gold']

f, ax = plt.subplots(figsize=np.array([16, 10]) * 1.5)
differences.plot(ax=ax, edgecolor='black', color=differences['colour'], linewidth=1, alpha=0.4)
geodfs['roman republic clients 44bc.shp'].plot(
    ax=ax, edgecolor='black', color='none', hatch='//', linewidth=1, alpha=0.6)

cities = geodfs['roman republic 44bc cities.shp']
cities.plot(ax=ax, marker='o', color='white', edgecolor='black')
cities.apply(lambda x: ax.annotate(text=x['name'], xy=np.array(x.geometry.coords)[0],
                                   ha='left', fontsize=16),
             axis=1)

cx.add_basemap(
    ax, crs=differences.crs.to_string(),
    # source=cx.providers.Stamen.TerrainBackground,
    # source=cx.providers.Esri.WorldPhysical,
    source=TILES_PATH,
    attribution=False,
    # zoom=9
)
ax.margins(0)
ax.set_axis_off()

ax.legend(
    handles=[
        mpatches.Patch(color='maroon', alpha=0.5, label='Roman territory in 63 BC'),
        mpatches.Patch(color='orange', alpha=0.5, label='Roman territory in 58 BC'),
        mpatches.Patch(color='gold', alpha=0.5, label='Roman territory in 44 BC'),
        mpatches.Patch(edgecolor='black', facecolor='#DCDCDC', hatch='//', 
                       linewidth=1, alpha=0.6,
                       label='Roman client states'),
    ],
    loc='lower left', frameon=True, fancybox=False, framealpha=1, borderpad=1,
    prop={'size': 20})

f.savefig(
    'charts/roman republic expansion to 44bc.svg', bbox_inches='tight', pad_inches=0)
