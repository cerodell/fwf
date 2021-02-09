var wx_station = L.layerGroup();

 
const div = document.createElement("div");
const div2 = div.cloneNode(true);

div.className = "wx-plot";

// const width =  '600px';
// const height =  '450px';

// div.style.width = width;
// div.style.height = height;
div.setAttribute("id", "wx_plot");


// h3= document.createElement("h3");
// div.appendChild(h3);
var btn_fire = document.createElement("BUTTON");   // Create a <button> element
btn_fire.setAttribute("id", "button");
btn_fire.className = "btn_fire";
btn_fire.innerHTML = "Fire Weather";
// Insert text
div.appendChild(btn_fire);               // Append <button> to <body>


var btn_wx = document.createElement("BUTTON");   // Create a <button> element
btn_wx.setAttribute("id", "button");
btn_wx.className = "btn_wx";
btn_wx.innerHTML = "Weather";                   // Insert text
div.appendChild(btn_wx);  


// const div2 = div.cloneNode(true);
// const div2 = document.createElement("div");
// document.body.appendChild(div2);



wx_station.onAdd = function(){
fetch(wxstations).then(function(response){
    return response.json();
}).then(function(json){   
        var wmo = JSON.parse(json.wmo);
        var lats = JSON.parse(json.lats);
        var lons = JSON.parse(json.lons);
        var ffmc_obs = JSON.parse(json.ffmc_obs);
        var temp_obs = JSON.parse(json.temp_obs);

        for (index = 0; index < lats.length; ++index) {
        var colors = ['#ff6760', '#ffff73', '#63a75c']
        if (temp_obs[temp_obs.length - 1][index] != -99 && ffmc_obs[temp_obs.length - 1][index] != -99) {
            color = colors[2];
        } else if (temp_obs[temp_obs.length - 1][index] != -99 && ffmc_obs[temp_obs.length - 1][index] == -99) {
            color = colors[1];
        }else {
                color = colors[0];
              }
        
        var dict = {}
        keys = ['elev', 'lats', 'lons','tz_correct', 'wmo']
        for (var key of keys) {
            var array = JSON.parse(json[key]);
            dict[key] = array[index];
        };



        wx_station.addLayer(L.circle([lats[index], lons[index]], {
            radius: 4000,
            // weight: 3,
            color: color,
            fillColor: color,
            fillOpacity: 1,
            customId: wmo[index].toString()


        // }).bindPopup(createPopupContent(dict)).on("click", circleClick));
        }).bindPopup(div, {maxWidth: "auto", maxHeight: "auto"}).on("click", circleClick));
    }
});
};


// wx_station.bindPopup(div);

