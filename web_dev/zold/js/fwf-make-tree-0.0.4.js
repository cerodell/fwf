var redIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

let intimeutc = tinital



const buffer = 0.5
var point_list = [];
var file_list = [];

map.doubleClickZoom.disable();
div2.className = "wx-plot2";
div2.setAttribute("id", "wx_plot2");

var btn_fire2 = document.createElement("BUTTON");   // Create a <button> element
btn_fire2.setAttribute("id", "button");
btn_fire2.className = "btn_fire2";
btn_fire2.innerHTML = "Fire Weather";
// Insert text
div2.appendChild(btn_fire2);                       // Append <button> to <body>


var btn_wx2 = document.createElement("BUTTON");   // Create a <button> element
btn_wx2.setAttribute("id", "button");
btn_wx2.className = "btn_wx2";
btn_wx2.innerHTML = "Weather";                   // Insert text
div2.appendChild(btn_wx2);


var btn_fbp = document.createElement("BUTTON");   // Create a <button> element
btn_fbp.setAttribute("id", "button");
btn_fbp.className = "btn_fbp";
btn_fbp.innerHTML = "Fire Behavior";                   // Insert text
div2.appendChild(btn_fbp);





div3 = div.cloneNode(!0);
div3.className = "wx-plot3";
div3.setAttribute("id", "wx_plot3");

var btn_fire3 = document.createElement("BUTTON");   // Create a <button> element
btn_fire3.setAttribute("id", "button");
btn_fire3.className = "btn_fire3";
btn_fire3.innerHTML = "Fire Weather";
// Insert text
div3.appendChild(btn_fire3);                       // Append <button> to <body>


var btn_wx3 = document.createElement("BUTTON");   // Create a <button> element
btn_wx3.setAttribute("id", "button");
btn_wx3.className = "btn_wx3";
btn_wx3.innerHTML = "Weather";                   // Insert text
div3.appendChild(btn_wx3);


var btn_fbp3 = document.createElement("BUTTON");   // Create a <button> element
btn_fbp3.setAttribute("id", "button");
btn_fbp3.className = "btn_fbp3";
btn_fbp3.innerHTML = "Fire Behavior";                   // Insert text
div3.appendChild(btn_fbp3);


let fwfclicklocation;
fwfclicklocation = new L.marker();


var filedate =  tinital.slice(0,4) +  tinital.slice(5,7) +  tinital.slice(8,10) +  tinital.slice(11,13)



var searchboxControl=createSearchboxControl();
const control = new searchboxControl({
    sidebarTitleText: 'Information',
    sidebarMenuItems: {
        Items: [
            { type: "link", name: "Smoke Forecasts", href: "https://firesmoke.ca/", icon: "icon-fire" },
            { type: "link", name: "Weather Forecast Research Team", href: "https://weather.eos.ubc.ca/cgi-bin/index.cgi", icon: "icon-cloudy" },
            { type: "link", name: "Contact Inforamtion", href: "https://firesmoke.ca/contact/", icon: "icon-phone" },
            { type: "link", name: "Documentation", href: "https://cerodell.github.io/fwf-docs/index.html", icon: "icon-git" },
            { type: "link", name: "fwf-daily-d02", href: "fwf-daily-d02-"+ filedate+".nc", download:"fwf-daily-d02", icon: "icon-data"},
            { type: "link", name: "fwf-hourly-d02", href: "fwf-hourly-d02-"+ filedate+".nc", download:"fwf-hourly-d02", icon: "icon-data"},
            { type: "link", name: "fwf-daily-d03", href: "fwf-daily-d03-"+ filedate+".nc", download:"fwf-daily-d03", icon: "icon-data"},
            { type: "link", name: "fwf-hourly-d03", href: "fwf-hourly-d03-"+ filedate+".nc", download:"fwf-hourly-d03s", icon: "icon-data"},
            { type: "link", name: "ReadMe", href: "https://cerodell.github.io/fwf-docs/build/html/view.html#general", icon: "icon-info" },
            { type: "text", name: "<br> The Fire Weather Forecasts are experimental in that they are produced by a system that is part of an ongoing research project. They are subject to uncertainties in both the weather forecasts and in the empirical formulas used to derive fuel moisture content."},

        ]
    }
});




ObjectFun = {
    confuels: function (a){
    console.log(parseInt(a));
    // var fuel_id = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'D1', 'M1 C25%', 'M1/M2 C35%', 'M1/M2 C50%', 'M1/M2 C65%', 'S1', 'O1a', 'O1b', 'Water', 'Non-fuel', 'Urban or built-up area'];
    var fuel_id = ['C1 - Spruce–Lichen Woodland', 'C2 - Boreal Spruce', 'C3 - Mature Jack or Lodgepole Pine', 'C4 - Immature Jack or Lodgepole Pine',
     'C5 - Red and White Pine', 'C6 - Conifer Plantation', 'C7 - Ponderosa Pine–Douglas-Fir', 'D1 - Leafless Aspen',
    'M1 C25% - Boreal Mixedwood', 'M1/M2 C35% - Boreal Mixedwood', 'M1/M2 C50% - Boreal Mixedwood', 'M1/M2 C65% - Boreal Mixedwood',
    'S1 - Jack or Lodgepole Pine Slash', 'O1a - Matted Grass', 'O1b - Tall Grass', 'Water', 'Non-fuel', 'Urban'];
    var fuel_code = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19];
    var index = fuel_code.indexOf(parseInt(a));
    var fu = fuel_id[index];
    console.log(fu);
    return fu
    }
}

