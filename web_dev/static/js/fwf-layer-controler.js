var ffmc_topo_file = 'data/ffmc-2020011100.json';
var geo_json_ffmc = L.layerGroup()
var dmc_topo_file = 'data/dmc-20200111.json';
var geo_json_dmc = L.layerGroup()
var dc_topo_file = 'data/dc-20200111.json';
var geo_json_dc = L.layerGroup()
var isi_topo_file = 'data/isi-2020011100.json';
var geo_json_isi = L.layerGroup()
var bui_topo_file = 'data/bui-20200111.json';
var geo_json_bui = L.layerGroup()
var fwi_topo_file = 'data/fwi-2020011100.json';
var geo_json_fwi = L.layerGroup()

var wsp_topo_file = 'data/wsp-2020011100.json';
var geo_json_wsp = L.layerGroup()

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
layerGroup = L.layerGroup();
layerGroup.addLayer(ffmcTimeLayer);
opacitySliderGroup = new L.Control.opacitySliderGroup().addTo(map);
opacitySliderGroup.setOpacityLayerGroup(layerGroup);


