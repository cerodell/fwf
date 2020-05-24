import context
# import matplotlib as mpl
import matplotlib.pyplot as plt
import xarray as xr
# import matplotlib.colors
# import cartopy.crs as crs
from pathlib import Path
# import cartopy.feature as cfeature
# from datetime import datetime
# from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER



"######################  Adjust for user/times of interest/plot customization ######################"

ds_file = "/home/crodell/fwf/data/xr/2019-08-05T19_ds_fwf.zarr"


ds_ffmc02 = xr.open_zarr(ds_file)

ds_ffmc02.P.plot()


# "############################# Make Plots #############################"

# for i in range(0,len(ffmc)):  
#     plot_start = datetime.now() # current date and time
#    #i = 2
#     fig = plt.figure(figsize=(16,10))
#     ax2 = plt.axes(projection=cart_proj)

#     # Download and create the states, land, and oceans using cartopy features
#     states = cfeature.NaturalEarthFeature(category='cultural', scale='50m',
#                                           facecolor='none',
#                                           name='admin_1_states_provinces_shp')
#     land = cfeature.NaturalEarthFeature(category='physical', name='land',
#                                         scale='50m',
#                                         facecolor=cfeature.COLORS['land'])
#     ocean = cfeature.NaturalEarthFeature(category='physical', name='ocean',
#                                         scale='50m',
#                                          facecolor=cfeature.COLORS['water'])
#     lake = cfeature.NaturalEarthFeature(category='physical', name='lakes',
#                                          scale='50m',
#                                          facecolor=cfeature.COLORS['water'])

#     ax2.add_feature(states, linewidth=.5, edgecolor="black")
#     #ax2.add_feature(land)
#     ax2.add_feature(ocean)              
#     ax2.add_feature(lake, linewidth=.25, edgecolor="black")

#     #ax2.add_feature(cart.feature.OCEAN, zorder=100, edgecolor='#A9D0F5')
#     #ax2.add_feature(cart.feature.LAKES, zorder=100, edgecolor='#A9D0F5')
#     ax2.coastlines('50m', linewidth=0.8)


#     colors = ["#0000FF","#00E000","#FFFF00", "#E0A000", "#FF0000"]
#     cmap= matplotlib.colors.ListedColormap(colors)
#     bounds = [0, 74, 84, 88, 91, math.inf]
#     norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

#     plt.contourf(to_np(lons), to_np(lats),ffmc[i], extend = 'both',
#                  transform=crs.PlateCarree(), norm = norm, cmap=cmap)

            
#     #    plt.tight_layout()
#     #plt.colorbar(ax=ax2, orientation="vertical", pad=.01, shrink=.6)


#     # Add the gridlines
#     #gl = ax2.gridlines(color="black", linestyle="dotted")
#     #gl.xformatter = LONGITUDE_FORMATTER
#     #gl.yformatter = LATITUDE_FORMATTER
#     #gl.xlabel_style = {'size': 15, 'color': 'gray'}

#     #ax2.axis("off")

#     plt.xticks([-1772000,-849900,-1125,831400,1737000,2754000],
#                ('130'u"\u00b0"" W", '120'u"\u00b0"" W", '110'u"\u00b0"" W", '100'u"\u00b0"" W", '90'u"\u00b0"" W", '80'u"\u00b0"" W"))
#     plt.yticks([-4520000,-4143000,-3753000,-3372000,-2991000],
#                ('45'u"\u00b0"" N", '48'u"\u00b0"" N", '51'u"\u00b0"" N", '54'u"\u00b0"" N", '57'u"\u00b0"" N"))

#     #plt.xlim(-753900,108200)
#     #plt.ylim(-4448000,-2989000)

#     plt.title(r"Fine Fuel Moisture Code" + "\n" + "Init: " +  path_str[0][-19:-3] + "Z        --->   Valid: " + path_str[i][-19:-3]+"Z")
#     fig.savefig(save + path_str[i][-19:-6])
#     #    plt.close('all')
#     plt.tight_layout(pad=1.08, h_pad=0.4, w_pad=None, rect=None)

#     print(path_str[i][-19:-6])

#     plot_stop = datetime.now() # current date and time
#     diff = plot_stop - plot_start

#     print(diff)


# plt.close('all')


