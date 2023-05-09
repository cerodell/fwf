function getColor(d) {
    return d === 'Fully Reporting'  ? "#008000" :
           d === 'Partially Reporting'  ? "#FFFF00" :
           d === 'Not Reporting' ? "#FF0000" :
                        "#008000";
}

function style(feature) {
    return {
        weight: 1.5,
        opacity: 1,
        fillOpacity: 1,
        radius: 6,
        fillColor: getColor(feature.properties.TypeOfIssue),
        color: "grey"

    };
}

var legend_wx = L.control({position: 'bottomright'});
legend_wx.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend');
    labels = ['<strong>Station Status</strong>'],
    categories = ['Fully Reporting', 'Partially Reporting', 'Not Reporting'];

    for (var i = 0; i < categories.length; i++) {

            div.innerHTML +=
            labels.push(
                '<i class="circle" style="background:' + getColor(categories[i]) + '"></i> ' +
            (categories[i] ? categories[i] : '+'));

        }
        div.innerHTML = labels.join('<br>');
    return div;
    };



var color_map_ffmc = L.control({position: "bottomleft"});
color_map_ffmc.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
    div.innerHTML =
'<table id="values">\
<tr id="colours">\
<td style="background:#000080; width:10px; border-left:none;"></td>\
<td style="background:#0000c4;"></td>\
<td style="background:#0000ff;"></td>\
<td style="background:#0034ff;"></td>\
<td style="background:#0070ff;"></td>\
<td style="background:#00acff;"></td>\
<td style="background:#02e8f4;"></td>\
<td style="background:#33ffc4;"></td>\
<td style="background:#63ff94;"></td>\
<td style="background:#94ff63;"></td>\
<td style="background:#c4ff33;"></td>\
<td style="background:#f4f802;"></td>\
<td style="background:#ffc100;"></td>\
<td style="background:#ff8900;"></td>\
<td style="background:#ff5200;"></td>\
<td style="background:#ff1a00;"></td>\
<td style="background:#c40000;"></td>\
<td style="background:#800000;"></td>\
</tr>\
<tr id="ticks">\
<td style="width:10px; border-left:none;"></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
</tr>\
</table>\
<table id="labels">\
<tr>\
<td width="10px">0</td>\
<td width="10px"></td>\
<td width="10px">60</td>\
<td width="12px"></td>\
<td width="10px">75</td>\
<td width="14px"></td>\
<td width="14px">81</td>\
<td width="14px"></td>\
<td width="10px">83</td>\
<td width="14px"></td>\
<td width="10px">85</td>\
<td width="14px"></td>\
<td width="14px">87</td>\
<td width="14px"></td>\
<td width="10px">89</td>\
<td width="14px"></td>\
<td width="10px">95</td>\
<td width="4px"></td>\
<td width="2px">100+</td>\
</tr>\
</table>\
<div class="legend-title">Fine Fuel Moisture Code</div>';
    return div;
}
color_map_ffmc.addTo(map);



var color_map_dmc = L.control({position: "bottomleft"});
color_map_dmc.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
    div.innerHTML =
'<table id="values">\
<tr id="colours">\
<td style="background:#000080; width:10px; border-left:none;"></td>\
<td style="background:#0000c4;"></td>\
<td style="background:#0000ff;"></td>\
<td style="background:#0034ff;"></td>\
<td style="background:#0070ff;"></td>\
<td style="background:#00acff;"></td>\
<td style="background:#02e8f4;"></td>\
<td style="background:#33ffc4;"></td>\
<td style="background:#63ff94;"></td>\
<td style="background:#94ff63;"></td>\
<td style="background:#c4ff33;"></td>\
<td style="background:#f4f802;"></td>\
<td style="background:#ffc100;"></td>\
<td style="background:#ff8900;"></td>\
<td style="background:#ff5200;"></td>\
<td style="background:#ff1a00;"></td>\
<td style="background:#c40000;"></td>\
<td style="background:#800000;"></td>\
</tr>\
<tr id="ticks">\
<td style="width:10px; border-left:none;"></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
</tr>\
</table>\
<table id="labels">\
<tr>\
<td width="2px">0</td>\
<td width="14px"></td>\
<td width="10px">7</td>\
<td width="14px"></td>\
<td width="10px">14</td>\
<td width="14px"></td>\
<td width="14px">21</td>\
<td width="14px"></td>\
<td width="10px">28</td>\
<td width="14px"></td>\
<td width="12px">35</td>\
<td width="12px"></td>\
<td width="14px">43</td>\
<td width="14px"></td>\
<td width="10px">50</td>\
<td width="16px"></td>\
<td width="10px">60</td>\
<td width="3px"></td>\
<td width="5px">70+</td>\
</tr>\
</table>\
<div class="legend-title">Duff Moisture Code</div>';
    return div;
}

var color_map_dc = L.control({position: "bottomleft"});
color_map_dc.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
    div.innerHTML =
'<table id="values">\
<tr id="colours">\
<td style="background:#000080; width:10px; border-left:none;"></td>\
<td style="background:#0000c4;"></td>\
<td style="background:#0000ff;"></td>\
<td style="background:#0034ff;"></td>\
<td style="background:#0070ff;"></td>\
<td style="background:#00acff;"></td>\
<td style="background:#02e8f4;"></td>\
<td style="background:#33ffc4;"></td>\
<td style="background:#63ff94;"></td>\
<td style="background:#94ff63;"></td>\
<td style="background:#c4ff33;"></td>\
<td style="background:#f4f802;"></td>\
<td style="background:#ffc100;"></td>\
<td style="background:#ff8900;"></td>\
<td style="background:#ff5200;"></td>\
<td style="background:#ff1a00;"></td>\
<td style="background:#c40000;"></td>\
<td style="background:#800000;"></td>\
</tr>\
<tr id="ticks">\
<td style="width:10px; border-left:none;"></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
</tr>\
</table>\
<table id="labels">\
<tr>\
<td width="0px">40</td>\
<td width="8px"></td>\
<td width="9px">82</td>\
<td width="12px"></td>\
<td width="15px">124</td>\
<td width="9px"></td>\
<td width="5px">167</td>\
<td width="8px"></td>\
<td width="5px">209</td>\
<td width="8px"></td>\
<td width="5px">252</td>\
<td width="9px"></td>\
<td width="5px">294</td>\
<td width="9px"></td>\
<td width="14px">337</td>\
<td width="9px"></td>\
<td width="5px">400</td>\
<td width="5px"></td>\
<td width="5px">480+</td>\
</tr>\
</table>\
<div class="legend-title">Drought Code</div>';
    return div;
}

var color_map_isi = L.control({position: "bottomleft"});
color_map_isi.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
    div.innerHTML =
'<table id="values">\
<tr id="colours">\
<td style="background:#000080; width:10px; border-left:none;"></td>\
<td style="background:#0000c4;"></td>\
<td style="background:#0000ff;"></td>\
<td style="background:#0034ff;"></td>\
<td style="background:#0070ff;"></td>\
<td style="background:#00acff;"></td>\
<td style="background:#02e8f4;"></td>\
<td style="background:#33ffc4;"></td>\
<td style="background:#63ff94;"></td>\
<td style="background:#94ff63;"></td>\
<td style="background:#c4ff33;"></td>\
<td style="background:#f4f802;"></td>\
<td style="background:#ffc100;"></td>\
<td style="background:#ff8900;"></td>\
<td style="background:#ff5200;"></td>\
<td style="background:#ff1a00;"></td>\
<td style="background:#c40000;"></td>\
<td style="background:#800000;"></td>\
</tr>\
<tr id="ticks">\
<td style="width:10px; border-left:none;"></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
</tr>\
</table>\
<table id="labels">\
<tr>\
<td width="2px">0</td>\
<td width="10px"></td>\
<td width="10px">1.8</td>\
<td width="12px"></td>\
<td width="10px">3.7</td>\
<td width="12px"></td>\
<td width="6px">5.6</td>\
<td width="12px"></td>\
<td width="6px">7.5</td>\
<td width="12px"></td>\
<td width="6px">9.4</td>\
<td width="12px"></td>\
<td width="6px">11.3</td>\
<td width="7px"></td>\
<td width="6px">13.2</td>\
<td width="4px"></td>\
<td width="4px">15.0</td>\
<td width="2px"></td>\
<td width="2px">16.0+</td>\
</tr>\
</table>\
<div class="legend-title">Initial Spread Index</div>';
    return div;
}

