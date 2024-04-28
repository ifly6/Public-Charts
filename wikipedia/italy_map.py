# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 06:42:52 2023
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


# world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
# cities = gpd.read_file(gpd.datasets.get_path('naturalearth_cities'))

# ax = world[world.name == 'Italy'].plot(edgecolor='black', linewidth=1)

df_regions = gpd \
    .read_file('shape files/italian regions/Reg01012023_g_WGS84.shp') \
    .to_crs('epsg:4326')
# ax0 = df_regions.plot(edgecolor='white', linewidth=1, figsize=(14, 14), color='black', alpha=0.25)
# cx.add_basemap(ax0, crs=df_regions.crs.to_string(), source=cx.providers.Stamen.Terrain)
# ax0.set_axis_off()

# df_regions.apply(
#     lambda x: ax.annotate(text=x['DEN_REG'], xy=x.geometry.centroid.coords[0], ha='center'),
#     axis=1)

# it_munis = gpd.read_file('shape files/italian municipalities/Com01012019_WGS84.shp')

sw_roman = gpd.read_file('shape files/social war/roman_land_boundaries.shp').to_crs(epsg=3857)
sw_roman['colour'] = 'firebrick'

sw_regions = df_regions[df_regions['DEN_REG'].isin([
    'Toscana', 'Umbria', 
    'Marche', 'Lazio', 'Abruzzo', 'Molise', 'Campania',
    'Puglia', 'Basilicata', 'Calabria'])].copy()
sw_regions['colour'] = 'green'

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

sw_regions = sw_regions.to_crs(epsg=3857)
sw_cities = gpd.GeoDataFrame(
    sw_cities, geometry=gpd.points_from_xy(sw_cities['x'], sw_cities['y']),
    crs='epsg:4326').to_crs(epsg=3857)

f, ax = plt.subplots(figsize=np.array([3, 2]) * 8)
sw_regions.plot(linewidth=1, ax=ax, alpha=0, color=sw_regions['colour'])
sw_roman.plot(linewidth=0, ax=ax, alpha=0.5, color=sw_roman['colour'])

ax.set_ylim(4.3 * 1e6, 5.75 * 1e6)
cx.add_basemap(
    ax, crs=sw_regions.crs.to_string(), source=cx.providers.Stamen.TerrainBackground,
    reset_extent=False, attribution=False)
ax.margins(0)
ax.set_axis_off()
ax.set_ylim(4.35 * 1e6, 5.75 * 1e6)
# ax.set_title('Roman land in 100 BC', fontsize=24)

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
