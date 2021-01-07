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

const fwfmodellocation = L.marker([51.5, -0.09],{icon: redIcon}).bindPopup("<b>Hello!</b><br />I am the closest model grid point to <br /> where you clicked or searched on the map.");
const fwfclicklocation = L.marker().bindPopup("<b>Hello!</b><br />I am where you clicked <br /> or searched on the map.");

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




                        function makeplotly(n, o, UTCTimeMap) {
                            var buff = 0.2
                            for (var t = n.XLAT, e = n.XLONG, l = [], a = [], r = [(r = [t.length, t[0].length])[1], r[0]], c = 0; c < t.length; c++) l = l.concat(t[c]);
                            for (c = 0; c < e.length; c++) a = a.concat(e[c]);
                            var i = t.map(function (n, o) {
                                return [n, e[o]];
                            });
                            var s = new KDBush(i);
                            point_list.push(o);
                            file_list.push(n);
                            var u = s.range(o[0] - buff, o[1] - buff, o[0] + buff, o[1] + buff).map((n) => i[n]);
                            (ll_diff = []),
                                (function (n, o) {
                                    for (var t = 0; t < n.length; t++) {
                                        var e = Math.abs(parseFloat(n[t][0]) - o[0]) + Math.abs(parseFloat(n[t][1]) - o[1]);
                                        ll_diff.push(e);
                                    }
                                })(u, o);

                            hh = ll_diff.indexOf(Math.min(...ll_diff));
                            var m = s.range(o[0] - buff, o[1] - buff, o[0] + buff, o[1] + buff);
                            h = m[hh]
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
                                            return Math.round(o / t[e]) % n;
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
                                        return Math.round(o / t[e]) % n;
                                    });
                                })(r, m[h], f(m[h])),

                        
                                x = y[1],
                                _ = y[0],
                                w = n.XLAT[h], 
                                v = n.XLONG[h],
                                time = n.Time,
                                z = n.Day,
                                C = document.getElementById("plot_fwi"),
                                F = JSON.parse(n.ffmc).map(function (n, o) {
                                    return n[h];
                                }),                      
                                R = JSON.parse(n.isi).map(function (n, o) {
                                    return n[h];
                                }),
                                // F = F.map(Number) 
                                L = JSON.parse(n.fwi).map(function (n, o) {
                                    return n[h];
                                }),
                                M = JSON.parse(n.temp).map(function (n, o) {
                                    return n[h];
                                }),
                                rh = JSON.parse(n.rh).map(function (n, o) {
                                    return n[h];
                                }),
                                wsp = JSON.parse(n.ws).map(function (n, o) {
                                    return n[h];
                                }),
                                wdir = JSON.parse(n.wdir).map(function (n, o) {
                                    return n[h];
                                }),
                                qpf = JSON.parse(n.precip).map(function (n, o) {
                                    return n[h];
                                }),
                                j = JSON.parse(n.dmc).map(function (n, o) {
                                    return n[h];
                                }),
                                b = JSON.parse(n.dc).map(function (n, o) {
                                    return n[h];
                                }),
                                k = JSON.parse(n.bui).map(function (n, o) {
                                    return n[h];
                                }),
                                fwi = JSON.parse(n.fwi).map(function (n, o) {
                                    return n[h];
                                }),
                                dsr = JSON.parse(n.dsr).map(function (n) {
                                    return n[h];
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
                                    (wsp = { x: time, y: wsp, type: "scatter", line: { color: "202020" }, yaxis: "y3",  name: "WSP (km/hr)" }),
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
                                    title: "Fire Weather Forecast <br> Lat: " + w.slice(0,6) + ", Long: " + v.slice(0,8),
                                    titlefont: { color: "#616161", autosize: !0 },
                                    showlegend: !1,
                                    yaxis7: { domain: [0.67, 0.78], title: { text: "FFMC", font: { color: "ff7f0e" } }, tickfont: {color: "ff7f0e"}},
                                    yaxis6: { domain: [0.56, 0.65], title: { text: "ISI", font: { color: "9467bd" } }, tickfont: {color: "9467bd"}},
                                    yaxis5: { domain: [0.45, 0.54], title: { text: "Temp<br>(C)", font: { color: "d62728" } }, tickfont: {color: "d62728"}},
                                    yaxis4: { domain: [0.34, 0.43],  title: { text: "RH<br>(%)", font: { color: "1f77b4" } }, tickfont: {color: "1f77b4"}},
                                    yaxis3: { domain: [0.23, 0.32], title: { text: "WSP<br>(km/hr)", font: { color: "202020" } } , tickfont: {color: "202020"}},
                                    yaxis2: { domain: [0.12, 0.21], title: { text: "WDIR<br>(deg)", font: { color: "7f7f7f" } }, tickfont: {color: "7f7f7f"}, range: [0, 360], tickvals:[0, 90, 180, 270, 360]},
                                    yaxis1: { domain: [0, 0.09], title: { text: "QPF<br>(mm)", font: { color: "2ca02c" } }, tickfont: {color: "2ca02c"}},
                                    xaxis: { title: "Date (UTC)" },
                                    shapes: [{
                                        type: 'line',
                                        x0: UTCTimeMap,
                                        y0: 0,
                                        x1: UTCTimeMap,
                                        yref: 'paper',
                                        y1: 0.8,
                                        line: {
                                          color: 'grey',
                                          width: 1.5,
                                          dash: 'dot'
                                        }},
                                        {
                                            type: 'rect',
                                            xref: 'x',
                                            yref: 'paper',
                                            x0: tinital,
                                            y0: 0,
                                            x1: UTCTimePlot,
                                            y1: 0.8,
                                            fillcolor: '#A7A7A7',
                                            opacity: 0.2,
                                            line: {
                                                width: 0
                                            }
                                        },],
                                };
                        
                                fwfmodellocation.setLatLng([w, v]).addTo(map)
                            Plotly.react(C, N, S);
                        }

