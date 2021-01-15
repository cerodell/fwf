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


div2.className = "wx-plot2";
div2.style.width = width;
div2.style.height = height;
div2.setAttribute("id", "wx_plot2");

// window.onload = function() {
//     alert(document.getElementById("wx_plot2"));
//     console.log('alert')
// };

// console.log(div2);
// console.log(TESTER);



// const fwfmodellocation = L.marker([51.5, -0.09],{icon: redIcon});
// fwfmodellocation.bindPopup(div2, {maxWidth: "auto", maxHeight: "auto"});
// fwfmodellocation.setZIndexOffset(1000);
const fwfclicklocation = L.marker().bindPopup("<b>Hello!</b><br />I am where you clicked <br /> or searched on the map.");
fwfclicklocation.setZIndexOffset(10);

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
    console.log(clickedCircle);
    var ll = clickedCircle._latlng
    console.log(ll);

    var o = [ll.lat,ll.lng]
    console.log(o);

    fetch(json_dir).then(function(response){
        return response.json();
    }).then(function(n){  

    var C = document.getElementById('wx_plot2')
    console.log(C);
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

    var hh = ll_diff.indexOf(Math.min(...ll_diff));
    var m = s.range(o[0] - buff, o[1] - buff, o[0] + buff, o[1] + buff);
    var h = m[hh];
    var w = n.XLAT[h];
    var v = n.XLONG[h];
    console.log(w);
    console.log(v);

    fwfmodellocation.setLatLng([w, v]).addTo(map);
    
    
})
}







var fwfmodellocation;             

function makeplots(n) {

    (json_dir = "static/json/fwf-zone-merge.json"),
        fetch(n)
            .then(function (n) {
                return n.json();
            })
            .then(function (n) {
                var o = [50.6745, -120.3273];
                // var o = [49.22, -126.37];
                // fwfclicklocation.setLatLng(o).addTo(map), makeplotly(n, o, UTCTimeMap);
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
                                var __ = tt[pp][yy];
                                (zone_json_d3 = n.slice(0, 14)),
                                (zone_json_d3 = zone_json_d3 + __ + n.slice(16, 36)),
                                console.log(zone_json_d3);
                                fwfmodellocation = new L.marker([ee[0],ee[1]],{icon: redIcon, customId: zone_json_d3});
                                fwfmodellocation.bindPopup(div2, {maxWidth: "auto", maxHeight: "auto"});
                                fwfmodellocation.setZIndexOffset(1000);
                                fwfmodellocation.on('click', makeplotly).addTo(map);
                                // fetch(zone_json_d3, { cache: "default"})
                                //     .then(function (nn) {
                                //         return nn.json();
                                //     })
                                //     .then(function (nn) {
                                //         console.log(nn);
                                //         console.log(ee);
                                //     }),
                                loaded_zones_d3.push(__);

                            } else {        
                            (zone_json = n.slice(0, 14)),
                            (zone_json = zone_json + _ + n.slice(16, 30) + '2.json'),
                            fwfmodellocation = new L.marker([e[0],e[1]],{icon: redIcon, customId: zone_json});
                            fwfmodellocation.bindPopup(div2, {maxWidth: "auto", maxHeight: "auto"});
                            fwfmodellocation.setZIndexOffset(1000);
                            fwfmodellocation.on('click', makeplotly).addTo(map);
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
                                var __ = tt[pp][yy];
                                (zone_json_d3 = n.slice(0, 14)),
                                (zone_json_d3 = zone_json_d3 + __ + n.slice(16, 36)),
                                fwfmodellocation = new L.marker([e[0],e[1]],{icon: redIcon, customId: zone_json_d3});
                                fwfmodellocation.bindPopup(div2, {maxWidth: "auto", maxHeight: "auto"});
                                fwfmodellocation.setZIndexOffset(1000);
                                fwfmodellocation.on('click', makeplotly).addTo(map);
                                loaded_zones_d3.push(__);

                            } else {        
                            (zone_json = n.slice(0, 14)),
                            (zone_json = zone_json + _ + n.slice(16, 30) + '2.json'),
                            fwfmodellocation = new L.marker([e[0],e[1]],{icon: redIcon, customId: zone_json});
                            fwfmodellocation.bindPopup(div2, {maxWidth: "auto", maxHeight: "auto"});
                            fwfmodellocation.setZIndexOffset(1000);
                            fwfmodellocation.on('click', makeplotly).addTo(map);
                            loaded_zones.push(_);
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

            
        // (window.onresize = function () {
        //     Plotly.Plots.resize(plot_fwi);
        // });
});
}
window.onload = function () {
    makeplots(json_fwf);

};
