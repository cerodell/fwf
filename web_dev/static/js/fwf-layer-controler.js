var ffmc_topo_file = 'data/map/ffmc-merge-2020011106.josn';
var dmc_topo_file = 'data/map/dmc-merge-20200111.json';
var dc_topo_file = 'data/map/dc-merge-20200111.json';
var isi_topo_file = 'data/map/isi-merge-2020011106.json';
var bui_topo_file = 'data/map/bui-merge-20200111.json';
var fwi_topo_file = 'data/map/fwi-merge-2020011106.json';
var hfi_topo_file = 'data/map/hfi-merge-2020011106.json';
var ros_topo_file = 'data/map/ros-merge-2020011106.json';
var cfb_topo_file = 'data/map/cfb-merge-2020011106.json';
var sfc_topo_file = 'data/map/sfc-merge-2020011106.json';
var tfc_topo_file = 'data/map/tfc-merge-2020011106.json';
var wsp_topo_file = 'data/map/ws-merge-2020011106.json';
var temp_topo_file = 'data/map/temp-merge-2020011106.json';
var rh_topo_file = 'data/map/rh-merge-2020011106.json';
var qpf_topo_file = 'data/map/precip-merge-2020011106.json';
var qpf_3h_topo_file = 'data/map/precip_3h-merge-2020011106.json';
var snw_topo_file = 'data/map/snw-merge-2020011106.json';



// Fires layer
var firesLayer = omnivore.kml('data/fire_outlines.kml')
    .on('ready', function() {
        this.setStyle({color: "#654321", fillOpacity: 0.8})
    });


// // Hotspots layer with marker clustering
// var hotspots = omnivore.kml('data/fire_locations.kml'),
hotspotsMarkers = L.markerClusterGroup({
    showCoverageOnHover: false,
    zoomToBoundsOnClick: true,
    spiderfyOnMaxZoom: true,
    removeOutsideVisibleBounds: true,
    spiderLegPolylineOptions: {weight: 1.5, color: '#ff1100', opacity: 0.8},
    maxClusterRadius: 60,
    disableClusteringAtZoom: 11,
});
// hotspots.on('ready', MyObject.please)

var fires = L.layerGroup([hotspotsMarkers, firesLayer]);



var geo_json_ffmc = L.layerGroup();
var geo_json_dmc = L.layerGroup();
var geo_json_dc = L.layerGroup();
var geo_json_isi = L.layerGroup();
var geo_json_bui = L.layerGroup();
var geo_json_fwi = L.layerGroup();
var geo_json_hfi = L.layerGroup();
var geo_json_ros = L.layerGroup();
var geo_json_cfb = L.layerGroup();
var geo_json_sfc = L.layerGroup();
var geo_json_tfc = L.layerGroup();
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
// console.log(ffmcTimeLayer);

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

var hfiTimeLayer = L.timeDimension.layer.layerGroup(geo_json_hfi, {
    getUrlFunction: getHourlyForecast,
    getFileDir: hfi_topo_file,
    getVar: 'HFI'

});

var rosTimeLayer = L.timeDimension.layer.layerGroup(geo_json_ros, {
    getUrlFunction: getHourlyForecast,
    getFileDir: ros_topo_file,
    getVar: 'ROS'

});

var cfbTimeLayer = L.timeDimension.layer.layerGroup(geo_json_cfb, {
    getUrlFunction: getHourlyForecast,
    getFileDir: cfb_topo_file,
    getVar: 'CFB'

});

var sfcTimeLayer = L.timeDimension.layer.layerGroup(geo_json_sfc, {
    getUrlFunction: getHourlyForecast,
    getFileDir: sfc_topo_file,
    getVar: 'SFC'

});

var tfcTimeLayer = L.timeDimension.layer.layerGroup(geo_json_tfc, {
    getUrlFunction: getHourlyForecast,
    getFileDir: tfc_topo_file,
    getVar: 'TFC'

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
        label: 'Fire Behavior Forecast',
        children: [
            {label: ' Head Fire Intensity (kW/m)', layer: hfiTimeLayer, radioGroup: 'bc'},
            {label: ' Rate of Spread (m/min)', layer: rosTimeLayer, radioGroup: 'bc'},
            {label: ' Crown Fraction Burned (%)', layer: cfbTimeLayer, radioGroup: 'bc'},
            {label: ' Surface Fuel Consumption (kg/m<sup>2</sup>)', layer: sfcTimeLayer, radioGroup: 'bc'},
            {label: ' Total Fuel Consumption (kg/m<sup>2</sup>)', layer: tfcTimeLayer, radioGroup: 'bc'},

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
        label: 'Observations',
        children: [
            {label: ' Weather Stations', layer: wx_station},
            // {label:" Modelled fires", layer:  firesLayer},
            {label:" Satellite hotspots / Modelled Fires", layer: fires},

        ]
    },
];

var groupedOptions = {
    exclusiveGroups: ["Fire Weather Forecast", "Fire Behavior Forecast"],

};

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
