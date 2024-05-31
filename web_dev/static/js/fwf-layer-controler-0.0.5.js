var ffmc_topo_file = "data/map/ffmc-merge-2020011106.josn",
    dmc_topo_file = "data/map/dmc-merge-20200111.json",
    dc_topo_file = "data/map/dc-merge-20200111.json",
    isi_topo_file = "data/map/isi-merge-2020011106.json",
    bui_topo_file = "data/map/bui-merge-20200111.json",
    fwi_topo_file = "data/map/fwi-merge-2020011106.json",
    hfi_topo_file = "data/map/hfi-merge-2020011106.json",
    ros_topo_file = "data/map/ros-merge-2020011106.json",
    cfb_topo_file = "data/map/cfb-merge-2020011106.json",
    sfc_topo_file = "data/map/sfc-merge-2020011106.json",
    tfc_topo_file = "data/map/tfc-merge-2020011106.json",
    wsp_topo_file = "data/map/ws-merge-2020011106.json",
    temp_topo_file = "data/map/temp-merge-2020011106.json",
    rh_topo_file = "data/map/rh-merge-2020011106.json",
    qpf_topo_file = "data/map/precip-merge-2020011106.json",
    qpf_3h_topo_file = "data/map/precip_3h-merge-2020011106.json",
    snw_topo_file = "data/map/snw-merge-2020011106.json",
    wd_topo_file = "data/map/wd-2020011106.json",

    firesLayer = omnivore.kml("data/fire_outlines.kml").on("ready", function() {
        this.setStyle({
            color: "#654321",
            fillOpacity: .8
        })
    });
hotspotsMarkers = L.markerClusterGroup({
    showCoverageOnHover: !1,
    zoomToBoundsOnClick: !0,
    spiderfyOnMaxZoom: !0,
    removeOutsideVisibleBounds: !0,
    spiderLegPolylineOptions: {
        weight: 1.5,
        color: "#ff1100",
        opacity: .8
    },
    maxClusterRadius: 60,
    disableClusteringAtZoom: 11
});

var radar = L.tileLayer.wms('https://geo.weather.gc.ca/geomet', {
    layers: 'RADAR_1KM_RRAI',
    format: 'image/png',
    transparent: true,
    opacity: .8,
    attribution: 'Weather data &copy; Environment and Climate Change Canada'
    });

var northAmericaBounds = [[20, -175], [88, -45]];
var  WAQI_URL    =  "https://tiles.waqi.info/tiles/usepa-pm25/{z}/{x}/{y}.png?token=_TOKEN_ID_";
var  WAQI_ATTR  =  'Air  Quality  Tiles  &copy;  <a  href="http://waqi.info">waqi.info</a>';
var  waqiLayer  =  L.tileLayer(WAQI_URL, {bounds: northAmericaBounds, attribution:  WAQI_ATTR});





var fires = L.layerGroup([hotspotsMarkers, firesLayer])
    geo_json_ffmc = L.layerGroup(),
    geo_json_ffmc = L.layerGroup(),
    geo_json_dmc = L.layerGroup(),
    geo_json_dc = L.layerGroup(),
    geo_json_isi = L.layerGroup(),
    geo_json_bui = L.layerGroup(),
    geo_json_fwi = L.layerGroup(),
    geo_json_hfi = L.layerGroup(),
    geo_json_ros = L.layerGroup(),
    geo_json_cfb = L.layerGroup(),
    geo_json_sfc = L.layerGroup(),
    geo_json_tfc = L.layerGroup(),
    geo_json_wsp = L.layerGroup(),
    geo_json_temp = L.layerGroup(),
    geo_json_rh = L.layerGroup(),
    geo_json_qpf = L.layerGroup(),
    geo_json_qpf_3h = L.layerGroup(),
    geo_json_snw = L.layerGroup(),
    geo_json_wd = L.layerGroup(),

    ffmcTimeLayer = L.timeDimension.layer.layerGroup(geo_json_ffmc, {
        getUrlFunction: getHourlyForecast,
        getFileDir: ffmc_topo_file,
        getVar: "FFMC"
    });
