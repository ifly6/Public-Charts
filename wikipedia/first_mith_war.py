# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 20:56:29 2023
@author: ifly6
"""
from os.path import expanduser
import numpy as np
import pandas as pd
import geopandas as gpd

import matplotlib.pyplot as plt
import contextily as cx

# https://www.naturalearthdata.com/downloads/10m-raster-data/10m-natural-earth-2/
TILES_PATH = expanduser(r"~\Documents\GIS map tiles\NE2_LR_LC_SR_W_DR\NE2_LR_LC_SR_W_DR.tif")


def get_coordinates(point):
    t = np.array(point.coords)[0]
    assert len(t) == 2
    return t[0], t[1]


roman_territory = gpd.read_file(
    "shape files/mithridates/roman territory antebellummith.shp").to_crs(epsg=3857)
roman_territory['colour'] = 'maroon'

roman_clientsta = gpd.read_file(
    "shape files/mithridates/roman client states antebellummith.shp").to_crs(epsg=3857)
roman_clientsta['colour'] = 'salmon'

pontus_etallies = gpd.read_file(
    "shape files/mithridates/pontic territory antebellummithridaticum.shp").to_crs(epsg=3857) \
    .rename(columns=str.lower) \
    .replace('pontus', 'purple')

f, ax = plt.subplots(figsize=np.array([9, 16]) * 2)
roman_territory.plot(edgecolor='black', linewidth=1, ax=ax,
                     alpha=0.5, color=roman_territory['colour'])
roman_clientsta.plot(edgecolor='black', linewidth=1, ax=ax,
                     alpha=0.5, color=roman_clientsta['colour'])
pontus_etallies.plot(edgecolor='black', linewidth=1, ax=ax,
                     alpha=0.5, color=pontus_etallies['colour'])

# for i, r in sw_cities.iterrows():
#     x, y = get_coordinates(r['geometry'])
#     ax.plot([x], [y], marker=r['marker'], color='black',
#             markersize=10 if r['marker'] == '*' else 5)

#     vert = -4 + -12 if r['loc'].startswith('b') else 4
#     hori = 5 if r['loc'].endswith('r') else -4
#     text_loc = (hori, vert)

#     ax.annotate(
#         r['name'], fontsize=14,
#         xy=(x, y), xytext=text_loc, textcoords='offset points',
#         ha='right' if r['loc'].endswith('l') else 'left')

cx.add_basemap(
    ax, crs=roman_territory.crs.to_string(),
    # source=cx.providers.Stamen.TerrainBackground,
    # source=cx.providers.Esri.WorldPhysical,
    source=TILES_PATH,
    reset_extent=False, attribution=False,
    # zoom=9
)
ax.margins(0)

ax.set_axis_off()
ax.set_ylim(*(1e6 * np.array([3.9, 5.5])))
ax.set_xlim(*(1e6 * np.array([2, 5.3])))

f.savefig('ante_first_mith_war__nolabels.svg', bbox_inches='tight', pad_inches=0)