function makeplots(n) {

    (json_dir = "static/json/fwf-zone-merge.json"),
        fetch(n)
            .then(function (n) {
                return n.json();
            })
            .then(function (n) {
                var o = [50.6745, -120.3273];
                // var o = [49.22, -126.37];
                fwfclicklocation.setLatLng(o).addTo(map), makeplotly(n, o, UTCTimeMap);
            })
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
                    map.on("click", function (o) {
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
                                var __ = tt[pp][yy];
                                (zone_json_d3 = n.slice(0, 14)),
                                (zone_json_d3 = zone_json_d3 + __ + n.slice(16, 36)),
                                fetch(zone_json_d3, { cache: "default"})
                                    .then(function (nn) {
                                        return nn.json();
                                    })
                                    .then(function (nn) {
                                        makeplotly(nn, ee, UTCTimeMap);
                                    }),
                                loaded_zones_d3.push(__)

                            } else {        
                            (zone_json = n.slice(0, 14)),
                            (zone_json = zone_json + _ + n.slice(16, 30) + '2.json'),
                            fetch(zone_json, { cache: "default"})
                                .then(function (n) {
                                    return n.json();
                                })
                                .then(function (n) {
                                    makeplotly(n, e, UTCTimeMap);
                                }),
                            loaded_zones.push(_)
                    }});
                
                    function searchcontrol(o) {
                        map.flyTo(o)
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
                                var __ = tt[pp][yy];
                                (zone_json_d3 = n.slice(0, 14)),
                                (zone_json_d3 = zone_json_d3 + __ + n.slice(16, 36)),
                                fetch(zone_json_d3, { cache: "default"})
                                    .then(function (nn) {
                                        return nn.json();
                                    })
                                    .then(function (nn) {
                                        makeplotly(nn, ee, UTCTimeMap);
                                    }),
                                loaded_zones_d3.push(__)

                            } else {        
                            (zone_json = n.slice(0, 14)),
                            (zone_json = zone_json + _ + n.slice(16, 30) + '2.json'),
                            fetch(zone_json, { cache: "default"})
                                .then(function (n) {
                                    return n.json();
                                })
                                .then(function (n) {
                                    makeplotly(n, e, UTCTimeMap);
                                }),
                            loaded_zones.push(_)
                    }
                        };

                        control._searchfunctionCallBack = function (searchkeywords){
                            if (!searchkeywords) {
                                searchkeywords = "The search call back is clicked !!"
                            }
                            var o = searchkeywords.split(',').map(Number);
                            searchcontrol(o);
                        }

                        map.addControl(control);

            
        (window.onresize = function () {
            Plotly.Plots.resize(plot_fwi);
        });
});
}
window.onload = function () {
    makeplots(json_fwf);
};