ffmcTimeLayer.addTo(map);
var dmcTimeLayer = L.timeDimension.layer.layerGroup(geo_json_dmc, {
        getUrlFunction: getDailyForecast,
        getFileDir: dmc_topo_file,
        getVar: "DMC"
    }),
    dcTimeLayer = L.timeDimension.layer.layerGroup(geo_json_dc, {
        getUrlFunction: getDailyForecast,
        getFileDir: dc_topo_file,
        getVar: "DC"
    }),
    isiTimeLayer = L.timeDimension.layer.layerGroup(geo_json_isi, {
        getUrlFunction: getHourlyForecast,
        getFileDir: isi_topo_file,
        getVar: "ISI"
    }),
    buiTimeLayer = L.timeDimension.layer.layerGroup(geo_json_bui, {
        getUrlFunction: getDailyForecast,
        getFileDir: bui_topo_file,
        getVar: "BUI"
    }),
    fwiTimeLayer = L.timeDimension.layer.layerGroup(geo_json_fwi, {
        getUrlFunction: getHourlyForecast,
        getFileDir: fwi_topo_file,
        getVar: "FWI"
    }),
    hfiTimeLayer = L.timeDimension.layer.layerGroup(geo_json_hfi, {
        getUrlFunction: getHourlyForecast,
        getFileDir: hfi_topo_file,
        getVar: "HFI"
    }),
    rosTimeLayer = L.timeDimension.layer.layerGroup(geo_json_ros, {
        getUrlFunction: getHourlyForecast,
        getFileDir: ros_topo_file,
        getVar: "ROS"
    }),
    cfbTimeLayer = L.timeDimension.layer.layerGroup(geo_json_cfb, {
        getUrlFunction: getHourlyForecast,
        getFileDir: cfb_topo_file,
        getVar: "CFB"
    }),
    sfcTimeLayer = L.timeDimension.layer.layerGroup(geo_json_sfc, {
        getUrlFunction: getHourlyForecast,
        getFileDir: sfc_topo_file,
        getVar: "SFC"
    }),
    tfcTimeLayer = L.timeDimension.layer.layerGroup(geo_json_tfc, {
        getUrlFunction: getHourlyForecast,
        getFileDir: tfc_topo_file,
        getVar: "TFC"
    }),
    wspTimeLayer = L.timeDimension.layer.layerGroup(geo_json_wsp, {
        getUrlFunction: getHourlyForecast,
        getFileDir: wsp_topo_file,
        getVar: "wsp"
    }),
    tempTimeLayer = L.timeDimension.layer.layerGroup(geo_json_temp, {
        getUrlFunction: getHourlyForecast,
        getFileDir: temp_topo_file,
        getVar: "temp"
    }),
    rhTimeLayer = L.timeDimension.layer.layerGroup(geo_json_rh, {
        getUrlFunction: getHourlyForecast,
        getFileDir: rh_topo_file,
        getVar: "rh"
    }),
    qpfTimeLayer = L.timeDimension.layer.layerGroup(geo_json_qpf, {
        getUrlFunction: getHourlyForecast,
        getFileDir: qpf_topo_file,
        getVar: "qpf"
    }),
    qpf_3hTimeLayer = L.timeDimension.layer.layerGroup(geo_json_qpf_3h, {
        getUrlFunction: getHourlyForecast,
        getFileDir: qpf_3h_topo_file,
        getVar: "qpf_3h"
    }),
    snwTimeLayer = L.timeDimension.layer.layerGroup(geo_json_snw, {
        getUrlFunction: getHourlyForecast,
        getFileDir: snw_topo_file,
        getVar: "snw"
    }),
    wdTimeLayer = L.timeDimension.layer.layerGroup(geo_json_wd, {
        getUrlFunction: getHourlyForecast,
        getFileDir: wd_topo_file,
        getVar: "wd"
    }),
    baseLayers = {
        Topography: gl
    },
    groupedOverlays = [{
        label: "Fire Weather Forecast",
        children: [{
            label: " Fine Fuel Moisture Code",
            layer: ffmcTimeLayer,
            radioGroup: "bc"
        }, {
            label: " Duff Moisture Code",
            layer: dmcTimeLayer,
            radioGroup: "bc"
        }, {
            label: " Drought Code",
            layer: dcTimeLayer,
            radioGroup: "bc"
        }, {
            label: " Initial Spread Index",
            layer: isiTimeLayer,
            radioGroup: "bc"
        }, {
            label: " Build Up Index",
            layer: buiTimeLayer,
            radioGroup: "bc"
        }, {
            label: " Fire Weather Index",
            layer: fwiTimeLayer,
            radioGroup: "bc"
        }]
    }, {
        label: "Fire Behavior Forecast",
        children: [{
            label: " Head Fire Intensity (kW/m)",
            layer: hfiTimeLayer,
            radioGroup: "bc"
        }, {
            label: " Rate of Spread (m/min)",
            layer: rosTimeLayer,
            radioGroup: "bc"
        }, {
            label: " Crown Fraction Burned (%)",
            layer: cfbTimeLayer,
            radioGroup: "bc"
        }, {
            label: " Surface Fuel Consumption (kg/m<sup>2</sup>)",
            layer: sfcTimeLayer,
            radioGroup: "bc"
        }, {
            label: " Total Fuel Consumption (kg/m<sup>2</sup>)",
            layer: tfcTimeLayer,
            radioGroup: "bc"
        }]
    }, {
        label: "Weather Forecast",
        children: [{
            label: " 2m Temperature (C)",
            layer: tempTimeLayer,
            radioGroup: "bc"
        }, {
            label: " 2m Relative Humidity (%)",
            layer: rhTimeLayer,
            radioGroup: "bc"
        },
        {
            label: " Total Accumulated Precipitation (mm)",
            layer: qpfTimeLayer,
            radioGroup: "bc"
        }, {
            label: " 3 Hour Accumulated Precipitation (mm)",
            layer: qpf_3hTimeLayer,
            radioGroup: "bc"
        }, {
            label: " Accumulated Snowfall (cm)",
            layer: snwTimeLayer,
            radioGroup: "bc"
        }, {
            label: " 10m Wind Speed (km/hr)",
            layer: wspTimeLayer,
            radioGroup: "bc"
        },
        {
            label: " 10m Wind Direction",
            layer: wdTimeLayer,
            // radioGroup: "bc"
        }
    ]
    }, {
        label: "Observations",
        children: [{
            label: " Weather Stations",
            layer: wx_station
        }, {
            label: " Satellite hotspots / Modelled Fires",
            layer: fires
        }, {
            label: " Doppler Radar",
            layer: radar
        },
        {
            label: " Air Quality PM2.5",
            layer: waqiLayer
        }
    ]
    }],
    groupedOptions = {
        exclusiveGroups: ["Fire Weather Forecast", "Fire Behavior Forecast"]
    };
L.control.layers.tree(baseLayers, groupedOverlays).addTo(map), map.zoomControl.setPosition("topright"), map.fullscreenControl.setPosition("topright"), map.zoomControl.remove();
var zoomHome = L.Control.zoomHome({
    position: "topright"
});
zoomHome.addTo(map);
