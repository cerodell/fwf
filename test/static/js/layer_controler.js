
///// THIS IS FOR LOOPING WITH VECTORGRID.SLICER 
var ffmcTimeLayer = L.timeDimension.layer.vectorGrid.slicer(geo_json_ffmc, {
    getUrlFunction: getForecastImageUrl,
    getFileDir: ffmc_topo_file

});
ffmcTimeLayer.addTo(map);



// // // Set current time, format should be "April 15, 2019 9:00 UTC"
// map.timeDimension.setCurrentTime(new Date("June 18, 2020 00:00 UTC").getTime());









var baseLayers = {
        "Carto Basemap Light" : tile_layer_Carto_Light,
        "Carto Basemap Dark" : tile_layer_Carto_Dark,
        "Open Street" : tile_layer_openstreetmap,
        "World Imagery" : tile_layer_Esri_World_Image,
        "NatGeo World Map" : tile_layer_Esri_NatGeo,
        // "Light Gray Base" : tile_layer_Esri_Light_Grey,
};


var groupedOverlays = {   
    "Forecasts" :  {
        "FFMC" : ffmcTimeLayer,
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
L.control.groupedLayers(baseLayers, groupedOverlays, groupedOptions).addTo(map);

geo_json_dmc.remove();
geo_json_dc.remove();
geo_json_isi.remove();
geo_json_bui.remove();
geo_json_fwi.remove();


tile_layer_Carto_Dark.remove();
tile_layer_openstreetmap.remove();
tile_layer_Esri_World_Image.remove();
tile_layer_Esri_NatGeo.remove();







var lat_lng_popup = L.popup();
function latLngPop(e) {
    lat_lng_popup
        .setLatLng(e.latlng)
        .setContent("Latitude: " + e.latlng.lat.toFixed(4) +
                    "<br>Longitude: " + e.latlng.lng.toFixed(4))
        .openOn(map);
    }
map.on('click', latLngPop);


// Move zoom and full screen controls to top-right
map.zoomControl.setPosition('topright');
map.fullscreenControl.setPosition('topright');
// 
// Replace default zoom controls with controls that re-center & reset zoom level
map.zoomControl.remove();
var zoomHome = L.Control.zoomHome({position: 'topright'});
zoomHome.addTo(map);

// // Opacity control
// var multiLayers = [groupedOverlays],
//     layerGroup = L.layerGroup(multiLayers),
//     opacitySliderGroup = new L.Control.opacitySliderGroup().addTo(map);
// opacitySliderGroup.setOpacityLayerGroup(layerGroup);


