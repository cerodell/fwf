var baseLayers = {
        "Carto Basemap Light" : tile_layer_Carto_Light,
        "Carto Basemap Dark" : tile_layer_Carto_Dark,
        "Open Street" : tile_layer_openstreetmap,
        "World Imagery" : tile_layer_Esri_World_Image,
        "NatGeo World Map" : tile_layer_Esri_NatGeo,
        "Light Gray Base" : tile_layer_Esri_Light_Grey,
};

var groupedOverlays = {   
    "Forecasts" :  {
        "FFMC" : geo_json_ffmc,
        "DMC"  : geo_json_dmc,
        "DC"   : geo_json_dc,
        "ISI"  : geo_json_isi,
        "BUI"  : geo_json_bui,
        "FWI"  : geo_json_fwi,
    },
};

var groupedOptions = {
    exclusiveGroups: ["Forecasts"],

};

L.control.groupedLayers(baseLayers, groupedOverlays, groupedOptions).addTo(map_fwi);

tile_layer_Carto_Dark.remove();
tile_layer_openstreetmap.remove();
tile_layer_Esri_World_Image.remove();
tile_layer_Esri_NatGeo.remove();
tile_layer_Esri_Light_Grey.remove();


geo_json_dmc.remove();
geo_json_dc.remove();
geo_json_isi.remove();
geo_json_bui.remove();
geo_json_fwi.remove();




var lat_lng_popup = L.popup();
function latLngPop(e) {
    lat_lng_popup
        .setLatLng(e.latlng)
        .setContent("Latitude: " + e.latlng.lat.toFixed(4) +
                    "<br>Longitude: " + e.latlng.lng.toFixed(4))
        .openOn(map_fwi);
    }
map_fwi.on('click', latLngPop);