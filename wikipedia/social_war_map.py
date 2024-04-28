# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 19:05:23 2023

@author: ifly6
"""
import numpy as np
import pandas as pd
import geopandas as gpd

import matplotlib.pyplot as plt
import contextily as cx


def get_coordinates(point):
    t = np.array(point.coords)[0]
    assert len(t) == 2
    return t[0], t[1]


romans = gpd.read_file(r"shape files\social war combatants\roman lands.shp").to_crs(epsg=3857)
romans['colour'] = 'maroon'

rebels0 = gpd.read_file(
    r"shape files\social war combatants\insurgents initial.shp").to_crs(epsg=3857)
rebels0['colour'] = 'darkgreen'

rebels1 = gpd.read_file(
    r"shape files\social war combatants\insurgents later.shp").to_crs(epsg=3857)
rebels1['colour'] = 'lightgreen'

sw_cities = pd.DataFrame([
    {'name': 'Rome', 'x': 12.482778, 'y': 41.893333, 'marker': '*', 'loc': 'bl'},
    {'name': 'Asculum', 'x': 13.575364475637551, 'y': 42.853713817923634, 'loc': 'br'},
    {'name': 'Nola', 'x': 14.52778458612593, 'y': 40.92636713696328},
    # {'name': 'Herculaneum', 'x': 14.348775188641591, 'y': 40.80589217338841},
    {'name': 'Firmum', 'x': 13.719029483982627, 'y': 43.15884994676438},
    {'name': 'Canusium', 'x': 16.065918002764924, 'y': 41.22276782963963},
    {'name': 'Aesernia', 'x': 14.233211459103114, 'y': 41.59610766191039,
     'marker': '*', 'loc': 'tr'},
    # {'name': 'Fucine lake', 'x': 13.539669464241276, 'y': 42.00897153049778, 'loc': 'br'},
    {'name': 'Bovianum', 'y':  41.48313984635348, 'x': 14.473218037560407,
     'loc': 'br', 'marker': '*'},
    {'name': 'Corfinium', 'y': 42.12202382668247, 'x': 13.840385449010704, 'marker': '*'},
    {'name': 'Pompeii', 'y': 40.74893540733072, 'x': 14.499087708982334, 'loc': 'bl'},
    {'name': 'Rhegium', 'y': 38.1098623481343, 'x': 15.647309018382721, 'loc': 'br'}
])
sw_cities['marker'] = sw_cities['marker'].fillna('o')
sw_cities['loc'] = sw_cities['loc'].fillna('tr')

sw_cities = gpd.GeoDataFrame(
    sw_cities, geometry=gpd.points_from_xy(sw_cities['x'], sw_cities['y']),
    crs='epsg:4326').to_crs(epsg=3857)

f, ax = plt.subplots(figsize=np.array([3, 2]) * 9)
romans.plot(edgecolor='black', linewidth=1, ax=ax, alpha=0.5, color=romans['colour'])
rebels0.plot(edgecolor='black', linewidth=1, ax=ax, alpha=0.5, color=rebels0['colour'])
rebels1.plot(edgecolor='black', linewidth=1, ax=ax, alpha=0.5, color=rebels1['colour'])

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

cx.add_basemap(
    ax, crs=romans.crs.to_string(), source=cx.providers.Stamen.TerrainBackground,
    reset_extent=False, attribution=False, zoom=9)
ax.margins(0)

ax.set_axis_off()
# ax.set_xlim(*(1e6 * np.array([1.1, 2.1])))
# ax.set_ylim(*(1e6 * np.array([4.5, 5.5])))

f.savefig('social_war_map.svg', bbox_inches='tight', pad_inches=0)