var color_map_bui = L.control({position: "bottomleft"});
color_map_bui.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
    div.innerHTML =
'<table id="values">\
<tr id="colours">\
<td style="background:#000080; width:10px; border-left:none;"></td>\
<td style="background:#0000c4;"></td>\
<td style="background:#0000ff;"></td>\
<td style="background:#0034ff;"></td>\
<td style="background:#0070ff;"></td>\
<td style="background:#00acff;"></td>\
<td style="background:#02e8f4;"></td>\
<td style="background:#33ffc4;"></td>\
<td style="background:#63ff94;"></td>\
<td style="background:#94ff63;"></td>\
<td style="background:#c4ff33;"></td>\
<td style="background:#f4f802;"></td>\
<td style="background:#ffc100;"></td>\
<td style="background:#ff8900;"></td>\
<td style="background:#ff5200;"></td>\
<td style="background:#ff1a00;"></td>\
<td style="background:#c40000;"></td>\
<td style="background:#800000;"></td>\
</tr>\
<tr id="ticks">\
<td style="width:10px; border-left:none;"></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
</tr>\
</table>\
<table id="labels">\
<tr>\
<td width="2px">0</td>\
<td width="10px"></td>\
<td width="10px">10</td>\
<td width="17px"></td>\
<td width="10px">21</td>\
<td width="14px"></td>\
<td width="14px">32</td>\
<td width="12px"></td>\
<td width="10px">42</td>\
<td width="15px"></td>\
<td width="12px">53</td>\
<td width="15px"></td>\
<td width="10px">64</td>\
<td width="14px"></td>\
<td width="12px">74</td>\
<td width="14px"></td>\
<td width="12px">95</td>\
<td width="1px"></td>\
<td width="1px">115+</td>\
</tr>\
</table>\
<div class="legend-title">Build Up Index</div>';
    return div;
}

var color_map_fwi = L.control({position: "bottomleft"});
color_map_fwi.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
    div.innerHTML =
'<table id="values">\
<tr id="colours">\
<td style="background:#000080; width:10px; border-left:none;"></td>\
<td style="background:#0000c4;"></td>\
<td style="background:#0000ff;"></td>\
<td style="background:#0034ff;"></td>\
<td style="background:#0070ff;"></td>\
<td style="background:#00acff;"></td>\
<td style="background:#02e8f4;"></td>\
<td style="background:#33ffc4;"></td>\
<td style="background:#63ff94;"></td>\
<td style="background:#94ff63;"></td>\
<td style="background:#c4ff33;"></td>\
<td style="background:#f4f802;"></td>\
<td style="background:#ffc100;"></td>\
<td style="background:#ff8900;"></td>\
<td style="background:#ff5200;"></td>\
<td style="background:#ff1a00;"></td>\
<td style="background:#c40000;"></td>\
<td style="background:#800000;"></td>\
</tr>\
<tr id="ticks">\
<td style="width:10px; border-left:none;"></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
</tr>\
</table>\
<table id="labels">\
<tr>\
<td width="2px">0</td>\
<td width="12px"></td>\
<td width="10px">3</td>\
<td width="14px"></td>\
<td width="14px">7</td>\
<td width="14px"></td>\
<td width="10px">10</td>\
<td width="14px"></td>\
<td width="10px">14</td>\
<td width="14px"></td>\
<td width="10px">18</td>\
<td width="14px"></td>\
<td width="16px">21</td>\
<td width="14px"></td>\
<td width="10px">25</td>\
<td width="14px"></td>\
<td width="10px">30</td>\
<td width="2px"></td>\
<td width="2px">40+</td>\
</tr>\
</table>\
<div class="legend-title">Fire Weather Index</div>';
    return div;
}



var color_map_hfi = L.control({position: "bottomleft"});
color_map_hfi.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
    div.innerHTML =
'<table id="values">\
<tr id="colours">\
<td style="background:#0000ff; width:30px; border-left:none;"></td>\
<td style="background:#00c0c0; width:30px;"></td>\
<td style="background:#008001; width:30px;"></td>\
<td style="background:#01e001; width:30px;"></td>\
<td style="background:#ffff00; width:30px;"></td>\
<td style="background:#dfa000; width:30px;"></td>\
<td style="background:#ff0000; width:30px;"></td>\
<td style="background:#8b0000; width:30px;"></td>\
</tr>\
<tr id="ticks">\
<td style="width:10px; border-left:none;"></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
</tr>\
</table>\
<table id="labels">\
<tr>\
<td width="2px">0</td>\
<td width="45px">10</td>\
<td width="20px">500</td>\
<td width="40px">2000</td>\
<td width="28px">4000</td>\
<td width="30px">10000</td>\
<td width="30px">30000</td>\
<td width="38px">40000+</td>\
</tr>\
</table>\
<div class="legend-title">Head Fire Intensity (kW/m)</div>';
    return div;
}


var color_map_ros = L.control({position: "bottomleft"});
color_map_ros.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
    div.innerHTML =
'<table id="values">\
<tr id="colours">\
<td style="background:#0000ff; width:30px; border-left:none;"></td>\
<td style="background:#008001; width:30px;"></td>\
<td style="background:#01e001; width:30px;"></td>\
<td style="background:#ffff00; width:30px;"></td>\
<td style="background:#dfa000; width:30px;"></td>\
<td style="background:#ff0000; width:30px;"></td>\
<td style="background:#8b0000; width:30px;"></td>\
</tr>\
<tr id="ticks">\
<td style="width:10px; border-left:none;"></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
</tr>\
</table>\
<table id="labels">\
<tr>\
<td width="2px">0</td>\
<td width="43px">1</td>\
<td width="23px">3</td>\
<td width="36px">10</td>\
<td width="30px">18</td>\
<td width="34px">25</td>\
<td width="35px">40+</td>\
</tr>\
</table>\
<div class="legend-title">Rate of Spread (m/min)</div>';
    return div;
}


var color_map_cfb = L.control({position: "bottomleft"});
color_map_cfb.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
    div.innerHTML =
'<table id="values">\
<tr id="colours">\
<td style="background:#0000ff; width:30px; border-left:none;"></td>\
<td style="background:#008001; width:30px;"></td>\
<td style="background:#01e001; width:30px;"></td>\
<td style="background:#ffff00; width:30px;"></td>\
<td style="background:#dfa000; width:30px;"></td>\
<td style="background:#ff0000; width:30px;"></td>\
</tr>\
<tr id="ticks">\
<td style="width:10px; border-left:none;"></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
</tr>\
</table>\
<table id="labels">\
<tr>\
<td width="2px">0</td>\
<td width="43px">10</td>\
<td width="23px">30</td>\
<td width="36px">50</td>\
<td width="30px">70</td>\
<td width="30px">90</td>\
<td width="32px">100</td>\
</tr>\
</table>\
<div class="legend-title">Crown Fraction Burned (%)</div>';
    return div;
}


var color_map_sfc = L.control({position: "bottomleft"});
color_map_sfc.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
    div.innerHTML =
'<table id="values">\
<tr id="colours">\
<td style="background:#0000ff; width:30px; border-left:none;"></td>\
<td style="background:#008001; width:30px;"></td>\
<td style="background:#01e001; width:30px;"></td>\
<td style="background:#ffff00; width:30px;"></td>\
<td style="background:#dfa000; width:30px;"></td>\
<td style="background:#ff0000; width:30px;"></td>\
<td style="background:#8b0000; width:30px;"></td>\
</tr>\
<tr id="ticks">\
<td style="width:10px; border-left:none;"></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
</tr>\
</table>\
<table id="labels">\
<tr>\
<td width="2px">0</td>\
<td width="46px">1</td>\
<td width="17px">2</td>\
<td width="44px">3</td>\
<td width="18px">4</td>\
<td width="44px">5</td>\
<td width="26px">6+</td>\
</tr>\
</table>\
<div class="legend-title">Surface Fuel Consumption (kg/m<sup>2</sup>)</div>';
    return div;
}


