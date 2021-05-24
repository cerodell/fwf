
// create a layer group for the weather stations
var wx_station = L.layerGroup();

// create a div tag for popup window...here you are making html in js..the div is the window the popup will display in
// make is const (ie global for use anywhere)
const div = document.createElement("div");

// name the div class...this will be refernces in css for styling
div.className = "wx-plot";
div2=div.cloneNode(!0);
// set attributes...again for css styling
div.setAttribute("id", "wx_plot");

// Create a <button> element and give attirbutes
var btn_fire = document.createElement("BUTTON");
btn_fire.setAttribute("id", "button");
btn_fire.className = "btn_fire";
btn_fire.innerHTML = "Fire Weather";
// add the button to our div we created above
div.appendChild(btn_fire);


// Create a <button> element and give attirbutes
var btn_wx = document.createElement("BUTTON");
btn_wx.setAttribute("id", "button");
btn_wx.className = "btn_wx";
btn_wx.innerHTML = "Weather";
// add the button to our div we created above
div.appendChild(btn_wx);






// add to our laygroup we created above..use fetch to retrive json file..could retrive json file with other functions but i like fetch
wx_station.onAdd = function(){
fetch(wx_keys).then(function(response){
    return response.json();
}).then(function(json){
        // parse data out of json
        var wmos = JSON.parse(json.wmo);
        var lats = JSON.parse(json.lats);
        var lons = JSON.parse(json.lons);
        var elev = JSON.parse(json.elev);
        var ffmc_obs = JSON.parse(json.ffmc_obs);
        var temp_obs = JSON.parse(json.temp_obs);
        var tz_correct = JSON.parse(json.tz_correct);

        // var name = name.split(',');
        // loop all lats/longs
        for (index = 0; index < lats.length; ++index) {
        var colors = ['#ff6760', '#ffff73', '#63a75c']
        //conditonal statment to give wx stations color
        if (temp_obs[index] != -99 && ffmc_obs[index] != -99) {
            color = colors[2];
        } else if (temp_obs[index] != -99 && ffmc_obs[index] == -99) {
            color = colors[1];
        }else {
                color = colors[0];
              }
        // add station based on lat and long and give some attibutes.. the custom(var) stuff is very helpful for later to make plots specific to that sttion
        wx_station.addLayer(L.circle([lats[index], lons[index]], {
            radius: 4000,
            weight: 0.8,
            color: 'black',
            fillColor: color,
            fillOpacity: 1,
            customId: wmos[index].toString(),
            customTZ: Math.abs(tz_correct[index]).toString(),
            customLAT: lats[index].toString(),
            customLON: lons[index].toString(),
            customEL: elev[index].toString(),
            // customNM: name[index].toString()

        // bind our div to the the popup and only active div window on click and launch circleClick function
        }).bindPopup(div, {maxWidth: "auto", maxHeight: "auto"}).on("click", circleClick));
    }
});
};


