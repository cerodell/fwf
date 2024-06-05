function getColor(t) {
    return "Fully Reporting" === t ? "#008000" : "Partially Reporting" === t ? "#FFFF00" : "Not Reporting" === t ? "#FF0000" : "#008000";
}
function style(t) {
    return { weight: 1.5, opacity: 1, fillOpacity: 1, radius: 6, fillColor: getColor(t.properties.TypeOfIssue), color: "grey" };
}
var legend_radar = L.control({ position: "bottomright" });
legend_radar.onAdd = function (t) {
    var d = L.DomUtil.create("div", "info legend");
    return (d.innerHTML += '<img src="https://geo.weather.gc.ca/geomet?version=1.3.0&service=WMS&request=GetLegendGraphic&sld_version=1.1.0&layer=RADAR_1KM_RRAI&format=image/png&STYLE=RADARURPPRECIPR14-LINEAR" alt="Legend">'), d;
};
var legend_wx = L.control({ position: "bottomright" });
legend_wx.onAdd = function (t) {
    var d = L.DomUtil.create("div", "info legend");
    (labels = ["<strong>Station Status</strong>"]), (categories = ["Fully Reporting", "Partially Reporting", "Not Reporting"]);
    for (var l = 0; l < categories.length; l++) d.innerHTML += labels.push('<i class="circle" style="background:' + getColor(categories[l]) + '"></i> ' + (categories[l] ? categories[l] : "+"));
    return (d.innerHTML = labels.join("<br>")), d;
};
var color_map_ffmc = L.control({ position: "bottomleft" });
color_map_ffmc.onAdd = function (t) {
    var d = L.DomUtil.create("div", "fcst-legend leaflet-bar leaflet-control");
    return (
        (d.innerHTML =
            '<table id="values"><tr id="colours"><td style="background:#000080; width:10px; border-left:none;"></td><td style="background:#0000c4;"></td><td style="background:#0000ff;"></td><td style="background:#0034ff;"></td><td style="background:#0070ff;"></td><td style="background:#00acff;"></td><td style="background:#02e8f4;"></td><td style="background:#33ffc4;"></td><td style="background:#63ff94;"></td><td style="background:#94ff63;"></td><td style="background:#c4ff33;"></td><td style="background:#f4f802;"></td><td style="background:#ffc100;"></td><td style="background:#ff8900;"></td><td style="background:#ff5200;"></td><td style="background:#ff1a00;"></td><td style="background:#c40000;"></td><td style="background:#800000;"></td></tr><tr id="ticks"><td style="width:10px; border-left:none;"></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table><table id="labels"><tr><td width="10px">0</td><td width="10px"></td><td width="10px">60</td><td width="12px"></td><td width="10px">75</td><td width="14px"></td><td width="14px">81</td><td width="14px"></td><td width="10px">83</td><td width="14px"></td><td width="10px">85</td><td width="14px"></td><td width="14px">87</td><td width="14px"></td><td width="10px">89</td><td width="14px"></td><td width="10px">95</td><td width="4px"></td><td width="2px">100+</td></tr></table><div class="legend-title">Fine Fuel Moisture Code</div>'),
        d
    );
};
var color_map_dmc = L.control({ position: "bottomleft" });
color_map_dmc.onAdd = function (t) {
    var d = L.DomUtil.create("div", "fcst-legend leaflet-bar leaflet-control");
    return (
        (d.innerHTML =
            '<table id="values"><tr id="colours"><td style="background:#000080; width:10px; border-left:none;"></td><td style="background:#0000c4;"></td><td style="background:#0000ff;"></td><td style="background:#0034ff;"></td><td style="background:#0070ff;"></td><td style="background:#00acff;"></td><td style="background:#02e8f4;"></td><td style="background:#33ffc4;"></td><td style="background:#63ff94;"></td><td style="background:#94ff63;"></td><td style="background:#c4ff33;"></td><td style="background:#f4f802;"></td><td style="background:#ffc100;"></td><td style="background:#ff8900;"></td><td style="background:#ff5200;"></td><td style="background:#ff1a00;"></td><td style="background:#c40000;"></td><td style="background:#800000;"></td></tr><tr id="ticks"><td style="width:10px; border-left:none;"></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table><table id="labels"><tr><td width="2px">0</td><td width="14px"></td><td width="10px">7</td><td width="14px"></td><td width="10px">14</td><td width="14px"></td><td width="14px">21</td><td width="14px"></td><td width="10px">28</td><td width="14px"></td><td width="12px">35</td><td width="12px"></td><td width="14px">43</td><td width="14px"></td><td width="10px">50</td><td width="16px"></td><td width="10px">60</td><td width="3px"></td><td width="5px">70+</td></tr></table><div class="legend-title">Duff Moisture Code</div>'),
        d
    );
};
var color_map_dc = L.control({ position: "bottomleft" });
color_map_dc.onAdd = function (t) {
    var d = L.DomUtil.create("div", "fcst-legend leaflet-bar leaflet-control");
    return (
        (d.innerHTML =
            '<table id="values"><tr id="colours"><td style="background:#000080; width:10px; border-left:none;"></td><td style="background:#0000c4;"></td><td style="background:#0000ff;"></td><td style="background:#0034ff;"></td><td style="background:#0070ff;"></td><td style="background:#00acff;"></td><td style="background:#02e8f4;"></td><td style="background:#33ffc4;"></td><td style="background:#63ff94;"></td><td style="background:#94ff63;"></td><td style="background:#c4ff33;"></td><td style="background:#f4f802;"></td><td style="background:#ffc100;"></td><td style="background:#ff8900;"></td><td style="background:#ff5200;"></td><td style="background:#ff1a00;"></td><td style="background:#c40000;"></td><td style="background:#800000;"></td></tr><tr id="ticks"><td style="width:10px; border-left:none;"></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table><table id="labels"><tr><td width="0px">40</td><td width="8px"></td><td width="9px">82</td><td width="12px"></td><td width="15px">124</td><td width="9px"></td><td width="5px">167</td><td width="8px"></td><td width="5px">209</td><td width="8px"></td><td width="5px">252</td><td width="9px"></td><td width="5px">294</td><td width="9px"></td><td width="14px">337</td><td width="9px"></td><td width="5px">400</td><td width="5px"></td><td width="5px">480+</td></tr></table><div class="legend-title">Drought Code</div>'),
        d
    );
};
var color_map_isi = L.control({ position: "bottomleft" });
color_map_isi.onAdd = function (t) {
    var d = L.DomUtil.create("div", "fcst-legend leaflet-bar leaflet-control");
    return (
        (d.innerHTML =
            '<table id="values"><tr id="colours"><td style="background:#000080; width:10px; border-left:none;"></td><td style="background:#0000c4;"></td><td style="background:#0000ff;"></td><td style="background:#0034ff;"></td><td style="background:#0070ff;"></td><td style="background:#00acff;"></td><td style="background:#02e8f4;"></td><td style="background:#33ffc4;"></td><td style="background:#63ff94;"></td><td style="background:#94ff63;"></td><td style="background:#c4ff33;"></td><td style="background:#f4f802;"></td><td style="background:#ffc100;"></td><td style="background:#ff8900;"></td><td style="background:#ff5200;"></td><td style="background:#ff1a00;"></td><td style="background:#c40000;"></td><td style="background:#800000;"></td></tr><tr id="ticks"><td style="width:10px; border-left:none;"></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table><table id="labels"><tr><td width="2px">0</td><td width="10px"></td><td width="10px">1.8</td><td width="12px"></td><td width="10px">3.7</td><td width="12px"></td><td width="6px">5.6</td><td width="12px"></td><td width="6px">7.5</td><td width="12px"></td><td width="6px">9.4</td><td width="12px"></td><td width="6px">11.3</td><td width="7px"></td><td width="6px">13.2</td><td width="4px"></td><td width="4px">15.0</td><td width="2px"></td><td width="2px">16.0+</td></tr></table><div class="legend-title">Initial Spread Index</div>'),
        d
    );
};
var color_map_bui = L.control({ position: "bottomleft" });
color_map_bui.onAdd = function (t) {
    var d = L.DomUtil.create("div", "fcst-legend leaflet-bar leaflet-control");
    return (
        (d.innerHTML =
            '<table id="values"><tr id="colours"><td style="background:#000080; width:10px; border-left:none;"></td><td style="background:#0000c4;"></td><td style="background:#0000ff;"></td><td style="background:#0034ff;"></td><td style="background:#0070ff;"></td><td style="background:#00acff;"></td><td style="background:#02e8f4;"></td><td style="background:#33ffc4;"></td><td style="background:#63ff94;"></td><td style="background:#94ff63;"></td><td style="background:#c4ff33;"></td><td style="background:#f4f802;"></td><td style="background:#ffc100;"></td><td style="background:#ff8900;"></td><td style="background:#ff5200;"></td><td style="background:#ff1a00;"></td><td style="background:#c40000;"></td><td style="background:#800000;"></td></tr><tr id="ticks"><td style="width:10px; border-left:none;"></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table><table id="labels"><tr><td width="2px">0</td><td width="10px"></td><td width="10px">10</td><td width="17px"></td><td width="10px">21</td><td width="14px"></td><td width="14px">32</td><td width="12px"></td><td width="10px">42</td><td width="15px"></td><td width="12px">53</td><td width="15px"></td><td width="10px">64</td><td width="14px"></td><td width="12px">74</td><td width="14px"></td><td width="12px">95</td><td width="1px"></td><td width="1px">115+</td></tr></table><div class="legend-title">Build Up Index</div>'),
        d
    );
};
var color_map_fwi = L.control({ position: "bottomleft" });
color_map_fwi.onAdd = function (t) {
    var d = L.DomUtil.create("div", "fcst-legend leaflet-bar leaflet-control");
    return (
        (d.innerHTML =
            '<table id="values"><tr id="colours"><td style="background:#000080; width:10px; border-left:none;"></td><td style="background:#0000c4;"></td><td style="background:#0000ff;"></td><td style="background:#0034ff;"></td><td style="background:#0070ff;"></td><td style="background:#00acff;"></td><td style="background:#02e8f4;"></td><td style="background:#33ffc4;"></td><td style="background:#63ff94;"></td><td style="background:#94ff63;"></td><td style="background:#c4ff33;"></td><td style="background:#f4f802;"></td><td style="background:#ffc100;"></td><td style="background:#ff8900;"></td><td style="background:#ff5200;"></td><td style="background:#ff1a00;"></td><td style="background:#c40000;"></td><td style="background:#800000;"></td></tr><tr id="ticks"><td style="width:10px; border-left:none;"></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table><table id="labels"><tr><td width="2px">0</td><td width="12px"></td><td width="10px">3</td><td width="14px"></td><td width="14px">7</td><td width="14px"></td><td width="10px">10</td><td width="14px"></td><td width="10px">14</td><td width="14px"></td><td width="10px">18</td><td width="14px"></td><td width="16px">21</td><td width="14px"></td><td width="10px">25</td><td width="14px"></td><td width="10px">30</td><td width="2px"></td><td width="2px">40+</td></tr></table><div class="legend-title">Fire Weather Index</div>'),
        d
    );
};
var color_map_hfi = L.control({ position: "bottomleft" });
color_map_hfi.onAdd = function (t) {
    var d = L.DomUtil.create("div", "fcst-legend leaflet-bar leaflet-control");
    return (
        (d.innerHTML =
            '<table id="values"><tr id="colours"><td style="background:#0000ff; width:30px; border-left:none;"></td><td style="background:#00c0c0; width:30px;"></td><td style="background:#008001; width:30px;"></td><td style="background:#01e001; width:30px;"></td><td style="background:#ffff00; width:30px;"></td><td style="background:#dfa000; width:30px;"></td><td style="background:#ff0000; width:30px;"></td><td style="background:#8b0000; width:30px;"></td></tr><tr id="ticks"><td style="width:10px; border-left:none;"></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table><table id="labels"><tr><td width="2px">0</td><td width="45px">10</td><td width="20px">500</td><td width="40px">2000</td><td width="28px">4000</td><td width="30px">10000</td><td width="30px">30000</td><td width="38px">40000+</td></tr></table><div class="legend-title">Head Fire Intensity (kW/m)</div>'),
        d
    );
};
var color_map_ros = L.control({ position: "bottomleft" });
color_map_ros.onAdd = function (t) {
    var d = L.DomUtil.create("div", "fcst-legend leaflet-bar leaflet-control");
    return (
        (d.innerHTML =
            '<table id="values"><tr id="colours"><td style="background:#0000ff; width:30px; border-left:none;"></td><td style="background:#008001; width:30px;"></td><td style="background:#01e001; width:30px;"></td><td style="background:#ffff00; width:30px;"></td><td style="background:#dfa000; width:30px;"></td><td style="background:#ff0000; width:30px;"></td><td style="background:#8b0000; width:30px;"></td></tr><tr id="ticks"><td style="width:10px; border-left:none;"></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table><table id="labels"><tr><td width="2px">0</td><td width="43px">1</td><td width="23px">3</td><td width="36px">10</td><td width="30px">18</td><td width="34px">25</td><td width="35px">40+</td></tr></table><div class="legend-title">Rate of Spread (m/min)</div>'),
        d
    );
};
var color_map_cfb = L.control({ position: "bottomleft" });
color_map_cfb.onAdd = function (t) {
    var d = L.DomUtil.create("div", "fcst-legend leaflet-bar leaflet-control");
    return (
        (d.innerHTML =
            '<table id="values"><tr id="colours"><td style="background:#0000ff; width:30px; border-left:none;"></td><td style="background:#008001; width:30px;"></td><td style="background:#01e001; width:30px;"></td><td style="background:#ffff00; width:30px;"></td><td style="background:#dfa000; width:30px;"></td><td style="background:#ff0000; width:30px;"></td></tr><tr id="ticks"><td style="width:10px; border-left:none;"></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table><table id="labels"><tr><td width="2px">0</td><td width="43px">10</td><td width="23px">30</td><td width="36px">50</td><td width="30px">70</td><td width="30px">90</td><td width="32px">100</td></tr></table><div class="legend-title">Crown Fraction Burned (%)</div>'),
        d
    );
};
var color_map_frp = L.control({ position: "bottomleft" });
color_map_frp.onAdd = function (t) {
    var d = L.DomUtil.create("div", "fcst-legend leaflet-bar leaflet-control");
    return (
        (d.innerHTML =
            '<table id="values"><tr id="colours"><td style="background:#ffffff; width:10px; border-left:none;"></td><td style="background:#fff8ba;"></td><td style="background:#fff0a7;"></td><td style="background:#ffe794;"></td><td style="background:#fede81;"></td><td style="background:#fed16d;"></td><td style="background:#fec05b;"></td><td style="background:#feaf4b;"></td><td style="background:#fd9e44;"></td><td style="background:#fd8d3c;"></td><td style="background:#fd7134;"></td><td style="background:#fc552c;"></td><td style="background:#f43d25;"></td><td style="background:#e9261f;"></td><td style="background:#da141e;"></td><td style="background:#c90823;"></td><td style="background:#b60026;"></td><td style="background:#9b0026;"></td></tr><tr id="ticks"><td style="width:10px; border-left:none;"></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table><table id="labels"><tr><td width="2px">0</td><td width="10px"></td><td width="10px">50</td><td width="13px"></td><td width="10px">150</td><td width="11px"></td><td width="10px">250</td><td width="9px"></td><td width="9px">400</td><td width="10px"></td><td width="12px">600</td><td width="6px"></td><td width="6px">1000</td><td width="6px"></td><td width="6px">1800</td><td width="4px"></td><td width="4px">2500</td><td width="1px"></td><td width="1px">3000+</td></tr></table><div class="legend-title">Potential Fire Radiative Power (MW)</div>'),
        d
    );
};
color_map_frp.addTo(map);
var color_map_tfc = L.control({ position: "bottomleft" });
color_map_tfc.onAdd = function (t) {
    var d = L.DomUtil.create("div", "fcst-legend leaflet-bar leaflet-control");
    return (
        (d.innerHTML =
            '<table id="values"><tr id="colours"><td style="background:#0000ff; width:30px; border-left:none;"></td><td style="background:#008001; width:30px;"></td><td style="background:#01e001; width:30px;"></td><td style="background:#ffff00; width:30px;"></td><td style="background:#dfa000; width:30px;"></td><td style="background:#ff0000; width:30px;"></td><td style="background:#8b0000; width:30px;"></td></tr><tr id="ticks"><td style="width:10px; border-left:none;"></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table><table id="labels"><tr><td width="2px">0</td><td width="46px">2</td><td width="17px">4</td><td width="44px">6</td><td width="18px">8</td><td width="44px">10</td><td width="26px">12+</td></tr></table><div class="legend-title">Total Fuel Consumption (kg/m<sup>2</sup>)</div>'),
        d
    );
};
var color_map_wsp = L.control({ position: "bottomleft" });
color_map_wsp.onAdd = function (t) {
    var d = L.DomUtil.create("div", "fcst-legend leaflet-bar leaflet-control");
    return (
        (d.innerHTML =
            '<table id="values"><tr id="colours"><td style="background:#FFFFFF; width:10px; border-left:none;"></td><td style="background:#BBBBBB;"></td><td style="background:#646464;"></td><td style="background:#1563D3;"></td><td style="background:#2883F1;"></td><td style="background:#50A5F5;"></td><td style="background:#97D3FB;"></td><td style="background:#0CA10D;"></td><td style="background:#37D33C;"></td><td style="background:#97F58D;"></td><td style="background:#B5FBAB;"></td><td style="background:#FFE978;"></td><td style="background:#FFC03D;"></td><td style="background:#FFA100;"></td><td style="background:#FF3300;"></td><td style="background:#C10000;"></td><td style="background:#960007;"></td><td style="background:#643C32;"></td></tr><tr id="ticks"><td style="width:10px; border-left:none;"></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table><table id="labels"><tr><td width="2px">0</td><td width="12px"></td><td width="8px">20</td><td width="15px"></td><td width="10px">28</td><td width="14px"></td><td width="10px">32</td><td width="15px"></td><td width="10px">40</td><td width="16px"></td><td width="10px">48</td><td width="16px"></td><td width="10px">56</td><td width="16px"></td><td width="10px">64</td><td width="14px"></td><td width="10px">72</td><td width="2px"></td><td width="2px">80+</td></tr></table><div class="legend-title">Wind Speed (km/hr) at 10m</div>'),
        d
    );
};
var color_map_temp = L.control({ position: "bottomleft" });
color_map_temp.onAdd = function (t) {
    var d = L.DomUtil.create("div", "fcst-legend leaflet-bar leaflet-control");
    return (
        (d.innerHTML =
            '<table id="values"><tr id="colours"><td style="background:#00ffff; width:10px; border-left:none;"></td><td style="background:#06e6ed;"></td><td style="background:#0bcddb;"></td><td style="background:#10b5ca;"></td><td style="background:#159eb9;"></td><td style="background:#1b86a8;"></td><td style="background:#206f97;"></td><td style="background:#255987;"></td><td style="background:#2a4276;"></td><td style="background:#2f2a65;"></td><td style="background:#360a4e;"></td><td style="background:#560b69;"></td><td style="background:#7b0c88;"></td><td style="background:#a30ca8;"></td><td style="background:#ce0bdc;"></td><td style="background:#af05e3;"></td><td style="background:#8904e1;"></td><td style="background:#5d04d8;"></td><td style="background:#1c0dcf;"></td><td style="background:#1b34d7;"></td><td style="background:#2460e2;"></td><td style="background:#348ced;"></td><td style="background:#44b1f6;"></td><td style="background:#51cbfa;"></td><td style="background:#80e0f7;"></td><td style="background:#a0eaf7;"></td><td style="background:#00ef7c;"></td><td style="background:#00e452;"></td><td style="background:#00c848;"></td><td style="background:#10b87a;"></td><td style="background:#297b5d;"></td><td style="background:#007229;"></td><td style="background:#3ca12c;"></td><td style="background:#79d030;"></td><td style="background:#b5ff33;"></td><td style="background:#d8f7a1;"></td><td style="background:#fff600;"></td><td style="background:#f8df0b;"></td><td style="background:#fdca0c;"></td><td style="background:#fcac05;"></td><td style="background:#f88d00;"></td><td style="background:#ff6600;"></td><td style="background:#fc4f00;"></td><td style="background:#ff0100;"></td><td style="background:#f31a00;"></td><td style="background:#f31861;"></td><td style="background:#f316c2;"></td></tr><tr id="ticks"><td style="width:10px; border-left:none;"></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table><table id="labels"><tr><td width="1px"></td><td width="10px">-75</td><td width="10px"></td><td width="10px">-65</td><td width="12px"></td><td width="10px">-55</td><td width="11px"></td><td width="10px">-45</td><td width="14px"></td><td width="10px">35</td><td width="12px"></td><td width="10px">-30</td><td width="11px"></td><td width="10px">-26</td><td width="10px"></td><td width="10px">-22</td><td width="11px"></td><td width="10px">-18</td><td width="12px"></td><td width="10px">-14</td><td width="12px"></td><td width="10px">-10</td><td width="12px"></td><td width="10px">-6</td><td width="17px"></td><td width="10px">-2</td><td width="17px"></td><td width="10px">2</td><td width="16px"></td><td width="10px">6</td><td width="16px"></td><td width="10px">10</td><td width="16px"></td><td width="10px">14</td><td width="14px"></td><td width="10px">18</td><td width="15px"></td><td width="10px">22</td><td width="15px"></td><td width="10px">26</td><td width="17px"></td><td width="10px">30</td><td width="14px"></td><td width="10px">34</td><td width="14px"></td><td width="10px">38</td><td width="10px"></td><td width="10px">42+</td></tr></table><div class="legend-title">Temperature (C) at 2m</div>'),
        d
    );
};
var color_map_rh = L.control({ position: "bottomleft" });
color_map_rh.onAdd = function (t) {
    var d = L.DomUtil.create("div", "fcst-legend leaflet-bar leaflet-control");
    return (
        (d.innerHTML =
            '<table id="values"><tr id="colours"><td style="background:#442d15; width:10px; border-left:none;"></td><td style="background:#653f1f;"></td><td style="background:#815228;"></td><td style="background:#9d622f;"></td><td style="background:#ad7644;"></td><td style="background:#b98b5c;"></td><td style="background:#c7a074;"></td><td style="background:#e1cdb3;"></td><td style="background:#efded9;"></td><td style="background:#d0d3bb;"></td><td style="background:#afc599;"></td><td style="background:#88bf87;"></td><td style="background:#7ab58d;"></td><td style="background:#6da893;"></td><td style="background:#59929b;"></td><td style="background:#568999;"></td><td style="background:#4c6497;"></td><td style="background:#6c4a97;"></td></tr><tr id="ticks"><td style="width:10px; border-left:none;"></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table><table id="labels"><tr><td width="2px">0</td><td width="12px"></td><td width="10px">2</td><td width="16px"></td><td width="10px">5</td><td width="16px"></td><td width="10px">15</td><td width="16px"></td><td width="10px">30</td><td width="14px"></td><td width="10px">50</td><td width="15px"></td><td width="10px">70</td><td width="14px"></td><td width="10px">90</td><td width="16px"></td><td width="10px">97</td><td width="2px"></td><td width="10px">100+</td></tr></table><div class="legend-title">Relative Humidity (%) at 2m</div>'),
        d
    );
};
var color_map_qpf = L.control({ position: "bottomleft" });
color_map_qpf.onAdd = function (t) {
    var d = L.DomUtil.create("div", "fcst-legend leaflet-bar leaflet-control");
    return (
        (d.innerHTML =
            '<table id="values"><tr id="colours"><td style="background:#ffffff; width:10px; border-left:none;"></td><td style="background:#a9a5a5;"></td><td style="background:#6e6e6e;"></td><td style="background:#b3f9a9;"></td><td style="background:#79f572;"></td><td style="background:#50f150;"></td><td style="background:#1fb51e;"></td><td style="background:#0ca10d;"></td><td style="background:#1563d3;"></td><td style="background:#54a8f5;"></td><td style="background:#b4f1fb;"></td><td style="background:#ffe978;"></td><td style="background:#ffa100;"></td><td style="background:#ff3300;"></td><td style="background:#a50000;"></td><td style="background:#b58d83;"></td><td style="background:#9886ba;"></td><td style="background:#8d008d;"></td></tr><tr id="ticks"><td style="width:10px; border-left:none;"></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table><table id="labels"><tr><td width="2px">0</td><td width="12px"></td><td width="10px">1</td><td width="16px"></td><td width="10px">3</td><td width="15px"></td><td width="10px">10</td><td width="16px"></td><td width="10px">20</td><td width="15px"></td><td width="10px">30</td><td width="15px"></td><td width="10px">50</td><td width="15px"></td><td width="10px">70</td><td width="12px"></td><td width="4px">100</td><td width="2px"></td><td width="2px">140+</td></tr></table><div class="legend-title">Total Accumulated Precipitation (mm)</div>'),
        d
    );
};
var color_map_qpf_3h = L.control({ position: "bottomleft" });
color_map_qpf_3h.onAdd = function (t) {
    var d = L.DomUtil.create("div", "fcst-legend leaflet-bar leaflet-control");
    return (
        (d.innerHTML =
            '<table id="values"><tr id="colours"><td style="background:#ffffff; width:10px; border-left:none;"></td><td style="background:#a9a5a5;"></td><td style="background:#6e6e6e;"></td><td style="background:#b3f9a9;"></td><td style="background:#79f572;"></td><td style="background:#50f150;"></td><td style="background:#1fb51e;"></td><td style="background:#0ca10d;"></td><td style="background:#1563d3;"></td><td style="background:#54a8f5;"></td><td style="background:#b4f1fb;"></td><td style="background:#ffe978;"></td><td style="background:#ffa100;"></td><td style="background:#ff3300;"></td><td style="background:#a50000;"></td><td style="background:#b58d83;"></td><td style="background:#9886ba;"></td><td style="background:#8d008d;"></td></tr><tr id="ticks"><td style="width:10px; border-left:none;"></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table><table id="labels"><tr><td width="2px">0</td><td width="12px"></td><td width="10px">1</td><td width="16px"></td><td width="10px">3</td><td width="15px"></td><td width="10px">10</td><td width="16px"></td><td width="10px">20</td><td width="15px"></td><td width="10px">30</td><td width="15px"></td><td width="10px">50</td><td width="15px"></td><td width="10px">70</td><td width="12px"></td><td width="4px">100</td><td width="2px"></td><td width="2px">140+</td></tr></table><div class="legend-title">3 Hour Accumulated Precipitation (mm)</div>'),
        d
    );
};
var color_map_snw = L.control({ position: "bottomleft" });
function geo_json_styler18(t, d) {
    switch (t.fill) {
        case "#000080":
            return { color: "#000080", opacity: 1, fillColor: "#000080", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#0000c4":
            return { color: "#0000c4", opacity: 1, fillColor: "#0000c4", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#0000ff":
            return { color: "#0000ff", opacity: 1, fillColor: "#0000ff", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#0034ff":
            return { color: "#0034ff", opacity: 1, fillColor: "#0034ff", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#0070ff":
            return { color: "#0070ff", opacity: 1, fillColor: "#0070ff", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#00acff":
            return { color: "#00acff", opacity: 1, fillColor: "#00acff", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#02e8f4":
            return { color: "#02e8f4", opacity: 1, fillColor: "#02e8f4", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#33ffc4":
            return { color: "#33ffc4", opacity: 1, fillColor: "#33ffc4", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#63ff94":
            return { color: "#63ff94", opacity: 1, fillColor: "#63ff94", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#94ff63":
            return { color: "#94ff63", opacity: 1, fillColor: "#94ff63", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#c4ff33":
            return { color: "#c4ff33", opacity: 1, fillColor: "#c4ff33", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#f4f802":
            return { color: "#f4f802", opacity: 1, fillColor: "#f4f802", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ffc100":
            return { color: "#ffc100", opacity: 1, fillColor: "#ffc100", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ff8900":
            return { color: "#ff8900", opacity: 1, fillColor: "#ff8900", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ff5200":
            return { color: "#ff5200", opacity: 1, fillColor: "#ff5200", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ff1a00":
            return { color: "#ff1a00", opacity: 1, fillColor: "#ff1a00", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#c40000":
            return { color: "#c40000", opacity: 1, fillColor: "#c40000", fillOpacity: 1, weight: 0.2, fill: !0 };
        default:
            return { color: "#800000", opacity: 1, fillColor: "#800000", fillOpacity: 1, weight: 0.2, fill: !0 };
    }
}
function geo_json_styler_fbp(t, d) {
    switch (t.fill) {
        case "#0000ff":
            return { color: "#0000ff", opacity: 1, fillColor: "#0000ff", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#008001":
            return { color: "#008001", opacity: 1, fillColor: "#008001", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#01e001":
            return { color: "#01e001", opacity: 1, fillColor: "#01e001", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ffff00":
            return { color: "#ffff00", opacity: 1, fillColor: "#ffff00", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#dfa000":
            return { color: "#dfa000", opacity: 1, fillColor: "#dfa000", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ff0000":
            return { color: "#ff0000", opacity: 1, fillColor: "#ff0000", fillOpacity: 1, weight: 0.2, fill: !0 };
        default:
            return { color: "#8b0000", opacity: 1, fillColor: "#8b0000", fillOpacity: 1, weight: 0.2, fill: !0 };
    }
}
function geo_json_styler_hfi(t, d) {
    switch (t.fill) {
        case "#0000ff":
            return { color: "#0000ff", opacity: 1, fillColor: "#0000ff", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#00c0c0":
            return { color: "#00c0c0", opacity: 1, fillColor: "#00c0c0", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#008001":
            return { color: "#008001", opacity: 1, fillColor: "#008001", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#01e001":
            return { color: "#01e001", opacity: 1, fillColor: "#01e001", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ffff00":
            return { color: "#ffff00", opacity: 1, fillColor: "#ffff00", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#dfa000":
            return { color: "#dfa000", opacity: 1, fillColor: "#dfa000", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ff0000":
            return { color: "#ff0000", opacity: 1, fillColor: "#ff0000", fillOpacity: 1, weight: 0.2, fill: !0 };
        default:
            return { color: "#8b0000", opacity: 1, fillColor: "#8b0000", fillOpacity: 1, weight: 0.2, fill: !0 };
    }
}
function geo_json_styler_wsp(t, d) {
    switch (t.fill) {
        case "#ffffff":
            return { color: "#ffffff", opacity: 1, fillColor: "#ffffff", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#bbbbbb":
            return { color: "#bbbbbb", opacity: 1, fillColor: "#bbbbbb", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#646464":
            return { color: "#646464", opacity: 1, fillColor: "#646464", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#1563d3":
            return { color: "#1563d3", opacity: 1, fillColor: "#1563d3", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#2883f1":
            return { color: "#2883f1", opacity: 1, fillColor: "#2883f1", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#50a5f5":
            return { color: "#50a5f5", opacity: 1, fillColor: "#50a5f5", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#97d3fb":
            return { color: "#97d3fb", opacity: 1, fillColor: "#97d3fb", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#0ca10d":
            return { color: "#0ca10d", opacity: 1, fillColor: "#0ca10d", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#37d33c":
            return { color: "#37d33c", opacity: 1, fillColor: "#37d33c", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#97f58d":
            return { color: "#97f58d", opacity: 1, fillColor: "#97f58d", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#b5fbab":
            return { color: "#b5fbab", opacity: 1, fillColor: "#b5fbab", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ffe978":
            return { color: "#ffe978", opacity: 1, fillColor: "#ffe978", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ffc03d":
            return { color: "#ffc03d", opacity: 1, fillColor: "#ffc03d", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ffa100":
            return { color: "#ffa100", opacity: 1, fillColor: "#ffa100", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ff3300":
            return { color: "#ff3300", opacity: 1, fillColor: "#ff3300", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#c10000":
            return { color: "#c10000", opacity: 1, fillColor: "#c10000", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#960007":
            return { color: "#960007", opacity: 1, fillColor: "#960007", fillOpacity: 1, weight: 0.2, fill: !0 };
        default:
            return { color: "#643C32", opacity: 1, fillColor: "#643C32", fillOpacity: 1, weight: 0.2, fill: !0 };
    }
}
function geo_json_styler_temp(t, d) {
    switch (t.fill) {
        case "#00ffff":
            return { color: "#00ffff", opacity: 1, fillColor: "#00ffff", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#06e6ed":
            return { color: "#06e6ed", opacity: 1, fillColor: "#06e6ed", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#0bcddb":
            return { color: "#0bcddb", opacity: 1, fillColor: "#0bcddb", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#10b5ca":
            return { color: "#10b5ca", opacity: 1, fillColor: "#10b5ca", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#159eb9":
            return { color: "#159eb9", opacity: 1, fillColor: "#159eb9", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#1b86a8":
            return { color: "#1b86a8", opacity: 1, fillColor: "#1b86a8", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#206f97":
            return { color: "#206f97", opacity: 1, fillColor: "#206f97", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#255987":
            return { color: "#255987", opacity: 1, fillColor: "#255987", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#2a4276":
            return { color: "#2a4276", opacity: 1, fillColor: "#2a4276", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#2f2a65":
            return { color: "#2f2a65", opacity: 1, fillColor: "#2f2a65", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#360a4e":
            return { color: "#360a4e", opacity: 1, fillColor: "#360a4e", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#560b69":
            return { color: "#560b69", opacity: 1, fillColor: "#560b69", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#7b0c88":
            return { color: "#7b0c88", opacity: 1, fillColor: "#7b0c88", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#a30ca8":
            return { color: "#a30ca8", opacity: 1, fillColor: "#a30ca8", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ce0bdc":
            return { color: "#ce0bdc", opacity: 1, fillColor: "#ce0bdc", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#af05e3":
            return { color: "#af05e3", opacity: 1, fillColor: "#af05e3", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#8904e1":
            return { color: "#8904e1", opacity: 1, fillColor: "#8904e1", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#5d04d8":
            return { color: "#5d04d8", opacity: 1, fillColor: "#5d04d8", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#1c0dcf":
            return { color: "#1c0dcf", opacity: 1, fillColor: "#1c0dcf", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#1b34d7":
            return { color: "#1b34d7", opacity: 1, fillColor: "#1b34d7", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#2460e2":
            return { color: "#2460e2", opacity: 1, fillColor: "#2460e2", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#348ced":
            return { color: "#348ced", opacity: 1, fillColor: "#348ced", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#44b1f6":
            return { color: "#44b1f6", opacity: 1, fillColor: "#44b1f6", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#51cbfa":
            return { color: "#51cbfa", opacity: 1, fillColor: "#51cbfa", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#80e0f7":
            return { color: "#80e0f7", opacity: 1, fillColor: "#80e0f7", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#a0eaf7":
            return { color: "#a0eaf7", opacity: 1, fillColor: "#a0eaf7", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#00ef7c":
            return { color: "#00ef7c", opacity: 1, fillColor: "#00ef7c", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#00e452":
            return { color: "#00e452", opacity: 1, fillColor: "#00e452", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#00c848":
            return { color: "#00c848", opacity: 1, fillColor: "#00c848", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#10b87a":
            return { color: "#10b87a", opacity: 1, fillColor: "#10b87a", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#297b5d":
            return { color: "#297b5d", opacity: 1, fillColor: "#297b5d", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#007229":
            return { color: "#007229", opacity: 1, fillColor: "#007229", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#3ca12c":
            return { color: "#3ca12c", opacity: 1, fillColor: "#3ca12c", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#79d030":
            return { color: "#79d030", opacity: 1, fillColor: "#79d030", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#b5ff33":
            return { color: "#b5ff33", opacity: 1, fillColor: "#b5ff33", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#d8f7a1":
            return { color: "#d8f7a1", opacity: 1, fillColor: "#d8f7a1", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#fff600":
            return { color: "#fff600", opacity: 1, fillColor: "#fff600", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#f8df0b":
            return { color: "#f8df0b", opacity: 1, fillColor: "#f8df0b", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#fdca0c":
            return { color: "#fdca0c", opacity: 1, fillColor: "#fdca0c", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#fcac05":
            return { color: "#fcac05", opacity: 1, fillColor: "#fcac05", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#f88d00":
            return { color: "#f88d00", opacity: 1, fillColor: "#f88d00", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ff6600":
            return { color: "#ff6600", opacity: 1, fillColor: "#ff6600", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#fc4f00":
            return { color: "#fc4f00", opacity: 1, fillColor: "#fc4f00", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ff0100":
            return { color: "#ff0100", opacity: 1, fillColor: "#ff0100", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#f31a00":
            return { color: "#f31a00", opacity: 1, fillColor: "#f31a00", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#f31861":
            return { color: "#f31861", opacity: 1, fillColor: "#f31861", fillOpacity: 1, weight: 0.2, fill: !0 };
        default:
            return { color: "#f316c2", opacity: 1, fillColor: "#f316c2", fillOpacity: 1, weight: 0.2, fill: !0 };
    }
}
function geo_json_styler_rh(t, d) {
    switch (t.fill) {
        case "#442d15":
            return { color: "#442d15", opacity: 1, fillColor: "#442d15", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#653f1f":
            return { color: "#653f1f", opacity: 1, fillColor: "#653f1f", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#815228":
            return { color: "#815228", opacity: 1, fillColor: "#815228", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#9d622f":
            return { color: "#9d622f", opacity: 1, fillColor: "#9d622f", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ad7644":
            return { color: "#ad7644", opacity: 1, fillColor: "#ad7644", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#b98b5c":
            return { color: "#b98b5c", opacity: 1, fillColor: "#b98b5c", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#c7a074":
            return { color: "#c7a074", opacity: 1, fillColor: "#c7a074", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#e1cdb3":
            return { color: "#e1cdb3", opacity: 1, fillColor: "#e1cdb3", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#efded9":
            return { color: "#efded9", opacity: 1, fillColor: "#efded9", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#d0d3bb":
            return { color: "#d0d3bb", opacity: 1, fillColor: "#d0d3bb", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#afc599":
            return { color: "#afc599", opacity: 1, fillColor: "#afc599", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#88bf87":
            return { color: "#88bf87", opacity: 1, fillColor: "#88bf87", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#7ab58d":
            return { color: "#7ab58d", opacity: 1, fillColor: "#7ab58d", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#6da893":
            return { color: "#6da893", opacity: 1, fillColor: "#6da893", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#59929b":
            return { color: "#59929b", opacity: 1, fillColor: "#59929b", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#568999":
            return { color: "#568999", opacity: 1, fillColor: "#568999", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#4c6497":
            return { color: "#4c6497", opacity: 1, fillColor: "#4c6497", fillOpacity: 1, weight: 0.2, fill: !0 };
        default:
            return { color: "#6c4a97", opacity: 1, fillColor: "#6c4a97", fillOpacity: 1, weight: 0.2, fill: !0 };
    }
}
function geo_json_styler_qpf(t, d) {
    switch (t.fill) {
        case "#ffffff":
            return { color: "", opacity: 0, fillColor: "", fillOpacity: 0, weight: 0.2, fill: !0 };
        case "#a9a5a5":
            return { color: "#a9a5a5", opacity: 1, fillColor: "#a9a5a5", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#6e6e6e":
            return { color: "#6e6e6e", opacity: 1, fillColor: "#6e6e6e", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#b3f9a9":
            return { color: "#b3f9a9", opacity: 1, fillColor: "#b3f9a9", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#79f572":
            return { color: "#79f572", opacity: 1, fillColor: "#79f572", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#50f150":
            return { color: "#50f150", opacity: 1, fillColor: "#50f150", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#1fb51e":
            return { color: "#1fb51e", opacity: 1, fillColor: "#1fb51e", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#0ca10d":
            return { color: "#0ca10d", opacity: 1, fillColor: "#0ca10d", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#1563d3":
            return { color: "#1563d3", opacity: 1, fillColor: "#1563d3", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#54a8f5":
            return { color: "#54a8f5", opacity: 1, fillColor: "#54a8f5", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#b4f1fb":
            return { color: "#b4f1fb", opacity: 1, fillColor: "#b4f1fb", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ffe978":
            return { color: "#ffe978", opacity: 1, fillColor: "#ffe978", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ffa100":
            return { color: "#ffa100", opacity: 1, fillColor: "#ffa100", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ff3300":
            return { color: "#ff3300", opacity: 1, fillColor: "#ff3300", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#a50000":
            return { color: "#a50000", opacity: 1, fillColor: "#a50000", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#b58d83":
            return { color: "#b58d83", opacity: 1, fillColor: "#b58d83", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#9886ba":
            return { color: "#9886ba", opacity: 1, fillColor: "#9886ba", fillOpacity: 1, weight: 0.2, fill: !0 };
        default:
            return { color: "#8d008d", opacity: 1, fillColor: "#8d008d", fillOpacity: 1, weight: 0.2, fill: !0 };
    }
}



function geo_json_styler_frp(t, d) {
    switch (t.fill) {
        case "#ffffff":
            return { color: "", opacity: 0, fillColor: "", fillOpacity: 0, weight: 0.2, fill: !0 };
        case "#fff8ba":
            return { color: "#fff8ba", opacity: 1, fillColor: "#fff8ba", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#fff0a7":
            return { color: "#fff0a7", opacity: 1, fillColor: "#fff0a7", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ffe794":
            return { color: "#ffe794", opacity: 1, fillColor: "#ffe794", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#fede81":
            return { color: "#fede81", opacity: 1, fillColor: "#fede81", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#fed16d":
            return { color: "#fed16d", opacity: 1, fillColor: "#fed16d", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#fec05b":
            return { color: "#fec05b", opacity: 1, fillColor: "#fec05b", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#feaf4b":
            return { color: "#feaf4b", opacity: 1, fillColor: "#feaf4b", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#fd9e44":
            return { color: "#fd9e44", opacity: 1, fillColor: "#fd9e44", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#fd8d3c":
            return { color: "#fd8d3c", opacity: 1, fillColor: "#fd8d3c", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#fd7134":
            return { color: "#fd7134", opacity: 1, fillColor: "#fd7134", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#fc552c":
            return { color: "#fc552c", opacity: 1, fillColor: "#fc552c", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#f43d25":
            return { color: "#f43d25", opacity: 1, fillColor: "#f43d25", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#e9261f":
            return { color: "#e9261f", opacity: 1, fillColor: "#e9261f", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#da141e":
            return { color: "#da141e", opacity: 1, fillColor: "#da141e", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#c90823":
            return { color: "#c90823", opacity: 1, fillColor: "#c90823", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#b60026":
            return { color: "#b60026", opacity: 1, fillColor: "#b60026", fillOpacity: 1, weight: 0.2, fill: !0 };
        default:
            return { color: "#9b0026", opacity: 1, fillColor: "#9b0026", fillOpacity: 1, weight: 0.2, fill: !0 };
    }
}

function geo_json_styler_snw(t, d) {
    switch (t.fill) {
        case "#ffffff":
            return { color: "", opacity: 0, fillColor: "", fillOpacity: 0, weight: 0.2, fill: !0 };
        case "#bdbdbd":
            return { color: "#bdbdbd", opacity: 1, fillColor: "#bdbdbd", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#979797":
            return { color: "#979797", opacity: 1, fillColor: "#979797", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#6e6e6e":
            return { color: "#6e6e6e", opacity: 1, fillColor: "#6e6e6e", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#4f5051":
            return { color: "#4f5051", opacity: 1, fillColor: "#4f5051", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#97d3fb":
            return { color: "#97d3fb", opacity: 1, fillColor: "#97d3fb", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#79b9fb":
            return { color: "#79b9fb", opacity: 1, fillColor: "#79b9fb", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#50a5f5":
            return { color: "#50a5f5", opacity: 1, fillColor: "#50a5f5", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#3d97f5":
            return { color: "#3d97f5", opacity: 1, fillColor: "#3d97f5", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#2883f1":
            return { color: "#2883f1", opacity: 1, fillColor: "#2883f1", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#1e6eeb":
            return { color: "#1e6eeb", opacity: 1, fillColor: "#1e6eeb", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#1563d3":
            return { color: "#1563d3", opacity: 1, fillColor: "#1563d3", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#085ac3":
            return { color: "#085ac3", opacity: 1, fillColor: "#085ac3", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#3e0291":
            return { color: "#3e0291", opacity: 1, fillColor: "#3e0291", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#4c028f":
            return { color: "#4c028f", opacity: 1, fillColor: "#4c028f", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#5a028c":
            return { color: "#5a028c", opacity: 1, fillColor: "#5a028c", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#68028b":
            return { color: "#68028b", opacity: 1, fillColor: "#68028b", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#850289":
            return { color: "#850289", opacity: 1, fillColor: "#850289", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#a00485":
            return { color: "#a00485", opacity: 1, fillColor: "#a00485", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#c90380":
            return { color: "#c90380", opacity: 1, fillColor: "#c90380", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#f3037c":
            return { color: "#f3037c", opacity: 1, fillColor: "#f3037c", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#f51485":
            return { color: "#f51485", opacity: 1, fillColor: "#f51485", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#f83b9b":
            return { color: "#f83b9b", opacity: 1, fillColor: "#f83b9b", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#fd5eae":
            return { color: "#fd5eae", opacity: 1, fillColor: "#fd5eae", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ff6eb7":
            return { color: "#ff6eb7", opacity: 1, fillColor: "#ff6eb7", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#fa85c2":
            return { color: "#fa85c2", opacity: 1, fillColor: "#fa85c2", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#f58dc6":
            return { color: "#f58dc6", opacity: 1, fillColor: "#f58dc6", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ed95cb":
            return { color: "#ed95cb", opacity: 1, fillColor: "#ed95cb", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#e79dcc":
            return { color: "#e79dcc", opacity: 1, fillColor: "#e79dcc", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#d9add4":
            return { color: "#d9add4", opacity: 1, fillColor: "#d9add4", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#d0b5d8":
            return { color: "#d0b5d8", opacity: 1, fillColor: "#d0b5d8", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#c3c7e1":
            return { color: "#c3c7e1", opacity: 1, fillColor: "#c3c7e1", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#b5d7e9":
            return { color: "#b5d7e9", opacity: 1, fillColor: "#b5d7e9", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ace2ef":
            return { color: "#ace2ef", opacity: 1, fillColor: "#ace2ef", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#a1eff3":
            return { color: "#a1eff3", opacity: 1, fillColor: "#a1eff3", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#95fbf9":
            return { color: "#95fbf9", opacity: 1, fillColor: "#95fbf9", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#92f3f1":
            return { color: "#92f3f1", opacity: 1, fillColor: "#92f3f1", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#7ddbd9":
            return { color: "#7ddbd9", opacity: 1, fillColor: "#7ddbd9", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#71bdc4":
            return { color: "#71bdc4", opacity: 1, fillColor: "#71bdc4", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#7cb9cb":
            return { color: "#7cb9cb", opacity: 1, fillColor: "#7cb9cb", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#81b7cc":
            return { color: "#81b7cc", opacity: 1, fillColor: "#81b7cc", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#85b3cf":
            return { color: "#85b3cf", opacity: 1, fillColor: "#85b3cf", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#89b1d1":
            return { color: "#89b1d1", opacity: 1, fillColor: "#89b1d1", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#90add4":
            return { color: "#90add4", opacity: 1, fillColor: "#90add4", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#94a9d8":
            return { color: "#94a9d8", opacity: 1, fillColor: "#94a9d8", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#99a6db":
            return { color: "#99a6db", opacity: 1, fillColor: "#99a6db", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#9aa5db":
            return { color: "#9aa5db", opacity: 1, fillColor: "#9aa5db", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#a3a3de":
            return { color: "#a3a3de", opacity: 1, fillColor: "#a3a3de", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#ab9ce5":
            return { color: "#ab9ce5", opacity: 1, fillColor: "#ab9ce5", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#af9be7":
            return { color: "#af9be7", opacity: 1, fillColor: "#af9be7", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#b399e8":
            return { color: "#b399e8", opacity: 1, fillColor: "#b399e8", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#b895eb":
            return { color: "#b895eb", opacity: 1, fillColor: "#b895eb", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#bb93ed":
            return { color: "#bb93ed", opacity: 1, fillColor: "#bb93ed", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#bf91f1":
            return { color: "#bf91f1", opacity: 1, fillColor: "#bf91f1", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#c38ff3":
            return { color: "#c38ff3", opacity: 1, fillColor: "#c38ff3", fillOpacity: 1, weight: 0.2, fill: !0 };
        case "#c98bf5":
            return { color: "#c98bf5", opacity: 1, fillColor: "#c98bf5", fillOpacity: 1, weight: 0.2, fill: !0 };
        default:
            return { color: "#d087f9", opacity: 1, fillColor: "#d087f9", fillOpacity: 1, weight: 0.2, fill: !0 };
    }
}
(color_map_snw.onAdd = function (t) {
    var d = L.DomUtil.create("div", "fcst-legend leaflet-bar leaflet-control");
    return (
        (d.innerHTML =
            '<table id="values"><tr id="colours"><td style="background:#ffffff; width:10px; border-left:none;"></td><td style="background:#bdbdbd;"></td><td style="background:#979797;"></td><td style="background:#6e6e6e;"></td><td style="background:#4f5051;"></td><td style="background:#97d3fb;"></td><td style="background:#79b9fb;"></td><td style="background:#50a5f5;"></td><td style="background:#3d97f5;"></td><td style="background:#2883f1;"></td><td style="background:#1e6eeb;"></td><td style="background:#1563d3;"></td><td style="background:#085ac3;"></td><td style="background:#3e0291;"></td><td style="background:#4c028f;"></td><td style="background:#5a028c;"></td><td style="background:#68028b;"></td><td style="background:#850289;"></td><td style="background:#a00485;"></td><td style="background:#c90380;"></td><td style="background:#f3037c;"></td><td style="background:#f51485;"></td><td style="background:#f83b9b;"></td><td style="background:#fd5eae;"></td><td style="background:#ff6eb7;"></td><td style="background:#fa85c2;"></td><td style="background:#f58dc6;"></td><td style="background:#ed95cb;"></td><td style="background:#e79dcc;"></td><td style="background:#d9add4;"></td><td style="background:#d0b5d8;"></td><td style="background:#c3c7e1;"></td><td style="background:#b5d7e9;"></td><td style="background:#ace2ef;"></td><td style="background:#a1eff3;"></td><td style="background:#95fbf9;"></td><td style="background:#92f3f1;"></td><td style="background:#7ddbd9;"></td><td style="background:#71bdc4;"></td><td style="background:#7cb9cb;"></td><td style="background:#81b7cc;"></td><td style="background:#85b3cf;"></td><td style="background:#89b1d1;"></td><td style="background:#90add4;"></td><td style="background:#94a9d8;"></td><td style="background:#99a6db;"></td><td style="background:#9aa5db;"></td><td style="background:#a3a3de;"></td><td style="background:#ab9ce5;"></td><td style="background:#af9be7;"></td><td style="background:#b399e8;"></td><td style="background:#b895eb;"></td><td style="background:#bb93ed;"></td><td style="background:#bf91f1;"></td><td style="background:#c38ff3;"></td><td style="background:#c98bf5;"></td><td style="background:#d087f9;"></td></tr><tr id="ticks"><td style="width:10px; border-left:none;"></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table><table id="labels"><tr><td width="2px"></td><td width="12px">0.2</td><td width="12px"></td><td width="16px">2.5</td><td width="10px"></td><td width="15px">5</td><td width="14px"></td><td width="10px">7.5</td><td width="13px"></td><td width="10px">10</td><td width="12px"></td><td width="10px">12.5</td><td width="9px"></td><td width="10px">15</td><td width="12px"></td><td width="4px">17.5</td><td width="10px"></td><td width="10px">20</td><td width="13px"></td><td width="10px">22.5</td><td width="9px"></td><td width="10px">25</td><td width="14px"></td><td width="10px">30</td><td width="16px"></td><td width="10px">35</td><td width="14px"></td><td width="10px">40</td><td width="15px"></td><td width="10px">45</td><td width="16px"></td><td width="10px">50</td><td width="15px"></td><td width="10px">55</td><td width="15px"></td><td width="10px">60</td><td width="15px"></td><td width="10px">65</td><td width="15px"></td><td width="10px">70</td><td width="15px"></td><td width="10px">75</td><td width="15px"></td><td width="10px">80</td><td width="15px"></td><td width="10px">85</td><td width="15px"></td><td width="10px">90</td><td width="15px"></td><td width="10px">95</td><td width="15px"></td><td width="10px">100</td><td width="15px"></td><td width="10px">105</td><td width="15px"></td><td width="10px">110</td><td width="1px"></td><td width="10px">140+</td></tr></table><div class="legend-title">Total Accumulated Snowfall (cm)</div>'),
        d
    );
}),
    map.on("overlayadd", function (t) {
        t.layer == wx_station && legend_wx.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == wx_station && legend_wx.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer == radar.setZIndex(550) && legend_radar.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == radar && legend_radar.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer, waqiLayer.setZIndex(600);
    }),
    map.on("overlayremove", function (t) {
        t.layer;
    }),
    map.on("overlayadd", function (t) {
        t.layer, geo_json_wd.setZIndex(700);
    }),
    map.on("overlayremove", function (t) {
        t.layer, geo_json_wd.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer == ffmcTimeLayer && color_map_ffmc.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == ffmcTimeLayer && color_map_ffmc.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer == dmcTimeLayer && color_map_dmc.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == dmcTimeLayer && color_map_dmc.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer == dcTimeLayer && color_map_dc.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == dcTimeLayer && color_map_dc.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer == isiTimeLayer && color_map_isi.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == isiTimeLayer && color_map_isi.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer == buiTimeLayer && color_map_bui.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == buiTimeLayer && color_map_bui.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer == fwiTimeLayer && color_map_fwi.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == fwiTimeLayer && color_map_fwi.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer == hfiTimeLayer && color_map_hfi.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == hfiTimeLayer && color_map_hfi.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer == rosTimeLayer && color_map_ros.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == rosTimeLayer && color_map_ros.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer == cfbTimeLayer && color_map_cfb.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == cfbTimeLayer && color_map_cfb.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer == frpTimeLayer && color_map_frp.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == frpTimeLayer && color_map_frp.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer == tfcTimeLayer && color_map_tfc.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == tfcTimeLayer && color_map_tfc.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer == wspTimeLayer && color_map_wsp.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == wspTimeLayer && color_map_wsp.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer == tempTimeLayer && color_map_temp.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == tempTimeLayer && color_map_temp.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer == rhTimeLayer && color_map_rh.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == rhTimeLayer && color_map_rh.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer == qpfTimeLayer && color_map_qpf.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == qpfTimeLayer && color_map_qpf.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer == qpf_3hTimeLayer && color_map_qpf_3h.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == qpf_3hTimeLayer && color_map_qpf_3h.remove(map);
    }),
    map.on("overlayadd", function (t) {
        t.layer == snwTimeLayer && color_map_snw.addTo(map);
    }),
    map.on("overlayremove", function (t) {
        t.layer == snwTimeLayer && color_map_snw.remove(map);
    });