function circleClick(e) {
    var clickedCircle = e.target;
    const target_wmo = clickedCircle.options.customId;
    btn_fire.onclick = fwiplot;
    btn_wx.onclick = wxplot;
    fwiplot();
    function fwiplot() {
        fetch(wxstations).then(function(response){
            return response.json();
        }).then(function(json){   
    
                var wmo = JSON.parse(json.wmo);
                var index = wmo.indexOf(parseInt(target_wmo));
    
                var dict = {};
                const arrayColumn = (arr, n) => arr.map(x => x[n]);
                function change99(array){    
                    for (i = 0; i < array.length; ++i){
                    if (array[i]== -99){
                        array[i] = null
                    } else{
                        array[i] = array[i]
                            }
                        }
                    return array
                }
                keys = ['dsr_fc','dsr_obs', 'dsr_pfc', 'ffmc_fc', 'ffmc_obs', 'ffmc_pfc', 
                        'rh_fc', 'rh_obs', 'rh_pfc', 'isi_fc', 'isi_obs', 'isi_pfc', 
                        'fwi_fc', 'fwi_obs', 'fwi_pfc', 'temp_fc', 'temp_obs', 'temp_pfc', 
                        'ws_fc', 'ws_obs', 'ws_pfc', 'wdir_fc', 'wdir_obs', 'wdir_pfc', 
                        'precip_fc', 'precip_obs', 'precip_pfc', 'dc_fc', 'dc_obs', 'dc_pfc',
                        'dmc_fc', 'dmc_obs', 'dmc_pfc', 'bui_fc', 'bui_obs', 'bui_pfc']
                for (var key of keys) {
                    var array = JSON.parse(json[key]);
                    var array = arrayColumn(array,index);
                    array = change99(array);
                    dict[key] = array;
            };
                keys = ['elev', 'lats', 'lons','tz_correct', 'wmo']
                for (var key of keys) {
                    var array = JSON.parse(json[key]);
                    dict[key] = array[index];
                };
    
                // var id = json['id']
                // var id = id.split(',');
                // dict['id'] = id[index];
        
                // var name = json['name']
                // var name = name.split(',');
                // dict['name'] = name[index];
    
                keys = ['time_obs','time_fch', 'time_fcd']
                for (var key of keys) {
                    var array = json[key];
                    dict[key] = array;
                };
                console.log(dict['precip_fc']);
    
    
                C = document.getElementById('wx_plot');
                console.log(C);
                hovsize = 10;
                N =
                [(ffmc_obs = {x: dict['time_obs'], y: dict['ffmc_obs'], mode: 'lines', line: { color: "ff7f0e", dash: "dot" }, yaxis: "y6",  hoverlabel:{font:{size: hovsize, color: "#ffffff"}, bordercolor: "#ffffff"}, hovertemplate: "<b> FFMC Obs </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (ffmc_fc = {x: dict['time_obs'], y: dict['ffmc_pfc'],mode: 'lines', line: { color: "ff7f0e", width: 0.5 }, yaxis: "y6",  hoverlabel:{font:{size: hovsize, color: "#ffffff"}, bordercolor: "#ffffff"}, hovertemplate: "<b> FFMC Modeled </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (ffmc_fc = {x: dict['time_fch'], y: dict['ffmc_fc'], mode: 'lines', line: { color: "ff7f0e" }, yaxis: "y6",  hoverlabel:{font:{size: hovsize, color: "#ffffff"}, bordercolor: "#ffffff"}, hovertemplate: "<b> FFMC Forecast </b><br>" + "%{y:.2f} <br>" + "<extra></extra>"}),
                
                (dmc_obs = {x: dict['time_obs'], y: dict['dmc_obs'], mode: 'lines', line: { color: "2ca02c", dash: "dot" }, yaxis: "y5",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> DMC Obs </b><br>" + "%{y:.2f} <br>" + "<extra></extra>"}),
                (dmc_fc = {x: dict['time_obs'], y: dict['dmc_pfc'],mode: 'lines', line: { color: "2ca02c", width: 0.5 }, yaxis: "y5",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> DMC Modeled </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (dmc_fc = { x: dict['time_fcd'], y: dict['dmc_fc'], mode: 'lines', line: { color: "2ca02c" }, yaxis: "y5", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> DMC Forecast </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                
                (dc_obs = {x: dict['time_obs'], y: dict['dc_obs'], mode: 'lines', line: { color: "8c564b", dash: "dot" }, yaxis: "y4", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> DC Obs </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (dc_fc = {x: dict['time_obs'], y: dict['dc_pfc'],mode: 'lines', line: { color: "8c564b", width: 0.5 }, yaxis: "y4", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> DC Modeled </b><br>" + "%{y:.2f} <br>" + "<extra></extra>"}),
                (dc_fc = {x: dict['time_fcd'], y: dict['dc_fc'], mode: 'lines', line: { color: "8c564b" }, yaxis: "y4",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> DC Forecast </b><br>" + "%{y:.2f} <br>" + "<extra></extra>"}),
                
                (isi_obs = {x: dict['time_obs'], y: dict['isi_obs'], mode: 'lines', line: { color: "9467bd", dash: "dot" }, yaxis: "y3",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> ISI Obs </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (isi_fc = {x: dict['time_obs'], y: dict['isi_pfc'],mode: 'lines', line: { color: "9467bd", width: 0.5 }, yaxis: "y3", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> ISI Modeled </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (isi_fc = {x: dict['time_fch'], y: dict['isi_fc'], mode: 'lines', line: { color: "9467bd" }, yaxis: "y3",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> ISI Forecast </b><br>" + "%{y:.2f} <br>" + "<extra></extra>"}),
                
                (bui_obs = {x: dict['time_obs'], y: dict['bui_obs'], mode: 'lines', line: { color: "7f7f7f", dash: "dot" }, yaxis: "y2",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> FWI Obs </b><br>" + "%{y:.2f} <br>" + "<extra></extra>"}),
                (bui_fc = {x: dict['time_obs'], y: dict['bui_pfc'],mode: 'lines', line: { color: "7f7f7f", width: 0.5 }, yaxis: "y2",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> BUI Modeled </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (bui_fc = {x: dict['time_fcd'], y: dict['bui_fc'], mode: 'lines', line: { color: "7f7f7f" }, yaxis: "y2",   hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> BUI Forecast </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                
                (fwi_obs = {x: dict['time_obs'], y: dict['fwi_obs'], mode: 'lines', line: { color: "d62728", dash: "dot" }, yaxis: "y1",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> FWI Obs </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (fwi_fc = {x: dict['time_obs'], y: dict['fwi_pfc'],mode: 'lines', line: { color: "d62728", width: 0.5 }, yaxis: "y1", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> FWI Modeled </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (fwi_fc = {x: dict['time_fcd'], y: dict['fwi_fc'], mode: 'lines', line: { color: "d62728" }, yaxis: "y1", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> FWI Forecast </b><br>" + "%{y:.2f} <br>" + "<extra></extra>"}),
                ];
                    
        
    

                if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
                labelsize = 10;
                ticksize = 9;
                
                S = {
                    autosize: false, 
                    width: 320,
                    height: 400,
                    margin: {
                      l: 50,
                      r: 30,
                      b: 50,
                      t: 68,
                      pad: 1
                    },                     
                    title: {text: "  WMO Station " + dict.wmo.toString() + " <br>Lat: " + dict.lats.toString().slice(0,6)+ ", Lon: " + dict.lons.toString().slice(0,8) + " <br>Elevation: " + dict.elev.toString().slice(0,8) + " m", x:0.05}, 
                    titlefont: { color: "#444444", size: 11 },
                    showlegend: !1,
                    yaxis6: {domain: [.8, .94], title: { text: "FFMC", font: { size: labelsize, color: "ff7f0e" } }, tickfont: {size: ticksize, color: "ff7f0e"}},
                    yaxis5: {domain: [0.64, 0.78], title: { text: "DMC", font: { size: labelsize,color: "2ca02c" } }, tickfont: {size: ticksize, color: "2ca02c"}},
                    yaxis4: { domain: [0.48, 0.62], title: { text: "DC", font: { size: labelsize,color: "8c564b" } }, tickfont: {size: ticksize, color: "8c564b"}},
                    yaxis3: { domain: [0.32, 0.46], title: { text: "ISI", font: {size: labelsize, color: "9467bd" } }, tickfont: {size: ticksize, color: "9467bd"}},
                    yaxis2: { domain: [0.16, 0.30], title: { text: "BUI", font: { size: labelsize, color: "7f7f7f" } }, tickfont: {size: ticksize, color: "7f7f7f"}},
                    yaxis1: { domain: [0, 0.14], title: { text: "FWI", font: {size: labelsize, color: "d62728" } }, tickfont: {size: ticksize, color: "d62728"}},
                    xaxis: { title: "Date (UTC)", titlefont: { size: 10, color: "444444" }, tickfont: {size: ticksize, color: "444444"}}
                };
                }else{
                labelsize = 10;
                ticksize = 9;

                S = {
                    autosize: false, 
                    width: 600,
                    height: 450,
                    margin: {
                      l: 50,
                      r: 30,
                      b: 50,
                      t: 100,
                      pad: 2
                    },                    
                    title: {text: "  WMO Station " + dict.wmo.toString() + " <br>Lat: " + dict.lats.toString().slice(0,6)+ ", Lon: " + dict.lons.toString().slice(0,8) + " <br>Elevation: " + dict.elev.toString().slice(0,8) + " m", x:0.05}, 
                    titlefont: { color: "#444444", size: 13 },
                    showlegend: !1,
                    yaxis6: {domain: [.8, .94], title: { text: "FFMC", font: { size: labelsize, color: "ff7f0e" } }, tickfont: {size: ticksize, color: "ff7f0e"}},
                    yaxis5: {domain: [0.64, 0.78], title: { text: "DMC", font: { size: labelsize,color: "2ca02c" } }, tickfont: {size: ticksize, color: "2ca02c"}},
                    yaxis4: { domain: [0.48, 0.62], title: { text: "DC", font: { size: labelsize,color: "8c564b" } }, tickfont: {size: ticksize, color: "8c564b"}},
                    yaxis3: { domain: [0.32, 0.46], title: { text: "ISI", font: {size: labelsize, color: "9467bd" } }, tickfont: {size: ticksize, color: "9467bd"}},
                    yaxis2: { domain: [0.16, 0.30], title: { text: "BUI", font: { size: labelsize, color: "7f7f7f" } }, tickfont: {size: ticksize, color: "7f7f7f"}},
                    yaxis1: { domain: [0, 0.14], title: { text: "FWI", font: {size: labelsize, color: "d62728" } }, tickfont: {size: ticksize, color: "d62728"}},
                    xaxis: { title: "Date (UTC)", titlefont: { size: 12, color: "444444" }}
                };
                    
                }
                Plotly.newPlot(C,  N, S);
                    });
                }
    
        

    function wxplot() {
        fetch(wxstations).then(function(response){
            return response.json();
        }).then(function(json){   
                var wmo = JSON.parse(json.wmo);
                var index = wmo.indexOf(parseInt(target_wmo));
    
                var dict = {};
                var arrayColumn = (arr, n) => arr.map(x => x[n]);
                function change99(array){
                    for (i = 0; i < array.length; ++i){
                    if (array[i]== -99){
                        array[i] = null
                    } else{
                        array[i] = array[i]
                            }
                        }
                    return array
                }
                keys = ['dsr_fc','dsr_obs', 'dsr_pfc', 'ffmc_fc', 'ffmc_obs', 'ffmc_pfc', 
                        'rh_fc', 'rh_obs', 'rh_pfc', 'isi_fc', 'isi_obs', 'isi_pfc', 
                        'fwi_fc', 'fwi_obs', 'fwi_pfc', 'temp_fc', 'temp_obs', 'temp_pfc', 
                        'ws_fc', 'ws_obs', 'ws_pfc', 'wdir_fc', 'wdir_obs', 'wdir_pfc', 
                        'precip_fc', 'precip_obs', 'precip_pfc', 'dc_fc', 'dc_obs', 'dc_pfc',
                        'dmc_fc', 'dmc_obs', 'dmc_pfc', 'bui_fc', 'bui_obs', 'bui_pfc']
                for (var key of keys) {
                    var array = JSON.parse(json[key]);
                    var array = arrayColumn(array,index);
                    array = change99(array);
                    dict[key] = array;
            };
                keys = ['elev', 'lats', 'lons','tz_correct', 'wmo']
                for (var key of keys) {
                    var array = JSON.parse(json[key]);
                    dict[key] = array[index];
                };
    
                // var id = json['id']
                // var id = id.split(',');
                // dict['id'] = id[index];
        
                // var name = json['name']
                // var name = name.split(',');
                // dict['name'] = name[index];
    
                keys = ['time_obs','time_fch', 'time_fcd']
                for (var key of keys) {
                    var array = json[key];
                    dict[key] = array;
                };
    
                C = document.getElementById('wx_plot');
                hovsize =10
                N =
                [(temp_obs = {x: dict['time_obs'], y: dict['temp_obs'], mode: 'lines', line: { color: "d62728", dash: "dot" }, yaxis: "y5", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> Temp Obs </b><br>" + "%{y:.2f} (C)<br>" + "<extra></extra>"}),
                (temp_fc = {x: dict['time_obs'], y: dict['temp_pfc'],mode: 'lines', line: { color: "d62728", width: 0.5 }, yaxis: "y5", hoverlabel:{font:{size: hovsize}},  hovertemplate: "<b> Temp Modeled </b><br>" + "%{y:.2f} (C)<br>" + "<extra></extra>" }),
                (temp_fc = {x: dict['time_fch'], y: dict['temp_fc'], mode: 'lines', line: { color: "d62728" }, yaxis: "y5",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> Temp Forecast </b><br>" + "%{y:.2f} (C)<br>" + "<extra></extra>" }),
                
                (rh_obs = {x: dict['time_obs'], y: dict['rh_obs'], mode: 'lines', line: { color: "1f77b4", dash: "dot" }, yaxis: "y4", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> RH Obs </b><br>" + "%{y:.2f} (%)<br>" + "<extra></extra>"}),
                (rh_fc = {x: dict['time_obs'], y: dict['rh_pfc'],mode: 'lines', line: { color: "1f77b4", width: 0.5 }, yaxis: "y4",   hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> RH Modeled </b><br>" + "%{y:.2f} (%)<br>" + "<extra></extra>"}),
                (rh_fc = { x: dict['time_fch'], y: dict['rh_fc'], mode: 'lines', line: { color: "1f77b4" }, yaxis: "y4",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> RH Forecast  </b><br>" + "%{y:.2f} (%)<br>" + "<extra></extra>"}),
                
                (ws_obs = {x: dict['time_obs'], y: dict['ws_obs'], mode: 'lines', line: { color: "202020", dash: "dot" }, yaxis: "y3", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> WSP Obs </b><br>" + "%{y:.2f} (km/hr)<br>" + "<extra></extra>"}),
                (ws_fc = {x: dict['time_obs'], y: dict['ws_pfc'],mode: 'lines', line: { color: "202020", width: 0.5 }, yaxis: "y3",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> WSP Modeled </b><br>" + "%{y:.2f} (km/hr)<br>" + "<extra></extra>" }),
                (ws_fc = {x: dict['time_fch'], y: dict['ws_fc'], mode: 'lines', line: { color: "202020" }, yaxis: "y3",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> WSP Forecast </b><br>" + "%{y:.2f} (km/hr)<br>" + "<extra></extra>"}),
                
                (wdir_obs = {x: dict['time_obs'], y: dict['wdir_obs'], mode: 'lines', line: { color: "7f7f7f", dash: "dot" }, yaxis: "y2",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> WDIR Obs </b><br>" + "%{y:.2f} (deg)<br>" + "<extra></extra>" }),
                (wdir_fc = {x: dict['time_obs'], y: dict['wdir_pfc'],mode: 'lines', line: { color: "7f7f7f", width: 0.5 }, yaxis: "y2",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> WDIR Modeled </b><br>" + "%{y:.2f} (deg)<br>" + "<extra></extra>"}),
                (wdir_fc = {x: dict['time_fch'], y: dict['wdir_fc'], mode: 'lines', line: { color: "7f7f7f" }, yaxis: "y2", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> WDIR Forecast </b><br>" + "%{y:.2f} (deg)<br>" + "<extra></extra>" }),
                
                (precip_obs = {x: dict['time_obs'], y: dict['precip_obs'], mode: 'lines', line: { color: "2ca02c", dash: "dot" }, yaxis: "y1",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> Precip Obs </b><br>" + "%{y:.2f} (mm)<br>" + "<extra></extra>" }),
                (precip_fc = {x: dict['time_obs'], y: dict['precip_pfc'],mode: 'lines', line: { color: "2ca02c", width: 0.5 }, yaxis: "y1",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> Precip Modeled </b><br>" + "%{y:.2f} (mm)<br>" + "<extra></extra>" }),
                (precip_fc = {x: dict['time_fch'], y: dict['precip_fc'], mode: 'lines', line: { color: "2ca02c" }, yaxis: "y1",   hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> Precip Forecast </b><br>" + "%{y:.2f} (mm)<br>" + "<extra></extra>" }),
                
                ];
                    
         
                if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
                labelsize = 10;
                ticksize = 9;
                S = {
                    autosize: false, 
                    width: 320,
                    height: 400,
                    margin: {
                      l: 50,
                      r: 30,
                      b: 50,
                      t: 68,
                      pad: 1
                    }, 
                   title: {text: "  WMO Station " + dict.wmo.toString() + " <br>Lat: " + dict.lats.toString().slice(0,6)+ ", Lon: " + dict.lons.toString().slice(0,8) + " <br>Elevation: " + dict.elev.toString().slice(0,8) + " m", x:0.05}, 
                    titlefont: { color: "#444444", size: 11 },
                    showlegend: !1,
                    yaxis5: { domain: [0.80, 0.98], title: { text: "Temp<br>(C)", font: {size: labelsize, color: "d62728" } }, tickfont: {size: ticksize, color: "d62728"}},
                    yaxis4: { domain: [0.60, 0.78],  title: { text: "RH<br>(%)", font: {size: labelsize, color: "1f77b4" } }, tickfont: {size: ticksize, color: "1f77b4"}},
                    yaxis3: { domain: [0.40, 0.58], title: { text: "WSP<br>(km/hr)", font: {size: labelsize, color: "202020" } } , tickfont: {size: ticksize, color: "202020"}},
                    yaxis2: { domain: [0.20, 0.38], title: { text: "WDIR<br>(deg)", font: {size: labelsize, color: "7f7f7f" } }, tickfont: {size: ticksize, color: "7f7f7f"}, range: [0, 360], tickvals:[0, 90, 180, 270, 360]},
                    yaxis1: { domain: [0, 0.18], title: { text: "Precip<br>(mm)", font: {size: labelsize, color: "2ca02c" } }, tickfont: {size: ticksize, color: "2ca02c"}},
                    xaxis: { title: "Date (UTC)", titlefont: { size: 10, color: "444444" }, tickfont: {size: ticksize, color: "444444"}}
                };
                }else{
                labelsize = 12;
                ticksize = 9;
                S = {
                    autosize: false, 
                    width: 600,
                    height: 450,
                    margin: {
                      l: 50,
                      r: 30,
                      b: 50,
                      t: 100,
                      pad: 2
                    },
                    title: {text: "  WMO Station " + dict.wmo.toString() + " <br>Lat: " + dict.lats.toString().slice(0,6)+ ", Lon: " + dict.lons.toString().slice(0,8) + " <br>Elevation: " + dict.elev.toString().slice(0,8) + " m", x:0.05}, 
                    titlefont: { color: "#444444", size: 13 },
                    showlegend: !1,
                    yaxis5: { domain: [0.80, 0.98], title: { text: "Temp<br>(C)", font: {size: labelsize, color: "d62728" } }, tickfont: {size: ticksize, color: "d62728"}},
                    yaxis4: { domain: [0.60, 0.78],  title: { text: "RH<br>(%)", font: {size: labelsize, color: "1f77b4" } }, tickfont: {size: ticksize, color: "1f77b4"}},
                    yaxis3: { domain: [0.40, 0.58], title: { text: "WSP<br>(km/hr)", font: {size: labelsize, color: "202020" } } , tickfont: {size: ticksize, color: "202020"}},
                    yaxis2: { domain: [0.20, 0.38], title: { text: "WDIR<br>(deg)", font: {size: labelsize, color: "7f7f7f" } }, tickfont: {size: ticksize, color: "7f7f7f"}, range: [0, 360], tickvals:[0, 90, 180, 270, 360]},
                    yaxis1: { domain: [0, 0.18], title: { text: "Precip<br>(mm)", font: {size: labelsize, color: "2ca02c" } }, tickfont: {size: ticksize, color: "2ca02c"}},
                    xaxis: { title: "Date (UTC)", titlefont: { size: 12, color: "#444444" }},
                    };           
                }
                    Plotly.newPlot(C,  N, S);
                    });
                }
    
                

    clickedCircle.openPopup()
        };