var color_map_tfc = L.control({position: "bottomleft"});
color_map_tfc.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
    div.innerHTML =
'<table id="values">\
<tr id="colours">\
<td style="background:#0000ff; width:30px; border-left:none;"></td>\
<td style="background:#008001; width:30px;"></td>\
<td style="background:#01e001; width:30px;"></td>\
<td style="background:#ffff00; width:30px;"></td>\
<td style="background:#dfa000; width:30px;"></td>\
<td style="background:#ff0000; width:30px;"></td>\
<td style="background:#8b0000; width:30px;"></td>\
</tr>\
<tr id="ticks">\
<td style="width:10px; border-left:none;"></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
</tr>\
</table>\
<table id="labels">\
<tr>\
<td width="2px">0</td>\
<td width="46px">2</td>\
<td width="17px">4</td>\
<td width="44px">6</td>\
<td width="18px">8</td>\
<td width="44px">10</td>\
<td width="26px">12+</td>\
</tr>\
</table>\
<div class="legend-title">Total Fuel Consumption (kg/m<sup>2</sup>)</div>';
    return div;
}

var color_map_wsp = L.control({position: "bottomleft"});
color_map_wsp.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
    div.innerHTML =
'<table id="values">\
<tr id="colours">\
<td style="background:#FFFFFF; width:10px; border-left:none;"></td>\
<td style="background:#BBBBBB;"></td>\
<td style="background:#646464;"></td>\
<td style="background:#1563D3;"></td>\
<td style="background:#2883F1;"></td>\
<td style="background:#50A5F5;"></td>\
<td style="background:#97D3FB;"></td>\
<td style="background:#0CA10D;"></td>\
<td style="background:#37D33C;"></td>\
<td style="background:#97F58D;"></td>\
<td style="background:#B5FBAB;"></td>\
<td style="background:#FFE978;"></td>\
<td style="background:#FFC03D;"></td>\
<td style="background:#FFA100;"></td>\
<td style="background:#FF3300;"></td>\
<td style="background:#C10000;"></td>\
<td style="background:#960007;"></td>\
<td style="background:#643C32;"></td>\
</tr>\
<tr id="ticks">\
<td style="width:10px; border-left:none;"></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
</tr>\
</table>\
<table id="labels">\
<tr>\
<td width="2px">0</td>\
<td width="12px"></td>\
<td width="8px">20</td>\
<td width="15px"></td>\
<td width="10px">28</td>\
<td width="14px"></td>\
<td width="10px">32</td>\
<td width="15px"></td>\
<td width="10px">40</td>\
<td width="16px"></td>\
<td width="10px">48</td>\
<td width="16px"></td>\
<td width="10px">56</td>\
<td width="16px"></td>\
<td width="10px">64</td>\
<td width="14px"></td>\
<td width="10px">72</td>\
<td width="2px"></td>\
<td width="2px">80+</td>\
</tr>\
</table>\
<div class="legend-title">Wind Speed (km/hr) at 10m</div>';
    return div;
}

// var color_map_temp = L.control({position: "bottomleft"});
// color_map_temp.onAdd = function(map) {
//     var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
//     div.innerHTML =
// '<table id="values">\
// <tr id="colours">\
// <td style="background:#1b34d7; width:10px; border-left:none;"></td>\
// <td style="background:#2460e2;"></td>\
// <td style="background:#348ced;"></td>\
// <td style="background:#44b1f6;"></td>\
// <td style="background:#51cbfa;"></td>\
// <td style="background:#80e0f7;"></td>\
// <td style="background:#a0eaf7;"></td>\
// <td style="background:#00efbb;"></td>\
// <td style="background:#00ef7c;"></td>\
// <td style="background:#00e452;"></td>\
// <td style="background:#00c848;"></td>\
// <td style="background:#10b87a;"></td>\
// <td style="background:#297b5d;"></td>\
// <td style="background:#007229;"></td>\
// <td style="background:#3ca12c;"></td>\
// <td style="background:#79d030;"></td>\
// <td style="background:#b5ff32;"></td>\
// <td style="background:#d6ff32;"></td>\
// <td style="background:#fff600;"></td>\
// <td style="background:#f8df0b;"></td>\
// <td style="background:#fdca0c;"></td>\
// <td style="background:#fcac05;"></td>\
// <td style="background:#f88d00;"></td>\
// <td style="background:#ff6600;"></td>\
// <td style="background:#fc4f00;"></td>\
// <td style="background:#ff0100;"></td>\
// </tr>\
// <tr id="ticks">\
// <td style="width:10px; border-left:none;"></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// <td></td>\
// </tr>\
// </table>\
// <table id="labels">\
// <tr>\
// <td width="2px"></td>\
// <td width="1px">-12</td>\
// <td width="12px"></td>\
// <td width="10px">-8</td>\
// <td width="16px"></td>\
// <td width="10px">-4</td>\
// <td width="18px"></td>\
// <td width="10px">0</td>\
// <td width="16px"></td>\
// <td width="10px">4</td>\
// <td width="16px"></td>\
// <td width="10px">8</td>\
// <td width="16px"></td>\
// <td width="10px">12</td>\
// <td width="16px"></td>\
// <td width="10px">16</td>\
// <td width="14px"></td>\
// <td width="10px">20</td>\
// <td width="15px"></td>\
// <td width="10px">24</td>\
// <td width="15px"></td>\
// <td width="10px">28</td>\
// <td width="16px"></td>\
// <td width="10px">32</td>\
// <td width="13px"></td>\
// <td width="10px">36+</td>\
// <td width="10px"></td>\
// </tr>\
// </table>\
// <div class="legend-title">Temperature (C) at 2m</div>';
//     return div;
// }

var color_map_temp = L.control({position: "bottomleft"});
color_map_temp.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
    div.innerHTML =
