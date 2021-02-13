var redIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

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
div2.appendChild(btn_fire2);               // Append <button> to <body>


var btn_wx2 = document.createElement("BUTTON");   // Create a <button> element
btn_wx2.setAttribute("id", "button");
btn_wx2.className = "btn_wx2";
btn_wx2.innerHTML = "Weather";                   // Insert text
div2.appendChild(btn_wx2);


let fwfclicklocation;
fwfclicklocation = new L.marker().bindPopup("<b>Hello!</b><br />The blue icon is where you clicked or searched on the map. <br /> <br />The red icon is the closest model grid point to where you clicked or searched on the map. <br />  <br /> Click the red icon for a point forecast");

var searchboxControl=createSearchboxControl();
                        const control = new searchboxControl({
                            sidebarTitleText: 'Information',
                            sidebarMenuItems: {
                                Items: [
                                    { type: "link", name: "Smoke Forecasts", href: "https://firesmoke.ca/", icon: "icon-fire" },
                                    { type: "link", name: "Weather Research Forecast Team", href: "https://weather.eos.ubc.ca/cgi-bin/index.cgi", icon: "icon-cloudy" },
                                    { type: "link", name: "Contact Inforamtion", href: "https://firesmoke.ca/contact/", icon: "icon-phone" },
                                    { type: "link", name: "Documentation", href: "https://cerodell.github.io/fwf-docs/index.html", icon: "icon-git" },

                                ]
                            }
                        });



