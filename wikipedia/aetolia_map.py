# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 20:28:04 2023
@author: ifly6
"""
from os.path import expanduser

import numpy as np
import pandas as pd
import geopandas as gpd

import contextily as cx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

TILES_PATH = expanduser(r"~\Documents\GIS map tiles\NE2_LR_LC_SR_W_DR\NE2_LR_LC_SR_W_DR.tif")

greece_shp = gpd.read_file('shape files/greece regions/GR_bsm_admn_adm0_py_EuroGeoGraphics_2015_pp.shp').to_crs(epsg=3857)
aetolia_shp = gpd.read_file('shape files/aetolia/aetolia trace.shp').to_crs(epsg=3857)

f, ax = plt.subplots(figsize=np.array([3, 2]) * 3)

greece_shp.plot(ax=ax, edgecolor='black', color='grey', alpha=0.4)
aetolia_shp.plot(
    ax=ax, edgecolor='black', color='green', linewidth=1, alpha=0.4)

cx.add_basemap(ax=ax, crs=aetolia_shp.crs.to_string(), source=TILES_PATH, attribution=False, 
               reset_extent=True)

ax.margins(0)
ax.set_axis_off()

ax.legend(
    title='Aetolia in Greece',
    handles=[
        mpatches.Patch(color='green', alpha=0.4, label='Aetolia'),
        mpatches.Patch(color='grey', alpha=0.4, label='Modern Greece')
    ],
    loc='upper right', frameon=True, fancybox=False, framealpha=1, borderpad=1,
    prop={'size': 9})

f.savefig('charts/aetolia in greece.svg', bbox_inches='tight', pad_inches=0)
