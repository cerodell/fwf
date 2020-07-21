var ffmcTimeLayer = L.timeDimension.layer.layerGroup(geo_json_ffmc, {
    getUrlFunction: getHourlyForecast,
    getFileDir: ffmc_topo_file,
    getVar: 'FFMC'

});
ffmcTimeLayer.addTo(map);


var dmcTimeLayer = L.timeDimension.layer.layerGroup(geo_json_dmc, {
    getUrlFunction: getDailyForecast,
    getFileDir: dmc_topo_file,
    getVar: 'DMC'

});
dmcTimeLayer.addTo(map);


var dcTimeLayer = L.timeDimension.layer.layerGroup(geo_json_dc, {
    getUrlFunction: getDailyForecast,
    getFileDir: dc_topo_file,
    getVar: 'DC'

});
dcTimeLayer.addTo(map);



var isiTimeLayer = L.timeDimension.layer.layerGroup(geo_json_isi, {
    getUrlFunction: getHourlyForecast,
    getFileDir: isi_topo_file,
    getVar: 'ISI'

});
isiTimeLayer.addTo(map);



var buiTimeLayer = L.timeDimension.layer.layerGroup(geo_json_bui, {
    getUrlFunction: getDailyForecast,
    getFileDir: bui_topo_file,
    getVar: 'BUI'
});
buiTimeLayer.addTo(map);


var fwiTimeLayer = L.timeDimension.layer.layerGroup(geo_json_fwi, {
    getUrlFunction: getHourlyForecast,
    getFileDir: fwi_topo_file,
    getVar: 'FWI'

});
fwiTimeLayer.addTo(map);



var baseLayers = {
    "Carto Light"       : CartoDB_PositronNoLabels,
    "Stamen Toner"      : Stamen_TonerBackground,
    "Esri WorldImagery" : Esri_WorldImagery,
    "Esri WorldTerrain" : Esri_WorldTerrain,
};

var groupedOverlays = {   
    "Forecasts" :  {
        "FFMC" : ffmcTimeLayer,
        "DMC"  : dmcTimeLayer,
        "DC"   : dcTimeLayer,
        "ISI"  : isiTimeLayer,
        "BUI"  : buiTimeLayer,
        "FWI"  : fwiTimeLayer,
    }

};

var groupedOptions = {
    exclusiveGroups: ["Forecasts"],

};
L.control.groupedLayers(baseLayers, groupedOverlays, groupedOptions).addTo(map);

// remove layers and basemaps options 
dmcTimeLayer.remove();
dcTimeLayer.remove();
isiTimeLayer.remove();
buiTimeLayer.remove();
fwiTimeLayer.remove();

Esri_WorldImagery.remove()
Esri_WorldTerrain.remove();


// Move zoom and full screen controls to top-right
map.zoomControl.setPosition('topright');
map.fullscreenControl.setPosition('topright');
// 
// Replace default zoom controls with controls that re-center & reset zoom level
map.zoomControl.remove();
var zoomHome = L.Control.zoomHome({position: 'topright'});
zoomHome.addTo(map);

// Opacity control
// var multiLayers = [ffmcTimeLayer, dmcTimeLayer, dcTimeLayer, isiTimeLayer, buiTimeLayer, fwiTimeLayer],
//     layerGroup = L.layerGroup(multiLayers),
//     opacitySliderGroup = new L.Control.opacitySliderGroup().addTo(map);
// opacitySliderGroup.setOpacityLayerGroup(layerGroup);


