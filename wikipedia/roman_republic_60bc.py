# -*- coding: utf-8 -*-
'''
Created on Thu Mar 16 00:06:03 2023

@author: ifly6
'''
import re
import glob
from os.path import expanduser, basename

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

CRS = 'ESRI:102031'

# load shape files
shape_files = glob.glob('shape files/roman republic 60bc territory/*.shp')
geodfs = {basename(f): gpd.read_file(f) for f in shape_files}
geodf = geodfs['roman_empire_bc_60_extent.shp'].to_crs(CRS)
geodf = gpd.GeoSeries(unary_union([
    i.buffer(0) for i in geodf['geometry'].values]), crs=CRS)

tile_provider = TileProvider({
    'url': 'http://cawm.lib.uiowa.edu/tiles/{z}/{x}/{y}.png',
    'name': '',
    'attribution': '',
    'cross_origin': 'Anonymous'}
)

# nb. fig size doesn't matter, projtection takes over
f, ax = plt.subplots(figsize=np.array([16, 10]) * 1.5)  
geodf.plot(ax=ax, edgecolor='black', color='maroon', linewidth=1, alpha=0.4)

xlim, ylim = ax.get_xlim(), ax.get_ylim()
lines = gpd.GeoSeries(data=[
    LineString([Point(longitude, latitude) for longitude
                in range(-20, 60 + 1)])
    for latitude in range(25, 55 + 1, 5)
] + [
    LineString([Point(longitude, latitude) for latitude
                in range(22, 55 + 1)])
    for longitude in range(-20, 60 + 1, 5)
], crs='EPSG:4326').to_crs(CRS)
lines.plot(ax=ax, color='black', linewidth=1, alpha=0.4)

# dynamic limits
# y1, y2 = ylim
# ax.set(xlim=xlim, ylim=(y1 - (y2 - y1) * 0.3, y2 + (y2 - y1) * 0.3))

# just copy the limits from the 44 bc one
xlim = (-1918124.0137884282, 2810924.800805287)
ylim = (-136184.6037888333, 2579666.7038910077)
ax.set(xlim=xlim, ylim=ylim)

cx.add_basemap(
    ax, crs=geodf.crs.to_string(),
    # source=cx.providers.Stamen.TerrainBackground,
    # source=cx.providers.Esri.WorldPhysical,
    source=tile_provider,
    attribution=False,
    zoom=6
)
ax.margins(0)
ax.set_axis_off()

f.savefig(
    'charts/roman republic 60bc.svg', bbox_inches='tight', pad_inches=0,
    transparent=True)
