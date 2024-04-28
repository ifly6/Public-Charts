# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 02:44:21 2023
@author: ifly6
"""
import numpy as np
import geopandas as gpd

import matplotlib.pyplot as plt
import contextily as cx


def get_coordinates(point):
    t = np.array(point.coords)[0]
    assert len(t) == 2
    return t[0], t[1]


gracch_cities = gpd.read_file(
    r"shape files\gracchan distributions\gracchan cities.shp").to_crs(epsg=3857)
gracch_cities.rename(columns={'city': 'name'}, inplace=True)
gracch_cities['marker'] = 'o'
gracch_cities['loc'] = 'tr'

gracch_cities.loc[gracch_cities['name'] == 'Napoli', 'loc'] = 'bl'
gracch_cities.loc[gracch_cities['name'] == 'Paestum', 'loc'] = 'bl'
gracch_cities.loc[gracch_cities['name'] == 'Beneventum', 'loc'] = 'br'

gracch_distri = gpd.read_file(
    r"shape files\gracchan distributions\gracchan distributions.shp").to_crs(epsg=3857)
gracch_distri['colour'] = gracch_distri['likelihood'].replace(
    {'hatch': 'maroon',
     'probable': 'goldenrod'})

f, ax = plt.subplots(figsize=np.array([3, 2]) * 5)

gracch_distri.plot(edgecolor='black', linewidth=1, ax=ax, alpha=0.5, color=gracch_distri['colour'])

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

cx.add_basemap(
    ax, crs=gracch_distri.crs.to_string(), source=cx.providers.Stamen.TerrainBackground,
    reset_extent=False, attribution=False)
ax.margins(0)
ax.set_axis_off()

f.savefig('roselaar_gracchan_land.svg', bbox_inches='tight', pad_inches=0)