'<table id="values">\
<tr id="colours">\
<td style="background:#00ffff; width:10px; border-left:none;"></td>\
<td style="background:#06e6ed;"></td>\
<td style="background:#0bcddb;"></td>\
<td style="background:#10b5ca;"></td>\
<td style="background:#159eb9;"></td>\
<td style="background:#1b86a8;"></td>\
<td style="background:#206f97;"></td>\
<td style="background:#255987;"></td>\
<td style="background:#2a4276;"></td>\
<td style="background:#2f2a65;"></td>\
<td style="background:#360a4e;"></td>\
<td style="background:#560b69;"></td>\
<td style="background:#7b0c88;"></td>\
<td style="background:#a30ca8;"></td>\
<td style="background:#ce0bdc;"></td>\
<td style="background:#af05e3;"></td>\
<td style="background:#8904e1;"></td>\
<td style="background:#5d04d8;"></td>\
<td style="background:#1c0dcf;"></td>\
<td style="background:#1b34d7;"></td>\
<td style="background:#2460e2;"></td>\
<td style="background:#348ced;"></td>\
<td style="background:#44b1f6;"></td>\
<td style="background:#51cbfa;"></td>\
<td style="background:#80e0f7;"></td>\
<td style="background:#a0eaf7;"></td>\
<td style="background:#00ef7c;"></td>\
<td style="background:#00e452;"></td>\
<td style="background:#00c848;"></td>\
<td style="background:#10b87a;"></td>\
<td style="background:#297b5d;"></td>\
<td style="background:#007229;"></td>\
<td style="background:#3ca12c;"></td>\
<td style="background:#79d030;"></td>\
<td style="background:#b5ff33;"></td>\
<td style="background:#d8f7a1;"></td>\
<td style="background:#fff600;"></td>\
<td style="background:#f8df0b;"></td>\
<td style="background:#fdca0c;"></td>\
<td style="background:#fcac05;"></td>\
<td style="background:#f88d00;"></td>\
<td style="background:#ff6600;"></td>\
<td style="background:#fc4f00;"></td>\
<td style="background:#ff0100;"></td>\
<td style="background:#f31a00;"></td>\
<td style="background:#f31861;"></td>\
<td style="background:#f316c2;"></td>\
</tr>\
<tr id="ticks">\
<td style="width:10px; border-left:none;"></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
</tr>\
</table>\
<table id="labels">\
<tr>\
<td width="1px"></td>\
<td width="10px">-75</td>\
<td width="10px"></td>\
<td width="10px">-65</td>\
<td width="12px"></td>\
<td width="10px">-55</td>\
<td width="11px"></td>\
<td width="10px">-45</td>\
<td width="14px"></td>\
<td width="10px">35</td>\
<td width="12px"></td>\
<td width="10px">-30</td>\
<td width="11px"></td>\
<td width="10px">-26</td>\
<td width="10px"></td>\
<td width="10px">-22</td>\
<td width="11px"></td>\
<td width="10px">-18</td>\
<td width="12px"></td>\
<td width="10px">-14</td>\
<td width="12px"></td>\
<td width="10px">-10</td>\
<td width="12px"></td>\
<td width="10px">-6</td>\
<td width="17px"></td>\
<td width="10px">-2</td>\
<td width="17px"></td>\
<td width="10px">2</td>\
<td width="16px"></td>\
<td width="10px">6</td>\
<td width="16px"></td>\
<td width="10px">10</td>\
<td width="16px"></td>\
<td width="10px">14</td>\
<td width="14px"></td>\
<td width="10px">18</td>\
<td width="15px"></td>\
<td width="10px">22</td>\
<td width="15px"></td>\
<td width="10px">26</td>\
<td width="17px"></td>\
<td width="10px">30</td>\
<td width="14px"></td>\
<td width="10px">34</td>\
<td width="14px"></td>\
<td width="10px">38</td>\
<td width="10px"></td>\
<td width="10px">42+</td>\
</tr>\
</table>\
<div class="legend-title">Temperature (C) at 2m</div>';
    return div;
}
var color_map_rh = L.control({position: "bottomleft"});
color_map_rh.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
    div.innerHTML =
'<table id="values">\
<tr id="colours">\
<td style="background:#442d15; width:10px; border-left:none;"></td>\
<td style="background:#653f1f;"></td>\
<td style="background:#815228;"></td>\
<td style="background:#9d622f;"></td>\
<td style="background:#ad7644;"></td>\
<td style="background:#b98b5c;"></td>\
<td style="background:#c7a074;"></td>\
<td style="background:#e1cdb3;"></td>\
<td style="background:#efded9;"></td>\
<td style="background:#d0d3bb;"></td>\
<td style="background:#afc599;"></td>\
<td style="background:#88bf87;"></td>\
<td style="background:#7ab58d;"></td>\
<td style="background:#6da893;"></td>\
<td style="background:#59929b;"></td>\
<td style="background:#568999;"></td>\
<td style="background:#4c6497;"></td>\
<td style="background:#6c4a97;"></td>\
</tr>\
<tr id="ticks">\
<td style="width:10px; border-left:none;"></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
</tr>\
</table>\
<table id="labels">\
<tr>\
<td width="2px">0</td>\
<td width="12px"></td>\
<td width="10px">2</td>\
<td width="16px"></td>\
<td width="10px">5</td>\
<td width="16px"></td>\
<td width="10px">15</td>\
<td width="16px"></td>\
<td width="10px">30</td>\
<td width="14px"></td>\
<td width="10px">50</td>\
<td width="15px"></td>\
<td width="10px">70</td>\
<td width="14px"></td>\
<td width="10px">90</td>\
<td width="16px"></td>\
<td width="10px">97</td>\
<td width="2px"></td>\
<td width="10px">100+</td>\
</tr>\
</table>\
<div class="legend-title">Relative Humidity (%) at 2m</div>';
    return div;
}

var color_map_qpf = L.control({position: "bottomleft"});
color_map_qpf.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
    div.innerHTML =
'<table id="values">\
<tr id="colours">\
<td style="background:#ffffff; width:10px; border-left:none;"></td>\
<td style="background:#a9a5a5;"></td>\
<td style="background:#6e6e6e;"></td>\
<td style="background:#b3f9a9;"></td>\
<td style="background:#79f572;"></td>\
<td style="background:#50f150;"></td>\
<td style="background:#1fb51e;"></td>\
<td style="background:#0ca10d;"></td>\
<td style="background:#1563d3;"></td>\
<td style="background:#54a8f5;"></td>\
<td style="background:#b4f1fb;"></td>\
<td style="background:#ffe978;"></td>\
<td style="background:#ffa100;"></td>\
<td style="background:#ff3300;"></td>\
<td style="background:#a50000;"></td>\
<td style="background:#b58d83;"></td>\
<td style="background:#9886ba;"></td>\
<td style="background:#8d008d;"></td>\
</tr>\
<tr id="ticks">\
<td style="width:10px; border-left:none;"></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
</tr>\
</table>\
<table id="labels">\
<tr>\
<td width="2px">0</td>\
<td width="12px"></td>\
<td width="10px">1</td>\
<td width="16px"></td>\
<td width="10px">3</td>\
<td width="15px"></td>\
<td width="10px">10</td>\
<td width="16px"></td>\
<td width="10px">20</td>\
<td width="15px"></td>\
<td width="10px">30</td>\
<td width="15px"></td>\
<td width="10px">50</td>\
<td width="15px"></td>\
<td width="10px">70</td>\
<td width="12px"></td>\
<td width="4px">100</td>\
<td width="2px"></td>\
<td width="2px">140+</td>\
</tr>\
</table>\
<div class="legend-title">Total Accumulated Precipitation (mm)</div>';
    return div;
}

var color_map_qpf_3h = L.control({position: "bottomleft"});
color_map_qpf_3h.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
    div.innerHTML =
'<table id="values">\
<tr id="colours">\
<td style="background:#ffffff; width:10px; border-left:none;"></td>\
<td style="background:#a9a5a5;"></td>\
<td style="background:#6e6e6e;"></td>\
<td style="background:#b3f9a9;"></td>\
<td style="background:#79f572;"></td>\
<td style="background:#50f150;"></td>\
<td style="background:#1fb51e;"></td>\
<td style="background:#0ca10d;"></td>\
<td style="background:#1563d3;"></td>\
<td style="background:#54a8f5;"></td>\
<td style="background:#b4f1fb;"></td>\
<td style="background:#ffe978;"></td>\
<td style="background:#ffa100;"></td>\
<td style="background:#ff3300;"></td>\
<td style="background:#a50000;"></td>\
<td style="background:#b58d83;"></td>\
<td style="background:#9886ba;"></td>\
<td style="background:#8d008d;"></td>\
</tr>\
<tr id="ticks">\
<td style="width:10px; border-left:none;"></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
</tr>\
</table>\
<table id="labels">\
<tr>\
<td width="2px">0</td>\
<td width="12px"></td>\
<td width="10px">1</td>\
<td width="16px"></td>\
<td width="10px">3</td>\
<td width="15px"></td>\
<td width="10px">10</td>\
<td width="16px"></td>\
<td width="10px">20</td>\
<td width="15px"></td>\
<td width="10px">30</td>\
<td width="15px"></td>\
<td width="10px">50</td>\
<td width="15px"></td>\
<td width="10px">70</td>\
<td width="12px"></td>\
<td width="4px">100</td>\
<td width="2px"></td>\
<td width="2px">140+</td>\
</tr>\
</table>\
<div class="legend-title">3 Hour Accumulated Precipitation (mm)</div>';
    return div;
}


var color_map_snw = L.control({position: "bottomleft"});
color_map_snw.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
    div.innerHTML =