function makeplotly(e) {
    let hovsize = 13;
    console.log(e);
    var clickedCircle = e.target;
    var json_dir = clickedCircle.options.customId;
    var index = clickedCircle.options.customIdx;

    console.log(index);
    var ll = clickedCircle._latlng
    btn_fire2.onclick = fwiplot2;
    btn_wx2.onclick = wxplot2;
    btn_fbp.onclick = fbpplot;
    var o = [ll.lat,ll.lng]

    // console.log(o);
    var C = document.getElementById('wx_plot2');

    fwiplot2();
    function fwiplot2() {
        fetch(json_dir).then(function(response){
            return response.json();
        }).then(function(n){
        var h = index
        var w = n.XLAT[h];
        var v = n.XLONG[h];
        var tz = n.TZONE[h];
        var ff = n.FUEL[h];
        var fu = ObjectFun.confuels(ff);
        console.log(fu);


        // console.log(Intl.DateTimeFormat().resolvedOptions().timeZone)
        var timezone = moment.tz(Intl.DateTimeFormat().resolvedOptions().timeZone).zoneAbbr();
        // console.log(timezone);

        //Create array of options to be added
        var array = [timezone ,"UTC","Geo Local"];

        //Create and append select list
        var selectList = document.createElement("select");
        selectList.setAttribute("id", "mySelect");
        selectList.className = "time_wx";
        div2.appendChild(selectList);

        //Create and append the options
        for (var i = 0; i < array.length; i++) {
            var option = document.createElement("option");
            option.setAttribute("value", array[i]);
            option.text = array[i];
            selectList.appendChild(option);
        };


        var dict = {};
        var arrayColumn = (arr, n) => arr.map(x => x[n]);
        keys = ['dsr', 'ffmc', 'rh', 'isi', 'fwi', 'temp',
                'ws', 'wdir', 'precip', 'dc', 'dmc', 'bui'];

        for (var key of keys) {
            var array = JSON.parse(n[key]);
            var array = arrayColumn(array,h);
            dict[key] = array;
        };

        dict['time'] = n["Time"];
        dict['day'] = n["Day"];

        local_list2 = [];
        arrayLength = dict['time'].length;
        for (i = 0; i < arrayLength; i++) {
        d = dict['time'][i] + ':00:00.000Z'
        var newtime2 = moment.utc(d).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
        var res = newtime2.slice(0, 16);
        local_list2.push(res);
        };
        dict['geo_time'] = local_list2;
        local_list = [];
        arrayLength = dict['time'].length;
        for (i = 0; i < arrayLength; i++) {
            a = new Date(dict['time'][i] + ':00Z').toLocaleString();
            local_list.push(moment(a).format('YYYY-MM-DD HH:mm'));
        };
        dict['local_time'] = local_list;

        selectList.onchange = function (){
            var value = this.value
            if (value == "UTC"){
                doplots(dict['time'],UTCTimeMap, intimeutc, UTCTimePlot)
            }else if (value == "Geo Local"){
                var geomaptimei = moment.utc(UTCTimeMap).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
                var geomaptime = geomaptimei.slice(0, 16);
                var geointtimei = moment.utc(intimeutc).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
                var geointtime = geointtimei.slice(0, 16);
                var geoplottimei = moment.utc(UTCTimePlot).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
                var geoplottime = geoplottimei.slice(0, 16);
                doplots(dict['geo_time'],geomaptime, geointtime, geoplottime)
            }else if (value == timezone){
                if (UTCTimeMap.length < 20)
                    UTCTimeMap = UTCTimeMap + 'Z';
                var localmaptime = moment(new Date(UTCTimeMap).toLocaleString()).format('YYYY-MM-DD HH:mm');
                var localinttime = moment(new Date(intimeutc).toLocaleString()).format('YYYY-MM-DD HH:mm');
                var localplottime = moment(new Date(UTCTimePlot).toLocaleString()).format('YYYY-MM-DD HH:mm');
                doplots(dict['local_time'],localmaptime, localinttime, localplottime)
          }};




        function doplots(final_time,maptime, intitme, plottime) {

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

            T = [
                ["DMC", "DC", "BUI", "FWI", "DSR"],
                [dict['dmc'][0], dict['dc'][0], dict['bui'][0], dict['fwi'][0], dict['dsr'][0]],
                [dict['dmc'][1], dict['dc'][1], dict['bui'][1], dict['fwi'][1], dict['dsr'][1]],
            ];

            N =
            ((ffmc = {x: final_time, y: dict['ffmc'], mode: 'lines', line: { color: "ff7f0e" }, yaxis: "y2",  hoverlabel:{font:{size: hovsize, color: "#ffffff"}, bordercolor: "#ffffff"}, hovertemplate: "<b> FFMC </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
            (isi = {x: final_time, y: dict['isi'], mode: 'lines', line: { color: "9467bd" }, yaxis: "y1",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> ISI </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),

            [
                {
                    type: "table",
                    header: { values: [["Index/Code"], [dict['day'][0]], [dict['day'][1]]], align: "center", height:t_height, line: {color: "444444" }, fill: { color: "444444E6" }, font: { family: "inherit", size: t_f, color: "white" } },
                    cells: { values: T, align: "center",  height:c_height, line: { color: "444444", width: 1 }, fill: { color:[["#2ca02c1A", "#8c564b1A", "7f7f7f1A", "d627281A", "0000001A"]] }, font: { family: "inherit", size: 11, color:[["#2ca02c", "#8c564b", "7f7f7f", "d62728", "000000"]]} },
                    xaxis: "x",
                    yaxis: "y",
                    domain: { x: [0.0, 1.0], y: [0.54, 1] },
                },
                ffmc,
                isi,
            ]
            );

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
                title: {text: "UBC Fire Weather Forecast " + "<br>Lat: " + w.toString().slice(0,6) + ", Lon: " + v.toString().slice(0,8) +"<br>Fuel Type: " + fu.toString(), x:0.05},

                titlefont: { color: "#444444", size: tsize },
                showlegend: !1,
                yaxis2: {domain: [.27, .54], title: { text: "FFMC", font: { size: labelsize, color: "ff7f0e" } }, tickfont: {size: ticksize, color: "ff7f0e"}},
                yaxis1: { domain: [0.0, 0.26], title: { text: "ISI", font: {size: labelsize, color: "9467bd" } }, tickfont: {size: ticksize, color: "9467bd"}},
                xaxis: { tickfont: {size: xticksize, color: "444444"}},
                shapes: [{
                    type: 'line',
                    x0: maptime,
                    y0: 0,
                    x1: maptime,
                    yref: 'paper',
                    y1: 0.54,
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
                        y1: 0.54,
                        fillcolor: '#A7A7A7',
                        opacity: 0.2,
                        line: {
                            width: 0
                        }
                    }]
            }

        Plotly.newPlot(C,  N, S);
        };
        if (UTCTimeMap.length < 20)
            UTCTimeMap = UTCTimeMap + 'Z';
        var maptime = moment(new Date(UTCTimeMap).toLocaleString()).format('YYYY-MM-DD HH:mm');
        var inttime = moment(new Date(intimeutc).toLocaleString()).format('YYYY-MM-DD HH:mm');
        var plottime = moment(new Date(UTCTimePlot).toLocaleString()).format('YYYY-MM-DD HH:mm');
        doplots(dict['local_time'],maptime, inttime, plottime);

        });

        };

        function wxplot2() {
            fetch(json_dir).then(function(response){
                return response.json();
            }).then(function(n){
            var h = index
            var w = n.XLAT[h];
            var v = n.XLONG[h];
            var tz = n.TZONE[h];
            var ff = n.FUEL[h];
            var fu = ObjectFun.confuels(ff);
            console.log(fu);

            // console.log(Intl.DateTimeFormat().resolvedOptions().timeZone)
            var timezone = moment.tz(Intl.DateTimeFormat().resolvedOptions().timeZone).zoneAbbr();
            // console.log(timezone);

            //Create array of options to be added
            var array = [timezone ,"UTC", "Geo Local"];

            //Create and append select list
            var selectList = document.createElement("select");
            selectList.setAttribute("id", "mySelect");
            selectList.className = "time_wx";
            div2.appendChild(selectList);

            //Create and append the options
            for (var i = 0; i < array.length; i++) {
                var option = document.createElement("option");
                option.setAttribute("value", array[i]);
                option.text = array[i];
                selectList.appendChild(option);
            }

            var dict = {};
            var arrayColumn = (arr, n) => arr.map(x => x[n]);
            keys = ['dsr', 'ffmc', 'rh', 'isi', 'fwi', 'temp',
                    'ws', 'wdir', 'precip', 'dc', 'dmc', 'bui'];

            for (var key of keys) {
                var array = JSON.parse(n[key]);
                var array = arrayColumn(array,h);
                dict[key] = array;
            };

            dict['time'] = n["Time"];
            dict['day'] = n["Day"];


            local_list2 = [];
            arrayLength = dict['time'].length;
            for (i = 0; i < arrayLength; i++) {
            d = dict['time'][i]
            var newtime2 = moment.utc(d).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
            var res = newtime2.slice(0, 16);
            local_list2.push(res)
            };
            dict['geo_time'] = local_list2;

            local_list = [];
            arrayLength = dict['time'].length;
            for (i = 0; i < arrayLength; i++) {
                a = new Date(dict['time'][i] + ':00Z').toLocaleString()
                local_list.push(moment(a).format('YYYY-MM-DD HH:mm'))
            };

            dict['local_time'] = local_list;

            selectList.onchange = function (){
                var value = this.value
                if (value == "UTC"){

                    doplots2(dict['time'],UTCTimeMap, intimeutc, UTCTimePlot)
                }else if (value == "Geo Local"){
                    var geomaptimei = moment.utc(UTCTimeMap).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
                    var geomaptime = geomaptimei.slice(0, 16);
                    var geointtimei = moment.utc(intimeutc).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
                    var geointtime = geointtimei.slice(0, 16);
                    var geoplottimei = moment.utc(UTCTimePlot).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
                    var geoplottime = geoplottimei.slice(0, 16);
                    doplots2(dict['geo_time'],geomaptime, geointtime, geoplottime)
                }else if (value == timezone){
                    if (UTCTimeMap.length < 20)
                        UTCTimeMap = UTCTimeMap + 'Z';
                    var localmaptime = moment(new Date(UTCTimeMap).toLocaleString()).format('YYYY-MM-DD HH:mm');
                    var localinttime = moment(new Date(intimeutc).toLocaleString()).format('YYYY-MM-DD HH:mm');
                    var localplottime = moment(new Date(UTCTimePlot).toLocaleString()).format('YYYY-MM-DD HH:mm');
                    doplots2(dict['local_time'],localmaptime, localinttime, localplottime)
              }};


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



            function doplots2(final_time,maptime, intitme, plottime) {
                N =
                [(temp = {x: final_time, y: dict['temp'], mode: 'lines', line: { color: "d62728" }, yaxis: "y5", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> Temp </b><br>" + "%{y:.2f} (C)<br>" + "<extra></extra>"}),
                (rh = {x: final_time, y: dict['rh'], mode: 'lines', line: { color: "1f77b4" }, yaxis: "y4", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> RH </b><br>" + "%{y:.2f} (%)<br>" + "<extra></extra>"}),
                (ws = {x: final_time, y: dict['ws'], mode: 'lines', line: { color: "202020" }, yaxis: "y3", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> WSP </b><br>" + "%{y:.2f} (km/hr)<br>" + "<extra></extra>"}),
                (wdir = {x: final_time, y: dict['wdir'], mode: 'lines', line: { color: "7f7f7f" }, yaxis: "y2",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> WDIR </b><br>" + "%{y:.2f} (deg)<br>" + "<extra></extra>" }),
                (precip = {x: final_time, y: dict['precip'], mode: 'lines', line: { color: "2ca02c" }, yaxis: "y1",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> Precip </b><br>" + "%{y:.2f} (mm)<br>" + "<extra></extra>" }),
                ];
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
                    title: {text: "UBC Weather Forecast " + "<br>Lat: " + w.toString().slice(0,6) + ", Lon: " + v.toString().slice(0,8) +"<br>Fuel Type: " + fu.toString(), x:0.05},

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
                        },],
                    };
                Plotly.newPlot(C,  N, S);
            };
            if (UTCTimeMap.length < 20)
                UTCTimeMap = UTCTimeMap + 'Z';
            var maptime = moment(new Date(UTCTimeMap).toLocaleString()).format('YYYY-MM-DD HH:mm');
            var inttime = moment(new Date(intimeutc).toLocaleString()).format('YYYY-MM-DD HH:mm');
            var plottime = moment(new Date(UTCTimePlot).toLocaleString()).format('YYYY-MM-DD HH:mm');

            doplots2(dict['local_time'],maptime, inttime, plottime);

            });
};

    function fbpplot() {
        fetch(json_dir).then(function(response){
            return response.json();
        }).then(function(n){
        var h = index
        var w = n.XLAT[h];
        var v = n.XLONG[h];
        var tz = n.TZONE[h];
        var ff = n.FUEL[h];
        var fu = ObjectFun.confuels(ff);
        console.log(fu);
        // console.log(Intl.DateTimeFormat().resolvedOptions().timeZone)
        var timezone = moment.tz(Intl.DateTimeFormat().resolvedOptions().timeZone).zoneAbbr();
        // console.log(timezone);

        //Create array of options to be added
        var array = [timezone ,"UTC", "Geo Local"];

        //Create and append select list
        var selectList = document.createElement("select");
        selectList.setAttribute("id", "mySelect");
        selectList.className = "time_wx";
        div2.appendChild(selectList);

        //Create and append the options
        for (var i = 0; i < array.length; i++) {
            var option = document.createElement("option");
            option.setAttribute("value", array[i]);
            option.text = array[i];
            selectList.appendChild(option);
        }


        var dict = {};
        var arrayColumn = (arr, n) => arr.map(x => x[n]);
        keys = ['dsr', 'ffmc', 'rh', 'isi', 'fwi', 'temp',
                'ws', 'wdir', 'precip', 'dc', 'dmc', 'bui',
                'hfi', 'ros', 'cfb', 'sfc', 'tfc'];

        for (var key of keys) {
            var array = JSON.parse(n[key]);
            var array = arrayColumn(array,h);
            dict[key] = array;
        };

        dict['time'] = n["Time"];
        dict['day'] = n["Day"];


        local_list2 = [];
        arrayLength = dict['time'].length;
        for (i = 0; i < arrayLength; i++) {
        d = dict['time'][i]
        var newtime2 = moment.utc(d).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
        var res = newtime2.slice(0, 16);
        local_list2.push(res)
        };
        dict['geo_time'] = local_list2;

        local_list = [];
        arrayLength = dict['time'].length;
        for (i = 0; i < arrayLength; i++) {
            a = new Date(dict['time'][i] + ':00Z').toLocaleString()
            local_list.push(moment(a).format('YYYY-MM-DD HH:mm'))
        };

        dict['local_time'] = local_list;

        selectList.onchange = function (){
            var value = this.value
            if (value == "UTC"){

                doplots3(dict['time'],UTCTimeMap, intimeutc, UTCTimePlot)
            }else if (value == "Geo Local"){
                var geomaptimei = moment.utc(UTCTimeMap).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
                var geomaptime = geomaptimei.slice(0, 16);
                var geointtimei = moment.utc(intimeutc).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
                var geointtime = geointtimei.slice(0, 16);
                var geoplottimei = moment.utc(UTCTimePlot).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
                var geoplottime = geoplottimei.slice(0, 16);
                doplots3(dict['geo_time'],geomaptime, geointtime, geoplottime)
            }else if (value == timezone){
                if (UTCTimeMap.length < 20)
                    UTCTimeMap = UTCTimeMap + 'Z';
                var localmaptime = moment(new Date(UTCTimeMap).toLocaleString()).format('YYYY-MM-DD HH:mm');
                var localinttime = moment(new Date(intimeutc).toLocaleString()).format('YYYY-MM-DD HH:mm');
                var localplottime = moment(new Date(UTCTimePlot).toLocaleString()).format('YYYY-MM-DD HH:mm');
                doplots3(dict['local_time'],localmaptime, localinttime, localplottime)
        }};


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



        function doplots3(final_time,maptime, intitme, plottime) {
            N =
            [(temp = {x: final_time, y: dict['hfi'], mode: 'lines', line: { color: "9e1809" }, yaxis: "y5", hoverlabel:{font:{size: hovsize, color: "ffffff"}}, hovertemplate: "<b> HFI </b><br>" + "%{y:.2f} (kW/m)<br>" + "<extra></extra>"}),
            (rh = {x: final_time, y: dict['ros'], mode: 'lines', line: { color: "21245b" }, yaxis: "y4", hoverlabel:{font:{size: hovsize, color: "ffffff"}}, hovertemplate: "<b> ROS </b><br>" + "%{y:.2f} (m/min))<br>" + "<extra></extra>"}),
            (ws = {x: final_time, y: dict['cfb'], mode: 'lines', line: { color: "c99725" }, yaxis: "y3", hoverlabel:{font:{size: hovsize, color: "ffffff"}}, hovertemplate: "<b> CFB </b><br>" + "%{y:.2f} (%)<br>" + "<extra></extra>"}),
            (wdir = {x: final_time, y: dict['sfc'], mode: 'lines', line: { color: "689783" }, yaxis: "y2",  hoverlabel:{font:{size: hovsize, color: "ffffff"}}, hovertemplate: "<b> SFC </b><br>" + "%{y:.2f} (kg/m<sup>2</sup>)<br>" + "<extra></extra>" }),
            (precip = {x: final_time, y: dict['tfc'], mode: 'lines', line: { color: "384a39" }, yaxis: "y1",  hoverlabel:{font:{size: hovsize, color: "ffffff"}}, hovertemplate: "<b> TFC </b><br>" + "%{y:.2f} (kg/m<sup>2</sup>)<br>" + "<extra></extra>" }),
            ];
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
                title: {text: "UBC Fire Behavior Forecast " + "<br>Lat: " + w.toString().slice(0,6) + ", Lon: " + v.toString().slice(0,8) +"<br>Fuel Type: " + fu.toString(), x:0.05},
                titlefont: { color: "#444444", size: tsize },
                showlegend: !1,
                yaxis5: { domain: [0.80, 0.98], title: { text: "HFI<br>(kW/m)", font: {size: labelsize, color: "9e1809" } }, tickfont: {size: ticksize, color: "9e1809"}},
                yaxis4: { domain: [0.60, 0.78],  title: { text: "ROS<br>(m/min)", font: {size: labelsize, color: "21245b" } }, tickfont: {size: ticksize, color: "21245b"}},
                yaxis3: { domain: [0.40, 0.58], title: { text: "CFB<br>(%)", font: {size: labelsize, color: "c99725" } } , tickfont: {size: ticksize, color: "c99725"}},
                yaxis2: { domain: [0.20, 0.38], title: { text: "SFC<br>(kg/m<sup>2</sup>)", font: {size: labelsize, color: "689783" } }, tickfont: {size: ticksize, color: "689783"},},
                yaxis1: { domain: [0, 0.18], title: { text: "TFC<br>(kg/m<sup>2</sup>)", font: {size: labelsize, color: "384a39" } }, tickfont: {size: ticksize, color: "384a39"}},
                xaxis: { tickfont: {size: xticksize, color: "444444"}},
                shapes: [{
                    type: 'line',
                    x0: maptime,
                    y0: 0,
                    x1: maptime,
                    yref: 'paper',
                    y1: 1,
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
                        y1: 1,
                        fillcolor: '#A7A7A7',
                        opacity: 0.2,
                        line: {
                            width: 0
                        }
                    },],
                };
            Plotly.newPlot(C,  N, S);
        };
        if (UTCTimeMap.length < 20)
            UTCTimeMap = UTCTimeMap + 'Z';
        var maptime = moment(new Date(UTCTimeMap).toLocaleString()).format('YYYY-MM-DD HH:mm');
        var inttime = moment(new Date(intimeutc).toLocaleString()).format('YYYY-MM-DD HH:mm');
        var plottime = moment(new Date(UTCTimePlot).toLocaleString()).format('YYYY-MM-DD HH:mm');

        doplots3(dict['local_time'],maptime, inttime, plottime);

        });
    };




};





function makeplotly3(e) {
    let hovsize = 13;
    var json_dir = e.customId;
    var index = e.customIdx;
    console.log(index);

    console.log(index);
    btn_fire3.onclick = fwiplot3;
    btn_wx3.onclick = wxplot3;
    btn_fbp3.onclick = fbpplot3;
    // btn_dnw.onclick = exportJson;
    var o = [e.lat,e.lng]

    // console.log(o);
    var C = document.getElementById('wx_plot3');

    fwiplot3();
    function fwiplot3() {
        fetch(json_dir).then(function(response){
            return response.json();
        }).then(function(n){
        var h = index
        var w = n.XLAT[h];
        var v = n.XLONG[h];
        var tz = n.TZONE[h];
        var ff = n.FUEL[h];
        var fu = ObjectFun.confuels(ff);
        console.log(fu);

        // console.log(Intl.DateTimeFormat().resolvedOptions().timeZone)
        var timezone = moment.tz(Intl.DateTimeFormat().resolvedOptions().timeZone).zoneAbbr();
        // console.log(timezone);

        //Create array of options to be added
        var array = [timezone ,"UTC","Geo Local"];

        //Create and append select list
        var selectList = document.createElement("select");
        selectList.setAttribute("id", "mySelect");
        selectList.className = "time_wx";
        div3.appendChild(selectList);

        //Create and append the options
        for (var i = 0; i < array.length; i++) {
            var option = document.createElement("option");
            option.setAttribute("value", array[i]);
            option.text = array[i];
            selectList.appendChild(option);
        };


        var dict = {};
        var arrayColumn = (arr, n) => arr.map(x => x[n]);
        keys = ['dsr', 'ffmc', 'rh', 'isi', 'fwi', 'temp',
                'ws', 'wdir', 'precip', 'dc', 'dmc', 'bui'];

        for (var key of keys) {
            var array = JSON.parse(n[key]);
            var array = arrayColumn(array,h);
            dict[key] = array;
        };

        dict['time'] = n["Time"];
        dict['day'] = n["Day"];

        local_list2 = [];
        arrayLength = dict['time'].length;
        for (i = 0; i < arrayLength; i++) {
        d = dict['time'][i] + ':00:00.000Z'
        var newtime2 = moment.utc(d).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
        var res = newtime2.slice(0, 16);
        local_list2.push(res);
        };
        dict['geo_time'] = local_list2;
        local_list = [];
        arrayLength = dict['time'].length;
        for (i = 0; i < arrayLength; i++) {
            a = new Date(dict['time'][i] + ':00Z').toLocaleString();
            local_list.push(moment(a).format('YYYY-MM-DD HH:mm'));
        };
        dict['local_time'] = local_list;

        selectList.onchange = function (){
            var value = this.value
            if (value == "UTC"){
                doplots4(dict['time'],UTCTimeMap, intimeutc, UTCTimePlot)
            }else if (value == "Geo Local"){
                var geomaptimei = moment.utc(UTCTimeMap).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
                var geomaptime = geomaptimei.slice(0, 16);
                var geointtimei = moment.utc(intimeutc).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
                var geointtime = geointtimei.slice(0, 16);
                var geoplottimei = moment.utc(UTCTimePlot).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
                var geoplottime = geoplottimei.slice(0, 16);
                doplots4(dict['geo_time'],geomaptime, geointtime, geoplottime)
            }else if (value == timezone){
                if (UTCTimeMap.length < 20)
                    UTCTimeMap = UTCTimeMap + 'Z';
                var localmaptime = moment(new Date(UTCTimeMap).toLocaleString()).format('YYYY-MM-DD HH:mm');
                var localinttime = moment(new Date(intimeutc).toLocaleString()).format('YYYY-MM-DD HH:mm');
                var localplottime = moment(new Date(UTCTimePlot).toLocaleString()).format('YYYY-MM-DD HH:mm');
                doplots4(dict['local_time'],localmaptime, localinttime, localplottime)
          }};




        function doplots4(final_time,maptime, intitme, plottime) {

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

            T = [
                ["DMC", "DC", "BUI", "FWI", "DSR"],
                [dict['dmc'][0], dict['dc'][0], dict['bui'][0], dict['fwi'][0], dict['dsr'][0]],
                [dict['dmc'][1], dict['dc'][1], dict['bui'][1], dict['fwi'][1], dict['dsr'][1]],
            ];

            N =
            ((ffmc = {x: final_time, y: dict['ffmc'], mode: 'lines', line: { color: "ff7f0e" }, yaxis: "y2",  hoverlabel:{font:{size: hovsize, color: "#ffffff"}, bordercolor: "#ffffff"}, hovertemplate: "<b> FFMC </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
            (isi = {x: final_time, y: dict['isi'], mode: 'lines', line: { color: "9467bd" }, yaxis: "y1",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> ISI </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),

            [
                {
                    type: "table",
                    header: { values: [["Index/Code"], [dict['day'][0]], [dict['day'][1]]], align: "center", height:t_height, line: {color: "444444" }, fill: { color: "444444E6" }, font: { family: "inherit", size: t_f, color: "white" } },
                    cells: { values: T, align: "center",  height:c_height, line: { color: "444444", width: 1 }, fill: { color:[["#2ca02c1A", "#8c564b1A", "7f7f7f1A", "d627281A", "0000001A"]] }, font: { family: "inherit", size: 11, color:[["#2ca02c", "#8c564b", "7f7f7f", "d62728", "000000"]]} },
                    xaxis: "x",
                    yaxis: "y",
                    domain: { x: [0.0, 1.0], y: [0.54, 1] },
                },
                ffmc,
                isi,
            ]
            );

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
                title: {text: "UBC Fire Weather Forecast " + "<br>Lat: " + w.toString().slice(0,6) + ", Lon: " + v.toString().slice(0,8) +"<br>Fuel Type: " + fu.toString(), x:0.05},

                titlefont: { color: "#444444", size: tsize },
                showlegend: !1,
                yaxis2: {domain: [.27, .54], title: { text: "FFMC", font: { size: labelsize, color: "ff7f0e" } }, tickfont: {size: ticksize, color: "ff7f0e"}},
                yaxis1: { domain: [0.0, 0.26], title: { text: "ISI", font: {size: labelsize, color: "9467bd" } }, tickfont: {size: ticksize, color: "9467bd"}},
                xaxis: { tickfont: {size: xticksize, color: "444444"}},
                shapes: [{
                    type: 'line',
                    x0: maptime,
                    y0: 0,
                    x1: maptime,
                    yref: 'paper',
                    y1: 0.54,
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
                        y1: 0.54,
                        fillcolor: '#A7A7A7',
                        opacity: 0.2,
                        line: {
                            width: 0
                        }
                    }]
            }

        Plotly.newPlot(C,  N, S);
        };
        if (UTCTimeMap.length < 20)
            UTCTimeMap = UTCTimeMap + 'Z';
        var maptime = moment(new Date(UTCTimeMap).toLocaleString()).format('YYYY-MM-DD HH:mm');
        var inttime = moment(new Date(intimeutc).toLocaleString()).format('YYYY-MM-DD HH:mm');
        var plottime = moment(new Date(UTCTimePlot).toLocaleString()).format('YYYY-MM-DD HH:mm');
        doplots4(dict['local_time'],maptime, inttime, plottime);

        });

        };

        function wxplot3() {
            fetch(json_dir).then(function(response){
                return response.json();
            }).then(function(n){
            var h = index
            var w = n.XLAT[h];
            var v = n.XLONG[h];
            var tz = n.TZONE[h];
            var ff = n.FUEL[h];
            var fu = ObjectFun.confuels(ff);
            console.log(fu);
            // console.log(Intl.DateTimeFormat().resolvedOptions().timeZone)
            var timezone = moment.tz(Intl.DateTimeFormat().resolvedOptions().timeZone).zoneAbbr();
            // console.log(timezone);

            //Create array of options to be added
            var array = [timezone ,"UTC", "Geo Local"];

            //Create and append select list
            var selectList = document.createElement("select");
            selectList.setAttribute("id", "mySelect");
            selectList.className = "time_wx";
            div3.appendChild(selectList);

            //Create and append the options
            for (var i = 0; i < array.length; i++) {
                var option = document.createElement("option");
                option.setAttribute("value", array[i]);
                option.text = array[i];
                selectList.appendChild(option);
            }

            var dict = {};
            var arrayColumn = (arr, n) => arr.map(x => x[n]);
            keys = ['dsr', 'ffmc', 'rh', 'isi', 'fwi', 'temp',
                    'ws', 'wdir', 'precip', 'dc', 'dmc', 'bui'];

            for (var key of keys) {
                var array = JSON.parse(n[key]);
                var array = arrayColumn(array,h);
                dict[key] = array;
            };

            dict['time'] = n["Time"];
            dict['day'] = n["Day"];


            local_list2 = [];
            arrayLength = dict['time'].length;
            for (i = 0; i < arrayLength; i++) {
            d = dict['time'][i]
            var newtime2 = moment.utc(d).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
            var res = newtime2.slice(0, 16);
            local_list2.push(res)
            };
            dict['geo_time'] = local_list2;

            local_list = [];
            arrayLength = dict['time'].length;
            for (i = 0; i < arrayLength; i++) {
                a = new Date(dict['time'][i] + ':00Z').toLocaleString()
                local_list.push(moment(a).format('YYYY-MM-DD HH:mm'))
            };

            dict['local_time'] = local_list;

            selectList.onchange = function (){
                var value = this.value
                if (value == "UTC"){

                    doplots5(dict['time'],UTCTimeMap, intimeutc, UTCTimePlot)
                }else if (value == "Geo Local"){
                    var geomaptimei = moment.utc(UTCTimeMap).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
                    var geomaptime = geomaptimei.slice(0, 16);
                    var geointtimei = moment.utc(intimeutc).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
                    var geointtime = geointtimei.slice(0, 16);
                    var geoplottimei = moment.utc(UTCTimePlot).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
                    var geoplottime = geoplottimei.slice(0, 16);
                    doplots5(dict['geo_time'],geomaptime, geointtime, geoplottime)
                }else if (value == timezone){
                    if (UTCTimeMap.length < 20)
                        UTCTimeMap = UTCTimeMap + 'Z';
                    var localmaptime = moment(new Date(UTCTimeMap).toLocaleString()).format('YYYY-MM-DD HH:mm');
                    var localinttime = moment(new Date(intimeutc).toLocaleString()).format('YYYY-MM-DD HH:mm');
                    var localplottime = moment(new Date(UTCTimePlot).toLocaleString()).format('YYYY-MM-DD HH:mm');
                    doplots5(dict['local_time'],localmaptime, localinttime, localplottime)
              }};


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



            function doplots5(final_time,maptime, intitme, plottime) {
                N =
                [(temp = {x: final_time, y: dict['temp'], mode: 'lines', line: { color: "d62728" }, yaxis: "y5", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> Temp </b><br>" + "%{y:.2f} (C)<br>" + "<extra></extra>"}),
                (rh = {x: final_time, y: dict['rh'], mode: 'lines', line: { color: "1f77b4" }, yaxis: "y4", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> RH </b><br>" + "%{y:.2f} (%)<br>" + "<extra></extra>"}),
                (ws = {x: final_time, y: dict['ws'], mode: 'lines', line: { color: "202020" }, yaxis: "y3", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> WSP </b><br>" + "%{y:.2f} (km/hr)<br>" + "<extra></extra>"}),
                (wdir = {x: final_time, y: dict['wdir'], mode: 'lines', line: { color: "7f7f7f" }, yaxis: "y2",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> WDIR </b><br>" + "%{y:.2f} (deg)<br>" + "<extra></extra>" }),
                (precip = {x: final_time, y: dict['precip'], mode: 'lines', line: { color: "2ca02c" }, yaxis: "y1",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> Precip </b><br>" + "%{y:.2f} (mm)<br>" + "<extra></extra>" }),
                ];
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
                    title: {text: "UBC Weather Forecast " + "<br>Lat: " + w.toString().slice(0,6) + ", Lon: " + v.toString().slice(0,8) +"<br>Fuel Type: " + fu.toString(), x:0.05},

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
                        },],
                    };
                Plotly.newPlot(C,  N, S);
            };
            if (UTCTimeMap.length < 20)
                UTCTimeMap = UTCTimeMap + 'Z';
            var maptime = moment(new Date(UTCTimeMap).toLocaleString()).format('YYYY-MM-DD HH:mm');
            var inttime = moment(new Date(intimeutc).toLocaleString()).format('YYYY-MM-DD HH:mm');
            var plottime = moment(new Date(UTCTimePlot).toLocaleString()).format('YYYY-MM-DD HH:mm');

            doplots5(dict['local_time'],maptime, inttime, plottime);

            });
};

    function fbpplot3() {
        fetch(json_dir).then(function(response){
            return response.json();
        }).then(function(n){
        var h = index
        var w = n.XLAT[h];
        var v = n.XLONG[h];
        var tz = n.TZONE[h];
        var ff = n.FUEL[h];
        var fu = ObjectFun.confuels(ff);
        console.log(fu);
        // console.log(Intl.DateTimeFormat().resolvedOptions().timeZone)
        var timezone = moment.tz(Intl.DateTimeFormat().resolvedOptions().timeZone).zoneAbbr();
        // console.log(timezone);

        //Create array of options to be added
        var array = [timezone ,"UTC", "Geo Local"];

        //Create and append select list
        var selectList = document.createElement("select");
        selectList.setAttribute("id", "mySelect");
        selectList.className = "time_wx";
        div3.appendChild(selectList);

        //Create and append the options
        for (var i = 0; i < array.length; i++) {
            var option = document.createElement("option");
            option.setAttribute("value", array[i]);
            option.text = array[i];
            selectList.appendChild(option);
        }


        var dict = {};
        var arrayColumn = (arr, n) => arr.map(x => x[n]);
        keys = ['dsr', 'ffmc', 'rh', 'isi', 'fwi', 'temp',
                'ws', 'wdir', 'precip', 'dc', 'dmc', 'bui',
                'hfi', 'ros', 'cfb', 'sfc', 'tfc'];

        for (var key of keys) {
            var array = JSON.parse(n[key]);
            var array = arrayColumn(array,h);
            dict[key] = array;
        };

        dict['time'] = n["Time"];
        dict['day'] = n["Day"];


        local_list2 = [];
        arrayLength = dict['time'].length;
        for (i = 0; i < arrayLength; i++) {
        d = dict['time'][i]
        var newtime2 = moment.utc(d).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
        var res = newtime2.slice(0, 16);
        local_list2.push(res)
        };
        dict['geo_time'] = local_list2;

        local_list = [];
        arrayLength = dict['time'].length;
        for (i = 0; i < arrayLength; i++) {
            a = new Date(dict['time'][i] + ':00Z').toLocaleString()
            local_list.push(moment(a).format('YYYY-MM-DD HH:mm'))
        };

        dict['local_time'] = local_list;

        selectList.onchange = function (){
            var value = this.value
            if (value == "UTC"){

                doplots6(dict['time'],UTCTimeMap, intimeutc, UTCTimePlot)
            }else if (value == "Geo Local"){
                var geomaptimei = moment.utc(UTCTimeMap).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
                var geomaptime = geomaptimei.slice(0, 16);
                var geointtimei = moment.utc(intimeutc).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
                var geointtime = geointtimei.slice(0, 16);
                var geoplottimei = moment.utc(UTCTimePlot).subtract({'hours': tz}).format('YYYY-MM-DD HH:mm z');
                var geoplottime = geoplottimei.slice(0, 16);
                doplots6(dict['geo_time'],geomaptime, geointtime, geoplottime)
            }else if (value == timezone){
                if (UTCTimeMap.length < 20)
                    UTCTimeMap = UTCTimeMap + 'Z';
                var localmaptime = moment(new Date(UTCTimeMap).toLocaleString()).format('YYYY-MM-DD HH:mm');
                var localinttime = moment(new Date(intimeutc).toLocaleString()).format('YYYY-MM-DD HH:mm');
                var localplottime = moment(new Date(UTCTimePlot).toLocaleString()).format('YYYY-MM-DD HH:mm');
                doplots6(dict['local_time'],localmaptime, localinttime, localplottime)
        }};


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



        function doplots6(final_time,maptime, intitme, plottime) {
            N =
            [(temp = {x: final_time, y: dict['hfi'], mode: 'lines', line: { color: "9e1809" }, yaxis: "y5", hoverlabel:{font:{size: hovsize, color: "ffffff"}}, hovertemplate: "<b> HFI </b><br>" + "%{y:.2f} (kW/m)<br>" + "<extra></extra>"}),
            (rh = {x: final_time, y: dict['ros'], mode: 'lines', line: { color: "21245b" }, yaxis: "y4", hoverlabel:{font:{size: hovsize, color: "ffffff"}}, hovertemplate: "<b> ROS </b><br>" + "%{y:.2f} (m/min))<br>" + "<extra></extra>"}),
            (ws = {x: final_time, y: dict['cfb'], mode: 'lines', line: { color: "c99725" }, yaxis: "y3", hoverlabel:{font:{size: hovsize, color: "ffffff"}}, hovertemplate: "<b> CFB </b><br>" + "%{y:.2f} (%)<br>" + "<extra></extra>"}),
            (wdir = {x: final_time, y: dict['sfc'], mode: 'lines', line: { color: "689783" }, yaxis: "y2",  hoverlabel:{font:{size: hovsize, color: "ffffff"}}, hovertemplate: "<b> SFC </b><br>" + "%{y:.2f} (kg/m<sup>2</sup>)<br>" + "<extra></extra>" }),
            (precip = {x: final_time, y: dict['tfc'], mode: 'lines', line: { color: "384a39" }, yaxis: "y1",  hoverlabel:{font:{size: hovsize, color: "ffffff"}}, hovertemplate: "<b> TFC </b><br>" + "%{y:.2f} (kg/m<sup>2</sup>)<br>" + "<extra></extra>" }),
            ];
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
                title: {text: "UBC Fire Behavior Forecast " + "<br>Lat: " + w.toString().slice(0,6) + ", Lon: " + v.toString().slice(0,8) +"<br>Fuel Type: " + fu.toString(), x:0.05},
                titlefont: { color: "#444444", size: tsize },
                showlegend: !1,
                yaxis5: { domain: [0.80, 0.98], title: { text: "HFI<br>(kW/m)", font: {size: labelsize, color: "9e1809" } }, tickfont: {size: ticksize, color: "9e1809"}},
                yaxis4: { domain: [0.60, 0.78],  title: { text: "ROS<br>(m/min)", font: {size: labelsize, color: "21245b" } }, tickfont: {size: ticksize, color: "21245b"}},
                yaxis3: { domain: [0.40, 0.58], title: { text: "CFB<br>(%)", font: {size: labelsize, color: "c99725" } } , tickfont: {size: ticksize, color: "c99725"}},
                yaxis2: { domain: [0.20, 0.38], title: { text: "SFC<br>(kg/m<sup>2</sup>)", font: {size: labelsize, color: "689783" } }, tickfont: {size: ticksize, color: "689783"},},
                yaxis1: { domain: [0, 0.18], title: { text: "TFC<br>(kg/m<sup>2</sup>)", font: {size: labelsize, color: "384a39" } }, tickfont: {size: ticksize, color: "384a39"}},
                xaxis: { tickfont: {size: xticksize, color: "444444"}},
                shapes: [{
                    type: 'line',
                    x0: maptime,
                    y0: 0,
                    x1: maptime,
                    yref: 'paper',
                    y1: 1,
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
                        y1: 1,
                        fillcolor: '#A7A7A7',
                        opacity: 0.2,
                        line: {
                            width: 0
                        }
                    },],
                };
            Plotly.newPlot(C,  N, S);
        };
        if (UTCTimeMap.length < 20)
            UTCTimeMap = UTCTimeMap + 'Z';
        var maptime = moment(new Date(UTCTimeMap).toLocaleString()).format('YYYY-MM-DD HH:mm');
        var inttime = moment(new Date(intimeutc).toLocaleString()).format('YYYY-MM-DD HH:mm');
        var plottime = moment(new Date(UTCTimePlot).toLocaleString()).format('YYYY-MM-DD HH:mm');

        doplots6(dict['local_time'],maptime, inttime, plottime);

        });
    };




};

// // Hotspot icon
// var hotspotIcon = L.icon({
//     iconUrl:   '/static/img/fire-marker-5.png',
//     shadowUrl: '',
//     iconSize:     [32, 37],
//     shadowSize:   [],
//     iconAnchor:   [16, 36],
//     shadowAnchor: [],
//     popupAnchor:  [0, -22],
// });


// MyObject = {
//     please: function () {
//     hotspots.eachLayer(function(layer) {
//         if (layer instanceof L.Marker) {
//             layer.setIcon(hotspotIcon);
//             layer.bindPopup(div3, {maxWidth: "auto", maxHeight: "auto"});
//         }
//     });
//     hotspotsMarkers.addLayer(hotspots);
// }
// }





var fwfmodellocation;

function makeplots(n) {

    (json_dir = "/static/json/fwf-zone-merge.json"),
        fetch(json_dir, { cache: "default"})
            .then(function (n) {
                return n.json();
            })
            .then(function (o) {
                for (var t = o.ZONE_d02, e = o.XLAT_d02, l = o.XLONG_d02, a = [], r = [], c = [(c = [e.length, e[0].length])[1], c[0]], i = 0; i < e.length; i++) a = a.concat(e[i]);
                for (i = 0; i < l.length; i++) r = r.concat(l[i]);
                (a = a.map(Number)), (r = r.map(Number));
                var s = a.map(function (n, o) {
                    return [n, r[o]];
                });
                const u = new KDBush(s);

                for (var tt = o.ZONE_d03, ee = o.XLAT_d03, ll = o.XLONG_d03, aa = [], rr = [], cc = [(cc = [ee.length, ee[0].length])[1], cc[0]], ii = 0; ii < ee.length; ii++) aa = aa.concat(ee[ii]);
                for (ii = 0; ii < ll.length; ii++) rr = rr.concat(ll[ii]);
                (aa = aa.map(Number)), (rr = rr.map(Number));
                var d3 = aa.map(function (nn, oo) {
                  return [nn, rr[oo]];
                });
                const d3_tree = new KDBush(d3);

                (loaded_zones = ["he"]);
                (loaded_zones_d3 = ["he"]);
                if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
                    var activate = 'dblclick'
                }else{
                    var activate = 'dblclick'
                    // console.log('desktop')

                };
                    map.on(activate, function (o) {
                        if (fwfmodellocation != undefined) {
                            fwfmodellocation.remove(map);
                        };
                        if (fwfclicklocation != undefined) {
                            fwfclicklocation.remove(map);
                        };
                        fwfclicklocation.setLatLng(o.latlng).addTo(map);
                        var e = [parseFloat(o.latlng.lat.toFixed(4)), parseFloat(o.latlng.lng.toFixed(4))];
                        var l = u.range(e[0] - buffer, e[1] - buffer, e[0] + buffer, e[1] + buffer).map((n) => s[n]);
                        (ll_diff = []),
                            (function (n, o) {
                                for (var t = 0; t < n.length; t++) {
                                    var e = Math.abs(n[t][0] - o[0]) + Math.abs(n[t][1] - o[1]);
                                    ll_diff.push(e);
                                }
                            })(l, e);
                        for (var a = 0, r = ll_diff[0], i = 1; i < ll_diff.length; i++) ll_diff[i] < r && ((r = ll_diff[i]), (a = i));
                        var h = u.range(e[0]- buffer, e[1] - buffer, e[0] + buffer, e[1] + buffer);
                        var d, m;
                        f =
                            ((m = (d = c).reduce(
                                function (n, o) {
                                    return n.concat(n[n.length - 1] * o);
                                },
                                [1]
                            )),
                            function (n) {
                                return (function (n, o, t) {
                                    return n.map(function (n, e) {
                                        return Math.round(o / t[e]) % n;
                                    });
                                })(d, n, m);
                            });
                        var g = (function (n, o) {
                                var t = n.reduce(
                                    function (n, o) {
                                        return n.concat(n[n.length - 1] * o);
                                    },
                                    [1]
                                );
                                return n.map(function (n, e) {
                                    return Math.round(o / t[e]) % n;
                                });
                            })(c, h[a], f(h[a])),
                            p = g[1],
                            y = g[0],
                            x = [p, y];
                        var _ = t[p][y];


                        if ( _ == 'd3'){
                                var ee = [parseFloat(o.latlng.lat.toFixed(4)), parseFloat(o.latlng.lng.toFixed(4))];
                                console.log(ee);
                                var ll = d3_tree.range(ee[0] - buffer, ee[1] - buffer, ee[0] + buffer, ee[1] + buffer).map((nn) => d3[nn]);
                                (ll_diff2 = []),
                                    (function (nn, oo) {
                                        for (var tt = 0; tt < nn.length; tt++) {
                                            var ee = Math.abs(nn[tt][0] - oo[0]) + Math.abs(nn[tt][1] - oo[1]);
                                            ll_diff2.push(ee);
                                        }
                                    })(ll, ee);
                                for (var aa = 0, rr = ll_diff2[0], ii = 1; ii < ll_diff2.length; ii++) ll_diff2[ii] < rr && ((rr = ll_diff2[ii]), (aa = ii));
                                var hh = d3_tree.range(ee[0]- buffer, ee[1] - buffer, ee[0] + buffer, ee[1] + buffer);
                                var dd, mm;
                                ff =
                                    ((mm = (dd = cc).reduce(
                                        function (nn, oo) {
                                            return nn.concat(nn[nn.length - 1] * oo);
                                        },
                                        [1]
                                    )),
                                    function (nn) {
                                        return (function (nn, oo, tt) {
                                            return nn.map(function (nn, ee) {
                                                return Math.round(o / t[e]) % n;
                                            });
                                        })(dd, nn, mm);
                                    });
                                var gg = (function (nn, oo) {
                                        var tt = nn.reduce(
                                            function (nn, oo) {
                                                return nn.concat(nn[nn.length - 1] * oo);
                                            },
                                            [1]
                                        );
                                        return nn.map(function (nn, ee) {
                                            return Math.round(oo / tt[ee]) % nn;
                                        });
                                    })(cc, hh[aa], ff(hh[aa])),
                                    pp = gg[1],
                                    yy = gg[0],
                                    xx = [pp, yy];
                                    oo = ee;
                                var __ = tt[pp][yy];
                                (zone_json_d3 = n.slice(0, 14)),
                                (zone_json_d3 = zone_json_d3 + __ + n.slice(16, 36)),
                                fetch(zone_json_d3).then(function(response){
                                    return response.json();
                                }).then(function(nn){
                                    // console.log(nn);
                                    // console.log(oo);

                                 var buff = 0.2
                                for (var t = nn.XLAT, e = nn.XLONG, l = [], a = [], r = [(r = [t.length, t[0].length])[1], r[0]], c = 0; c < t.length; c++) l = l.concat(t[c]);
                                for (c = 0; c < e.length; c++) a = a.concat(e[c]);
                                var i = t.map(function (nn, oo) {
                                    return [nn, e[oo]];
                                });
                                var ss = new KDBush(i);
                                // console.log(ss);

                                point_list.push(oo);
                                file_list.push(nn);
                                var uu = ss.range(oo[0] - buff, oo[1] - buff, oo[0] + buff, oo[1] + buff).map((nn) => i[nn]);
                                // console.log(uu);

                                (ll_diff = []),
                                    (function (nn, oo) {
                                        for (var t = 0; t < nn.length; t++) {
                                            var ee = Math.abs(parseFloat(nn[t][0]) - oo[0]) + Math.abs(parseFloat(nn[t][1]) - oo[1]);
                                            ll_diff.push(ee);
                                        }
                                    })(uu, oo);

                                var hh = ll_diff.indexOf(Math.min(...ll_diff));
                                // console.log(hh);
                                var mm = ss.range(oo[0] - buff, oo[1] - buff, oo[0] + buff, oo[1] + buff);
                                var hh = mm[hh];
                                // console.log(hh);

                                var ww = nn.XLAT[hh];
                                var vv = nn.XLONG[hh];

                                console.log(zone_json_d3);
                                fwfmodellocation = new L.marker([ww,vv],{icon: redIcon, customId: zone_json_d3, customIdx: hh});
                                fwfmodellocation.bindPopup(div2, {maxWidth: "auto", maxHeight: "auto"});
                                fwfmodellocation.setZIndexOffset(1000);
                                // fwfmodellocation.on('click', makeplotly({customId: zone_json_d3, customIdx: hh, lat: ww, lng: vv})).addTo(map);
                                fwfmodellocation.on('click', makeplotly).addTo(map);

                                });
                                loaded_zones_d3.push(__);

                            } else {
                            o = e;
                            (zone_json = n.slice(0, 14)),
                            (zone_json = zone_json + _ + n.slice(16, 30) + '2.json'),
                            fetch(zone_json).then(function(response){
                                return response.json();
                            }).then(function(n){
                                // console.log(n);
                                // console.log(o);

                             var buff = 0.2
                            for (var t = n.XLAT, e = n.XLONG, l = [], a = [], r = [(r = [t.length, t[0].length])[1], r[0]], c = 0; c < t.length; c++) l = l.concat(t[c]);
                            for (c = 0; c < e.length; c++) a = a.concat(e[c]);
                            var i = t.map(function (n, o) {
                                return [n, e[o]];
                            });
                            var s = new KDBush(i);
                            // console.log(s);

                            point_list.push(o);
                            file_list.push(n);
                            // console.log(o);
                            var u = s.range(o[0] - buff, o[1] - buff, o[0] + buff, o[1] + buff).map((n) => i[n]);
                            // console.log(u);

                            (ll_diff = []),
                                (function (n, o) {
                                    for (var t = 0; t < n.length; t++) {
                                        var e = Math.abs(parseFloat(n[t][0]) - o[0]) + Math.abs(parseFloat(n[t][1]) - o[1]);
                                        ll_diff.push(e);
                                    }
                                })(u, o);

                            var h = ll_diff.indexOf(Math.min(...ll_diff));
                            // console.log(h);
                            var m = s.range(o[0] - buff, o[1] - buff, o[0] + buff, o[1] + buff);
                            var h = m[h];
                            // console.log(h);

                            var w = n.XLAT[h];
                            var v = n.XLONG[h];

                            // console.log(zone_json);
                            fwfmodellocation = new L.marker([w,v],{icon: redIcon, customId: zone_json, customIdx: h});
                            fwfmodellocation.bindPopup(div2, {maxWidth: "auto", maxHeight: "auto"});
                            fwfmodellocation.setZIndexOffset(1000);
                            // fwfmodellocation.on('click', makeplotly({customId: zone_json, customIdx: h, lat: w, lng: v})).addTo(map);
                            fwfmodellocation.on('click', makeplotly).addTo(map);

                            });
                            loaded_zones.push(_);
                    }});

                        // Hotspot icon
                        // Hotspots layer with marker clustering
                        const hotspots = omnivore.kml('data/fire_locations.kml');
                        var hotspotIcon = L.icon({
                            iconUrl:   'static/img/fwf-fire3.png',
                            shadowUrl: '',
                            // iconSize:     [32, 37],
                            iconSize:     [16, 21],
                            shadowSize:   [],
                            // iconAnchor:   [16, 36],
                            iconAnchor:   [8, 18],
                            shadowAnchor: [],
                            popupAnchor:  [0, -22],
                        });



                        hotspots.on('ready', function () {
                        hotspots.eachLayer(function(layer) {
                            if (layer instanceof L.Marker) {
                                layer.setIcon(hotspotIcon);
                                layer.bindPopup(div3, {maxWidth: "auto", maxHeight: "auto"});
                                layer.on('click', hotplots);
                            }
                        });
                        hotspotsMarkers.addLayer(hotspots);
                        });

                        function hotplots(e) {
                        console.log(e);
                        var clickedFire = e.target;
                        lat = clickedFire._latlng.lat
                        lng = clickedFire._latlng.lng


                        console.log(clickedFire)
                        console.log(lat)
                        console.log(lng)


                        var e = [parseFloat(clickedFire._latlng.lat.toFixed(4)), parseFloat(clickedFire._latlng.lng.toFixed(4))];
                        var l = u.range(e[0] - buffer, e[1] - buffer, e[0] + buffer, e[1] + buffer).map((n) => s[n]);
                        console.log(l);
                        if (l === undefined || l.length == 0) {
                            // Do stuff if condition is true
                            map.closePopup();

                         }
                        (ll_diff = []),
                            (function (n, o) {
                                for (var t = 0; t < n.length; t++) {
                                    var e = Math.abs(n[t][0] - o[0]) + Math.abs(n[t][1] - o[1]);
                                    ll_diff.push(e);
                                }
                            })(l, e);
                        for (var a = 0, r = ll_diff[0], i = 1; i < ll_diff.length; i++) ll_diff[i] < r && ((r = ll_diff[i]), (a = i));
                        var h = u.range(e[0]- buffer, e[1] - buffer, e[0] + buffer, e[1] + buffer);
                        var d, m;
                        f =
                            ((m = (d = c).reduce(
                                function (n, o) {
                                    return n.concat(n[n.length - 1] * o);
                                },
                                [1]
                            )),
                            function (n) {
                                return (function (n, o, t) {
                                    return n.map(function (n, e) {
                                        return Math.round(o / t[e]) % n;
                                    });
                                })(d, n, m);
                            });
                        var g = (function (n, o) {
                                var t = n.reduce(
                                    function (n, o) {
                                        return n.concat(n[n.length - 1] * o);
                                    },
                                    [1]
                                );
                                return n.map(function (n, e) {
                                    return Math.round(o / t[e]) % n;
                                });
                            })(c, h[a], f(h[a])),
                            p = g[1],
                            y = g[0],
                            x = [p, y];
                        var _ = t[p][y];

                        if ( _ == 'd3'){
                                var ee = [parseFloat(clickedFire._latlng.lat.toFixed(4)), parseFloat(clickedFire._latlng.lng.toFixed(4))];
                                console.log(ee);
                                var ll = d3_tree.range(ee[0] - buffer, ee[1] - buffer, ee[0] + buffer, ee[1] + buffer).map((nn) => d3[nn]);
                                (ll_diff2 = []),
                                    (function (nn, oo) {
                                        for (var tt = 0; tt < nn.length; tt++) {
                                            var ee = Math.abs(nn[tt][0] - oo[0]) + Math.abs(nn[tt][1] - oo[1]);
                                            ll_diff2.push(ee);
                                        }
                                    })(ll, ee);
                                for (var aa = 0, rr = ll_diff2[0], ii = 1; ii < ll_diff2.length; ii++) ll_diff2[ii] < rr && ((rr = ll_diff2[ii]), (aa = ii));
                                var hh = d3_tree.range(ee[0]- buffer, ee[1] - buffer, ee[0] + buffer, ee[1] + buffer);
                                var dd, mm;
                                ff =
                                    ((mm = (dd = cc).reduce(
                                        function (nn, oo) {
                                            return nn.concat(nn[nn.length - 1] * oo);
                                        },
                                        [1]
                                    )),
                                    function (nn) {
                                        return (function (nn, oo, tt) {
                                            return nn.map(function (nn, ee) {
                                                return Math.round(o / t[e]) % n;
                                            });
                                        })(dd, nn, mm);
                                    });
                                var gg = (function (nn, oo) {
                                        var tt = nn.reduce(
                                            function (nn, oo) {
                                                return nn.concat(nn[nn.length - 1] * oo);
                                            },
                                            [1]
                                        );
                                        return nn.map(function (nn, ee) {
                                            return Math.round(oo / tt[ee]) % nn;
                                        });
                                    })(cc, hh[aa], ff(hh[aa])),
                                    pp = gg[1],
                                    yy = gg[0],
                                    xx = [pp, yy];
                                    oo = ee;
                                var __ = tt[pp][yy];

                                (zone_json_d3 = n.slice(0, 14)),
                                (zone_json_d3 = zone_json_d3 + __ + n.slice(16, 36)),
                                fetch(zone_json_d3).then(function(response){
                                    return response.json();
                                }).then(function(nn){
                                    // console.log(nn);
                                    // console.log(oo);

                                 var buff = 0.2
                                for (var t = nn.XLAT, e = nn.XLONG, l = [], a = [], r = [(r = [t.length, t[0].length])[1], r[0]], c = 0; c < t.length; c++) l = l.concat(t[c]);
                                for (c = 0; c < e.length; c++) a = a.concat(e[c]);
                                var i = t.map(function (nn, oo) {
                                    return [nn, e[oo]];
                                });
                                var ss = new KDBush(i);
                                // console.log(ss);

                                point_list.push(oo);
                                file_list.push(nn);
                                var uu = ss.range(oo[0] - buff, oo[1] - buff, oo[0] + buff, oo[1] + buff).map((nn) => i[nn]);
                                // console.log(uu);

                                (ll_diff = []),
                                    (function (nn, oo) {
                                        for (var t = 0; t < nn.length; t++) {
                                            var ee = Math.abs(parseFloat(nn[t][0]) - oo[0]) + Math.abs(parseFloat(nn[t][1]) - oo[1]);
                                            ll_diff.push(ee);
                                        }
                                    })(uu, oo);

                                var hh = ll_diff.indexOf(Math.min(...ll_diff));
                                // console.log(hh);
                                var mm = ss.range(oo[0] - buff, oo[1] - buff, oo[0] + buff, oo[1] + buff);
                                var hh = mm[hh];
                                // console.log(hh);

                                var ww = nn.XLAT[hh];
                                var vv = nn.XLONG[hh];

                                console.log(zone_json_d3);
                                makeplotly3({customId: zone_json_d3, customIdx: hh, lat: ww, lng: vv});

                                });
                                loaded_zones_d3.push(__);

                            } else {
                            o = e;
                            (zone_json = n.slice(0, 14)),
                            (zone_json = zone_json + _ + n.slice(16, 30) + '2.json'),
                            fetch(zone_json).then(function(response){
                                return response.json();
                            }).then(function(n){
                                // console.log(n);
                                // console.log(o);

                             var buff = 0.2
                            for (var t = n.XLAT, e = n.XLONG, l = [], a = [], r = [(r = [t.length, t[0].length])[1], r[0]], c = 0; c < t.length; c++) l = l.concat(t[c]);
                            for (c = 0; c < e.length; c++) a = a.concat(e[c]);
                            var i = t.map(function (n, o) {
                                return [n, e[o]];
                            });
                            var s = new KDBush(i);
                            // console.log(s);

                            point_list.push(o);
                            file_list.push(n);
                            // console.log(o);
                            var u = s.range(o[0] - buff, o[1] - buff, o[0] + buff, o[1] + buff).map((n) => i[n]);
                            // console.log(u);

                            (ll_diff = []),
                                (function (n, o) {
                                    for (var t = 0; t < n.length; t++) {
                                        var e = Math.abs(parseFloat(n[t][0]) - o[0]) + Math.abs(parseFloat(n[t][1]) - o[1]);
                                        ll_diff.push(e);
                                    }
                                })(u, o);

                            var h = ll_diff.indexOf(Math.min(...ll_diff));
                            // console.log(h);
                            var m = s.range(o[0] - buff, o[1] - buff, o[0] + buff, o[1] + buff);
                            var h = m[h];
                            // console.log(h);

                            var w = n.XLAT[h];
                            var v = n.XLONG[h];

                            console.log(zone_json);
                            makeplotly3({customId: zone_json, customIdx: h, lat: w, lng: v});
                            });
                            loaded_zones.push(_);


                      }};


                    function searchcontrol(o) {
                        if (fwfmodellocation != undefined) {
                            fwfmodellocation.remove(map);
                        };

                        map.flyTo(o);
                        fwfclicklocation.setLatLng(o).addTo(map);
                        var e = [parseFloat(o[0]), parseFloat(o[1])];
                        var l = u.range(e[0] - buffer, e[1] - buffer, e[0] + buffer, e[1] + buffer).map((n) => s[n]);
                        (ll_diff = []),
                            (function (n, o) {
                                for (var t = 0; t < n.length; t++) {
                                    var e = Math.abs(n[t][0] - o[0]) + Math.abs(n[t][1] - o[1]);
                                    ll_diff.push(e);
                                }
                            })(l, e);
                        for (var a = 0, r = ll_diff[0], i = 1; i < ll_diff.length; i++) ll_diff[i] < r && ((r = ll_diff[i]), (a = i));
                        var h = u.range(e[0]- buffer, e[1] - buffer, e[0] + buffer, e[1] + buffer);
                        var d, m;
                        f =
                            ((m = (d = c).reduce(
                                function (n, o) {
                                    return n.concat(n[n.length - 1] * o);
                                },
                                [1]
                            )),
                            function (n) {
                                return (function (n, o, t) {
                                    return n.map(function (n, e) {
                                        return Math.round(o / t[e]) % n;
                                    });
                                })(d, n, m);
                            });
                        var g = (function (n, o) {
                                var t = n.reduce(
                                    function (n, o) {
                                        return n.concat(n[n.length - 1] * o);
                                    },
                                    [1]
                                );
                                return n.map(function (n, e) {
                                    return Math.round(o / t[e]) % n;
                                });
                            })(c, h[a], f(h[a])),
                            p = g[1],
                            y = g[0],
                            x = [p, y];
                        var _ = t[p][y];
                        if ( _ == 'd3'){

                                var ee = [parseFloat(o[0]), parseFloat(o[1])];
                                var ll = d3_tree.range(ee[0] - buffer, ee[1] - buffer, ee[0] + buffer, ee[1] + buffer).map((nn) => d3[nn]);
                                (ll_diff2 = []),
                                    (function (nn, oo) {
                                        for (var tt = 0; tt < nn.length; tt++) {
                                            var ee = Math.abs(nn[tt][0] - oo[0]) + Math.abs(nn[tt][1] - oo[1]);
                                            ll_diff2.push(ee);
                                        }
                                    })(ll, ee);
                                for (var aa = 0, rr = ll_diff2[0], ii = 1; ii < ll_diff2.length; ii++) ll_diff2[ii] < rr && ((rr = ll_diff2[ii]), (aa = ii));
                                var hh = d3_tree.range(ee[0]- buffer, ee[1] - buffer, ee[0] + buffer, ee[1] + buffer);
                                var dd, mm;
                                ff =
                                    ((mm = (dd = cc).reduce(
                                        function (nn, oo) {
                                            return nn.concat(nn[nn.length - 1] * oo);
                                        },
                                        [1]
                                    )),
                                    function (nn) {
                                        return (function (nn, oo, tt) {
                                            return nn.map(function (nn, ee) {
                                                return Math.round(o / t[e]) % n;
                                            });
                                        })(dd, nn, mm);
                                    });
                                var gg = (function (nn, oo) {
                                        var tt = nn.reduce(
                                            function (nn, oo) {
                                                return nn.concat(nn[nn.length - 1] * oo);
                                            },
                                            [1]
                                        );
                                        return nn.map(function (nn, ee) {
                                            return Math.round(oo / tt[ee]) % nn;
                                        });
                                    })(cc, hh[aa], ff(hh[aa])),
                                    pp = gg[1],
                                    yy = gg[0],
                                    xx = [pp, yy];
                                    oo = ee;
                                var __ = tt[pp][yy];
                                (zone_json_d3 = n.slice(0, 14)),
                                (zone_json_d3 = zone_json_d3 + __ + n.slice(16, 36)),
                                fetch(zone_json_d3).then(function(response){
                                    return response.json();
                                }).then(function(nn){
                                    // console.log(nn);
                                    // console.log(oo);

                                 var buff = 0.2
                                for (var t = nn.XLAT, e = nn.XLONG, l = [], a = [], r = [(r = [t.length, t[0].length])[1], r[0]], c = 0; c < t.length; c++) l = l.concat(t[c]);
                                for (c = 0; c < e.length; c++) a = a.concat(e[c]);
                                var i = t.map(function (nn, oo) {
                                    return [nn, e[oo]];
                                });
                                var ss = new KDBush(i);
                                // console.log(ss);

                                point_list.push(oo);
                                file_list.push(nn);
                                var uu = ss.range(oo[0] - buff, oo[1] - buff, oo[0] + buff, oo[1] + buff).map((nn) => i[nn]);
                                // console.log(uu);

                                (ll_diff = []),
                                    (function (nn, oo) {
                                        for (var t = 0; t < nn.length; t++) {
                                            var ee = Math.abs(parseFloat(nn[t][0]) - oo[0]) + Math.abs(parseFloat(nn[t][1]) - oo[1]);
                                            ll_diff.push(ee);
                                        }
                                    })(uu, oo);

                                var hh = ll_diff.indexOf(Math.min(...ll_diff));
                                // console.log(hh);
                                var mm = ss.range(oo[0] - buff, oo[1] - buff, oo[0] + buff, oo[1] + buff);
                                var hh = mm[hh];
                                // console.log(hh);

                                var ww = nn.XLAT[hh];
                                var vv = nn.XLONG[hh];

                                // console.log(zone_json_d3);
                                fwfmodellocation = new L.marker([ww,vv],{icon: redIcon, customId: zone_json_d3, customIdx: hh});
                                fwfmodellocation.bindPopup(div2, {maxWidth: "auto", maxHeight: "auto"});
                                fwfmodellocation.setZIndexOffset(1000);
                                // fwfmodellocation.on('click', makeplotly({customId: zone_json_d3, customIdx: hh, lat: ww, lng: vv})).addTo(map);
                                fwfmodellocation.on('click', makeplotly).addTo(map);

                                });
                                loaded_zones_d3.push(__);

                            } else {
                            o = e;
                            (zone_json = n.slice(0, 14)),
                            (zone_json = zone_json + _ + n.slice(16, 30) + '2.json'),
                            fetch(zone_json).then(function(response){
                                return response.json();
                            }).then(function(n){
                                console.log(n);
                                console.log(o);

                             var buff = 0.2
                            for (var t = n.XLAT, e = n.XLONG, l = [], a = [], r = [(r = [t.length, t[0].length])[1], r[0]], c = 0; c < t.length; c++) l = l.concat(t[c]);
                            for (c = 0; c < e.length; c++) a = a.concat(e[c]);
                            var i = t.map(function (n, o) {
                                return [n, e[o]];
                            });
                            var s = new KDBush(i);
                            // console.log(s);

                            point_list.push(o);
                            file_list.push(n);
                            // console.log(o);
                            var u = s.range(o[0] - buff, o[1] - buff, o[0] + buff, o[1] + buff).map((n) => i[n]);
                            // console.log(u);

                            (ll_diff = []),
                                (function (n, o) {
                                    for (var t = 0; t < n.length; t++) {
                                        var e = Math.abs(parseFloat(n[t][0]) - o[0]) + Math.abs(parseFloat(n[t][1]) - o[1]);
                                        ll_diff.push(e);
                                    }
                                })(u, o);

                            var h = ll_diff.indexOf(Math.min(...ll_diff));
                            // console.log(h);
                            var m = s.range(o[0] - buff, o[1] - buff, o[0] + buff, o[1] + buff);
                            var h = m[h];
                            // console.log(h);

                            var w = n.XLAT[h];
                            var v = n.XLONG[h];

                            // console.log(zone_json);
                            fwfmodellocation = new L.marker([w,v],{icon: redIcon, customId: zone_json, customIdx: h});
                            fwfmodellocation.bindPopup(div2, {maxWidth: "auto", maxHeight: "auto"});
                            fwfmodellocation.setZIndexOffset(1000);
                            // fwfmodellocation.on('click', makeplotly({customId: zone_json, customIdx: h, lat: w, lng: v})).addTo(map);
                            fwfmodellocation.on('click', makeplotly).addTo(map);

                            loaded_zones.push(_);
                    });
                        };
                    }
                    control._searchfunctionCallBack = function (searchkeywords){
                        if (!searchkeywords) {
                            searchkeywords = "The search call back is clicked !!"
                        }
                        var o = searchkeywords.split(',').map(Number);
                        searchcontrol(o);
                    }
                    map.addControl(control);

});

}

makeplots(json_fwf);
