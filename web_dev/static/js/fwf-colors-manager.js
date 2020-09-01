function getColor(d) {
    return d >  1.0    ? '#276419'  :
            d > 0.8    ? '#4d9221' :
            d > 0.6    ? '#7fbc41' :
            d > 0.4    ? '#b8e186' :
            d > 0.2    ? '#e6f5d0' :
            d > 0.0    ? '#f7f7f7' :
            d > -0.2   ? '#fde0ef' :
            d > -0.4   ? '#f1b6da' :
            d > -0.6   ? '#de77ae' :
            d > -0.8   ? '#c51b7d' :
            d > -1.0   ? '#8e0152' :
                         '#8e0152' ;
}

var legend_wx = L.control({position: 'bottomright'});

legend_wx.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend'),
        grades = [1.0, 0.8, 0.6, 0.4, 0.2, 0.00, -0.2, -0.4, -0.6, -0.8, -1.0],
        labels = ['<strong> Pearsons Correlation </strong>'],
        from, to;

    for (var i = 0; i < grades.length; i++) {
        from = grades[i];
        to = grades[i + 1];
        console.log(to);
        labels.push(
            '<i style="background:' + getColor(from + 0.001) + '"></i> ' +
            from + (to ? '      &ndash;       ' + to : ''));
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
<td width="2px">0</td>\
<td width="10px"></td>\
<td width="10px">60</td>\
<td width="10px"></td>\
<td width="10px">75</td>\
<td width="10px"></td>\
<td width="14px">81</td>\
<td width="10px"></td>\
<td width="10px">83</td>\
<td width="10px"></td>\
<td width="10px">85</td>\
<td width="10px"></td>\
<td width="14px">87</td>\
<td width="10px"></td>\
<td width="10px">89</td>\
<td width="10px"></td>\
<td width="10px">95</td>\
<td width="2px"></td>\
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
<td width="10px"></td>\
<td width="10px">7</td>\
<td width="10px"></td>\
<td width="10px">14</td>\
<td width="10px"></td>\
<td width="14px">21</td>\
<td width="10px"></td>\
<td width="10px">28</td>\
<td width="10px"></td>\
<td width="12px">35</td>\
<td width="10px"></td>\
<td width="14px">43</td>\
<td width="10px"></td>\
<td width="10px">50</td>\
<td width="10px"></td>\
<td width="10px">60</td>\
<td width="5px"></td>\
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
<td width="6px"></td>\
<td width="2px">82</td>\
<td width="5px"></td>\
<td width="15px">124</td>\
<td width="5px"></td>\
<td width="5px">167</td>\
<td width="5px"></td>\
<td width="5px">209</td>\
<td width="5px"></td>\
<td width="5px">252</td>\
<td width="5px"></td>\
<td width="5px">294</td>\
<td width="5px"></td>\
<td width="14px">337</td>\
<td width="5px"></td>\
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
<td width="8px"></td>\
<td width="10px">1.8</td>\
<td width="10px"></td>\
<td width="8px">3.7</td>\
<td width="6px"></td>\
<td width="6px">5.6</td>\
<td width="8px"></td>\
<td width="6px">7.5</td>\
<td width="6px"></td>\
<td width="6px">9.4</td>\
<td width="6px"></td>\
<td width="6px">11.3</td>\
<td width="6px"></td>\
<td width="6px">13.2</td>\
<td width="2px"></td>\
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
<td width="10px"></td>\
<td width="10px">21</td>\
<td width="10px"></td>\
<td width="14px">32</td>\
<td width="10px"></td>\
<td width="10px">42</td>\
<td width="10px"></td>\
<td width="12px">53</td>\
<td width="10px"></td>\
<td width="10px">64</td>\
<td width="10px"></td>\
<td width="12px">74</td>\
<td width="10px"></td>\
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
<td width="10px"></td>\
<td width="10px">3</td>\
<td width="10px"></td>\
<td width="14px">7</td>\
<td width="10px"></td>\
<td width="10px">10</td>\
<td width="10px"></td>\
<td width="10px">14</td>\
<td width="10px"></td>\
<td width="10px">18</td>\
<td width="10px"></td>\
<td width="16px">21</td>\
<td width="8px"></td>\
<td width="10px">25</td>\
<td width="12px"></td>\
<td width="10px">30</td>\
<td width="2px"></td>\
<td width="2px">40+</td>\
</tr>\
</table>\
<div class="legend-title">Fire Weather Index</div>';
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
<td width="10px"></td>\
<td width="8px">20</td>\
<td width="10px"></td>\
<td width="10px">28</td>\
<td width="12px"></td>\
<td width="10px">32</td>\
<td width="10px"></td>\
<td width="10px">40</td>\
<td width="10px"></td>\
<td width="10px">48</td>\
<td width="12px"></td>\
<td width="10px">56</td>\
<td width="12px"></td>\
<td width="10px">64</td>\
<td width="10px"></td>\
<td width="10px">72</td>\
<td width="2px"></td>\
<td width="2px">80+</td>\
</tr>\
</table>\
<div class="legend-title">Wind Speed (km/hr) at 10m</div>';
    return div;
}

