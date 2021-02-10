var geo_json_ffmc = L.layerGroup();
var geo_json_dmc = L.layerGroup();
var geo_json_dc = L.layerGroup();
var geo_json_isi = L.layerGroup();
var geo_json_bui = L.layerGroup();
var geo_json_fwi = L.layerGroup();
var geo_json_wsp = L.layerGroup();
var geo_json_temp = L.layerGroup();
var geo_json_rh = L.layerGroup();
var geo_json_qpf = L.layerGroup();
var geo_json_qpf_3h = L.layerGroup();
var geo_json_snw = L.layerGroup();


var ffmcTimeLayer = L.timeDimension.layer.layerGroup(geo_json_ffmc, {
    getUrlFunction: getHourlyForecast,
    getFileDir: ffmc_topo_file,
    getVar: 'FFMC'

});
ffmcTimeLayer.addTo(map);
console.log(ffmcTimeLayer);

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

var qpf_3hTimeLayer = L.timeDimension.layer.layerGroup(geo_json_qpf_3h, {
    getUrlFunction: getHourlyForecast,
    getFileDir: qpf_3h_topo_file,
    getVar: 'qpf_3h'

});

var snwTimeLayer = L.timeDimension.layer.layerGroup(geo_json_snw, {
    getUrlFunction: getHourlyForecast,
    getFileDir: snw_topo_file,
    getVar: 'snw'

});

var baseLayers = {
    "Topography"       : gl,
};


// The tree containing the layers
var groupedOverlays = [
    {
        label: 'Fire Weather Forecast',
        children: [
            {label: ' Fine Fuel Moisture Code', layer: ffmcTimeLayer, radioGroup: 'bc'},
            {label: ' Duff Moisture Code', layer: dmcTimeLayer, radioGroup: 'bc'},
            {label: ' Drought Code', layer: dcTimeLayer, radioGroup: 'bc'},
            {label: ' Initial Spread Index', layer: isiTimeLayer, radioGroup: 'bc'},
            {label: ' Build Up Index', layer: buiTimeLayer, radioGroup: 'bc'},
            {label: ' Fire Weather Index', layer: fwiTimeLayer, radioGroup: 'bc'},

        ]
    },
    {
        label: 'Weather Forecast',
        children: [
            {label: ' Temperature (C)', layer: tempTimeLayer, radioGroup: 'bc'},
            {label: ' Relative Humidity (%)', layer: rhTimeLayer, radioGroup: 'bc'},
            {label: ' Wind Speed (km/hr)', layer: wspTimeLayer, radioGroup: 'bc'},
            {label: ' Total Accumulated Precipitation (mm)', layer: qpfTimeLayer, radioGroup: 'bc'},
            {label: ' 3 Hour Accumulated Precipitation (mm)', layer: qpf_3hTimeLayer, radioGroup: 'bc'},
            {label: ' Accumulated Snowfall (cm)', layer: snwTimeLayer, radioGroup: 'bc'},


        ]
    },
    {
        label: 'Weather Observations',
        children: [
            {label: ' Weather Stations', layer: wx_station},
        ]
    },
];

var groupedOptions = {
    exclusiveGroups: ["Fire Weather Forecast"],

};
// L.control.groupedLayers(baseLayers, groupedOverlays).addTo(map);

L.control.layers.tree(baseLayers,groupedOverlays).addTo(map);


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