function makeplotly(e) {
    var clickedCircle = e.target;
    var json_dir = clickedCircle.options.customId;
    var index = clickedCircle.options.customIdx;

    console.log(clickedCircle);
    console.log(index);

    var ll = clickedCircle._latlng
    console.log(ll);
    btn_fire2.onclick = fwiplot2;
    btn_wx2.onclick = wxplot2;

    var o = [ll.lat,ll.lng]
    console.log(o);
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
        console.log(n);
        console.log(w);
        console.log('TIME ZONE');
        console.log(tz);

        //Create array of options to be added
        var array = ["UTC","Geo Local","Your Local"];

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

        console.log(dict);

        selectList.onchange = function (){
            var value = this.value
            console.log(value);

            if (value == "UTC"){
                N =
                ((ffmc = {x: dict['time'], y: dict['ffmc'], mode: 'lines', line: { color: "ff7f0e" }, yaxis: "y2",  hoverlabel:{font:{size: hovsize, color: "#ffffff"}, bordercolor: "#ffffff"}, hovertemplate: "<b> FFMC </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (isi = {x: dict['time'], y: dict['isi'], mode: 'lines', line: { color: "9467bd" }, yaxis: "y1",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> ISI </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),

                [
                    {
                        type: "table",
                        header: { values: [["Index/Code"], [dict['day'][0]], [dict['day'][1]]], align: "center", height:18, line: {color: "444444" }, fill: { color: "444444E6" }, font: { family: "inherit", size: 10, color: "white" } },
                        // cells: { values: T, align: "center",  height:18, line: { color: "444444", width: 1 }, fill: { color: ["white", "white", "white", "white"], fillopacity:0.5 }, font: { family: "inherit", size: 10, color:[["#2ca02c", "#8c564b", "7f7f7f", "d62728", "000000"]] } },
                        cells: { values: T, align: "center",  height:18, line: { color: "444444", width: 1 }, fill: { color:[["#2ca02c1A", "#8c564b1A", "7f7f7f1A", "d627281A", "0000001A"]] }, font: { family: "inherit", size: 10, color:[["#2ca02c", "#8c564b", "7f7f7f", "d62728", "000000"]]} },

                        xaxis: "x",
                        yaxis: "y",
                        domain: { x: [0.0, 1.0], y: [0.54, 1] },
                    },
                    ffmc,
                    isi,
                ]
                );
                Plotly.react(C,  N, S);


            }else if (value == "Geo Local"){

                N =
                ((ffmc = {x: dict['geo_time'], y: dict['ffmc'], mode: 'lines', line: { color: "ff7f0e" }, yaxis: "y2",  hoverlabel:{font:{size: hovsize, color: "#ffffff"}, bordercolor: "#ffffff"}, hovertemplate: "<b> FFMC </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
                (isi = {x: dict['geo_time'], y: dict['isi'], mode: 'lines', line: { color: "9467bd" }, yaxis: "y1",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> ISI </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),

                [
                    {
                        type: "table",
                        header: { values: [["Index/Code"], [dict['day'][0]], [dict['day'][1]]], align: "center", height:18, line: {color: "444444" }, fill: { color: "444444E6" }, font: { family: "inherit", size: 10, color: "white" } },
                        // cells: { values: T, align: "center",  height:18, line: { color: "444444", width: 1 }, fill: { color: ["white", "white", "white", "white"], fillopacity:0.5 }, font: { family: "inherit", size: 10, color:[["#2ca02c", "#8c564b", "7f7f7f", "d62728", "000000"]] } },
                        cells: { values: T, align: "center",  height:18, line: { color: "444444", width: 1 }, fill: { color:[["#2ca02c1A", "#8c564b1A", "7f7f7f1A", "d627281A", "0000001A"]] }, font: { family: "inherit", size: 10, color:[["#2ca02c", "#8c564b", "7f7f7f", "d62728", "000000"]]} },

                        xaxis: "x",
                        yaxis: "y",
                        domain: { x: [0.0, 1.0], y: [0.54, 1] },
                    },
                    ffmc,
                    isi,
                ]
                );
                Plotly.react(C,  N, S);
            }
            else if (value == "Your Local"){

            N =
            ((ffmc = {x: dict['local_time'], y: dict['ffmc'], mode: 'lines', line: { color: "ff7f0e" }, yaxis: "y2",  hoverlabel:{font:{size: hovsize, color: "#ffffff"}, bordercolor: "#ffffff"}, hovertemplate: "<b> FFMC </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
            (isi = {x: dict['local_time'], y: dict['isi'], mode: 'lines', line: { color: "9467bd" }, yaxis: "y1",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> ISI </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),

            [
                {
                    type: "table",
                    header: { values: [["Index/Code"], [dict['day'][0]], [dict['day'][1]]], align: "center", height:18, line: {color: "444444" }, fill: { color: "444444E6" }, font: { family: "inherit", size: 10, color: "white" } },
                    // cells: { values: T, align: "center",  height:18, line: { color: "444444", width: 1 }, fill: { color: ["white", "white", "white", "white"], fillopacity:0.5 }, font: { family: "inherit", size: 10, color:[["#2ca02c", "#8c564b", "7f7f7f", "d62728", "000000"]] } },
                    cells: { values: T, align: "center",  height:18, line: { color: "444444", width: 1 }, fill: { color:[["#2ca02c1A", "#8c564b1A", "7f7f7f1A", "d627281A", "0000001A"]] }, font: { family: "inherit", size: 10, color:[["#2ca02c", "#8c564b", "7f7f7f", "d62728", "000000"]]} },

                    xaxis: "x",
                    yaxis: "y",
                    domain: { x: [0.0, 1.0], y: [0.54, 1] },
                },
                ffmc,
                isi,
            ]
            );
            Plotly.react(C,  N, S);

          }};

        local_list = []
        arrayLength = dict['time'].length;
        for (i = 0; i < arrayLength; i++) {
            a = new Date(dict['time'][i] + ':00Z').toLocaleString()
            local_list.push(moment(a).format('YYYY-MM-DD HH:mm'))
        }
        dict['local_time'] = local_list
        console.log(local_list);

        local_list2 = []
        arrayLength = n["Time"].length;
        for (i = 0; i < arrayLength; i++) {
        var tz_time = tz +":00";
        console.log(tz_time);
        var time = moment.duration(tz_time);
        a = new Date(n["Time"][i] + ':00Z')
        var date = moment(a)
        var newtime = date.subtract(time).format('YYYY-MM-DD HH:mm');

        local_list2.push(newtime)
        }
        dict['geo_time'] = local_list2;
        console.log(local_list2);

        console.log(C);
        hovsize = 10;
        labelsize = 12;
        ticksize = 9;

        T = [
            ["DMC", "DC", "BUI", "FWI", "DSR"],
            [dict['dmc'][0], dict['dc'][0], dict['bui'][0], dict['fwi'][0], dict['dsr'][0]],
            [dict['dmc'][1], dict['dc'][1], dict['bui'][1], dict['fwi'][1], dict['dsr'][1]],
        ],

        N =
        ((ffmc = {x: dict['time'], y: dict['ffmc'], mode: 'lines', line: { color: "ff7f0e" }, yaxis: "y2",  hoverlabel:{font:{size: hovsize, color: "#ffffff"}, bordercolor: "#ffffff"}, hovertemplate: "<b> FFMC </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),
        (isi = {x: dict['time'], y: dict['isi'], mode: 'lines', line: { color: "9467bd" }, yaxis: "y1",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> ISI </b><br>" + "%{y:.2f} <br>" + "<extra></extra>" }),

        [
            {
                type: "table",
                header: { values: [["Index/Code"], [dict['day'][0]], [dict['day'][1]]], align: "center", height:18, line: {color: "444444" }, fill: { color: "444444E6" }, font: { family: "inherit", size: 10, color: "white" } },
                // cells: { values: T, align: "center",  height:18, line: { color: "444444", width: 1 }, fill: { color: ["white", "white", "white", "white"], fillopacity:0.5 }, font: { family: "inherit", size: 10, color:[["#2ca02c", "#8c564b", "7f7f7f", "d62728", "000000"]] } },
                cells: { values: T, align: "center",  height:18, line: { color: "444444", width: 1 }, fill: { color:[["#2ca02c1A", "#8c564b1A", "7f7f7f1A", "d627281A", "0000001A"]] }, font: { family: "inherit", size: 10, color:[["#2ca02c", "#8c564b", "7f7f7f", "d62728", "000000"]]} },

                xaxis: "x",
                yaxis: "y",
                domain: { x: [0.0, 1.0], y: [0.54, 1] },
            },
            ffmc,
            isi,
        ]
        );




        S = {
            autosize: true,
            title: {text: "Fire Weather Forecast " + "<br>Lat: " + w.toString().slice(0,6) + ", Lon: " + v.toString().slice(0,8) , x:0.05},
            titlefont: { color: "#444444", size: 13 },
            showlegend: !1,
            yaxis2: {domain: [.26, .52], title: { text: "FFMC", font: { size: labelsize, color: "ff7f0e" } }, tickfont: {size: ticksize, color: "ff7f0e"}},
            yaxis1: { domain: [0.0, 0.24], title: { text: "ISI", font: {size: labelsize, color: "9467bd" } }, tickfont: {size: ticksize, color: "9467bd"}},
            // yaxis1: {domain: [0.0, 0.4], title: { text: "DMC", font: { size: labelsize,color: "2ca02c" } }, tickfont: {size: ticksize, color: "2ca02c"}},
            // yaxis4: { domain: [0.48, 0.62], title: { text: "DC", font: { size: labelsize,color: "8c564b" } }, tickfont: {size: ticksize, color: "8c564b"}},
            // yaxis3: { domain: [0.32, 0.46], title: { text: "ISI", font: {size: labelsize, color: "9467bd" } }, tickfont: {size: ticksize, color: "9467bd"}},
            // yaxis2: { domain: [0.16, 0.30], title: { text: "BUI", font: { size: labelsize, color: "7f7f7f" } }, tickfont: {size: ticksize, color: "7f7f7f"}},
            // yaxis1: { domain: [0, 0.14], title: { text: "FWI", font: {size: labelsize, color: "d62728" } }, tickfont: {size: ticksize, color: "d62728"}},
            xaxis: { title: "Date (UTC)", font: { size: labelsize, color: "444444" }}
        };
            Plotly.newPlot(C,  N, S);
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
            console.log(n);
            console.log(w);
            console.log('TIME ZONE');
            console.log(tz);


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

            console.log(dict);



            console.log(C);
            hovsize = 10;
            N =
            [(temp = {x: dict['time'], y: dict['temp'], mode: 'lines', line: { color: "d62728" }, yaxis: "y5", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> Temp </b><br>" + "%{y:.2f} (C)<br>" + "<extra></extra>"}),
            (rh = {x: dict['time'], y: dict['rh'], mode: 'lines', line: { color: "1f77b4" }, yaxis: "y4", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> RH </b><br>" + "%{y:.2f} (%)<br>" + "<extra></extra>"}),
            (ws = {x: dict['time'], y: dict['ws'], mode: 'lines', line: { color: "202020" }, yaxis: "y3", hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> WSP </b><br>" + "%{y:.2f} (km/hr)<br>" + "<extra></extra>"}),
            (wdir = {x: dict['time'], y: dict['wdir'], mode: 'lines', line: { color: "7f7f7f" }, yaxis: "y2",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> WDIR </b><br>" + "%{y:.2f} (deg)<br>" + "<extra></extra>" }),
            (precip = {x: dict['time'], y: dict['precip'], mode: 'lines', line: { color: "2ca02c" }, yaxis: "y1",  hoverlabel:{font:{size: hovsize}}, hovertemplate: "<b> Precip </b><br>" + "%{y:.2f} (mm)<br>" + "<extra></extra>" }),

            ]



            labelsize = 12,
            ticksize = 9,
            S = {
                autosize: true,
                title: {text: "Weather Forecast " + "<br>Lat: " + w.toString().slice(0,6) + ", Lon: " + v.toString().slice(0,8) , x:0.05},
                titlefont: { color: "#444444", size: 13 },
                showlegend: !1,
                yaxis5: { domain: [0.80, 0.98], title: { text: "Temp<br>(C)", font: {size: labelsize, color: "d62728" } }, tickfont: {size: ticksize, color: "d62728"}},
                yaxis4: { domain: [0.60, 0.78],  title: { text: "RH<br>(%)", font: {size: labelsize, color: "1f77b4" } }, tickfont: {size: ticksize, color: "1f77b4"}},
                yaxis3: { domain: [0.40, 0.58], title: { text: "WSP<br>(km/hr)", font: {size: labelsize, color: "202020" } } , tickfont: {size: ticksize, color: "202020"}},
                yaxis2: { domain: [0.20, 0.38], title: { text: "WDIR<br>(deg)", font: {size: labelsize, color: "7f7f7f" } }, tickfont: {size: ticksize, color: "7f7f7f"}, range: [0, 360], tickvals:[0, 90, 180, 270, 360]},
                yaxis1: { domain: [0, 0.18], title: { text: "Precip<br>(mm)", font: {size: labelsize, color: "2ca02c" } }, tickfont: {size: ticksize, color: "2ca02c"}},
                xaxis: { title: "Date (UTC)", font: { size: labelsize, color: "#444444" }},
                };
                Plotly.newPlot(C,  N, S);
                });
            }
};







var fwfmodellocation;

function makeplots(n) {
    (json_dir = "static/json/fwf-zone-merge.json"),
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

                (loaded_zones = ["he"]),
                (loaded_zones_d3 = ["he"]),
                    map.on("dblclick", function (o) {
                        if (fwfmodellocation != undefined) {
                            fwfmodellocation.remove(map);
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
                                    console.log(nn);
                                    console.log(oo);

                                 var buff = 0.2
                                for (var t = nn.XLAT, e = nn.XLONG, l = [], a = [], r = [(r = [t.length, t[0].length])[1], r[0]], c = 0; c < t.length; c++) l = l.concat(t[c]);
                                for (c = 0; c < e.length; c++) a = a.concat(e[c]);
                                var i = t.map(function (nn, oo) {
                                    return [nn, e[oo]];
                                });
                                var ss = new KDBush(i);
                                console.log(ss);

                                point_list.push(oo);
                                file_list.push(nn);
                                var uu = ss.range(oo[0] - buff, oo[1] - buff, oo[0] + buff, oo[1] + buff).map((nn) => i[nn]);
                                console.log(uu);

                                (ll_diff = []),
                                    (function (nn, oo) {
                                        for (var t = 0; t < nn.length; t++) {
                                            var ee = Math.abs(parseFloat(nn[t][0]) - oo[0]) + Math.abs(parseFloat(nn[t][1]) - oo[1]);
                                            ll_diff.push(ee);
                                        }
                                    })(uu, oo);

                                var hh = ll_diff.indexOf(Math.min(...ll_diff));
                                console.log(hh);
                                var mm = ss.range(oo[0] - buff, oo[1] - buff, oo[0] + buff, oo[1] + buff);
                                var hh = mm[hh];
                                console.log(hh);

                                var ww = nn.XLAT[hh];
                                var vv = nn.XLONG[hh];

                                console.log(zone_json_d3);
                                fwfmodellocation = new L.marker([ww,vv],{icon: redIcon, customId: zone_json_d3, customIdx: hh});
                                fwfmodellocation.bindPopup(div2, {maxWidth: "auto", maxHeight: "auto"});
                                fwfmodellocation.setZIndexOffset(1000);
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
                            console.log(s);

                            point_list.push(o);
                            file_list.push(n);
                            console.log(o);
                            var u = s.range(o[0] - buff, o[1] - buff, o[0] + buff, o[1] + buff).map((n) => i[n]);
                            console.log(u);

                            (ll_diff = []),
                                (function (n, o) {
                                    for (var t = 0; t < n.length; t++) {
                                        var e = Math.abs(parseFloat(n[t][0]) - o[0]) + Math.abs(parseFloat(n[t][1]) - o[1]);
                                        ll_diff.push(e);
                                    }
                                })(u, o);

                            var h = ll_diff.indexOf(Math.min(...ll_diff));
                            console.log(h);
                            var m = s.range(o[0] - buff, o[1] - buff, o[0] + buff, o[1] + buff);
                            var h = m[h];
                            console.log(h);

                            var w = n.XLAT[h];
                            var v = n.XLONG[h];

                            console.log(zone_json);
                            fwfmodellocation = new L.marker([w,v],{icon: redIcon, customId: zone_json, customIdx: h});
                            fwfmodellocation.bindPopup(div2, {maxWidth: "auto", maxHeight: "auto"});
                            fwfmodellocation.setZIndexOffset(1000);
                            fwfmodellocation.on('click', makeplotly).addTo(map);

                            });
                            loaded_zones.push(_);
                    }});
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
                                    console.log(nn);
                                    console.log(oo);

                                 var buff = 0.2
                                for (var t = nn.XLAT, e = nn.XLONG, l = [], a = [], r = [(r = [t.length, t[0].length])[1], r[0]], c = 0; c < t.length; c++) l = l.concat(t[c]);
                                for (c = 0; c < e.length; c++) a = a.concat(e[c]);
                                var i = t.map(function (nn, oo) {
                                    return [nn, e[oo]];
                                });
                                var ss = new KDBush(i);
                                console.log(ss);

                                point_list.push(oo);
                                file_list.push(nn);
                                var uu = ss.range(oo[0] - buff, oo[1] - buff, oo[0] + buff, oo[1] + buff).map((nn) => i[nn]);
                                console.log(uu);

                                (ll_diff = []),
                                    (function (nn, oo) {
                                        for (var t = 0; t < nn.length; t++) {
                                            var ee = Math.abs(parseFloat(nn[t][0]) - oo[0]) + Math.abs(parseFloat(nn[t][1]) - oo[1]);
                                            ll_diff.push(ee);
                                        }
                                    })(uu, oo);

                                var hh = ll_diff.indexOf(Math.min(...ll_diff));
                                console.log(hh);
                                var mm = ss.range(oo[0] - buff, oo[1] - buff, oo[0] + buff, oo[1] + buff);
                                var hh = mm[hh];
                                console.log(hh);

                                var ww = nn.XLAT[hh];
                                var vv = nn.XLONG[hh];

                                console.log(zone_json_d3);
                                fwfmodellocation = new L.marker([ww,vv],{icon: redIcon, customId: zone_json_d3, customIdx: hh});
                                fwfmodellocation.bindPopup(div2, {maxWidth: "auto", maxHeight: "auto"});
                                fwfmodellocation.setZIndexOffset(1000);
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
                            console.log(s);

                            point_list.push(o);
                            file_list.push(n);
                            console.log(o);
                            var u = s.range(o[0] - buff, o[1] - buff, o[0] + buff, o[1] + buff).map((n) => i[n]);
                            console.log(u);

                            (ll_diff = []),
                                (function (n, o) {
                                    for (var t = 0; t < n.length; t++) {
                                        var e = Math.abs(parseFloat(n[t][0]) - o[0]) + Math.abs(parseFloat(n[t][1]) - o[1]);
                                        ll_diff.push(e);
                                    }
                                })(u, o);

                            var h = ll_diff.indexOf(Math.min(...ll_diff));
                            console.log(h);
                            var m = s.range(o[0] - buff, o[1] - buff, o[0] + buff, o[1] + buff);
                            var h = m[h];
                            console.log(h);

                            var w = n.XLAT[h];
                            var v = n.XLONG[h];

                            console.log(zone_json);
                            fwfmodellocation = new L.marker([w,v],{icon: redIcon, customId: zone_json, customIdx: h});
                            fwfmodellocation.bindPopup(div2, {maxWidth: "auto", maxHeight: "auto"});
                            fwfmodellocation.setZIndexOffset(1000);
                            fwfmodellocation.on('click', makeplotly).addTo(map);
                            loaded_zones.push(_);
                    });
                        };
                    };

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
window.onload = function () {
    makeplots(json_fwf);
    // alert("Hello WFRT Team tester, please click on the map for point forecasts. Youll's see a red icon where you clicked. Click that red icon for a popup Meteogram. \n \n Also, please test the weather station layer. Look under the drop-down menu in the upper right to active the Weather Station layer. Each WxStation has a popup plot bound to it with past observations and model forecasts. \n \n Thank you :)");

};