var color_map_temp = L.control({position: "bottomleft"});
color_map_temp.onAdd = function(map) {
    var div = L.DomUtil.create('div', 'fcst-legend leaflet-bar leaflet-control');
    div.innerHTML =
'<table id="values">\
<tr id="colours">\
<td style="background:#1b34d7; width:10px; border-left:none;"></td>\
<td style="background:#2460e2;"></td>\
<td style="background:#348ced;"></td>\
<td style="background:#44b1f6;"></td>\
<td style="background:#51cbfa;"></td>\
<td style="background:#80e0f7;"></td>\
<td style="background:#a0eaf7;"></td>\
<td style="background:#00efbb;"></td>\
<td style="background:#00ef7c;"></td>\
<td style="background:#00e452;"></td>\
<td style="background:#00c848;"></td>\
<td style="background:#10b87a;"></td>\
<td style="background:#297b5d;"></td>\
<td style="background:#007229;"></td>\
<td style="background:#3ca12c;"></td>\
<td style="background:#79d030;"></td>\
<td style="background:#b5ff32;"></td>\
<td style="background:#d6ff32;"></td>\
<td style="background:#fff600;"></td>\
<td style="background:#f8df0b;"></td>\
<td style="background:#fdca0c;"></td>\
<td style="background:#fcac05;"></td>\
<td style="background:#f88d00;"></td>\
<td style="background:#ff6600;"></td>\
<td style="background:#fc4f00;"></td>\
<td style="background:#ff0100;"></td>\
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
</tr>\
</table>\
<table id="labels">\
<tr>\
<td width="2px"></td>\
<td width="1px">-12</td>\
<td width="8px"></td>\
<td width="10px">-8</td>\
<td width="12px"></td>\
<td width="10px">-4</td>\
<td width="14px"></td>\
<td width="10px">0</td>\
<td width="11px"></td>\
<td width="10px">4</td>\
<td width="14px"></td>\
<td width="9px">8</td>\
<td width="10px"></td>\
<td width="10px">12</td>\
<td width="12px"></td>\
<td width="10px">16</td>\
<td width="12px"></td>\
<td width="10px">20</td>\
<td width="10px"></td>\
<td width="10px">24</td>\
<td width="12px"></td>\
<td width="10px">28</td>\
<td width="10px"></td>\
<td width="10px">32</td>\
<td width="12px"></td>\
<td width="10px">36+</td>\
<td width="10px"></td>\
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
<td width="10px"></td>\
<td width="10px">2</td>\
<td width="12px"></td>\
<td width="10px">5</td>\
<td width="10px"></td>\
<td width="10px">15</td>\
<td width="12px"></td>\
<td width="10px">30</td>\
<td width="12px"></td>\
<td width="10px">50</td>\
<td width="10px"></td>\
<td width="10px">70</td>\
<td width="12px"></td>\
<td width="10px">90</td>\
<td width="10px"></td>\
<td width="10px">99</td>\
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
<td width="10px"></td>\
<td width="10px">1</td>\
<td width="12px"></td>\
<td width="10px">3</td>\
<td width="12px"></td>\
<td width="10px">10</td>\
<td width="10px"></td>\
<td width="10px">20</td>\
<td width="12px"></td>\
<td width="10px">30</td>\
<td width="10px"></td>\
<td width="10px">50</td>\
<td width="10px"></td>\
<td width="10px">70</td>\
<td width="10px"></td>\
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
<td width="10px"></td>\
<td width="10px">1</td>\
<td width="12px"></td>\
<td width="10px">3</td>\
<td width="12px"></td>\
<td width="10px">10</td>\
<td width="10px"></td>\
<td width="10px">20</td>\
<td width="12px"></td>\
<td width="10px">30</td>\
<td width="10px"></td>\
<td width="10px">50</td>\
<td width="10px"></td>\
<td width="10px">70</td>\
<td width="10px"></td>\
<td width="4px">100</td>\
<td width="2px"></td>\
<td width="2px">140+</td>\
</tr>\
</table>\
<div class="legend-title">3 Hour Accumulated Precipitation (mm)</div>';
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
        case "#00efbb": 
            return {"color": "#00efbb", "opacity": opacity, "fillColor": "#00efbb", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
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
        case "#b5ff32": 
            return {"color": "#b5ff32", "opacity": opacity, "fillColor": "#b5ff32", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
        case "#d6ff32": 
            return {"color": "#d6ff32", "opacity": opacity, "fillColor": "#d6ff32", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
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
        default:
            return {"color": "#ff0100", "opacity": opacity, "fillColor": "#ff0100", "fillOpacity": fillOpacity, "weight": 0.2, fill: true};
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






   

