var geo_json_ffmc = L.layerGroup()
var geo_json_dmc = L.layerGroup()
var geo_json_dc = L.layerGroup()
var geo_json_isi = L.layerGroup()
var geo_json_bui = L.layerGroup()
var geo_json_fwi = L.layerGroup()
var geo_json_wsp = L.layerGroup()
var geo_json_temp = L.layerGroup()
var geo_json_rh = L.layerGroup()
var geo_json_qpf = L.layerGroup()

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

var dcTimeLayer = L.timeDimension.layer.layerGroup(geo_json_dc, {
    getUrlFunction: getDailyForecast,
    getFileDir: dc_topo_file,
    getVar: 'DC'

});


var isiTimeLayer = L.timeDimension.layer.layerGroup(geo_json_isi, {
    getUrlFunction: getHourlyForecast,
    getFileDir: isi_topo_file,
    getVar: 'ISI'

});


var buiTimeLayer = L.timeDimension.layer.layerGroup(geo_json_bui, {
    getUrlFunction: getDailyForecast,
    getFileDir: bui_topo_file,
    getVar: 'BUI'
});

var fwiTimeLayer = L.timeDimension.layer.layerGroup(geo_json_fwi, {
    getUrlFunction: getHourlyForecast,
    getFileDir: fwi_topo_file,
    getVar: 'FWI'

});

var wspTimeLayer = L.timeDimension.layer.layerGroup(geo_json_wsp, {
    getUrlFunction: getHourlyForecast,
    getFileDir: wsp_topo_file,
    getVar: 'wsp'

});

var tempTimeLayer = L.timeDimension.layer.layerGroup(geo_json_temp, {
    getUrlFunction: getHourlyForecast,
    getFileDir: temp_topo_file,
    getVar: 'temp'

});

var rhTimeLayer = L.timeDimension.layer.layerGroup(geo_json_rh, {
    getUrlFunction: getHourlyForecast,
    getFileDir: rh_topo_file,
    getVar: 'rh'

});

var qpfTimeLayer = L.timeDimension.layer.layerGroup(geo_json_qpf, {
    getUrlFunction: getHourlyForecast,
    getFileDir: qpf_topo_file,
    getVar: 'qpf'

});


var baseLayers = {
    "Topography"       : gl,
};

var groupedOverlays = {   
    "Fire Weather Forecast" :  {
        "FFMC" : ffmcTimeLayer,
        "DMC"  : dmcTimeLayer,
        "DC"   : dcTimeLayer,
        "ISI"  : isiTimeLayer,
        "BUI"  : buiTimeLayer,
        "FWI"  : fwiTimeLayer,
        "Wind Speed"  : wspTimeLayer,
        "Temperature 2m"  : tempTimeLayer,
        "Relative Humidity 2m"  : rhTimeLayer,
        "Total Accumulated Precipitation"  : qpfTimeLayer,



    },
};

var groupedOptions = {
    exclusiveGroups: ["Fire Weather Forecast"],

};
L.control.groupedLayers(baseLayers, groupedOverlays, groupedOptions).addTo(map);



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
// layerGroup = L.layerGroup();
// layerGroup.addLayer(ffmcTimeLayer);
// opacitySliderGroup = new L.Control.opacitySliderGroup().addTo(map);
// opacitySliderGroup.setOpacityLayerGroup(layerGroup);


