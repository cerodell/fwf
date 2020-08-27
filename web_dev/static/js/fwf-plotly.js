var redIcon = new L.Icon({
    iconUrl: 'marker-icon-2x-red.png',
    shadowUrl: 'marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });
console.log(redIcon);
const fwfmodellocation = L.marker({icon: redIcon }).bindPopup("<b>Hello!</b><br />I am the closet model grid point<br /> to where you clicked on the map.");
const fwfclicklocation = L.marker().bindPopup("<b>Hello!</b><br />I am where you clicked <br /> or searched on the map.");

var blah = Math.floor((new Date()).getTime() / 1000)
console.log(blah)

function makeplotly(n, o) {
    for (var t = n.XLAT, e = n.XLONG, l = [], a = [], r = [(r = [t.length, t[0].length])[1], r[0]], c = 0; c < t.length; c++) l = l.concat(t[c]);
    for (c = 0; c < e.length; c++) a = a.concat(e[c]);
    var i = l.map(function (n, o) {
        return [n, a[o]];
    });
    const s = new KDBush(i);
    console.log('Start')
    console.log(s), console.log(o);
    const u = s.range(o[0], o[1], o[0] + 0.5, o[1] + 0.5).map((n) => i[n]);

    console.log(u);
    (ll_diff = []),
        (function (n, o) {
            for (var t = 0; t < n.length; t++) {
                var e = (n[t][0] - o[0]) + (n[t][1] - o[1]);
                ll_diff.push(e);
            }
        })(u, o);
    var h = 0,
        d = ll_diff[0];
    for (c = 1; c < ll_diff.length; c++) ll_diff[c] < d && ((d = ll_diff[c]), (h = c));
    const m = s.range(o[0], o[1], o[0] + 0.5, o[1] + 0.5);
    var g, p;
    f =
        ((p = (g = r).reduce(
            function (n, o) {
                return n.concat(n[n.length - 1] * o);
            },
            [1]
        )),
        function (n) {
            return (function (n, o, t) {
                return n.map(function (n, e) {
                    return Math.floor(o / t[e]) % n;
                });
            })(g, n, p);
        });
    var y = (function (n, o) {
            var t = n.reduce(
                function (n, o) {
                    return n.concat(n[n.length - 1] * o);
                },
                [1]
            );
            return n.map(function (n, e) {
                return Math.floor(o / t[e]) % n;
            });
        })(r, m[h], f(m[h])),
        x = y[1],
        _ = y[0],
        w = n.XLAT[x][_],
        v = n.XLONG[x][_],
        time = n.Time,
        z = n.Day,
        C = document.getElementById("plot_fwi"),
        F = n.FFMC.map(function (n, o) {
            return n[x][_];
        }),
        R = n.ISI.map(function (n, o) {
            return n[x][_];
        }),
        L = n.FWI.map(function (n, o) {
            return n[x][_];
        }),
        M = n.temp.map(function (n, o) {
            return n[x][_];
        }),
        rh = n.rh.map(function (n, o) {
            return n[x][_];
        }),
        wsp = n.wsp.map(function (n, o) {
            return n[x][_];
        }),
        wdir = n.wdir.map(function (n, o) {
            return n[x][_];
        }),
        qpf = n.qpf.map(function (n, o) {
            return n[x][_];
        }),
        j = n.DMC.map(function (n, o) {
            return n[x][_];
        }),
        b = n.DC.map(function (n, o) {
            return n[x][_];
        }),
        k = n.BUI.map(function (n, o) {
            return n[x][_];
        }),
        fwi = n.FWI.map(function (n, o) {
            return n[x][_];
        }),
        dsr = n.DSR.map(function (n, o) {
            return n[x][_];
        }),

        T = [
            ["DMC", "DC", "BUI", "FWI", "DSR"],
            [j[0], b[0], k[0], fwi[0], dsr[0]],
            [j[1], b[1], k[1], fwi[1], dsr[1]],
        ],
        N =
            ((F = { x: time, y: F, type: "scatter", line: { color: "ff7f0e" }, yaxis: "y7", name: "FFMC" }),
            (R = { x: time, y: R, type: "scatter", line: { color: "9467bd" }, yaxis: "y6", name: "ISI" }),
            (M = { x: time, y: M, type: "scatter", line: { color: "d62728" }, yaxis: "y5", name: "Temp (C)" }),
            (rh = { x: time, y: rh, type: "scatter", line: { color: "1f77b4" }, yaxis: "y4", name: "RH (%)" }),
            (wsp = { x: time, y: wsp, type: "scatter", line: { color: "202020" }, yaxis: "y3", name: "WSP (km/hr)" }),
            (wdir = { x: time, y: wdir, type: "scatter", line: { color: "7f7f7f" }, yaxis: "y2", name: "WDIR (deg)" }),
            (qpf = { x: time, y: qpf, type: "scatter", line: { color: "2ca02c" }, yaxis: "y1", name: "QPF (mm)" }),

            [
                {
                    type: "table",
                    header: { values: [["<b>Index/Code</b>"], [z[0]], [z[1]]], align: "center", line: { width: 1, color: "616161" }, fill: { color: "7f7f7f" }, font: { family: "inherit", size: 12, color: "white" } },
                    cells: { values: T, align: "center", line: { color: "616161", width: 1 }, fill: { color: [["white", "white", "white", "white", "white"]] }, font: { family: "inherit", size: 11, color: ["616161"] } },
                    xaxis: "x",
                    yaxis: "y",
                    domain: { x: [0, 1], y: [0.8, 1] },
                },
                F,
                R,
                rh,
                M,
                wsp,
                wdir,
                qpf,
            ]),
        S = {
            autosize: true, 
            title: "Fire Weather Forecast <br> Lat: " + w.toFixed(3) + ", Long: " + v.toFixed(3),
            titlefont: { color: "#616161", autosize: !0 },
            showlegend: !1,
            yaxis7: { domain: [0.67, 0.78], title: { text: "FFMC", font: { color: "ff7f0e" } }, tickfont: {color: "ff7f0e"}},
            yaxis6: { domain: [0.56, 0.65], title: { text: "ISI", font: { color: "9467bd" } }, tickfont: {color: "9467bd"}},
            yaxis5: { domain: [0.45, 0.54], title: { text: "Temp", font: { color: "d62728" } }, tickfont: {color: "d62728"}},
            yaxis4: { domain: [0.34, 0.43],  title: { text: "RH", font: { color: "1f77b4" } }, tickfont: {color: "1f77b4"}},
            yaxis3: { domain: [0.23, 0.32], title: { text: "WSP", font: { color: "202020" } } , tickfont: {color: "202020"}},
            yaxis2: { domain: [0.12, 0.21], title: { text: "WDIR", font: { color: "7f7f7f" } }, tickfont: {color: "7f7f7f"}},
            yaxis1: { domain: [0, 0.09], title: { text: "QPF", font: { color: "2ca02c" } }, tickfont: {color: "2ca02c"}},
            xaxis: { title: "Date (UTC)" },
        };
        fwfmodellocation.setLatLng([w.toFixed(3), v.toFixed(3)]).addTo(map)
    Plotly.react(C, N, S);
}
function makeplots(n) {
    (json_dir = "fwf-zone.json"),
        fetch(n, { cache: "default" })
            .then(function (n) {
                return n.json();
            })
            .then(function (n) {
                var o = [50.6599, -120.3552];
                fwfclicklocation.setLatLng(o).addTo(map), makeplotly(n, o), console.log(n);
            }),
        fetch(json_dir, { cache: "default"})
            .then(function (n) {
                return n.json();
            })
            .then(function (o) {
                for (var t = o.ZONE, e = o.XLAT, l = o.XLONG, a = [], r = [], c = [(c = [e.length, e[0].length])[1], c[0]], i = 0; i < e.length; i++) a = a.concat(e[i]);
                for (i = 0; i < l.length; i++) r = r.concat(l[i]);
                (a = a.map(Number)), (r = r.map(Number));
                var s = a.map(function (n, o) {
                    return [n, r[o]];
                });
                const u = new KDBush(s);
                (loaded_zones = ["he"]),
                    console.log(loaded_zones),
                    map.on("click", function (o) {
                        fwfclicklocation.setLatLng(o.latlng).addTo(map);
                        var e = [parseFloat(o.latlng.lat.toFixed(4)), parseFloat(o.latlng.lng.toFixed(4))];
                        const l = u.range(e[0], e[1], e[0] + 0.5, e[1] + 0.5).map((n) => s[n]);
                        (ll_diff = []),
                            (function (n, o) {
                                for (var t = 0; t < n.length; t++) {
                                    var e = (n[t][0] - o[0]) + (n[t][1] - o[1]);
                                    ll_diff.push(e);
                                }
                            })(l, e);
                        for (var a = 0, r = ll_diff[0], i = 1; i < ll_diff.length; i++) ll_diff[i] < r && ((r = ll_diff[i]), (a = i));
                        const h = u.range(e[0], e[1], e[0] + 0.5, e[1] + 0.5);
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
                                        return Math.floor(o / t[e]) % n;
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
                                    return Math.floor(o / t[e]) % n;
                                });
                            })(c, h[a], f(h[a])),
                            p = g[1],
                            y = g[0],
                            x = [p, y];
                        console.log(x);
                        var _ = t[p][y];
                        console.log(_),
                            (zone_json = n.slice(0, 14)),
                            (zone_json = zone_json + _ + n.slice(16, 32)),
                            console.log(zone_json),
                            fetch(zone_json, { cache: "default" })
                                .then(function (n) {
                                    return n.json();
                                })
                                .then(function (n) {
                                    makeplotly(n, e);
                                }),
                            -1 == loaded_zones.indexOf(_) ? console.log("item not exist") : console.log("item exist"),
                            loaded_zones.push(_),
                            console.log(loaded_zones);
                    });
                    function searchcontrol(o) {
                        map.flyTo(o)
                        fwfclicklocation.setLatLng(o).addTo(map);
                        var e = [parseFloat(o[0]), parseFloat(o[1])];
                        const l = u.range(e[0]-0.25, e[1]-0.25, e[0] + 0.25, e[1] + 0.25).map((n) => s[n]);
                        (ll_diff = []),
                            (function (n, o) {
                                for (var t = 0; t < n.length; t++) {
                                    var e = (n[t][0] - o[0]) + (n[t][1] - o[1]);
                                    ll_diff.push(e);
                                }
                            })(l, e);
                        for (var a = 0, r = ll_diff[0], i = 1; i < ll_diff.length; i++) ll_diff[i] < r && ((r = ll_diff[i]), (a = i));
                        const h = u.range(e[0], e[1], e[0] + 0.5, e[1] + 0.5);
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
                                        return Math.floor(o / t[e]) % n;
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
                                    return Math.floor(o / t[e]) % n;
                                });
                            })(c, h[a], f(h[a])),
                            p = g[1],
                            y = g[0],
                            x = [p, y];
                        console.log(x);
                        var _ = t[p][y];
                        console.log(_),
                            (zone_json = n.slice(0, 14)),
                            (zone_json = zone_json + _ + n.slice(16, 32)),
                            console.log(zone_json),
                            fetch(zone_json, { cache: "default"})
                                .then(function (n) {
                                    return n.json();
                                })
                                .then(function (n) {
                                    makeplotly(n, e);
                                }),
                            -1 == loaded_zones.indexOf(_) ? console.log("item not exist") : console.log("item exist"),
                            loaded_zones.push(_),
                            console.log(loaded_zones)
                        };
                        var searchboxControl=createSearchboxControl();
                        var control = new searchboxControl({
                            sidebarTitleText: 'Information',
                            sidebarMenuItems: {
                                Items: [
                                    { type: "link", name: "Smoke Forecasts", href: "https://firesmoke.ca/", icon: "icon-fire" },
                                    { type: "link", name: "Weather Research Forecast Team", href: "https://weather.eos.ubc.ca/cgi-bin/index.cgi", icon: "icon-cloudy" },
                                    { type: "link", name: "Contact Inforamtion", href: "https://firesmoke.ca/contact/", icon: "icon-phone" },

                                ]
                            }
                        });

                        control._searchfunctionCallBack = function (searchkeywords){
                            if (!searchkeywords) {
                                searchkeywords = "The search call back is clicked !!"
                            }
                            // alert(searchkeywords);
                            var o = searchkeywords.split(',').map(Number);
                            searchcontrol(o);
                            console.log(o);
                        }

                        map.addControl(control);

            }),
        (window.onresize = function () {
            Plotly.Plots.resize(plot_fwi);
        });
}
window.onload = function () {
    makeplots(json_fwf);
};