// define circleClick function..this makes the plots for each wxstation
function circleClick(e) {
    // look at the meta target data stored when genrated the wxstation circles
    var clickedCircle = e.target;
    var target_wmo = clickedCircle.options.customId;
    var tzone = clickedCircle.options.customTZ;
    var lat = clickedCircle.options.customLAT;
    var lon = clickedCircle.options.customLON;
    var elev = clickedCircle.options.customEL;

    // give purpose to our button we created in our div
    btn_fire.onclick = fwiplot;
    btn_wx.onclick = wxplot;
    // get the josn file associated with the time zone region we are in...this was done to be economical on file size
    var target_json = wxstations.slice(0,13) + String(tzone) + wxstations.slice(14,);
    // activate fwf plotting fucntion
    fwiplot();

    // define fwi ploting fucntion
    function fwiplot() {
        // use fetch to retrive our target json the tzone we are in
        fetch(target_json).then(function(response){
            return response.json();
        }).then(function(json){

                // parse data from json file
                // var name = JSON.parse(json.name);
                console.log(json.wmo);

                var wmo = JSON.parse(json.wmo);
                var index = wmo.indexOf(parseInt(target_wmo));
                // set up dictionary to populate specific wx station data from json
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
                // set keys to loop and mkae dictionary and change -99 to nan
                // i store as -99 not nan to save on file size....-99 can be 3 bits
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

                // loop other keys that dont have -99
                keys = ['wmo']
                for (var key of keys) {
                    var array = JSON.parse(json[key]);
                    console.log(array.length);

                    dict[key] = array[index];
                };

                var wx_name = json.name;
                wx_name = wx_name.replace(/'/g, '');
                wx_name = wx_name.replace('[', '');
                wx_name = wx_name.replace(']', '');
                var wx_name = wx_name.split(',')
                console.log(wx_name.length);
                console.log(index);
                dict['wx_name'] = wx_name[index].trim();
                console.log(dict['wx_name']);


                // timezone keys for the plot
                keys = ['time_obs','time_fch', 'time_fcd']
                for (var key of keys) {
                    var array = json[key];
                    dict[key] = array;
                };


                Array.prototype.insert = function ( index, item ) {
                    this.splice( index, 0, item );
                };

                // extend a few of the time arrays
                dict['time_fcd'].insert(0, dict['time_obs'][dict['time_obs'].length - 1]);
                dict['dmc_fc'].insert(0, dict['dmc_pfc'][dict['dmc_pfc'].length - 1]);
                dict['dc_fc'].insert(0, dict['dc_pfc'][dict['dc_pfc'].length - 1]);
                dict['bui_fc'].insert(0, dict['bui_pfc'][dict['bui_pfc'].length - 1]);
                dict['fwi_fc'].insert(0, dict['fwi_pfc'][dict['fwi_pfc'].length - 1]);

                // get users time zone info
                var timezone = moment.tz(Intl.DateTimeFormat().resolvedOptions().timeZone).zoneAbbr();
                // console.log(timezone);

                //Create array of timezone options to be added
                var array = [timezone ,"UTC","Geo Local"];

                //Create and append select list of timezone options
                var selectList = document.createElement("select");
                selectList.setAttribute("id", "mySelect");
                selectList.className = "time_wx";
                div.appendChild(selectList);

                //Create and append the options
                for (var i = 0; i < array.length; i++) {
                    var option = document.createElement("option");
                    option.setAttribute("value", array[i]);
                    option.text = array[i];
                    selectList.appendChild(option);
                };
                // convert time arrays based on timezone information
                function converttime(time_array, time_name) {
                        local_list2 = [];
                        arrayLength = time_array.length;
                        for (i = 0; i < arrayLength; i++) {
                        d = time_array[i] + ':00:00.000Z'
                        var newtime2 = moment.utc(d).subtract({'hours': Math.abs(tzone)}).format('YYYY-MM-DD HH:mm z');
                        var res = newtime2.slice(0, 16);
                        local_list2.push(res);
                        };
                        dict['geo_time' + time_name] = local_list2;
                        // console.log('UTC TIME');
                        // console.log(time_array);
                        // console.log('GEO TIME');
                        // console.log(local_list2);

                        local_list = [];
                        arrayLength = time_array.length;
                        for (i = 0; i < arrayLength; i++) {
                            a = new Date(time_array[i] + ':00Z').toLocaleString();
                            local_list.push(moment(a).format('YYYY-MM-DD HH:mm'));
                        };
                        dict['local_time' + time_name] = local_list;
                        // console.log('LOCAL TIME');
                        // console.log(local_list);
                    };

                    // do the time zone converstions and add to our dictiona array
                    converttime(dict['time_fcd'], '_fcd');
                    converttime(dict['time_obs'], '_obs');
                    converttime(dict['time_fch'], '_fch');

                    // console.log(dict['local_time_fcd']);
                    var int_time_obs = dict['time_obs'][0] +':00:00Z'
                    // console.log(intimeutc)

                    // console.log(int_time_obs)
                    // change our plots when user changes the prefered time zone
                    selectList.onchange = function (){
                        var value = this.value
                        if (value == "UTC"){

                            doplots3(dict['time_obs'],dict['time_fcd'], dict['time_fch'], UTCTimeMap, int_time_obs, UTCTimePlot)
                        }else if (value == "Geo Local"){
                            var geomaptimei = moment.utc(UTCTimeMap).subtract({'hours': Math.abs(tzone)}).format('YYYY-MM-DD HH:mm z');
                            var geomaptime = geomaptimei.slice(0, 16);
                            var geointtimei = moment.utc(int_time_obs).subtract({'hours': Math.abs(tzone)}).format('YYYY-MM-DD HH:mm z');
                            var geointtime = geointtimei.slice(0, 16);
                            var geoplottimei = moment.utc(UTCTimePlot).subtract({'hours': Math.abs(tzone)}).format('YYYY-MM-DD HH:mm z');
                            var geoplottime = geoplottimei.slice(0, 16);
                            doplots3(dict['geo_time_obs'],dict['geo_time_fcd'], dict['geo_time_fch'],geomaptime, geointtime, geoplottime)
                        }else if (value == timezone){
                            if (UTCTimeMap.length < 20)
                                UTCTimeMap = UTCTimeMap + 'Z';
                            var localmaptime = moment(new Date(UTCTimeMap).toLocaleString()).format('YYYY-MM-DD HH:mm');
                            var localinttime = moment(new Date(int_time_obs).toLocaleString()).format('YYYY-MM-DD HH:mm');
                            var localplottime = moment(new Date(UTCTimePlot).toLocaleString()).format('YYYY-MM-DD HH:mm');
                            doplots3(dict['local_time_obs'],dict['local_time_fcd'], dict['local_time_fch'],localmaptime, localinttime, localplottime)
                      }};



                // create our ploting function for fwi!!
                function doplots3(time_obs, time_fcd, time_fch,maptime, intitme, plottime) {
                    // check if user is on mobile devise and adjust plot size
                    if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
                        var swidth = 320;
                        var sheight = 400;
                        var sl = 50;
                        var sr = 30;
                        var sb = 60;
                        var st = 68;
                        var spad = 1;
                        var xticksize = 6;
                        var labelsize = 9;
                        var ticksize = 8;
                        var tsize = 8;
                        var t_height = 16;
                        var c_height = 18;
                        var t_f = 8;

                    }else{

                        var swidth = 700;
                        var sheight = 500;
                        var sl = 60;
                        var sr = 30;
                        var sb = 80;
                        var st = 100;
                        var spad = 2;
                        var xticksize = 11;
                        var labelsize = 11.5;
                        var ticksize = 10;
                        var tsize = 14;
                        var t_height = 20;
                        var c_height = 22;
                        var t_f = 12;

                    };


                // call on div the plotly js with populate
                C = document.getElementById('wx_plot');
                hovsize = 12
                // this is ungly but sets up all the vars to be ploted and defines the subplot they are in
                N =
                [(ffmc_obs = {x: time_obs, y: dict['ffmc_obs'], mode: 'lines', line: { color: "ff7f0e", dash: "dot" }, yaxis: "y6",  hoverlabel:{font:{size: hovsize, color: "#ffffff"}, bordercolor: "#ffffff"}, hovertemplate: "<b> FFMC Observed </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (ffmc_fc = {x: time_obs, y: dict['ffmc_pfc'],mode: 'lines', line: { color: "ff7f0e", width: 0.5 }, yaxis: "y6",  hoverlabel:{font:{size: hovsize, color: "#ffffff"}, bordercolor: "#ffffff"}, hovertemplate: "<b> FFMC Previous Forecast </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (ffmc_fc = {x: time_fch, y: dict['ffmc_fc'], mode: 'lines', line: { color: "ff7f0e" }, yaxis: "y6",  hoverlabel:{font:{size: hovsize, color: "#ffffff"}, bordercolor: "#ffffff"}, hovertemplate: "<b> FFMC Current Forecast </b><br>" + "%{y:.2f} <br>" + "<extra></extra>"}),

                (dmc_obs = {x: time_obs, y: dict['dmc_obs'], mode: 'lines', line: { color: "2ca02c", dash: "dot" }, yaxis: "y5",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> DMC Observed </b><br>" + "%{y:.2f} <br>" + "<extra></extra>"}),
                (dmc_fc = {x: time_obs, y: dict['dmc_pfc'],mode: 'lines', line: { color: "2ca02c", width: 0.5 }, yaxis: "y5",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> DMC Previous Forecast </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (dmc_fc = { x: time_fcd, y: dict['dmc_fc'], mode: 'lines', line: { color: "2ca02c" }, yaxis: "y5", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> DMC Current Forecast </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),

                (dc_obs = {x: time_obs, y: dict['dc_obs'], mode: 'lines', line: { color: "8c564b", dash: "dot" }, yaxis: "y4", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> DC Observed </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (dc_fc = {x: time_obs, y: dict['dc_pfc'],mode: 'lines', line: { color: "8c564b", width: 0.5 }, yaxis: "y4", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> DC Previous Forecast </b><br>" + "%{y:.2f} <br>" + "<extra></extra>"}),
                (dc_fc = {x: time_fcd, y: dict['dc_fc'], mode: 'lines', line: { color: "8c564b" }, yaxis: "y4",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> DC Current Forecast </b><br>" + "%{y:.2f} <br>" + "<extra></extra>"}),

                (isi_obs = {x: time_obs, y: dict['isi_obs'], mode: 'lines', line: { color: "9467bd", dash: "dot" }, yaxis: "y3",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> ISI Observed </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (isi_fc = {x: time_obs, y: dict['isi_pfc'],mode: 'lines', line: { color: "9467bd", width: 0.5 }, yaxis: "y3", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> ISI Previous Forecast </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (isi_fc = {x: time_fch, y: dict['isi_fc'], mode: 'lines', line: { color: "9467bd" }, yaxis: "y3",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> ISI Current Forecast </b><br>" + "%{y:.2f} <br>" + "<extra></extra>"}),

                (bui_obs = {x: time_obs, y: dict['bui_obs'], mode: 'lines', line: { color: "7f7f7f", dash: "dot" }, yaxis: "y2",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> BUI Observed </b><br>" + "%{y:.2f} <br>" + "<extra></extra>"}),
                (bui_fc = {x: time_obs, y: dict['bui_pfc'],mode: 'lines', line: { color: "7f7f7f", width: 0.5 }, yaxis: "y2",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> BUI Previous Forecast </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (bui_fc = {x: time_fcd, y: dict['bui_fc'], mode: 'lines', line: { color: "7f7f7f" }, yaxis: "y2",   hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> BUI Current Forecast </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),

                (fwi_obs = {x: time_obs, y: dict['fwi_obs'], mode: 'lines', line: { color: "d62728", dash: "dot" }, yaxis: "y1",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> FWI Observed </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (fwi_fc = {x: time_obs, y: dict['fwi_pfc'],mode: 'lines', line: { color: "d62728", width: 0.5 }, yaxis: "y1", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> FWI Previous Forecast </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (fwi_fc = {x: time_fcd, y: dict['fwi_fc'], mode: 'lines', line: { color: "d62728" }, yaxis: "y1", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> FWI Current Forecast </b><br>" + "%{y:.2f} <br>" + "<extra></extra>"}),
                ]


                // set some figure attirbutes
                labelsize = 12,
                ticksize = 9,
                S = {
                    autosize: false,
                    width: swidth,
                    height: sheight,
                    margin: {
                      l: sl,
                      r: sr,
                      b: sb,
                      t: st,
                      pad: spad
                    },
                    title: {text: dict.wx_name + " <br>WMO: " + dict.wmo.toString() + " <br>Lat: " + lat.toString().slice(0,6)+ ", Lon: " + lon.toString().slice(0,8) + " <br>Elevation: " +  elev.toString().slice(0,8) + " m", x:0.05},
                    titlefont: { color: "#444444", size: tsize },
                    showlegend: !1,
                    yaxis6: {domain: [.8, .94], title: { text: "FFMC", font: { size: labelsize, color: "ff7f0e" } }, tickfont: {size: ticksize, color: "ff7f0e"}},
                    yaxis5: {domain: [0.64, 0.78], title: { text: "DMC", font: { size: labelsize,color: "2ca02c" } }, tickfont: {size: ticksize, color: "2ca02c"}},
                    yaxis4: { domain: [0.48, 0.62], title: { text: "DC", font: { size: labelsize,color: "8c564b" } }, tickfont: {size: ticksize, color: "8c564b"}},
                    yaxis3: { domain: [0.32, 0.46], title: { text: "ISI", font: {size: labelsize, color: "9467bd" } }, tickfont: {size: ticksize, color: "9467bd"}},
                    yaxis2: { domain: [0.16, 0.30], title: { text: "BUI", font: { size: labelsize, color: "7f7f7f" } }, tickfont: {size: ticksize, color: "7f7f7f"}},
                    yaxis1: { domain: [0, 0.14], title: { text: "FWI", font: {size: labelsize, color: "d62728" } }, tickfont: {size: ticksize, color: "d62728"}},
                    xaxis: { tickfont: {size: xticksize, color: "444444"}},
                    shapes: [{
                        type: 'line',
                        x0: maptime,
                        y0: 0,
                        x1: maptime,
                        yref: 'paper',
                        y1: 0.94,
                        line: {
                          color: 'grey',
                          width: 1.5,
                          dash: 'dot'
                        }},
                        {
                            type: 'rect',
                            xref: 'x',
                            yref: 'paper',
                            x0: intitme,
                            y0: 0,
                            x1: plottime,
                            y1: 0.94,
                            fillcolor: '#A7A7A7',
                            opacity: 0.2,
                            line: {
                                width: 0
                            }
                        }]
                };
                    Plotly.newPlot(C,  N, S);
                }
                if (UTCTimeMap.length < 20)
                UTCTimeMap = UTCTimeMap + 'Z';
                var maptime = moment(new Date(UTCTimeMap).toLocaleString()).format('YYYY-MM-DD HH:mm');
                var inttime = moment(new Date(int_time_obs).toLocaleString()).format('YYYY-MM-DD HH:mm');
                var plottime = moment(new Date(UTCTimePlot).toLocaleString()).format('YYYY-MM-DD HH:mm');

                // trgiger the plot fucntion with default setup
                doplots3(dict['local_time_obs'],dict['local_time_fcd'], dict['local_time_fch'],maptime, inttime, plottime);
             });

                }


    // define meterology ploting fucntion...i didnt comment this section as its nearly identical to the fwi fucntion but with met vars
    function wxplot() {
        fetch(target_json).then(function(response){
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
                // keys = ['elev', 'lats', 'lons','tz_correct', 'wmo']
                keys = ['wmo']
                for (var key of keys) {
                    var array = JSON.parse(json[key]);
                    dict[key] = array[index];
                };

                var wx_name = json.name;
                wx_name = wx_name.replace(/'/g, '');
                wx_name = wx_name.replace('[', '');
                wx_name = wx_name.replace(']', '');
                var wx_name = wx_name.split(',')
                console.log(wx_name);
                console.log(index);
                dict['wx_name'] = wx_name[index].trim();
                console.log(dict['wx_name']);

                keys = ['time_obs','time_fch', 'time_fcd']
                for (var key of keys) {
                    var array = json[key];
                    dict[key] = array;
                };

                // console.log(Intl.DateTimeFormat().resolvedOptions().timeZone)
                var timezone = moment.tz(Intl.DateTimeFormat().resolvedOptions().timeZone).zoneAbbr();
                // console.log(timezone);

                //Create array of options to be added
                var array = [timezone ,"UTC","Geo Local"];

                //Create and append select list
                var selectList = document.createElement("select");
                selectList.setAttribute("id", "mySelect");
                selectList.className = "time_wx";
                div.appendChild(selectList);

                //Create and append the options
                for (var i = 0; i < array.length; i++) {
                    var option = document.createElement("option");
                    option.setAttribute("value", array[i]);
                    option.text = array[i];
                    selectList.appendChild(option);
                };

                function converttime(time_array, time_name) {
                        local_list2 = [];
                        arrayLength = time_array.length;
                        for (i = 0; i < arrayLength; i++) {
                        d = time_array[i] + ':00:00.000Z'
                        var newtime2 = moment.utc(d).subtract({'hours': Math.abs(tzone)}).format('YYYY-MM-DD HH:mm z');
                        var res = newtime2.slice(0, 16);
                        local_list2.push(res);
                        };
                        dict['geo_time' + time_name] = local_list2;
                        // console.log('UTC TIME');
                        // console.log(time_array);
                        // console.log('GEO TIME');
                        // console.log(local_list2);

                        local_list = [];
                        arrayLength = time_array.length;
                        for (i = 0; i < arrayLength; i++) {
                            a = new Date(time_array[i] + ':00Z').toLocaleString();
                            local_list.push(moment(a).format('YYYY-MM-DD HH:mm'));
                        };
                        dict['local_time' + time_name] = local_list;
                        // console.log('LOCAL TIME');
                        // console.log(local_list);
                    };

                    converttime(dict['time_fcd'], '_fcd');
                    converttime(dict['time_obs'], '_obs');
                    converttime(dict['time_fch'], '_fch');

                    // console.log(dict['local_time_fcd']);
                    var int_time_obs = dict['time_obs'][0] +':00:00Z'
                    // console.log(intimeutc)

                    // console.log(int_time_obs)

                    selectList.onchange = function (){
                        var value = this.value
                        if (value == "UTC"){

                            doplots4(dict['time_obs'],dict['time_fcd'], dict['time_fch'], UTCTimeMap, int_time_obs, UTCTimePlot)
                        }else if (value == "Geo Local"){
                            var geomaptimei = moment.utc(UTCTimeMap).subtract({'hours': Math.abs(tzone)}).format('YYYY-MM-DD HH:mm z');
                            var geomaptime = geomaptimei.slice(0, 16);
                            var geointtimei = moment.utc(int_time_obs).subtract({'hours': Math.abs(tzone)}).format('YYYY-MM-DD HH:mm z');
                            var geointtime = geointtimei.slice(0, 16);
                            var geoplottimei = moment.utc(UTCTimePlot).subtract({'hours': Math.abs(tzone)}).format('YYYY-MM-DD HH:mm z');
                            var geoplottime = geoplottimei.slice(0, 16);
                            doplots4(dict['geo_time_obs'],dict['geo_time_fcd'], dict['geo_time_fch'],geomaptime, geointtime, geoplottime)
                        }else if (value == timezone){
                            if (UTCTimeMap.length < 20)
                                UTCTimeMap = UTCTimeMap + 'Z';
                            var localmaptime = moment(new Date(UTCTimeMap).toLocaleString()).format('YYYY-MM-DD HH:mm');
                            var localinttime = moment(new Date(int_time_obs).toLocaleString()).format('YYYY-MM-DD HH:mm');
                            var localplottime = moment(new Date(UTCTimePlot).toLocaleString()).format('YYYY-MM-DD HH:mm');
                            doplots4(dict['local_time_obs'],dict['local_time_fcd'], dict['local_time_fch'],localmaptime, localinttime, localplottime)
                      }};


                      function doplots4(time_obs, time_fcd, time_fch,maptime, intitme, plottime) {
                        if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
                            var swidth = 320;
                            var sheight = 400;
                            var sl = 50;
                            var sr = 30;
                            var sb = 60;
                            var st = 68;
                            var spad = 1;
                            var xticksize = 6;
                            var labelsize = 9;
                            var ticksize = 8;
                            var tsize = 8;
                            var t_height = 16;
                            var c_height = 18;
                            var t_f = 8;

                        }else{

                            var swidth = 700;
                            var sheight = 500;
                            var sl = 60;
                            var sr = 30;
                            var sb = 80;
                            var st = 100;
                            var spad = 2;
                            var xticksize = 11;
                            var labelsize = 11.5;
                            var ticksize = 10;
                            var tsize = 14;
                            var t_height = 20;
                            var c_height = 22;
                            var t_f = 12;

                        };

                C = document.getElementById('wx_plot');
                hovsize =13
                N =
                [(temp_obs = {x: time_obs, y: dict['temp_obs'], mode: 'lines', line: { color: "d62728", dash: "dot" }, yaxis: "y5", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> Temp Observed </b><br>" + "%{y:.2f} (C)<br>" + "<extra></extra>"}),
                (temp_fc = {x: time_obs, y: dict['temp_pfc'],mode: 'lines', line: { color: "d62728", width: 0.5 }, yaxis: "y5", hoverlabel:{font:{size: hovsize}},  hovertemplate: "<b> Temp Previous Forecast </b><br>" + "%{y:.2f} (C)<br>" + "<extra></extra>" }),
                (temp_fc = {x: time_fch, y: dict['temp_fc'], mode: 'lines', line: { color: "d62728" }, yaxis: "y5",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> Temp Current Forecast </b><br>" + "%{y:.2f} (C)<br>" + "<extra></extra>" }),

                (rh_obs = {x: time_obs, y: dict['rh_obs'], mode: 'lines', line: { color: "1f77b4", dash: "dot" }, yaxis: "y4", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> RH Observed </b><br>" + "%{y:.2f} (%)<br>" + "<extra></extra>"}),
                (rh_fc = {x: time_obs, y: dict['rh_pfc'],mode: 'lines', line: { color: "1f77b4", width: 0.5 }, yaxis: "y4",   hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> RH Previous Forecast </b><br>" + "%{y:.2f} (%)<br>" + "<extra></extra>"}),
                (rh_fc = { x: time_fch, y: dict['rh_fc'], mode: 'lines', line: { color: "1f77b4" }, yaxis: "y4",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> RH Current Forecast  </b><br>" + "%{y:.2f} (%)<br>" + "<extra></extra>"}),

                (ws_obs = {x: time_obs, y: dict['ws_obs'], mode: 'lines', line: { color: "202020", dash: "dot" }, yaxis: "y3", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> WSP Observed </b><br>" + "%{y:.2f} (km/hr)<br>" + "<extra></extra>"}),
                (ws_fc = {x: time_obs, y: dict['ws_pfc'],mode: 'lines', line: { color: "202020", width: 0.5 }, yaxis: "y3",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> WSP Previous Forecast </b><br>" + "%{y:.2f} (km/hr)<br>" + "<extra></extra>" }),
                (ws_fc = {x: time_fch, y: dict['ws_fc'], mode: 'lines', line: { color: "202020" }, yaxis: "y3",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> WSP Current Forecast </b><br>" + "%{y:.2f} (km/hr)<br>" + "<extra></extra>"}),

                (wdir_obs = {x: time_obs, y: dict['wdir_obs'], mode: 'lines', line: { color: "7f7f7f", dash: "dot" }, yaxis: "y2",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> WDIR Observed </b><br>" + "%{y:.2f} (deg)<br>" + "<extra></extra>" }),
                (wdir_fc = {x: time_obs, y: dict['wdir_pfc'],mode: 'lines', line: { color: "7f7f7f", width: 0.5 }, yaxis: "y2",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> WDIR Previous Forecast </b><br>" + "%{y:.2f} (deg)<br>" + "<extra></extra>"}),
                (wdir_fc = {x: time_fch, y: dict['wdir_fc'], mode: 'lines', line: { color: "7f7f7f" }, yaxis: "y2", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> WDIR Current Forecast </b><br>" + "%{y:.2f} (deg)<br>" + "<extra></extra>" }),

                (precip_obs = {x: time_obs, y: dict['precip_obs'], mode: 'lines', line: { color: "2ca02c", dash: "dot" }, yaxis: "y1",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> Precip Observed </b><br>" + "%{y:.2f} (mm)<br>" + "<extra></extra>" }),
                (precip_fc = {x: time_obs, y: dict['precip_pfc'],mode: 'lines', line: { color: "2ca02c", width: 0.5 }, yaxis: "y1",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> Precip Previous Forecast </b><br>" + "%{y:.2f} (mm)<br>" + "<extra></extra>" }),
                (precip_fc = {x: time_fch, y: dict['precip_fc'], mode: 'lines', line: { color: "2ca02c" }, yaxis: "y1",   hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> Precip Current Forecast </b><br>" + "%{y:.2f} (mm)<br>" + "<extra></extra>" }),

                ]


                labelsize = 12,
                ticksize = 9,
                S = {
                    autosize: false,
                    width: swidth,
                    height: sheight,
                    margin: {
                      l: sl,
                      r: sr,
                      b: sb,
                      t: st,
                      pad: spad
                    },                    title: {text: dict.wx_name + " <br>WMO: " + dict.wmo.toString() + " <br>Lat: " + lat.toString().slice(0,6)+ ", Lon: " + lon.toString().slice(0,8) + " <br>Elevation: " +  elev.toString().slice(0,8) + " m", x:0.05},
                    titlefont: { color: "#444444", size: tsize },
                    showlegend: !1,
                    yaxis5: { domain: [0.80, 0.98], title: { text: "Temp<br>(C)", font: {size: labelsize, color: "d62728" } }, tickfont: {size: ticksize, color: "d62728"}},
                    yaxis4: { domain: [0.60, 0.78],  title: { text: "RH<br>(%)", font: {size: labelsize, color: "1f77b4" } }, tickfont: {size: ticksize, color: "1f77b4"}},
                    yaxis3: { domain: [0.40, 0.58], title: { text: "WSP<br>(km/hr)", font: {size: labelsize, color: "202020" } } , tickfont: {size: ticksize, color: "202020"}},
                    yaxis2: { domain: [0.20, 0.38], title: { text: "WDIR<br>(deg)", font: {size: labelsize, color: "7f7f7f" } }, tickfont: {size: ticksize, color: "7f7f7f"}, range: [0, 360], tickvals:[0, 90, 180, 270, 360]},
                    yaxis1: { domain: [0, 0.18], title: { text: "Precip<br>(mm)", font: {size: labelsize, color: "2ca02c" } }, tickfont: {size: ticksize, color: "2ca02c"}},
                    xaxis: { tickfont: {size: xticksize, color: "444444"}},
                    shapes: [{
                        type: 'line',
                        x0: maptime,
                        y0: 0,
                        x1: maptime,
                        yref: 'paper',
                        y1: 0.98,
                        line: {
                          color: 'grey',
                          width: 1.5,
                          dash: 'dot'
                        }},
                        {
                            type: 'rect',
                            xref: 'x',
                            yref: 'paper',
                            x0: intitme,
                            y0: 0,
                            x1: plottime,
                            y1: 0.98,
                            fillcolor: '#A7A7A7',
                            opacity: 0.2,
                            line: {
                                width: 0
                            }
                         }]
                        };
                        Plotly.newPlot(C,  N, S);
                        }
                        if (UTCTimeMap.length < 20)
                    UTCTimeMap = UTCTimeMap + 'Z';
                    var maptime = moment(new Date(UTCTimeMap).toLocaleString()).format('YYYY-MM-DD HH:mm');
                    var inttime = moment(new Date(int_time_obs).toLocaleString()).format('YYYY-MM-DD HH:mm');
                    var plottime = moment(new Date(UTCTimePlot).toLocaleString()).format('YYYY-MM-DD HH:mm');

                    doplots4(dict['local_time_obs'],dict['local_time_fcd'], dict['local_time_fch'],maptime, inttime, plottime);

                    });
                }



    // get meta info of wxstation on popup!
    clickedCircle.openPopup()
        };