'<table id="values">\
<tr id="colours">\
<td style="background:#ffffff; width:10px; border-left:none;"></td>\
<td style="background:#bdbdbd;"></td>\
<td style="background:#979797;"></td>\
<td style="background:#6e6e6e;"></td>\
<td style="background:#4f5051;"></td>\
<td style="background:#97d3fb;"></td>\
<td style="background:#79b9fb;"></td>\
<td style="background:#50a5f5;"></td>\
<td style="background:#3d97f5;"></td>\
<td style="background:#2883f1;"></td>\
<td style="background:#1e6eeb;"></td>\
<td style="background:#1563d3;"></td>\
<td style="background:#085ac3;"></td>\
<td style="background:#3e0291;"></td>\
<td style="background:#4c028f;"></td>\
<td style="background:#5a028c;"></td>\
<td style="background:#68028b;"></td>\
<td style="background:#850289;"></td>\
<td style="background:#a00485;"></td>\
<td style="background:#c90380;"></td>\
<td style="background:#f3037c;"></td>\
<td style="background:#f51485;"></td>\
<td style="background:#f83b9b;"></td>\
<td style="background:#fd5eae;"></td>\
<td style="background:#ff6eb7;"></td>\
<td style="background:#fa85c2;"></td>\
<td style="background:#f58dc6;"></td>\
<td style="background:#ed95cb;"></td>\
<td style="background:#e79dcc;"></td>\
<td style="background:#d9add4;"></td>\
<td style="background:#d0b5d8;"></td>\
<td style="background:#c3c7e1;"></td>\
<td style="background:#b5d7e9;"></td>\
<td style="background:#ace2ef;"></td>\
<td style="background:#a1eff3;"></td>\
<td style="background:#95fbf9;"></td>\
<td style="background:#92f3f1;"></td>\
<td style="background:#7ddbd9;"></td>\
<td style="background:#71bdc4;"></td>\
<td style="background:#7cb9cb;"></td>\
<td style="background:#81b7cc;"></td>\
<td style="background:#85b3cf;"></td>\
<td style="background:#89b1d1;"></td>\
<td style="background:#90add4;"></td>\
<td style="background:#94a9d8;"></td>\
<td style="background:#99a6db;"></td>\
<td style="background:#9aa5db;"></td>\
<td style="background:#a3a3de;"></td>\
<td style="background:#ab9ce5;"></td>\
<td style="background:#af9be7;"></td>\
<td style="background:#b399e8;"></td>\
<td style="background:#b895eb;"></td>\
<td style="background:#bb93ed;"></td>\
<td style="background:#bf91f1;"></td>\
<td style="background:#c38ff3;"></td>\
<td style="background:#c98bf5;"></td>\
<td style="background:#d087f9;"></td>\
</tr>\
<tr id="ticks">\
<td style="width:10px; border-left:none;"></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
<td></td>\
</tr>\
</table>\
<table id="labels">\
<tr>\
<td width="2px"></td>\
<td width="12px">0.2</td>\
<td width="12px"></td>\
<td width="16px">2.5</td>\
<td width="10px"></td>\
<td width="15px">5</td>\
<td width="14px"></td>\
<td width="10px">7.5</td>\
<td width="13px"></td>\
<td width="10px">10</td>\
<td width="12px"></td>\
<td width="10px">12.5</td>\
<td width="9px"></td>\
<td width="10px">15</td>\
<td width="12px"></td>\
<td width="4px">17.5</td>\
<td width="10px"></td>\
<td width="10px">20</td>\
<td width="13px"></td>\
<td width="10px">22.5</td>\
<td width="9px"></td>\
<td width="10px">25</td>\
<td width="14px"></td>\
<td width="10px">30</td>\
<td width="16px"></td>\
<td width="10px">35</td>\
<td width="14px"></td>\
<td width="10px">40</td>\
<td width="15px"></td>\
<td width="10px">45</td>\
<td width="16px"></td>\
<td width="10px">50</td>\
<td width="15px"></td>\
<td width="10px">55</td>\
<td width="15px"></td>\
<td width="10px">60</td>\
<td width="15px"></td>\
<td width="10px">65</td>\
<td width="15px"></td>\
<td width="10px">70</td>\
<td width="15px"></td>\
<td width="10px">75</td>\
<td width="15px"></td>\
<td width="10px">80</td>\
<td width="15px"></td>\
<td width="10px">85</td>\
<td width="15px"></td>\
<td width="10px">90</td>\
<td width="15px"></td>\
<td width="10px">95</td>\
<td width="15px"></td>\
<td width="10px">100</td>\
<td width="15px"></td>\
<td width="10px">105</td>\
<td width="15px"></td>\
<td width="10px">110</td>\
<td width="1px"></td>\
<td width="10px">140+</td>\
</tr>\
</table>\
<div class="legend-title">Total Accumulated Snowfall (cm)</div>';
    return div;
}


map.on('overlayadd', function (eventLayer) {
    if (eventLayer.layer == wx_station) {
        legend_wx.addTo(map);
    }});
map.on('overlayremove', function (eventLayer) {
if (eventLayer.layer == wx_station) {
    legend_wx.remove(map);
}});

map.on('overlayadd', function (eventLayer) {
if (eventLayer.layer == ffmcTimeLayer) {
    color_map_ffmc.addTo(map);
}});
map.on('overlayremove', function (eventLayer) {
if (eventLayer.layer == ffmcTimeLayer) {
    color_map_ffmc.remove(map);
}});

map.on('overlayadd', function (eventLayer) {
    if (eventLayer.layer == dmcTimeLayer) {
        color_map_dmc.addTo(map);
    }});
map.on('overlayremove', function (eventLayer) {
if (eventLayer.layer == dmcTimeLayer) {
    color_map_dmc.remove(map);
}});

map.on('overlayadd', function (eventLayer) {
    if (eventLayer.layer == dcTimeLayer) {
        color_map_dc.addTo(map);
    }});
map.on('overlayremove', function (eventLayer) {
if (eventLayer.layer == dcTimeLayer) {
    color_map_dc.remove(map);
}});

map.on('overlayadd', function (eventLayer) {
    if (eventLayer.layer == isiTimeLayer) {
        color_map_isi.addTo(map);
    }});
map.on('overlayremove', function (eventLayer) {
if (eventLayer.layer == isiTimeLayer) {
    color_map_isi.remove(map);
}});


map.on('overlayadd', function (eventLayer) {
    if (eventLayer.layer == buiTimeLayer) {
        color_map_bui.addTo(map);
    }});
map.on('overlayremove', function (eventLayer) {
if (eventLayer.layer == buiTimeLayer) {
    color_map_bui.remove(map);
}});

map.on('overlayadd', function (eventLayer) {
    if (eventLayer.layer == fwiTimeLayer) {
        color_map_fwi.addTo(map);
    }});
map.on('overlayremove', function (eventLayer) {
if (eventLayer.layer == fwiTimeLayer) {
    color_map_fwi.remove(map);
}});

map.on('overlayadd', function (eventLayer) {
    if (eventLayer.layer == hfiTimeLayer) {
        color_map_hfi.addTo(map);
    }});
map.on('overlayremove', function (eventLayer) {
if (eventLayer.layer == hfiTimeLayer) {
    color_map_hfi.remove(map);
}});

map.on('overlayadd', function (eventLayer) {
    if (eventLayer.layer == rosTimeLayer) {
        color_map_ros.addTo(map);
    }});
map.on('overlayremove', function (eventLayer) {
if (eventLayer.layer == rosTimeLayer) {
    color_map_ros.remove(map);
}});

map.on('overlayadd', function (eventLayer) {
    if (eventLayer.layer == cfbTimeLayer) {
        color_map_cfb.addTo(map);
    }});
map.on('overlayremove', function (eventLayer) {
if (eventLayer.layer == cfbTimeLayer) {
    color_map_cfb.remove(map);
}});

map.on('overlayadd', function (eventLayer) {
    if (eventLayer.layer == sfcTimeLayer) {
        color_map_sfc.addTo(map);
    }});
map.on('overlayremove', function (eventLayer) {
if (eventLayer.layer == sfcTimeLayer) {
    color_map_sfc.remove(map);
}});

