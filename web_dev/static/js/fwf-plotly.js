const fwflocation = L.marker();
function makeplotly(n, o) {
    for (var t = n.XLAT, e = n.XLONG, l = [], a = [], r = [(r = [t.length, t[0].length])[1], r[0]], c = 0; c < t.length; c++) l = l.concat(t[c]);
    for (c = 0; c < e.length; c++) a = a.concat(e[c]);
    var i = l.map(function (n, o) {
        return [n, a[o]];
    });
    const s = new KDBush(i);
    console.log(s), console.log(o);
    const u = s.range(o[0], o[1], o[0] + 0.5, o[1] + 0.5).map((n) => i[n]);
    (ll_diff = []),
        (function (n, o) {
            for (var t = 0; t < n.length; t++) {
                var e = Math.abs(n[t][0] - o[0]) + Math.abs(n[t][1] - o[1]);
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
        F = n.Time,
        z = n.Day,
        C = document.getElementById("plot_fwi"),
        D = n.FFMC.map(function (n, o) {
            return n[x][_];
        }),
        I = n.ISI.map(function (n, o) {
            return n[x][_];
        }),
        L = n.FWI.map(function (n, o) {
            return n[x][_];
        }),
        M = n.DSR.map(function (n, o) {
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
        T = [
            ["DMC", "DC", "BUI"],
            [j[0], b[0], k[0]],
            [j[1], b[1], k[1]],
        ],
        N =
            ((D = { x: F, y: D, type: "scatter", line: { color: "ff8500" }, yaxis: "y4", name: "FFMC" }),
            (I = { x: F, y: I, type: "scatter", line: { color: "9900cc" }, yaxis: "y3", name: "ISI" }),
            (L = { x: F, y: L, type: "scatter", line: { color: "0052cc" }, yaxis: "y2", name: "FWI" }),
            (M = { x: F, y: M, type: "scatter", line: { color: "CD2C0A" }, yaxis: "y1", name: "DSR" }),
            [
                {
                    type: "table",
                    header: { values: [["<b>Index/Code</b>"], [z[0]], [z[1]]], align: "center", line: { width: 1, color: "616161" }, fill: { color: "6F737C" }, font: { family: "inherit", size: 12, color: "white" } },
                    cells: { values: T, align: "center", line: { color: "616161", width: 1 }, fill: { color: [["white", "white", "white", "white", "white"]] }, font: { family: "inherit", size: 11, color: ["616161"] } },
                    xaxis: "x",
                    yaxis: "y",
                    domain: { x: [0, 1], y: [0.8, 1] },
                },
                D,
                I,
                L,
                M,
            ]),
        S = {
            title: "Fire Weather Forecast <br> Lat: " + w.toFixed(3) + ", Long: " + v.toFixed(3),
            titlefont: { color: "#7f7f7f", autosize: !0 },
            showlegend: !1,
            yaxis4: { domain: [0.6, 0.8], title: { text: "FFMC", font: { color: "ff8500" } } },
            yaxis3: { domain: [0.4, 0.6], title: { text: "ISI", font: { color: "9900cc" } } },
            yaxis2: { domain: [0.2, 0.4], title: { text: "FWI", font: { color: "0052cc" } } },
            yaxis1: { domain: [0, 0.2], title: { text: "DSR", font: { color: "CD2C0A" } } },
            xaxis: { title: "Date (UTC)" },
        };
    Plotly.react(C, N, S);
}
function makeplots(n) {
    (json_dir = "fwf-zone.json"),
        fetch(n, { cache: "force-cache" })
            .then(function (n) {
                return n.json();
            })
            .then(function (n) {
                var o = [50.632, -120.3333];
                fwflocation.setLatLng(o).addTo(map), makeplotly(n, o), console.log(n);
            }),
        fetch(json_dir, { cache: "force-cache" })
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
                (loaded_zones = ["db"]),
                    console.log(loaded_zones),
                    map.on("click", function (o) {
                        fwflocation.setLatLng(o.latlng).addTo(map);
                        var e = [parseFloat(o.latlng.lat.toFixed(4)), parseFloat(o.latlng.lng.toFixed(4))];
                        const l = u.range(e[0], e[1], e[0] + 0.5, e[1] + 0.5).map((n) => s[n]);
                        (ll_diff = []),
                            (function (n, o) {
                                for (var t = 0; t < n.length; t++) {
                                    var e = Math.abs(n[t][0] - o[0]) + Math.abs(n[t][1] - o[1]);
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
                            fetch(zone_json, { cache: "force-cache" })
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
            }),
        (window.onresize = function () {
            Plotly.Plots.resize(plot_fwi);
        });
}
window.onload = function () {
    makeplots(json_fwf);
};
