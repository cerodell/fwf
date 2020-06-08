import json

d = {"World Imagery":{ "tiles": 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                                "attrs": 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'},
              "NatGeo World Map":{ "tiles": 'https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}',
                                "attrs": 'Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC'},                 
              "Light Gray Base":{ "tiles": 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
                                "attrs": 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'},                  
              "Carto Basemap Light":{ "tiles": 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
                                "attrs": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'},                  
              "Carto Basemap Dark":{ "tiles": 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
                                "attrs": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'},                   
                                
                                }





colors = ["#004ddb", "#0057c8", "#0162b4", "#016ca0", "#01778d", "#028179", "#028c65", "#029651", "#19a045", "#37a93a", "#55b22f", "#73bb25", "#91c51a", "#afce10", "#ccd705", "#d9d200", "#d4c000", "#cfae00", "#ca9c00", "#c58a00", "#c07801", "#bb6601", "#b75501", "#b64902", "#b43d03", "#b33105", "#b22406", "#b01807", "#af0c08", "#ae0009"]

with open("config.json","w") as f:
    json.dump(colors,f)