map.on('overlayadd', function (eventLayer) {
    if (eventLayer.layer == tfcTimeLayer) {
        color_map_tfc.addTo(map);
    }});
map.on('overlayremove', function (eventLayer) {
if (eventLayer.layer == tfcTimeLayer) {
    color_map_tfc.remove(map);
}});


map.on('overlayadd', function (eventLayer) {
    if (eventLayer.layer == wspTimeLayer) {
        color_map_wsp.addTo(map);
    }});
map.on('overlayremove', function (eventLayer) {
if (eventLayer.layer == wspTimeLayer) {
    color_map_wsp.remove(map);
}});

map.on('overlayadd', function (eventLayer) {
    if (eventLayer.layer == tempTimeLayer) {
        color_map_temp.addTo(map);
    }});
map.on('overlayremove', function (eventLayer) {
if (eventLayer.layer == tempTimeLayer) {
    color_map_temp.remove(map);
}});

map.on('overlayadd', function (eventLayer) {
    if (eventLayer.layer == rhTimeLayer) {
        color_map_rh.addTo(map);
    }});
map.on('overlayremove', function (eventLayer) {
if (eventLayer.layer == rhTimeLayer) {
    color_map_rh.remove(map);
}});


map.on('overlayadd', function (eventLayer) {
    if (eventLayer.layer == qpfTimeLayer) {
        color_map_qpf.addTo(map);
    }});
map.on('overlayremove', function (eventLayer) {
if (eventLayer.layer == qpfTimeLayer) {
    color_map_qpf.remove(map);
}});

map.on('overlayadd', function (eventLayer) {
    if (eventLayer.layer == qpf_3hTimeLayer) {
        color_map_qpf_3h.addTo(map);
    }});
map.on('overlayremove', function (eventLayer) {
if (eventLayer.layer == qpf_3hTimeLayer) {
    color_map_qpf_3h.remove(map);
}});

map.on('overlayadd', function (eventLayer) {
    if (eventLayer.layer == snwTimeLayer) {
        color_map_snw.addTo(map);
    }});
map.on('overlayremove', function (eventLayer) {
if (eventLayer.layer == snwTimeLayer) {
    color_map_snw.remove(map);
}});

