var wx_station = L.layerGroup();
const div = document.createElement("div");
div.className = "wx-plot";
const div2 = div.cloneNode(!0);
div.setAttribute("id", "wx_plot");
var btn_fire = document.createElement("BUTTON");
btn_fire.setAttribute("id", "button"), (btn_fire.className = "btn_fire"), (btn_fire.innerHTML = "Fire Weather"), div.appendChild(btn_fire);
var btn_wx = document.createElement("BUTTON");
function circleClick(e) {
    var t = e.target,
        o = t.options.customId,
        r = t.options.customTZ,
        i = t.options.customLAT,
        c = t.options.customLON,
        s = t.options.customEL;
    (btn_fire.onclick = f),
        (btn_wx.onclick = function () {
            fetch(l)
                .then(function (e) {
                    return e.json();
                })
                .then(function (e) {
                    var t = JSON.parse(e.wmo),
                        l = t.indexOf(parseInt(o)),
                        f = {},
                        n = (e, t) => e.map((e) => e[t]);
                    function m(e) {
                        for (y = 0; y < e.length; ++y) -99 == e[y] ? (e[y] = null) : (e[y] = e[y]);
                        return e;
                    }
                    for (var b of ((keys = [
                        "dsr_fc",
                        "dsr_obs",
                        "dsr_pfc",
                        "ffmc_fc",
                        "ffmc_obs",
                        "ffmc_pfc",
                        "rh_fc",
                        "rh_obs",
                        "rh_pfc",
                        "isi_fc",
                        "isi_obs",
                        "isi_pfc",
                        "fwi_fc",
                        "fwi_obs",
                        "fwi_pfc",
                        "temp_fc",
                        "temp_obs",
                        "temp_pfc",
                        "ws_fc",
                        "ws_obs",
                        "ws_pfc",
                        "wdir_fc",
                        "wdir_obs",
                        "wdir_pfc",
                        "precip_fc",
                        "precip_obs",
                        "precip_pfc",
                        "dc_fc",
                        "dc_obs",
                        "dc_pfc",
                        "dmc_fc",
                        "dmc_obs",
                        "dmc_pfc",
                        "bui_fc",
                        "bui_obs",
                        "bui_pfc",
                    ]),
                    keys)) {
                        var _ = JSON.parse(e[b]),
                            _ = n(_, l);
                        (_ = m(_)), (f[b] = _);
                    }
                    for (var b of ((keys = ["wmo"]), keys)) {
                        var _ = JSON.parse(e[b]);
                        f[b] = _[l];
                    }
                    var h = e.name,
                        h = (h = (h = (h = h.replace(/'/g, "")).replace("[", "")).replace("]", "")).split(",");
                    for (var b of (console.log(h), console.log(l), (f.wx_name = h[l].trim()), console.log(f.wx_name), (keys = ["time_obs", "time_fch", "time_fcd"]), keys)) {
                        var _ = e[b];
                        f[b] = _;
                    }
                    var p = moment.tz(Intl.DateTimeFormat().resolvedOptions().timeZone).zoneAbbr(),
                        _ = [p, "UTC", "Geo Local"],
                        x = document.createElement("select");
                    x.setAttribute("id", "mySelect"), (x.className = "time_wx"), div.appendChild(x);
                    for (var y = 0; y < _.length; y++) {
                        var v = document.createElement("option");
                        v.setAttribute("value", _[y]), (v.text = _[y]), x.appendChild(v);
                    }
                    function u(e, t) {
                        for (local_list2 = [], arrayLength = e.length, y = 0; y < arrayLength; y++) {
                            d = e[y] + ":00:00.000Z";
                            var o = moment
                                    .utc(d)
                                    .subtract({ hours: Math.abs(r) })
                                    .format("YYYY-MM-DD HH:mm z"),
                                i = o.slice(0, 16);
                            local_list2.push(i);
                        }
                        for (f["geo_time" + t] = local_list2, local_list = [], arrayLength = e.length, y = 0; y < arrayLength; y++) (a = new Date(e[y] + ":00Z").toLocaleString()), local_list.push(moment(a).format("YYYY-MM-DD HH:mm"));
                        f["local_time" + t] = local_list;
                    }
                    u(f.time_fcd, "_fcd"), u(f.time_obs, "_obs"), u(f.time_fch, "_fch");
                    var w = f.time_obs[0] + ":00:00Z";
                    function z(e, t, o, r, a, l) {
                        if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent))
                            var n = 320,
                                m = 400,
                                b = 50,
                                d = 30,
                                _ = 60,
                                h = 68,
                                p = 1,
                                x = 6,
                                y = 9,
                                v = 8,
                                u = 8;
                        else
                            var n = 700,
                                m = 500,
                                b = 60,
                                d = 30,
                                _ = 80,
                                h = 100,
                                p = 2,
                                x = 11,
                                y = 11.5,
                                v = 10,
                                u = 14;
                        (C = document.getElementById("wx_plot")),
                            (hovsize = 13),
                            (N = [
                                (temp_obs = {
                                    x: e,
                                    y: f.temp_obs,
                                    mode: "lines",
                                    line: { color: "d62728", dash: "dot" },
                                    yaxis: "y5",
                                    hoverlabel: { font: { size: hovsize } },
                                    hovertemplate: "<b> Temp Observed </b><br>%{y:.2f} (C)<br><extra></extra>",
                                }),
                                (temp_fc = {
                                    x: e,
                                    y: f.temp_pfc,
                                    mode: "lines",
                                    line: { color: "d62728", width: 0.5 },
                                    yaxis: "y5",
                                    hoverlabel: { font: { size: hovsize } },
                                    hovertemplate: "<b> Temp Previous Forecast </b><br>%{y:.2f} (C)<br><extra></extra>",
                                }),
                                (temp_fc = {
                                    x: o,
                                    y: f.temp_fc,
                                    mode: "lines",
                                    line: { color: "d62728" },
                                    yaxis: "y5",
                                    hoverlabel: { font: { size: hovsize } },
                                    hovertemplate: "<b> Temp Current Forecast </b><br>%{y:.2f} (C)<br><extra></extra>",
                                }),
                                (rh_obs = {
                                    x: e,
                                    y: f.rh_obs,
                                    mode: "lines",
                                    line: { color: "1f77b4", dash: "dot" },
                                    yaxis: "y4",
                                    hoverlabel: { font: { size: hovsize } },
                                    hovertemplate: "<b> RH Observed </b><br>%{y:.2f} (%)<br><extra></extra>",
                                }),
                                (rh_fc = {
                                    x: e,
                                    y: f.rh_pfc,
                                    mode: "lines",
                                    line: { color: "1f77b4", width: 0.5 },
                                    yaxis: "y4",
                                    hoverlabel: { font: { size: hovsize } },
                                    hovertemplate: "<b> RH Previous Forecast </b><br>%{y:.2f} (%)<br><extra></extra>",
                                }),
                                (rh_fc = {
                                    x: o,
                                    y: f.rh_fc,
                                    mode: "lines",
                                    line: { color: "1f77b4" },
                                    yaxis: "y4",
                                    hoverlabel: { font: { size: hovsize } },
                                    hovertemplate: "<b> RH Current Forecast  </b><br>%{y:.2f} (%)<br><extra></extra>",
                                }),
                                (ws_obs = {
                                    x: e,
                                    y: f.ws_obs,
                                    mode: "lines",
                                    line: { color: "202020", dash: "dot" },
                                    yaxis: "y3",
                                    hoverlabel: { font: { size: hovsize } },
                                    hovertemplate: "<b> WSP Observed </b><br>%{y:.2f} (km/hr)<br><extra></extra>",
                                }),
                                (ws_fc = {
                                    x: e,
                                    y: f.ws_pfc,
                                    mode: "lines",
                                    line: { color: "202020", width: 0.5 },
                                    yaxis: "y3",
                                    hoverlabel: { font: { size: hovsize } },
                                    hovertemplate: "<b> WSP Previous Forecast </b><br>%{y:.2f} (km/hr)<br><extra></extra>",
                                }),
                                (ws_fc = {
                                    x: o,
                                    y: f.ws_fc,
                                    mode: "lines",
                                    line: { color: "202020" },
                                    yaxis: "y3",
                                    hoverlabel: { font: { size: hovsize } },
                                    hovertemplate: "<b> WSP Current Forecast </b><br>%{y:.2f} (km/hr)<br><extra></extra>",
                                }),
                                (wdir_obs = {
                                    x: e,
                                    y: f.wdir_obs,
                                    mode: "lines",
                                    line: { color: "7f7f7f", dash: "dot" },
                                    yaxis: "y2",
                                    hoverlabel: { font: { size: hovsize } },
                                    hovertemplate: "<b> WDIR Observed </b><br>%{y:.2f} (deg)<br><extra></extra>",
                                }),
                                (wdir_fc = {
                                    x: e,
                                    y: f.wdir_pfc,
                                    mode: "lines",
                                    line: { color: "7f7f7f", width: 0.5 },
                                    yaxis: "y2",
                                    hoverlabel: { font: { size: hovsize } },
                                    hovertemplate: "<b> WDIR Previous Forecast </b><br>%{y:.2f} (deg)<br><extra></extra>",
                                }),
                                (wdir_fc = {
                                    x: o,
                                    y: f.wdir_fc,
                                    mode: "lines",
                                    line: { color: "7f7f7f" },
                                    yaxis: "y2",
                                    hoverlabel: { font: { size: hovsize } },
                                    hovertemplate: "<b> WDIR Current Forecast </b><br>%{y:.2f} (deg)<br><extra></extra>",
                                }),
                                (precip_obs = {
                                    x: e,
                                    y: f.precip_obs,
                                    mode: "lines",
                                    line: { color: "2ca02c", dash: "dot" },
                                    yaxis: "y1",
                                    hoverlabel: { font: { size: hovsize } },
                                    hovertemplate: "<b> Precip Observed </b><br>%{y:.2f} (mm)<br><extra></extra>",
                                }),
                                (precip_fc = {
                                    x: e,
                                    y: f.precip_pfc,
                                    mode: "lines",
                                    line: { color: "2ca02c", width: 0.5 },
                                    yaxis: "y1",
                                    hoverlabel: { font: { size: hovsize } },
                                    hovertemplate: "<b> Precip Previous Forecast </b><br>%{y:.2f} (mm)<br><extra></extra>",
                                }),
                                (precip_fc = {
                                    x: o,
                                    y: f.precip_fc,
                                    mode: "lines",
                                    line: { color: "2ca02c" },
                                    yaxis: "y1",
                                    hoverlabel: { font: { size: hovsize } },
                                    hovertemplate: "<b> Precip Current Forecast </b><br>%{y:.2f} (mm)<br><extra></extra>",
                                }),
                            ]),
                            (y = 12),
                            (v = 9),
                            (S = {
                                autosize: !1,
                                width: n,
                                height: m,
                                margin: { l: b, r: d, b: _, t: h, pad: p },
                                title: { text: f.wx_name + " <br>WMO: " + f.wmo.toString() + " <br>Lat: " + i.toString().slice(0, 6) + ", Lon: " + c.toString().slice(0, 8) + " <br>Elevation: " + s.toString().slice(0, 8) + " m", x: 0.05 },
                                titlefont: { color: "#444444", size: u },
                                showlegend: !1,
                                yaxis5: { domain: [0.8, 0.98], title: { text: "Temp<br>(C)", font: { size: y, color: "d62728" } }, tickfont: { size: v, color: "d62728" } },
                                yaxis4: { domain: [0.6, 0.78], title: { text: "RH<br>(%)", font: { size: y, color: "1f77b4" } }, tickfont: { size: v, color: "1f77b4" } },
                                yaxis3: { domain: [0.4, 0.58], title: { text: "WSP<br>(km/hr)", font: { size: y, color: "202020" } }, tickfont: { size: v, color: "202020" } },
                                yaxis2: { domain: [0.2, 0.38], title: { text: "WDIR<br>(deg)", font: { size: y, color: "7f7f7f" } }, tickfont: { size: v, color: "7f7f7f" }, range: [0, 360], tickvals: [0, 90, 180, 270, 360] },
                                yaxis1: { domain: [0, 0.18], title: { text: "Precip<br>(mm)", font: { size: y, color: "2ca02c" } }, tickfont: { size: v, color: "2ca02c" } },
                                xaxis: { tickfont: { size: x, color: "444444" } },
                                shapes: [
                                    { type: "line", x0: r, y0: 0, x1: r, yref: "paper", y1: 0.98, line: { color: "grey", width: 1.5, dash: "dot" } },
                                    { type: "rect", xref: "x", yref: "paper", x0: a, y0: 0, x1: l, y1: 0.98, fillcolor: "#A7A7A7", opacity: 0.2, line: { width: 0 } },
                                ],
                            }),
                            Plotly.newPlot(C, N, S);
                    }
                    (x.onchange = function () {
                        var e = this.value;
                        if ("UTC" == e) z(f.time_obs, f.time_fcd, f.time_fch, UTCTimeMap, w, UTCTimePlot);
                        else if ("Geo Local" == e) {
                            var t = moment
                                    .utc(UTCTimeMap)
                                    .subtract({ hours: Math.abs(r) })
                                    .format("YYYY-MM-DD HH:mm z"),
                                o = t.slice(0, 16),
                                i = moment
                                    .utc(w)
                                    .subtract({ hours: Math.abs(r) })
                                    .format("YYYY-MM-DD HH:mm z"),
                                a = i.slice(0, 16),
                                c = moment
                                    .utc(UTCTimePlot)
                                    .subtract({ hours: Math.abs(r) })
                                    .format("YYYY-MM-DD HH:mm z"),
                                s = c.slice(0, 16);
                            z(f.geo_time_obs, f.geo_time_fcd, f.geo_time_fch, o, a, s);
                        } else if (e == p) {
                            UTCTimeMap.length < 20 && (UTCTimeMap += "Z");
                            var l = moment(new Date(UTCTimeMap).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                                n = moment(new Date(w).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                                m = moment(new Date(UTCTimePlot).toLocaleString()).format("YYYY-MM-DD HH:mm");
                            z(f.local_time_obs, f.local_time_fcd, f.local_time_fch, l, n, m);
                        }
                    }),
                        UTCTimeMap.length < 20 && (UTCTimeMap += "Z");
                    var g = moment(new Date(UTCTimeMap).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                        Y = moment(new Date(w).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                        M = moment(new Date(UTCTimePlot).toLocaleString()).format("YYYY-MM-DD HH:mm");
                    z(f.local_time_obs, f.local_time_fcd, f.local_time_fch, g, Y, M);
                });
        });
    var l = wxstations.slice(0, 13) + String(r) + wxstations.slice(14);
    function f() {
        fetch(l)
            .then(function (e) {
                return e.json();
            })
            .then(function (e) {
                console.log(e.wmo);
                var t = JSON.parse(e.wmo).indexOf(parseInt(o)),
                    l = {};
                const f = (e, t) => e.map((e) => e[t]);
                function n(e) {
                    for (x = 0; x < e.length; ++x) -99 == e[x] ? (e[x] = null) : (e[x] = e[x]);
                    return e;
                }
                for (var m of ((keys = [
                    "dsr_fc",
                    "dsr_obs",
                    "dsr_pfc",
                    "ffmc_fc",
                    "ffmc_obs",
                    "ffmc_pfc",
                    "rh_fc",
                    "rh_obs",
                    "rh_pfc",
                    "isi_fc",
                    "isi_obs",
                    "isi_pfc",
                    "fwi_fc",
                    "fwi_obs",
                    "fwi_pfc",
                    "temp_fc",
                    "temp_obs",
                    "temp_pfc",
                    "ws_fc",
                    "ws_obs",
                    "ws_pfc",
                    "wdir_fc",
                    "wdir_obs",
                    "wdir_pfc",
                    "precip_fc",
                    "precip_obs",
                    "precip_pfc",
                    "dc_fc",
                    "dc_obs",
                    "dc_pfc",
                    "dmc_fc",
                    "dmc_obs",
                    "dmc_pfc",
                    "bui_fc",
                    "bui_obs",
                    "bui_pfc",
                ]),
                keys)) {
                    console.log('ERROR');
                    console.log(m);
                    console.log(e[m]);
                    (b = n((b = f((b = JSON.parse(e[m])), t)))), (l[m] = b);
                    console.log(b);
                }
                for (var m of ((keys = ["wmo"]), keys)) {
                    var b = JSON.parse(e[m]);
                    console.log(b.length), (l[m] = b[t]);
                }
                var _ = (_ = (_ = (_ = (_ = e.name).replace(/'/g, "")).replace("[", "")).replace("]", "")).split(",");
                for (var m of (console.log(_.length), console.log(t), (l.wx_name = _[t].trim()), console.log(l.wx_name), (keys = ["time_obs", "time_fch", "time_fcd"]), keys)) {
                    b = e[m];
                    l[m] = b;
                }
                (Array.prototype.insert = function (e, t) {
                    this.splice(e, 0, t);
                }),
                    l.time_fcd.insert(0, l.time_obs[l.time_obs.length - 1]),
                    l.dmc_fc.insert(0, l.dmc_pfc[l.dmc_pfc.length - 1]),
                    l.dc_fc.insert(0, l.dc_pfc[l.dc_pfc.length - 1]),
                    l.bui_fc.insert(0, l.bui_pfc[l.bui_pfc.length - 1]),
                    l.fwi_fc.insert(0, l.fwi_pfc[l.fwi_pfc.length - 1]);
                var h = moment.tz(Intl.DateTimeFormat().resolvedOptions().timeZone).zoneAbbr(),
                    p = ((b = [h, "UTC", "Geo Local"]), document.createElement("select"));
                p.setAttribute("id", "mySelect"), (p.className = "time_wx"), div.appendChild(p);
                for (var x = 0; x < b.length; x++) {
                    var y = document.createElement("option");
                    y.setAttribute("value", b[x]), (y.text = b[x]), p.appendChild(y);
                }
                function v(e, t) {
                    for (local_list2 = [], arrayLength = e.length, x = 0; x < arrayLength; x++) {
                        d = e[x] + ":00:00.000Z";
                        var o = moment
                            .utc(d)
                            .subtract({ hours: Math.abs(r) })
                            .format("YYYY-MM-DD HH:mm z")
                            .slice(0, 16);
                        local_list2.push(o);
                    }
                    for (l["geo_time" + t] = local_list2, local_list = [], arrayLength = e.length, x = 0; x < arrayLength; x++) (a = new Date(e[x] + ":00Z").toLocaleString()), local_list.push(moment(a).format("YYYY-MM-DD HH:mm"));
                    l["local_time" + t] = local_list;
                }
                v(l.time_fcd, "_fcd"), v(l.time_obs, "_obs"), v(l.time_fch, "_fch");
                var u = l.time_obs[0] + ":00:00Z";
                function w(e, t, o, r, a, f) {
                    if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent))
                        var n = 320,
                            m = 400,
                            b = 50,
                            d = 30,
                            _ = 60,
                            h = 68,
                            p = 1,
                            x = 6,
                            y = 9,
                            v = 8,
                            u = 8;
                    else (n = 700), (m = 500), (b = 60), (d = 30), (_ = 80), (h = 100), (p = 2), (x = 11), (y = 11.5), (v = 10), (u = 14);
                    (C = document.getElementById("wx_plot")),
                        (hovsize = 12),
                        (N = [
                            (ffmc_obs = {
                                x: e,
                                y: l.ffmc_obs,
                                mode: "lines",
                                line: { color: "ff7f0e", dash: "dot" },
                                yaxis: "y6",
                                hoverlabel: { font: { size: hovsize, color: "#ffffff" }, bordercolor: "#ffffff" },
                                hovertemplate: "<b> FFMC Observed </b><br>%{y:.2f} <br><extra></extra>",
                            }),
                            (ffmc_fc = {
                                x: e,
                                y: l.ffmc_pfc,
                                mode: "lines",
                                line: { color: "ff7f0e", width: 0.5 },
                                yaxis: "y6",
                                hoverlabel: { font: { size: hovsize, color: "#ffffff" }, bordercolor: "#ffffff" },
                                hovertemplate: "<b> FFMC Previous Forecast </b><br>%{y:.2f} <br><extra></extra>",
                            }),
                            (ffmc_fc = {
                                x: o,
                                y: l.ffmc_fc,
                                mode: "lines",
                                line: { color: "ff7f0e" },
                                yaxis: "y6",
                                hoverlabel: { font: { size: hovsize, color: "#ffffff" }, bordercolor: "#ffffff" },
                                hovertemplate: "<b> FFMC Current Forecast </b><br>%{y:.2f} <br><extra></extra>",
                            }),
                            (dmc_obs = {
                                x: e,
                                y: l.dmc_obs,
                                mode: "lines",
                                line: { color: "2ca02c", dash: "dot" },
                                yaxis: "y5",
                                hoverlabel: { font: { size: hovsize } },
                                hovertemplate: "<b> DMC Observed </b><br>%{y:.2f} <br><extra></extra>",
                            }),
                            (dmc_fc = {
                                x: e,
                                y: l.dmc_pfc,
                                mode: "lines",
                                line: { color: "2ca02c", width: 0.5 },
                                yaxis: "y5",
                                hoverlabel: { font: { size: hovsize } },
                                hovertemplate: "<b> DMC Previous Forecast </b><br>%{y:.2f} <br><extra></extra>",
                            }),
                            (dmc_fc = { x: t, y: l.dmc_fc, mode: "lines", line: { color: "2ca02c" }, yaxis: "y5", hoverlabel: { font: { size: hovsize } }, hovertemplate: "<b> DMC Current Forecast </b><br>%{y:.2f} <br><extra></extra>" }),
                            (dc_obs = {
                                x: e,
                                y: l.dc_obs,
                                mode: "lines",
                                line: { color: "8c564b", dash: "dot" },
                                yaxis: "y4",
                                hoverlabel: { font: { size: hovsize } },
                                hovertemplate: "<b> DC Observed </b><br>%{y:.2f} <br><extra></extra>",
                            }),
                            (dc_fc = {
                                x: e,
                                y: l.dc_pfc,
                                mode: "lines",
                                line: { color: "8c564b", width: 0.5 },
                                yaxis: "y4",
                                hoverlabel: { font: { size: hovsize } },
                                hovertemplate: "<b> DC Previous Forecast </b><br>%{y:.2f} <br><extra></extra>",
                            }),
                            (dc_fc = { x: t, y: l.dc_fc, mode: "lines", line: { color: "8c564b" }, yaxis: "y4", hoverlabel: { font: { size: hovsize } }, hovertemplate: "<b> DC Current Forecast </b><br>%{y:.2f} <br><extra></extra>" }),
                            (isi_obs = {
                                x: e,
                                y: l.isi_obs,
                                mode: "lines",
                                line: { color: "9467bd", dash: "dot" },
                                yaxis: "y3",
                                hoverlabel: { font: { size: hovsize } },
                                hovertemplate: "<b> ISI Observed </b><br>%{y:.2f} <br><extra></extra>",
                            }),
                            (isi_fc = {
                                x: e,
                                y: l.isi_pfc,
                                mode: "lines",
                                line: { color: "9467bd", width: 0.5 },
                                yaxis: "y3",
                                hoverlabel: { font: { size: hovsize } },
                                hovertemplate: "<b> ISI Previous Forecast </b><br>%{y:.2f} <br><extra></extra>",
                            }),
                            (isi_fc = { x: o, y: l.isi_fc, mode: "lines", line: { color: "9467bd" }, yaxis: "y3", hoverlabel: { font: { size: hovsize } }, hovertemplate: "<b> ISI Current Forecast </b><br>%{y:.2f} <br><extra></extra>" }),
                            (bui_obs = {
                                x: e,
                                y: l.bui_obs,
                                mode: "lines",
                                line: { color: "7f7f7f", dash: "dot" },
                                yaxis: "y2",
                                hoverlabel: { font: { size: hovsize } },
                                hovertemplate: "<b> BUI Observed </b><br>%{y:.2f} <br><extra></extra>",
                            }),
                            (bui_fc = {
                                x: e,
                                y: l.bui_pfc,
                                mode: "lines",
                                line: { color: "7f7f7f", width: 0.5 },
                                yaxis: "y2",
                                hoverlabel: { font: { size: hovsize } },
                                hovertemplate: "<b> BUI Previous Forecast </b><br>%{y:.2f} <br><extra></extra>",
                            }),
                            (bui_fc = { x: t, y: l.bui_fc, mode: "lines", line: { color: "7f7f7f" }, yaxis: "y2", hoverlabel: { font: { size: hovsize } }, hovertemplate: "<b> BUI Current Forecast </b><br>%{y:.2f} <br><extra></extra>" }),
                            (fwi_obs = {
                                x: e,
                                y: l.fwi_obs,
                                mode: "lines",
                                line: { color: "d62728", dash: "dot" },
                                yaxis: "y1",
                                hoverlabel: { font: { size: hovsize } },
                                hovertemplate: "<b> FWI Observed </b><br>%{y:.2f} <br><extra></extra>",
                            }),
                            (fwi_fc = {
                                x: e,
                                y: l.fwi_pfc,
                                mode: "lines",
                                line: { color: "d62728", width: 0.5 },
                                yaxis: "y1",
                                hoverlabel: { font: { size: hovsize } },
                                hovertemplate: "<b> FWI Previous Forecast </b><br>%{y:.2f} <br><extra></extra>",
                            }),
                            (fwi_fc = { x: t, y: l.fwi_fc, mode: "lines", line: { color: "d62728" }, yaxis: "y1", hoverlabel: { font: { size: hovsize } }, hovertemplate: "<b> FWI Current Forecast </b><br>%{y:.2f} <br><extra></extra>" }),
                        ]),
                        (y = 12),
                        (v = 9),
                        (S = {
                            autosize: !1,
                            width: n,
                            height: m,
                            margin: { l: b, r: d, b: _, t: h, pad: p },
                            title: { text: l.wx_name + " <br>WMO: " + l.wmo.toString() + " <br>Lat: " + i.toString().slice(0, 6) + ", Lon: " + c.toString().slice(0, 8) + " <br>Elevation: " + s.toString().slice(0, 8) + " m", x: 0.05 },
                            titlefont: { color: "#444444", size: u },
                            showlegend: !1,
                            yaxis6: { domain: [0.8, 0.94], title: { text: "FFMC", font: { size: y, color: "ff7f0e" } }, tickfont: { size: v, color: "ff7f0e" } },
                            yaxis5: { domain: [0.64, 0.78], title: { text: "DMC", font: { size: y, color: "2ca02c" } }, tickfont: { size: v, color: "2ca02c" } },
                            yaxis4: { domain: [0.48, 0.62], title: { text: "DC", font: { size: y, color: "8c564b" } }, tickfont: { size: v, color: "8c564b" } },
                            yaxis3: { domain: [0.32, 0.46], title: { text: "ISI", font: { size: y, color: "9467bd" } }, tickfont: { size: v, color: "9467bd" } },
                            yaxis2: { domain: [0.16, 0.3], title: { text: "BUI", font: { size: y, color: "7f7f7f" } }, tickfont: { size: v, color: "7f7f7f" } },
                            yaxis1: { domain: [0, 0.14], title: { text: "FWI", font: { size: y, color: "d62728" } }, tickfont: { size: v, color: "d62728" } },
                            xaxis: { tickfont: { size: x, color: "444444" } },
                            shapes: [
                                { type: "line", x0: r, y0: 0, x1: r, yref: "paper", y1: 0.94, line: { color: "grey", width: 1.5, dash: "dot" } },
                                { type: "rect", xref: "x", yref: "paper", x0: a, y0: 0, x1: f, y1: 0.94, fillcolor: "#A7A7A7", opacity: 0.2, line: { width: 0 } },
                            ],
                        }),
                        Plotly.newPlot(C, N, S);
                }
                (p.onchange = function () {
                    var e = this.value;
                    if ("UTC" == e) w(l.time_obs, l.time_fcd, l.time_fch, UTCTimeMap, u, UTCTimePlot);
                    else if ("Geo Local" == e) {
                        var t = moment
                                .utc(UTCTimeMap)
                                .subtract({ hours: Math.abs(r) })
                                .format("YYYY-MM-DD HH:mm z")
                                .slice(0, 16),
                            o = moment
                                .utc(u)
                                .subtract({ hours: Math.abs(r) })
                                .format("YYYY-MM-DD HH:mm z")
                                .slice(0, 16),
                            i = moment
                                .utc(UTCTimePlot)
                                .subtract({ hours: Math.abs(r) })
                                .format("YYYY-MM-DD HH:mm z")
                                .slice(0, 16);
                        w(l.geo_time_obs, l.geo_time_fcd, l.geo_time_fch, t, o, i);
                    } else if (e == h) {
                        UTCTimeMap.length < 20 && (UTCTimeMap += "Z");
                        var a = moment(new Date(UTCTimeMap).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                            c = moment(new Date(u).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                            s = moment(new Date(UTCTimePlot).toLocaleString()).format("YYYY-MM-DD HH:mm");
                        w(l.local_time_obs, l.local_time_fcd, l.local_time_fch, a, c, s);
                    }
                }),
                    UTCTimeMap.length < 20 && (UTCTimeMap += "Z");
                var z = moment(new Date(UTCTimeMap).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                    g = moment(new Date(u).toLocaleString()).format("YYYY-MM-DD HH:mm"),
                    Y = moment(new Date(UTCTimePlot).toLocaleString()).format("YYYY-MM-DD HH:mm");
                w(l.local_time_obs, l.local_time_fcd, l.local_time_fch, z, g, Y);
            });
    }
    f(), t.openPopup();
}
btn_wx.setAttribute("id", "button"),
    (btn_wx.className = "btn_wx"),
    (btn_wx.innerHTML = "Weather"),
    div.appendChild(btn_wx),
    (wx_station.onAdd = function () {
        fetch(wx_keys)
            .then(function (e) {
                return e.json();
            })
            .then(function (e) {
                var t = JSON.parse(e.wmo),
                    o = JSON.parse(e.lats),
                    r = JSON.parse(e.lons),
                    i = JSON.parse(e.elev),
                    a = JSON.parse(e.ffmc_obs),
                    c = JSON.parse(e.temp_obs),
                    s = JSON.parse(e.tz_correct);
                for (index = 0; index < o.length; ++index) {
                    var l = ["#ff6760", "#ffff73", "#63a75c"];
                    -99 != c[index] && -99 != a[index] ? (color = l[2]) : -99 != c[index] && -99 == a[index] ? (color = l[1]) : (color = l[0]),
                        wx_station.addLayer(
                            L.circle([o[index], r[index]], {
                                radius: 4e3,
                                weight: 0.8,
                                color: "black",
                                fillColor: color,
                                fillOpacity: 1,
                                customId: t[index].toString(),
                                customTZ: Math.abs(s[index]).toString(),
                                customLAT: o[index].toString(),
                                customLON: r[index].toString(),
                                customEL: i[index].toString(),
                            })
                                .bindPopup(div, { maxWidth: "auto", maxHeight: "auto" })
                                .on("click", circleClick)
                        );
                }
            });
    });