function geo_json_styler18(properties, zoom) {
    var fillOpacity = 1
    var opacity = 1
    switch(properties.fill) {
        case "#000080":
            return {"color": "#000080", "opacity": opacity, "fillColor": "#000080", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#0000c4":
            return {"color": "#0000c4", "opacity": opacity, "fillColor": "#0000c4", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#0000ff":
            return {"color": "#0000ff", "opacity": opacity, "fillColor": "#0000ff", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#0034ff":
            return {"color": "#0034ff", "opacity": opacity, "fillColor": "#0034ff", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#0070ff":
            return {"color": "#0070ff", "opacity": opacity, "fillColor": "#0070ff", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#00acff":
            return {"color": "#00acff", "opacity": opacity, "fillColor": "#00acff", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#02e8f4":
            return {"color": "#02e8f4", "opacity": opacity, "fillColor": "#02e8f4", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#33ffc4":
            return {"color": "#33ffc4", "opacity": opacity, "fillColor": "#33ffc4", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#63ff94":
            return {"color": "#63ff94", "opacity": opacity, "fillColor": "#63ff94", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#94ff63":
            return {"color": "#94ff63", "opacity": opacity, "fillColor": "#94ff63", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#c4ff33":
            return {"color": "#c4ff33", "opacity": opacity, "fillColor": "#c4ff33", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#f4f802":
            return {"color": "#f4f802", "opacity": opacity, "fillColor": "#f4f802", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ffc100":
            return {"color": "#ffc100", "opacity": opacity, "fillColor": "#ffc100", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ff8900":
            return {"color": "#ff8900", "opacity": opacity, "fillColor": "#ff8900", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ff5200":
            return {"color": "#ff5200", "opacity": opacity, "fillColor": "#ff5200", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ff1a00":
            return {"color": "#ff1a00", "opacity": opacity, "fillColor": "#ff1a00", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#c40000":
            return {"color": "#c40000", "opacity": opacity, "fillColor": "#c40000", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        default:
            return {"color": "#800000", "opacity": opacity, "fillColor": "#800000", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
            }
        }


function geo_json_styler_fbp(properties, zoom) {
    var fillOpacity = 1
    var opacity = 1
    switch(properties.fill) {
        case "#0000ff":
            return {"color": "#0000ff", "opacity": opacity, "fillColor": "#0000ff", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#008001":
            return {"color": "#008001", "opacity": opacity, "fillColor": "#008001", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#01e001":
            return {"color": "#01e001", "opacity": opacity, "fillColor": "#01e001", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ffff00":
            return {"color": "#ffff00", "opacity": opacity, "fillColor": "#ffff00", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#dfa000":
            return {"color": "#dfa000", "opacity": opacity, "fillColor": "#dfa000", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ff0000":
            return {"color": "#ff0000", "opacity": opacity, "fillColor": "#ff0000", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        default:
            return {"color": "#8b0000", "opacity": opacity, "fillColor": "#8b0000", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        }
    }


function geo_json_styler_hfi(properties, zoom) {
    var fillOpacity = 1
    var opacity = 1
    switch(properties.fill) {
        case "#0000ff":
            return {"color": "#0000ff", "opacity": opacity, "fillColor": "#0000ff", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#00c0c0":
            return {"color": "#00c0c0", "opacity": opacity, "fillColor": "#00c0c0", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#008001":
            return {"color": "#008001", "opacity": opacity, "fillColor": "#008001", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#01e001":
            return {"color": "#01e001", "opacity": opacity, "fillColor": "#01e001", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ffff00":
            return {"color": "#ffff00", "opacity": opacity, "fillColor": "#ffff00", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#dfa000":
            return {"color": "#dfa000", "opacity": opacity, "fillColor": "#dfa000", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ff0000":
                return {"color": "#ff0000", "opacity": opacity, "fillColor": "#ff0000", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        default:
            return {"color": "#8b0000", "opacity": opacity, "fillColor": "#8b0000", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        }
    }

function geo_json_styler_wsp(properties, zoom) {
    var fillOpacity = 1
    var opacity = 1
    switch(properties.fill) {
        case "#ffffff":
            return {"color": "#ffffff", "opacity": opacity, "fillColor": "#ffffff", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#bbbbbb":
            return {"color": "#bbbbbb", "opacity": opacity, "fillColor": "#bbbbbb", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#646464":
            return {"color": "#646464", "opacity": opacity, "fillColor": "#646464", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#1563d3":
            return {"color": "#1563d3", "opacity": opacity, "fillColor": "#1563d3", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#2883f1":
            return {"color": "#2883f1", "opacity": opacity, "fillColor": "#2883f1", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#50a5f5":
            return {"color": "#50a5f5", "opacity": opacity, "fillColor": "#50a5f5", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#97d3fb":
            return {"color": "#97d3fb", "opacity": opacity, "fillColor": "#97d3fb", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#0ca10d":
            return {"color": "#0ca10d", "opacity": opacity, "fillColor": "#0ca10d", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#37d33c":
            return {"color": "#37d33c", "opacity": opacity, "fillColor": "#37d33c", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#97f58d":
            return {"color": "#97f58d", "opacity": opacity, "fillColor": "#97f58d", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#b5fbab":
            return {"color": "#b5fbab", "opacity": opacity, "fillColor": "#b5fbab", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ffe978":
            return {"color": "#ffe978", "opacity": opacity, "fillColor": "#ffe978", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ffc03d":
            return {"color": "#ffc03d", "opacity": opacity, "fillColor": "#ffc03d", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ffa100":
            return {"color": "#ffa100", "opacity": opacity, "fillColor": "#ffa100", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ff3300":
            return {"color": "#ff3300", "opacity": opacity, "fillColor": "#ff3300", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#c10000":
            return {"color": "#c10000", "opacity": opacity, "fillColor": "#c10000", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#960007":
            return {"color": "#960007", "opacity": opacity, "fillColor": "#960007", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        default:
            return {"color": "#643C32", "opacity": opacity, "fillColor": "#643C32", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
            }
        }



function geo_json_styler_temp(properties, zoom) {
    var fillOpacity = 1
    var opacity = 1
    switch(properties.fill) {
        case "#00ffff":
            return {"color": "#00ffff", "opacity": opacity, "fillColor": "#00ffff", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#06e6ed":
            return {"color": "#06e6ed", "opacity": opacity, "fillColor": "#06e6ed", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#0bcddb":
            return {"color": "#0bcddb", "opacity": opacity, "fillColor": "#0bcddb", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#10b5ca":
            return {"color": "#10b5ca", "opacity": opacity, "fillColor": "#10b5ca", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#159eb9":
            return {"color": "#159eb9", "opacity": opacity, "fillColor": "#159eb9", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#1b86a8":
            return {"color": "#1b86a8", "opacity": opacity, "fillColor": "#1b86a8", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#206f97":
            return {"color": "#206f97", "opacity": opacity, "fillColor": "#206f97", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#255987":
            return {"color": "#255987", "opacity": opacity, "fillColor": "#255987", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#2a4276":
            return {"color": "#2a4276", "opacity": opacity, "fillColor": "#2a4276", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#2f2a65":
            return {"color": "#2f2a65", "opacity": opacity, "fillColor": "#2f2a65", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#360a4e":
            return {"color": "#360a4e", "opacity": opacity, "fillColor": "#360a4e", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#560b69":
            return {"color": "#560b69", "opacity": opacity, "fillColor": "#560b69", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#7b0c88":
            return {"color": "#7b0c88", "opacity": opacity, "fillColor": "#7b0c88", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#a30ca8":
            return {"color": "#a30ca8", "opacity": opacity, "fillColor": "#a30ca8", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ce0bdc":
            return {"color": "#ce0bdc", "opacity": opacity, "fillColor": "#ce0bdc", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#af05e3":
            return {"color": "#af05e3", "opacity": opacity, "fillColor": "#af05e3", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#8904e1":
            return {"color": "#8904e1", "opacity": opacity, "fillColor": "#8904e1", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#5d04d8":
            return {"color": "#5d04d8", "opacity": opacity, "fillColor": "#5d04d8", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#1c0dcf":
            return {"color": "#1c0dcf", "opacity": opacity, "fillColor": "#1c0dcf", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#1b34d7":
            return {"color": "#1b34d7", "opacity": opacity, "fillColor": "#1b34d7", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#2460e2":
            return {"color": "#2460e2", "opacity": opacity, "fillColor": "#2460e2", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#348ced":
            return {"color": "#348ced", "opacity": opacity, "fillColor": "#348ced", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#44b1f6":
            return {"color": "#44b1f6", "opacity": opacity, "fillColor": "#44b1f6", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#51cbfa":
            return {"color": "#51cbfa", "opacity": opacity, "fillColor": "#51cbfa", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#80e0f7":
            return {"color": "#80e0f7", "opacity": opacity, "fillColor": "#80e0f7", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#a0eaf7":
            return {"color": "#a0eaf7", "opacity": opacity, "fillColor": "#a0eaf7", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#00ef7c":
            return {"color": "#00ef7c", "opacity": opacity, "fillColor": "#00ef7c", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#00e452":
            return {"color": "#00e452", "opacity": opacity, "fillColor": "#00e452", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#00c848":
            return {"color": "#00c848", "opacity": opacity, "fillColor": "#00c848", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#10b87a":
            return {"color": "#10b87a", "opacity": opacity, "fillColor": "#10b87a", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#297b5d":
            return {"color": "#297b5d", "opacity": opacity, "fillColor": "#297b5d", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#007229":
            return {"color": "#007229", "opacity": opacity, "fillColor": "#007229", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#3ca12c":
            return {"color": "#3ca12c", "opacity": opacity, "fillColor": "#3ca12c", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#79d030":
            return {"color": "#79d030", "opacity": opacity, "fillColor": "#79d030", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#b5ff33":
            return {"color": "#b5ff33", "opacity": opacity, "fillColor": "#b5ff33", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#d8f7a1":
            return {"color": "#d8f7a1", "opacity": opacity, "fillColor": "#d8f7a1", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#fff600":
            return {"color": "#fff600", "opacity": opacity, "fillColor": "#fff600", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#f8df0b":
            return {"color": "#f8df0b", "opacity": opacity, "fillColor": "#f8df0b", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#fdca0c":
            return {"color": "#fdca0c", "opacity": opacity, "fillColor": "#fdca0c", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#fcac05":
            return {"color": "#fcac05", "opacity": opacity, "fillColor": "#fcac05", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#f88d00":
            return {"color": "#f88d00", "opacity": opacity, "fillColor": "#f88d00", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ff6600":
            return {"color": "#ff6600", "opacity": opacity, "fillColor": "#ff6600", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#fc4f00":
            return {"color": "#fc4f00", "opacity": opacity, "fillColor": "#fc4f00", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ff0100":
            return {"color": "#ff0100", "opacity": opacity, "fillColor": "#ff0100", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#f31a00":
            return {"color": "#f31a00", "opacity": opacity, "fillColor": "#f31a00", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#f31861":
            return {"color": "#f31861", "opacity": opacity, "fillColor": "#f31861", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        default:
            return {"color": "#f316c2", "opacity": opacity, "fillColor": "#f316c2", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
            }
        }

function geo_json_styler_rh(properties, zoom) {
    var fillOpacity = 1
    var opacity = 1
    switch(properties.fill) {
        case "#442d15":
            return {"color": "#442d15", "opacity": opacity, "fillColor": "#442d15", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#653f1f":
            return {"color": "#653f1f", "opacity": opacity, "fillColor": "#653f1f", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#815228":
            return {"color": "#815228", "opacity": opacity, "fillColor": "#815228", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#9d622f":
            return {"color": "#9d622f", "opacity": opacity, "fillColor": "#9d622f", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ad7644":
            return {"color": "#ad7644", "opacity": opacity, "fillColor": "#ad7644", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#b98b5c":
            return {"color": "#b98b5c", "opacity": opacity, "fillColor": "#b98b5c", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#c7a074":
            return {"color": "#c7a074", "opacity": opacity, "fillColor": "#c7a074", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#e1cdb3":
            return {"color": "#e1cdb3", "opacity": opacity, "fillColor": "#e1cdb3", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#efded9":
            return {"color": "#efded9", "opacity": opacity, "fillColor": "#efded9", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#d0d3bb":
            return {"color": "#d0d3bb", "opacity": opacity, "fillColor": "#d0d3bb", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#afc599":
            return {"color": "#afc599", "opacity": opacity, "fillColor": "#afc599", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#88bf87":
            return {"color": "#88bf87", "opacity": opacity, "fillColor": "#88bf87", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#7ab58d":
            return {"color": "#7ab58d", "opacity": opacity, "fillColor": "#7ab58d", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#6da893":
            return {"color": "#6da893", "opacity": opacity, "fillColor": "#6da893", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#59929b":
            return {"color": "#59929b", "opacity": opacity, "fillColor": "#59929b", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#568999":
            return {"color": "#568999", "opacity": opacity, "fillColor": "#568999", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#4c6497":
            return {"color": "#4c6497", "opacity": opacity, "fillColor": "#4c6497", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        default:
            return {"color": "#6c4a97", "opacity": opacity, "fillColor": "#6c4a97", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
            }
        }

function geo_json_styler_qpf(properties, zoom) {
    var fillOpacity = 1
    var opacity = 1
    switch(properties.fill) {
        case "#ffffff":
            return {"color": "#ffffff", "opacity": opacity, "fillColor": "#ffffff", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#a9a5a5":
            return {"color": "#a9a5a5", "opacity": opacity, "fillColor": "#a9a5a5", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#6e6e6e":
            return {"color": "#6e6e6e", "opacity": opacity, "fillColor": "#6e6e6e", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#b3f9a9":
            return {"color": "#b3f9a9", "opacity": opacity, "fillColor": "#b3f9a9", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#79f572":
            return {"color": "#79f572", "opacity": opacity, "fillColor": "#79f572", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#50f150":
            return {"color": "#50f150", "opacity": opacity, "fillColor": "#50f150", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#1fb51e":
            return {"color": "#1fb51e", "opacity": opacity, "fillColor": "#1fb51e", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#0ca10d":
            return {"color": "#0ca10d", "opacity": opacity, "fillColor": "#0ca10d", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#1563d3":
            return {"color": "#1563d3", "opacity": opacity, "fillColor": "#1563d3", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#54a8f5":
            return {"color": "#54a8f5", "opacity": opacity, "fillColor": "#54a8f5", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#b4f1fb":
            return {"color": "#b4f1fb", "opacity": opacity, "fillColor": "#b4f1fb", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ffe978":
            return {"color": "#ffe978", "opacity": opacity, "fillColor": "#ffe978", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ffa100":
            return {"color": "#ffa100", "opacity": opacity, "fillColor": "#ffa100", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ff3300":
            return {"color": "#ff3300", "opacity": opacity, "fillColor": "#ff3300", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#a50000":
            return {"color": "#a50000", "opacity": opacity, "fillColor": "#a50000", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#b58d83":
            return {"color": "#b58d83", "opacity": opacity, "fillColor": "#b58d83", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#9886ba":
            return {"color": "#9886ba", "opacity": opacity, "fillColor": "#9886ba", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        default:
            return {"color": "#8d008d", "opacity": opacity, "fillColor": "#8d008d", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
            }
        }




function geo_json_styler_snw(properties, zoom) {
    var fillOpacity = 1
    var opacity = 1
    switch(properties.fill) {
        case "#ffffff":
            return {"color": "#ffffff", "opacity": opacity, "fillColor": "#ffffff", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#bdbdbd":
            return {"color": "#bdbdbd", "opacity": opacity, "fillColor": "#bdbdbd", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#979797":
            return {"color": "#979797", "opacity": opacity, "fillColor": "#979797", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#6e6e6e":
            return {"color": "#6e6e6e", "opacity": opacity, "fillColor": "#6e6e6e", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#4f5051":
            return {"color": "#4f5051", "opacity": opacity, "fillColor": "#4f5051", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#97d3fb":
            return {"color": "#97d3fb", "opacity": opacity, "fillColor": "#97d3fb", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#79b9fb":
            return {"color": "#79b9fb", "opacity": opacity, "fillColor": "#79b9fb", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#50a5f5":
            return {"color": "#50a5f5", "opacity": opacity, "fillColor": "#50a5f5", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#3d97f5":
            return {"color": "#3d97f5", "opacity": opacity, "fillColor": "#3d97f5", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#2883f1":
            return {"color": "#2883f1", "opacity": opacity, "fillColor": "#2883f1", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#1e6eeb":
            return {"color": "#1e6eeb", "opacity": opacity, "fillColor": "#1e6eeb", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#1563d3":
            return {"color": "#1563d3", "opacity": opacity, "fillColor": "#1563d3", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#085ac3":
            return {"color": "#085ac3", "opacity": opacity, "fillColor": "#085ac3", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#3e0291":
            return {"color": "#3e0291", "opacity": opacity, "fillColor": "#3e0291", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#4c028f":
            return {"color": "#4c028f", "opacity": opacity, "fillColor": "#4c028f", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#5a028c":
            return {"color": "#5a028c", "opacity": opacity, "fillColor": "#5a028c", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#68028b":
            return {"color": "#68028b", "opacity": opacity, "fillColor": "#68028b", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#850289":
            return {"color": "#850289", "opacity": opacity, "fillColor": "#850289", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#a00485":
            return {"color": "#a00485", "opacity": opacity, "fillColor": "#a00485", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#c90380":
            return {"color": "#c90380", "opacity": opacity, "fillColor": "#c90380", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#f3037c":
            return {"color": "#f3037c", "opacity": opacity, "fillColor": "#f3037c", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#f51485":
            return {"color": "#f51485", "opacity": opacity, "fillColor": "#f51485", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#f83b9b":
            return {"color": "#f83b9b", "opacity": opacity, "fillColor": "#f83b9b", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#fd5eae":
            return {"color": "#fd5eae", "opacity": opacity, "fillColor": "#fd5eae", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ff6eb7":
            return {"color": "#ff6eb7", "opacity": opacity, "fillColor": "#ff6eb7", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#fa85c2":
            return {"color": "#fa85c2", "opacity": opacity, "fillColor": "#fa85c2", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#f58dc6":
            return {"color": "#f58dc6", "opacity": opacity, "fillColor": "#f58dc6", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ed95cb":
            return {"color": "#ed95cb", "opacity": opacity, "fillColor": "#ed95cb", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#e79dcc":
            return {"color": "#e79dcc", "opacity": opacity, "fillColor": "#e79dcc", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#d9add4":
            return {"color": "#d9add4", "opacity": opacity, "fillColor": "#d9add4", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#d0b5d8":
            return {"color": "#d0b5d8", "opacity": opacity, "fillColor": "#d0b5d8", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#c3c7e1":
            return {"color": "#c3c7e1", "opacity": opacity, "fillColor": "#c3c7e1", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#b5d7e9":
            return {"color": "#b5d7e9", "opacity": opacity, "fillColor": "#b5d7e9", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ace2ef":
            return {"color": "#ace2ef", "opacity": opacity, "fillColor": "#ace2ef", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#a1eff3":
            return {"color": "#a1eff3", "opacity": opacity, "fillColor": "#a1eff3", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#95fbf9":
            return {"color": "#95fbf9", "opacity": opacity, "fillColor": "#95fbf9", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#92f3f1":
            return {"color": "#92f3f1", "opacity": opacity, "fillColor": "#92f3f1", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#7ddbd9":
            return {"color": "#7ddbd9", "opacity": opacity, "fillColor": "#7ddbd9", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#71bdc4":
            return {"color": "#71bdc4", "opacity": opacity, "fillColor": "#71bdc4", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#7cb9cb":
            return {"color": "#7cb9cb", "opacity": opacity, "fillColor": "#7cb9cb", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#81b7cc":
            return {"color": "#81b7cc", "opacity": opacity, "fillColor": "#81b7cc", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#85b3cf":
            return {"color": "#85b3cf", "opacity": opacity, "fillColor": "#85b3cf", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#89b1d1":
            return {"color": "#89b1d1", "opacity": opacity, "fillColor": "#89b1d1", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#90add4":
            return {"color": "#90add4", "opacity": opacity, "fillColor": "#90add4", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#94a9d8":
            return {"color": "#94a9d8", "opacity": opacity, "fillColor": "#94a9d8", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#99a6db":
            return {"color": "#99a6db", "opacity": opacity, "fillColor": "#99a6db", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#9aa5db":
            return {"color": "#9aa5db", "opacity": opacity, "fillColor": "#9aa5db", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#a3a3de":
            return {"color": "#a3a3de", "opacity": opacity, "fillColor": "#a3a3de", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#ab9ce5":
            return {"color": "#ab9ce5", "opacity": opacity, "fillColor": "#ab9ce5", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#af9be7":
            return {"color": "#af9be7", "opacity": opacity, "fillColor": "#af9be7", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#b399e8":
            return {"color": "#b399e8", "opacity": opacity, "fillColor": "#b399e8", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#b895eb":
            return {"color": "#b895eb", "opacity": opacity, "fillColor": "#b895eb", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#bb93ed":
            return {"color": "#bb93ed", "opacity": opacity, "fillColor": "#bb93ed", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#bf91f1":
            return {"color": "#bf91f1", "opacity": opacity, "fillColor": "#bf91f1", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#c38ff3":
            return {"color": "#c38ff3", "opacity": opacity, "fillColor": "#c38ff3", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#c98bf5":
            return {"color": "#c98bf5", "opacity": opacity, "fillColor": "#c98bf5", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        default:
            return {"color": "#d087f9", "opacity": opacity, "fillColor": "#d087f9", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
            }
        }
